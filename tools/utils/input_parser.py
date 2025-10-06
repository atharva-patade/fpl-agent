"""Shared parsing utilities for LangChain tool inputs."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Tuple, Type, TypeVar

from pydantic import BaseModel, ConfigDict, ValidationError


T = TypeVar("T", bound=BaseModel)


def parse_tool_input(
    raw_input: Any,
    model: Type[T],
    *,
    primary_field: Optional[str] = None,
    aliases: Optional[Dict[str, List[str]]] = None,
    example: Optional[str] = None,
) -> Tuple[Optional[T], Optional[str]]:
    """Normalise raw tool input into a validated pydantic model.

    Args:
        raw_input: Payload supplied by LangChain or a direct caller.
        model: Pydantic model describing the expected schema.
        primary_field: Canonical key to wrap scalar inputs.
        aliases: Mapping from canonical field names to accepted aliases.
        example: Example JSON snippet for error messages.

    Returns:
        Tuple of (parsed_model, error_message). Exactly one element is non-None.
    """

    normalized, error = _normalize_input(raw_input, primary_field)
    if error:
        return None, _attach_example(error, example)

    if not isinstance(normalized, dict):
        normalized = {}

    if aliases:
        normalized = _apply_aliases(normalized, aliases)

    try:
        parsed = model(**normalized)
        return parsed, None
    except ValidationError as exc:
        return None, _format_validation_error(exc, example)


def _normalize_input(raw_input: Any, primary_field: Optional[str]) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    if raw_input is None:
        return {}, None

    if isinstance(raw_input, dict):
        return dict(raw_input), None

    if isinstance(raw_input, str):
        stripped = raw_input.strip()
        if not stripped:
            return {}, None
        if stripped.startswith("{"):
            try:
                parsed = json.loads(stripped)
            except json.JSONDecodeError as exc:
                message = (
                    f"❌ Error parsing JSON input: {exc.msg} (line {exc.lineno}, column {exc.colno})."
                )
                return None, message
            if isinstance(parsed, dict):
                return parsed, None
            return None, "❌ Error parsing JSON input: expected an object with key/value pairs."
        if primary_field:
            return {primary_field: stripped}, None
        return {"value": stripped}, None

    if isinstance(raw_input, (int, float, bool)):
        if primary_field:
            return {primary_field: raw_input}, None
        return {"value": raw_input}, None

    return None, (
        "❌ Unsupported input type. Please provide a JSON object, dictionary, or scalar "
        "value (e.g., an ID or name)."
    )


def _apply_aliases(data: Dict[str, Any], aliases: Dict[str, List[str]]) -> Dict[str, Any]:
    updated = dict(data)
    for canonical, alias_list in aliases.items():
        if canonical in updated:
            continue
        for alias in alias_list:
            if alias in updated:
                updated[canonical] = updated.pop(alias)
                break
    return updated


def _format_validation_error(exc: ValidationError, example: Optional[str]) -> str:
    bullet_points = []
    for err in exc.errors():
        loc = ".".join(str(part) for part in err.get("loc", []) if part is not None) or "input"
        msg = err.get("msg", "Invalid value")
        bullet_points.append(f"• `{loc}` – {msg}")

    message = "❌ Unable to process the provided input.\n\n**Issues detected:**\n" + "\n".join(bullet_points)
    return _attach_example(message, example)


def _attach_example(message: str, example: Optional[str]) -> str:
    if example:
        return message + f"\n\n**Example Input:**\n```json\n{example}\n```"
    return message


# ---------------------------------------------------------------------------
# Shared pydantic models for tool schemas
# ---------------------------------------------------------------------------


class PlayerSearchParams(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str


class PlayerStatsParams(BaseModel):
    model_config = ConfigDict(extra="ignore")

    player_name: str


class PlayerComparisonParams(BaseModel):
    model_config = ConfigDict(extra="ignore")

    player1_name: str
    player2_name: str


class BestPlayersParams(BaseModel):
    model_config = ConfigDict(extra="ignore")

    position: str
    max_price: float = 15.0
    min_price: float = 0.0
    min_minutes: int = 200


class GameweekLookupParams(BaseModel):
    model_config = ConfigDict(extra="ignore")

    gameweek_number: int


class TeamIdParams(BaseModel):
    model_config = ConfigDict(extra="ignore")

    team_id: int


class TeamIdGameweekParams(TeamIdParams):
    gameweek: Optional[int] = None


class TeamTransfersParams(TeamIdParams):
    limit: int = 10


class TeamPerformanceParams(TeamIdParams):
    last_n_weeks: int = 5