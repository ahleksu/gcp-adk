# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio
import concurrent.futures
import datetime
from zoneinfo import ZoneInfo

import aiohttp
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types


MODEL = "gemini-3.6-flash"

# WMO Weather interpretation codes → human-readable descriptions.
_WMO_WEATHER_CODES: dict[int, str] = {
    0: "clear sky",
    1: "mainly clear",
    2: "partly cloudy",
    3: "overcast",
    45: "foggy",
    48: "depositing rime fog",
    51: "light drizzle",
    53: "moderate drizzle",
    55: "dense drizzle",
    56: "light freezing drizzle",
    57: "dense freezing drizzle",
    61: "slight rain",
    63: "moderate rain",
    65: "heavy rain",
    66: "light freezing rain",
    67: "heavy freezing rain",
    71: "slight snowfall",
    73: "moderate snowfall",
    75: "heavy snowfall",
    77: "snow grains",
    80: "slight rain showers",
    81: "moderate rain showers",
    82: "violent rain showers",
    85: "slight snow showers",
    86: "heavy snow showers",
    95: "thunderstorm",
    96: "thunderstorm with slight hail",
    99: "thunderstorm with heavy hail",
}

_GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
_HTTP_TIMEOUT = aiohttp.ClientTimeout(total=30)

# Thread-pool for running async HTTP calls from synchronous ADK tool functions.
# ADK may invoke tools from within a running event loop, so asyncio.run() would
# raise "This event loop is already running".  Instead we spin up a fresh loop
# on a worker thread.
_executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)


def _run_async(coro):
    """Run an async coroutine from sync code, even inside a running event loop."""
    try:
        asyncio.get_running_loop()
        # Already inside an event loop — offload to a worker thread.
        future = _executor.submit(asyncio.run, coro)
        return future.result(timeout=60)
    except RuntimeError:
        # No running loop — safe to use asyncio.run directly.
        return asyncio.run(coro)


async def _geocode(location: str) -> dict | None:
    """Resolve a location name to coordinates and timezone via Open-Meteo."""
    params = {"name": location, "count": 1, "language": "en", "format": "json"}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(_GEOCODING_URL, params=params, timeout=_HTTP_TIMEOUT) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                results = data.get("results")
                if not results:
                    return None
                return results[0]
    except (asyncio.TimeoutError, aiohttp.ClientError):
        return None


def get_weather(query: str) -> str:
    """Get real-time weather for any location using the Open-Meteo API.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the current weather information for the queried location.
    """

    async def _fetch() -> str:
        geo = await _geocode(query)
        if geo is None:
            return f"Sorry, I couldn't find location information for: {query}."

        lat = geo["latitude"]
        lon = geo["longitude"]
        name = geo.get("name", query)
        country = geo.get("country", "")

        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,weather_code",
            "timezone": "auto",
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(_FORECAST_URL, params=params, timeout=_HTTP_TIMEOUT) as resp:
                    if resp.status != 200:
                        return f"Sorry, I couldn't fetch weather data for {name}."
                    data = await resp.json()
        except (asyncio.TimeoutError, aiohttp.ClientError):
            return f"Sorry, the weather service timed out for {name}. Please try again."

        current = data.get("current", {})
        temp_c = current.get("temperature_2m")
        weather_code = current.get("weather_code")
        temp_unit = data.get("current_units", {}).get("temperature_2m", "°C")

        if temp_c is None:
            return f"Sorry, weather data was incomplete for {name}."

        temp_f = round(temp_c * 9 / 5 + 32, 1)
        condition = _WMO_WEATHER_CODES.get(weather_code, "unknown conditions")
        location_label = f"{name}, {country}" if country else name

        return (
            f"Current weather in {location_label}: "
            f"{temp_c}{temp_unit} ({temp_f}°F), {condition}."
        )

    try:
        return _run_async(_fetch())
    except TimeoutError:
        return f"Sorry, the weather service is not responding for: {query}. Please try again."


def get_current_time(query: str) -> str:
    """Get the current local time for any location using Open-Meteo geocoding.

    Args:
        query: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """

    async def _fetch() -> str:
        geo = await _geocode(query)
        if geo is None:
            return f"Sorry, I couldn't find timezone information for: {query}."

        tz_identifier = geo.get("timezone")
        if not tz_identifier:
            return f"Sorry, timezone data is unavailable for: {query}."

        name = geo.get("name", query)
        country = geo.get("country", "")
        location_label = f"{name}, {country}" if country else name

        tz = ZoneInfo(tz_identifier)
        now = datetime.datetime.now(tz)
        return (
            f"The current time in {location_label} is "
            f"{now.strftime('%Y-%m-%d %H:%M:%S %Z (%z)')}."
        )

    try:
        return _run_async(_fetch())
    except TimeoutError:
        return f"Sorry, the time service is not responding for: {query}. Please try again."


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="You are a helpful AI assistant designed to provide accurate and useful information.",
    tools=[get_weather, get_current_time],
)

app = App(
    root_agent=root_agent,
    name="app",
)
