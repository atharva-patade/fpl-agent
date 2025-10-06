"""
LangChain tools for player analysis and search.
"""
from typing import List, Dict, Any
from langchain.tools import tool
from fpl_api.client import FPLClient
from fpl_api.bootstrap import BootstrapAPI
from fpl_api.players import PlayerAPI
from tools.utils.input_parser import (
    parse_tool_input,
    PlayerSearchParams,
    PlayerStatsParams,
    PlayerComparisonParams,
    BestPlayersParams,
)


# Initialize API clients
_client = None
_bootstrap = None
_player_api = None


def _get_apis():
    """Lazy initialization of API clients."""
    global _client, _bootstrap, _player_api
    if _client is None:
        _client = FPLClient()
        _bootstrap = BootstrapAPI(_client)
        _player_api = PlayerAPI(_client)
    return _bootstrap, _player_api


@tool
def search_player_by_name(tool_input: Any) -> str:
    """
    Search for players by name (partial match supported).
    Accepts JSON, dict, or plain string representing the player's name.
    """
    params, error = parse_tool_input(
        tool_input,
        PlayerSearchParams,
        primary_field="name",
        aliases={"name": ["name", "player_name", "player"]},
        example='{"name": "Mohamed Salah"}',
    )
    if error:
        return error

    name = params.name
    bootstrap, _ = _get_apis()
    players = bootstrap.get_player_by_name(name)

    if not players:
        return (f"❌ No players found matching '{name}' in the current FPL season.\n\n"
                f"**Possible reasons:**\n"
                f"• Player may have transferred to a non-Premier League club\n"
                f"• Check spelling (try just last name or first name)\n"
                f"• Player may be injured/not registered for FPL this season\n\n"
                f"💡 **Tip:** Try searching with just the last name for better results.")

    result = f"Found {len(players)} player(s) matching '{name}':\n\n"
    for p in players[:5]:  # Limit to top 5 results
        team_name = _get_team_short_name(p['team'], bootstrap)
        result += f"• {p['first_name']} {p['second_name']} ({team_name})\n"
        result += f"  Position: {_get_position_name(p['element_type'])}\n"
        result += f"  Price: £{p['now_cost']/10}m, Points: {p['total_points']}\n"
        result += f"  Form: {p['form']}, Selected by: {p['selected_by_percent']}%\n\n"

    return result


@tool
def get_player_detailed_stats(tool_input: Any) -> str:
    """
    Get comprehensive statistics for a specific player including form, fixtures, and recent performance.
    Accepts JSON, dict, or plain string inputs with the player's name.
    """
    params, error = parse_tool_input(
        tool_input,
        PlayerStatsParams,
        primary_field="player_name",
        aliases={"player_name": ["player_name", "name", "player"]},
        example='{"player_name": "Heung-Min Son"}',
    )
    if error:
        return error

    player_name = params.player_name
    bootstrap, player_api = _get_apis()
    players = bootstrap.get_player_by_name(player_name)

    if not players:
        return (f"❌ Player '{player_name}' not found in the current FPL season.\n\n"
                f"**Possible reasons:**\n"
                f"• Player may have transferred outside the Premier League\n"
                f"• Check spelling - try searching with search_player_by_name first\n"
                f"• Player may not be registered for FPL this season\n\n"
                f"💡 **Tip:** Use search_player_by_name to find the correct player name.")

    player = players[0]  # Take first match
    player_id = player['id']
    
    # Get detailed summary
    try:
        summary = player_api.get_player_summary(player_id)
        history = summary.get('history', [])[-5:]  # Last 5 gameweeks
        fixtures = summary.get('fixtures', [])[:5]  # Next 5 fixtures
    except:
        history = []
        fixtures = []
    
    result = f"📊 **{player['first_name']} {player['second_name']}** - Detailed Analysis\n\n"
    
    # Basic Info
    team_name = _get_team_name(player['team'], bootstrap)
    team_short = _get_team_short_name(player['team'], bootstrap)
    result += f"**Basic Info:**\n"
    result += f"• Position: {_get_position_name(player['element_type'])}\n"
    result += f"• Team: {team_name} ({team_short})\n"
    result += f"• Price: £{player['now_cost']/10}m\n"
    result += f"• Ownership: {player['selected_by_percent']}%\n\n"
    
    # Performance Stats
    result += f"**Season Performance:**\n"
    result += f"• Total Points: {player['total_points']}\n"
    result += f"• Points per Game: {player['points_per_game']}\n"
    result += f"• Form: {player['form']}\n"
    result += f"• Goals: {player.get('goals_scored', 0)}\n"
    result += f"• Assists: {player.get('assists', 0)}\n"
    result += f"• Clean Sheets: {player.get('clean_sheets', 0)}\n\n"
    
    # Recent Form (last 5 GWs)
    if history:
        result += f"**Recent Form (Last {len(history)} GWs):**\n"
        total_pts = sum(h.get('total_points', 0) for h in history)
        result += f"• Points: {total_pts} ({total_pts/len(history):.1f} avg)\n"
        result += f"• Minutes: {sum(h.get('minutes', 0) for h in history)}\n\n"
    
    # Upcoming Fixtures with opponent team names
    if fixtures:
        result += f"**Next {len(fixtures)} Fixtures:**\n"
        player_team_id = player['team']
        
        for f in fixtures:
            event = f.get('event')
            diff = f.get('difficulty', 3)
            is_home = f.get('is_home', False)
            
            # Get opponent team
            if is_home:
                opponent_id = f.get('team_a')
                venue = 'H'
            else:
                opponent_id = f.get('team_h')
                venue = 'A'
            
            opponent_short = _get_team_short_name(opponent_id, bootstrap) if opponent_id else 'TBD'
            
            result += f"• GW{event}: vs {opponent_short} ({venue}) - Difficulty {diff}/5\n"
    
    # Value Analysis
    points_per_million = player['total_points'] / (player['now_cost'] / 10) if player['now_cost'] > 0 else 0
    result += f"\n**Value Metrics:**\n"
    result += f"• Points per £1m: {points_per_million:.1f}\n"
    result += f"• ICT Index: {player.get('ict_index', 'N/A')}\n"
    
    return result


@tool
def compare_two_players(tool_input: Any) -> str:
    """Compare two players across key metrics to help with transfer decisions."""
    params, error = parse_tool_input(
        tool_input,
        PlayerComparisonParams,
        aliases={
            "player1_name": ["player1_name", "player_a", "first_player"],
            "player2_name": ["player2_name", "player_b", "second_player"],
        },
        example='{"player1_name": "Erling Haaland", "player2_name": "Ollie Watkins"}',
    )
    if error:
        return error

    return _compare_two_players_func(params.player1_name, params.player2_name)


def _compare_two_players_func(player1_name: str, player2_name: str) -> str:
    """
    Compare two players across key metrics to help with transfer decisions.
    
    Args:
        player1_name: First player's name
        player2_name: Second player's name
        
    Returns:
        Side-by-side comparison of both players
    """
    bootstrap, _ = _get_apis()
    
    p1_list = bootstrap.get_player_by_name(player1_name)
    p2_list = bootstrap.get_player_by_name(player2_name)
    
    if not p1_list:
        return (f"❌ Player '{player1_name}' not found in the current FPL season.\n\n"
                f"**Possible reasons:**\n"
                f"• Player may have transferred outside the Premier League (e.g., Harry Kane to Bayern Munich)\n"
                f"• Check spelling - try searching with search_player_by_name first\n"
                f"• Player may not be registered for FPL this season\n\n"
                f"💡 **Tip:** Use search_player_by_name to find current Premier League players.")
    if not p2_list:
        return (f"❌ Player '{player2_name}' not found in the current FPL season.\n\n"
                f"**Possible reasons:**\n"
                f"• Player may have transferred outside the Premier League (e.g., Harry Kane to Bayern Munich)\n"
                f"• Check spelling - try searching with search_player_by_name first\n"
                f"• Player may not be registered for FPL this season\n\n"
                f"💡 **Tip:** Use search_player_by_name to find current Premier League players.")
    
    p1 = p1_list[0]
    p2 = p2_list[0]
    
    name1 = f"{p1['first_name']} {p1['second_name']}"
    name2 = f"{p2['first_name']} {p2['second_name']}"
    
    team1 = _get_team_short_name(p1['team'], bootstrap)
    team2 = _get_team_short_name(p2['team'], bootstrap)
    
    result = f"⚖️ **Player Comparison: {name1} ({team1}) vs {name2} ({team2})**\n\n"
    
    metrics = [
        ("Team", _get_team_name(p1['team'], bootstrap), _get_team_name(p2['team'], bootstrap)),
        ("Price", f"£{p1['now_cost']/10}m", f"£{p2['now_cost']/10}m"),
        ("Total Points", p1['total_points'], p2['total_points']),
        ("Points/Game", p1['points_per_game'], p2['points_per_game']),
        ("Form", p1['form'], p2['form']),
        ("Ownership", f"{p1['selected_by_percent']}%", f"{p2['selected_by_percent']}%"),
        ("Goals", p1.get('goals_scored', 0), p2.get('goals_scored', 0)),
        ("Assists", p1.get('assists', 0), p2.get('assists', 0)),
        ("Clean Sheets", p1.get('clean_sheets', 0), p2.get('clean_sheets', 0)),
    ]
    
    for metric, val1, val2 in metrics:
        result += f"**{metric}:**\n"
        result += f"  {name1}: {val1}\n"
        result += f"  {name2}: {val2}\n\n"
    
    # Recommendation
    p1_ppm = p1['total_points'] / (p1['now_cost']/10) if p1['now_cost'] > 0 else 0
    p2_ppm = p2['total_points'] / (p2['now_cost']/10) if p2['now_cost'] > 0 else 0
    
    result += f"**Value Analysis:**\n"
    result += f"  {name1}: {p1_ppm:.1f} pts/£m\n"
    result += f"  {name2}: {p2_ppm:.1f} pts/£m\n"
    
    return result


@tool
def find_best_players_by_position(tool_input: Any) -> str:
    """Find top performing players in a specific position within budget constraints."""
    params, error = parse_tool_input(
        tool_input,
        BestPlayersParams,
        primary_field="position",
        aliases={
            "position": ["position", "pos"],
            "max_price": ["max_price", "maxPrice"],
            "min_price": ["min_price", "minPrice"],
            "min_minutes": ["min_minutes", "minMinutes", "minutes"],
        },
        example='{"position": "Midfielder", "max_price": 8.5, "min_minutes": 300}',
    )
    if error:
        return error

    if not params.position:
        return ('❌ Error: Position is required.\n\n'
                '**Valid positions:** Goalkeeper, Defender, Midfielder, Forward')

    return _find_best_players_by_position_func(
        position=params.position,
        max_price=params.max_price,
        min_price=params.min_price,
        min_minutes=params.min_minutes,
    )


def _find_best_players_by_position_func(
    position: str,
    max_price: float = 15.0,
    min_price: float = 0.0,
    min_minutes: int = 200
) -> str:
    """
    Internal function to find top performing players in a specific position.
    
    Args:
        position: Position name (Goalkeeper, Defender, Midfielder, Forward)
        max_price: Maximum price in millions (e.g., 10.0)
        min_price: Minimum price in millions (e.g., 4.0)
        min_minutes: Minimum minutes played to filter out non-starters
        
    Returns:
        Formatted string with list of top players
    """
    bootstrap, _ = _get_apis()
    
    # Position mapping with various aliases
    position_map = {
        'goalkeeper': 1, 'gk': 1, 'gkp': 1, 'keeper': 1, 'goalkeepers': 1,
        'defender': 2, 'def': 2, 'defenders': 2, 'defence': 2, 'defense': 2,
        'midfielder': 3, 'mid': 3, 'midfielders': 3, 'midfield': 3,
        'forward': 4, 'fwd': 4, 'striker': 4, 'forwards': 4, 'strikers': 4, 'attacker': 4, 'attackers': 4
    }
    
    pos_id = position_map.get(position.lower().strip())
    
    if not pos_id:
        # Provide helpful error with valid options
        valid_positions = ['Goalkeeper', 'Defender', 'Midfielder', 'Forward']
        return (f"❌ Invalid position: '{position}'\n\n"
                f"**Valid positions:**\n" + 
                '\n'.join(f"• {pos}" for pos in valid_positions) + 
                f"\n\n**Aliases also work:** GK, Def, Mid, Fwd, Striker, etc.")
    
    # Position name for display
    position_names = {1: 'Goalkeeper', 2: 'Defender', 3: 'Midfielder', 4: 'Forward'}
    position_display = position_names[pos_id]
    
    try:
        all_players = bootstrap.get_all_players()
    except Exception as e:
        return f"❌ Error fetching player data: {str(e)}\n\nPlease try again later."
    
    # Filter players based on criteria
    filtered = [
        p for p in all_players
        if p['element_type'] == pos_id
        and min_price * 10 <= p['now_cost'] <= max_price * 10
        and p.get('minutes', 0) >= min_minutes
    ]
    
    if not filtered:
        return (f"❌ No {position_display}s found matching your criteria:\n"
                f"• Price range: £{min_price}m - £{max_price}m\n"
                f"• Minimum minutes: {min_minutes}\n\n"
                f"💡 **Tips:**\n"
                f"• Try increasing the max_price\n"
                f"• Try decreasing min_minutes (default is 200)\n"
                f"• Some positions have fewer playing options")
    
    # Sort by points per million (best value first)
    filtered.sort(
        key=lambda p: p['total_points'] / (p['now_cost']/10) if p['now_cost'] > 0 else 0,
        reverse=True
    )
    
    # Build result string
    price_range = f"£{min_price}m - £{max_price}m" if min_price > 0 else f"under £{max_price}m"
    result = f"🎯 **Top {position_display}s ({price_range})**\n"
    result += f"*Minimum {min_minutes} minutes played*\n\n"
    
    # Show top 10 players
    for i, p in enumerate(filtered[:10], 1):
        ppm = p['total_points'] / (p['now_cost']/10) if p['now_cost'] > 0 else 0
        team_short = _get_team_short_name(p['team'], bootstrap)
        
        result += f"{i}. **{p['first_name']} {p['second_name']}** ({team_short}) - £{p['now_cost']/10}m\n"
        result += f"   Points: {p['total_points']} | PPM: {ppm:.1f} | Form: {p['form']}\n"
        result += f"   Ownership: {p['selected_by_percent']}% | Mins: {p.get('minutes', 0)}\n\n"
    
    # Add summary stats
    if len(filtered) > 10:
        result += f"*Showing top 10 of {len(filtered)} {position_display}s matching criteria*\n"
    
    return result


def _get_position_name(element_type: int) -> str:
    """Helper to convert position ID to name."""
    positions = {1: 'Goalkeeper', 2: 'Defender', 3: 'Midfielder', 4: 'Forward'}
    return positions.get(element_type, 'Unknown')


def _get_team_name(team_id: int, bootstrap: BootstrapAPI) -> str:
    """Helper to get football team name from team ID."""
    team = bootstrap.get_team_by_id(team_id)
    return team.get('name', f'Team {team_id}')


def _get_team_short_name(team_id: int, bootstrap: BootstrapAPI) -> str:
    """Helper to get football team short name (3-letter code)."""
    team = bootstrap.get_team_by_id(team_id)
    return team.get('short_name', 'UNK')
