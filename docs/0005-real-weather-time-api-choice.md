# ADR 0005: Use Open-Meteo free APIs for weather and timezone resolution

## Status
Accepted

## Context
The agent scaffold shipped with stub tool functions (`get_weather`, `get_current_time`) that only handled hard-coded cities. We needed to replace them with real implementations that work for any user-supplied location string. Key constraints:

- Must use free, no-auth-key HTTP APIs (no secrets to manage).
- Must resolve arbitrary location names to coordinates (geocoding).
- Must return real-time weather data (temperature, conditions).
- Must determine the correct IANA timezone for any location to report local time.
- Should minimise new dependencies; `aiohttp` is already in `pyproject.toml`.

## Decision
Use **Open-Meteo** (open-meteo.com) for all three needs:

| Endpoint | Purpose |
|---|---|
| `geocoding-api.open-meteo.com/v1/search` | Resolve location name → latitude, longitude, IANA timezone |
| `api.open-meteo.com/v1/forecast` | Current weather (temperature, WMO weather code) for given coordinates |

Timezone is extracted directly from the geocoding response's `timezone` field, then used with Python's stdlib `zoneinfo.ZoneInfo` to compute local time. No additional geocoding or timezone library is needed.

HTTP calls are made with `aiohttp` (already a project dependency), wrapped in synchronous helpers using `asyncio.run()` since ADK tool functions are synchronous.

## Alternatives considered

| Alternative | Why rejected |
|---|---|
| **Nominatim (OpenStreetMap) + timezonefinder** | Requires two extra dependencies (`geopy`, `timezonefinder`). `timezonefinder` bundles ~50 MB of boundary data and has a slow first-load. Nominatim's usage policy requires a custom `User-Agent` and rate-limits to 1 req/s. |
| **wttr.in** | Returns weather as formatted text, harder to parse reliably. No structured timezone data. |
| **OpenWeatherMap free tier** | Requires an API key (secret management overhead). Free tier limited to 1,000 calls/day. |
| **WorldTimeAPI** | Only covers timezone lookup, not weather. Would still need a second API for weather. Limited city coverage. |

## Consequences

- **Easier:** No API keys to provision or rotate; no new runtime dependencies to add to `pyproject.toml`; a single provider for geocoding, weather, and timezone keeps the implementation simple.
- **Harder:** Open-Meteo is a volunteer-run project with no SLA — if it goes down, both tools degrade. Acceptable for a prototype agent but would need revisiting for production.
- **Forecloses:** Nothing significant. Switching to a keyed API later is a drop-in change inside the two tool functions.
