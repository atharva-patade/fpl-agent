"""
LangChain tools for player analysis and search.
"""
from typing import List, Dict, Any
from langchain.tools import tool
from fpl_api.client import FPLClient
from fpl_api.bootstrap import BootstrapAPI
from fpl_api.players import PlayerAPI


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
def search_player_by_name(name: str) -> str:
    """
    Search for players by name (partial match supported).
    Use this when you need to find a player's ID or basic info.
    
    Args:
        name: Player's first name, last name, or full name
        
    Returns:
        Formatted string with player details
    """
    bootstrap, _ = _get_apis()
    players = bootstrap.get_player_by_name(name)
    
    if not players:
        return f"No players found matching '{name}'"
    
    result = f"Found {len(players)} player(s) matching '{name}':\n\n"
    for p in players[:5]:  # Limit to top 5 results
        result += f"• {p['first_name']} {p['second_name']}\n"
        result += f"  ID: {p['id']}, Team: {p['team']}, Position: {p['element_type']}\n"
        result += f"  Price: £{p['now_cost']/10}m, Points: {p['total_points']}\n"
        result += f"  Form: {p['form']}, Selected by: {p['selected_by_percent']}%\n\n"
    
    return result


@tool
def get_player_detailed_stats(player_name: str) -> str:
    """
    Get comprehensive statistics for a specific player including form, fixtures, and recent performance.
    Use this when you need deep analysis of a single player.
    
    Args:
        player_name: Player's name
        
    Returns:
        Detailed player statistics and analysis
    """
    bootstrap, player_api = _get_apis()
    players = bootstrap.get_player_by_name(player_name)
    
    if not players:
        return f"Player '{player_name}' not found"
    
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
    result += f"**Basic Info:**\n"
    result += f"• Position: {_get_position_name(player['element_type'])}\n"
    result += f"• Team: Team ID {player['team']}\n"
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
    
    # Upcoming Fixtures
    if fixtures:
        result += f"**Next {len(fixtures)} Fixtures:**\n"
        for f in fixtures:
            diff = f.get('difficulty', 3)
            result += f"• GW{f.get('event')}: Difficulty {diff}/5\n"
    
    # Value Analysis
    points_per_million = player['total_points'] / (player['now_cost'] / 10) if player['now_cost'] > 0 else 0
    result += f"\n**Value Metrics:**\n"
    result += f"• Points per £1m: {points_per_million:.1f}\n"
    result += f"• ICT Index: {player.get('ict_index', 'N/A')}\n"
    
    return result


@tool
def compare_two_players(player1_name: str, player2_name: str) -> str:
    """
    Compare two players across key metrics to help with transfer decisions.
    Use this when choosing between two players.
    
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
        return f"Player '{player1_name}' not found"
    if not p2_list:
        return f"Player '{player2_name}' not found"
    
    p1 = p1_list[0]
    p2 = p2_list[0]
    
    name1 = f"{p1['first_name']} {p1['second_name']}"
    name2 = f"{p2['first_name']} {p2['second_name']}"
    
    result = f"⚖️ **Player Comparison: {name1} vs {name2}**\n\n"
    
    metrics = [
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
def find_best_players_by_position(position: str, max_price: float = 15.0, min_minutes: int = 200) -> str:
    """
    Find top performing players in a specific position within budget.
    Use this when looking for transfer targets in a specific position.
    
    Args:
        position: Position name (Goalkeeper, Defender, Midfielder, Forward)
        max_price: Maximum price in millions (e.g., 8.5)
        min_minutes: Minimum minutes played to filter out non-starters
        
    Returns:
        List of top players sorted by points per million
    """
    bootstrap, _ = _get_apis()
    
    position_map = {
        'goalkeeper': 1, 'gk': 1, 'gkp': 1,
        'defender': 2, 'def': 2,
        'midfielder': 3, 'mid': 3,
        'forward': 4, 'fwd': 4, 'striker': 4
    }
    
    pos_id = position_map.get(position.lower())
    if not pos_id:
        return f"Invalid position '{position}'. Use: Goalkeeper, Defender, Midfielder, or Forward"
    
    all_players = bootstrap.get_all_players()
    
    # Filter players
    filtered = [
        p for p in all_players
        if p['element_type'] == pos_id
        and p['now_cost'] <= max_price * 10
        and p.get('minutes', 0) >= min_minutes
    ]
    
    # Sort by points per million
    filtered.sort(
        key=lambda p: p['total_points'] / (p['now_cost']/10) if p['now_cost'] > 0 else 0,
        reverse=True
    )
    
    result = f"🎯 **Top {position.title()}s under £{max_price}m**\n\n"
    
    for i, p in enumerate(filtered[:10], 1):
        ppm = p['total_points'] / (p['now_cost']/10) if p['now_cost'] > 0 else 0
        result += f"{i}. **{p['first_name']} {p['second_name']}** (£{p['now_cost']/10}m)\n"
        result += f"   Points: {p['total_points']} | PPM: {ppm:.1f} | Form: {p['form']}\n"
        result += f"   Ownership: {p['selected_by_percent']}% | Mins: {p.get('minutes', 0)}\n\n"
    
    return result


def _get_position_name(element_type: int) -> str:
    """Helper to convert position ID to name."""
    positions = {1: 'Goalkeeper', 2: 'Defender', 3: 'Midfielder', 4: 'Forward'}
    return positions.get(element_type, 'Unknown')
