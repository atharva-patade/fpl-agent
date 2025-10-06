"""Unit tests for the shared tool input parser."""

from tools.utils.input_parser import (
    parse_tool_input,
    PlayerSearchParams,
    PlayerStatsParams,
    TeamIdParams,
)


def test_parse_player_search_plain_string():
    params, error = parse_tool_input(
        "Bukayo Saka",
        PlayerSearchParams,
        primary_field="name",
    )
    assert error is None
    assert params
    assert params.name == "Bukayo Saka"


def test_parse_player_search_with_alias():
    params, error = parse_tool_input(
        '{"player_name": "Mohamed Salah"}',
        PlayerSearchParams,
        primary_field="name",
        aliases={"name": ["player_name"]},
    )
    assert error is None
    assert params
    assert params.name == "Mohamed Salah"


def test_parse_invalid_json_returns_error():
    _, error = parse_tool_input(
        "{invalid json",
        PlayerStatsParams,
        primary_field="player_name",
    )
    assert error is not None
    assert "Error parsing JSON" in error


def test_missing_required_field_reports_error():
    _, error = parse_tool_input(
        {},
        PlayerStatsParams,
        primary_field="player_name",
        example='{"player_name": "Erling Haaland"}',
    )
    assert error is not None
    assert "player_name" in error


def test_team_id_scalar_is_wrapped():
    params, error = parse_tool_input(
        7798096,
        TeamIdParams,
        primary_field="team_id",
    )
    assert error is None
    assert params
    assert params.team_id == 7798096