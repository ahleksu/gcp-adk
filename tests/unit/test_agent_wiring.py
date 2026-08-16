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
"""Structural smoke tests for the agent definition.

These import and inspect the agent wiring only — no network/LLM call is
made, so this suite runs without a GOOGLE_API_KEY. Behavioral checks on
what the model actually says belong in tests/eval, not here.
"""

from app.agent import MODEL, app, root_agent


def test_root_agent_is_wired_into_app() -> None:
    assert app.root_agent is root_agent


def test_root_agent_has_a_model_and_instruction() -> None:
    assert root_agent.model.model == MODEL
    assert root_agent.instruction


def test_root_agent_exposes_its_tools() -> None:
    tool_names = {tool.__name__ for tool in root_agent.tools}
    assert tool_names == {"get_weather", "get_current_time"}
