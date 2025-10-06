"""
LangChain tools for team/squad analysis.
"""
from typing import Optional, Any
from langchain.tools import tool
from fpl_api.client import FPLClient
from fpl_api.bootstrap import BootstrapAPI
from fpl_api.managers import ManagerAPI
from tools.utils.input_parser import (
    parse_tool_input,
    TeamIdGameweekParams,
    TeamIdParams,
    TeamTransfersParams,
    TeamPerformanceParams,
)


# Initialize API clients
_client = None
_bootstrap = None
_manager_api = None


def _get_apis():
    """Lazy initialization of API clients."""
    global _client, _bootstrap, _manager_api
    if _client is None:
        _client = FPLClient()
        _bootstrap = BootstrapAPI(_client)
        _manager_api = ManagerAPI(_client)
    return _bootstrap, _manager_api


def _get_team_name(team_id: int, bootstrap: BootstrapAPI) -> str:
    """Helper to get football team name from team ID."""
    team = bootstrap.get_team_by_id(team_id)
    return team.get('name', f'Team {team_id}')


def _get_team_short_name(team_id: int, bootstrap: BootstrapAPI) -> str:
    """Helper to get football team short name (3-letter code)."""
    team = bootstrap.get_team_by_id(team_id)
    return team.get('short_name', 'UNK')


def _get_position_name(element_type: int) -> str:
    """Helper to convert position ID to name."""
    positions = {1: 'Goalkeeper', 2: 'Defender', 3: 'Midfielder', 4: 'Forward'}
    return positions.get(element_type, 'Unknown')


def _get_position_emoji(element_type: int) -> str:
    """Helper to get emoji for position."""
    emojis = {1: '🥅', 2: '🛡️', 3: '⚽', 4: '⚡'}
    return emojis.get(element_type, '❓')


@tool
def get_my_team(tool_input: Any) -> str:
    """
    Display your current FPL team with player names, positions, and formation.
    Accepts JSON, dict, or scalar inputs containing the required team ID and optional gameweek.
    """
    params, error = parse_tool_input(
        tool_input,
        TeamIdGameweekParams,
        primary_field="team_id",
        example='{"team_id": 7798096, "gameweek": 5}',
    )
    if error:
        return error

    team_id = params.team_id
    gameweek = params.gameweek
    bootstrap, manager_api = _get_apis()
    
    # Get current gameweek if not specified
    if gameweek is None:
        current_gw = bootstrap.get_current_gameweek()
        gameweek = current_gw.get('id', 1)
    
    try:
        # Get team picks for the gameweek
        team_data = manager_api.get_manager_team(team_id, gameweek)
        picks = team_data.get('picks', [])
        entry_history = team_data.get('entry_history', {})
        
        if not picks:
            return f"No team data found for Team ID {team_id} in Gameweek {gameweek}"
        
        # Get all players data for lookups
        all_players = {p['id']: p for p in bootstrap.get_all_players()}
        
        # Separate starting XI and bench
        starting_xi = [p for p in picks if p['position'] <= 11]
        bench = [p for p in picks if p['position'] > 11]
        
        # Sort starting XI by position for display
        starting_xi.sort(key=lambda x: x['position'])
        bench.sort(key=lambda x: x['position'])
        
        # Count formation
        formation = {'gk': 0, 'def': 0, 'mid': 0, 'fwd': 0}
        for pick in starting_xi:
            player = all_players.get(pick['element'])
            if player:
                pos_type = player['element_type']
                if pos_type == 1:
                    formation['gk'] += 1
                elif pos_type == 2:
                    formation['def'] += 1
                elif pos_type == 3:
                    formation['mid'] += 1
                elif pos_type == 4:
                    formation['fwd'] += 1
        
        formation_str = f"{formation['def']}-{formation['mid']}-{formation['fwd']}"
        
        # Build output
        result = f"🏆 **Your FPL Team - Gameweek {gameweek}**\n\n"
        result += f"**Formation: {formation_str}**\n\n"
        
        # Group starting XI by position
        by_position = {1: [], 2: [], 3: [], 4: []}
        for pick in starting_xi:
            player = all_players.get(pick['element'])
            if player:
                by_position[player['element_type']].append((pick, player))
        
        # Display starting XI by position
        position_labels = {
            1: ('🥅 Goalkeeper', 'Goalkeepers'),
            2: ('🛡️ Defenders', 'Defenders'),
            3: ('⚽ Midfielders', 'Midfielders'),
            4: ('⚡ Forwards', 'Forwards')
        }
        
        for pos_id in [1, 2, 3, 4]:
            players_in_pos = by_position[pos_id]
            if players_in_pos:
                label = position_labels[pos_id][0] if len(players_in_pos) == 1 else position_labels[pos_id][0]
                result += f"{label}:\n"
                
                for pick, player in players_in_pos:
                    team_short = _get_team_short_name(player['team'], bootstrap)
                    captain_mark = ' ⓒ' if pick['is_captain'] else ''
                    vice_mark = ' ⓥ' if pick['is_vice_captain'] else ''
                    
                    result += f"{pick['position']}. {player['first_name']} {player['second_name']} "
                    result += f"({team_short}){captain_mark}{vice_mark} - "
                    result += f"£{player['now_cost']/10}m - {player['total_points']} pts\n"
                
                result += "\n"
        
        # Display bench
        result += "🪑 **Bench:**\n"
        for pick in bench:
            player = all_players.get(pick['element'])
            if player:
                team_short = _get_team_short_name(player['team'], bootstrap)
                result += f"{pick['position']}. {player['first_name']} {player['second_name']} "
                result += f"({team_short}) - £{player['now_cost']/10}m - {player['total_points']} pts\n"
        
        # Team value and gameweek stats
        team_value = entry_history.get('value', 0) / 10
        bank = entry_history.get('bank', 0) / 10
        gw_points = entry_history.get('points', 0)
        total_points = entry_history.get('total_points', 0)
        points_on_bench = entry_history.get('points_on_bench', 0)
        
        result += f"\n💰 **Team Value:** £{team_value}m | **Bank:** £{bank}m\n"
        result += f"📊 **Gameweek {gameweek}:** {gw_points} pts | **Overall:** {total_points} pts\n"
        if points_on_bench > 0:
            result += f"🪑 **Points on Bench:** {points_on_bench} pts\n"
        
        return result
        
    except Exception as e:
        return f"Error fetching team data: {str(e)}"


@tool
def get_my_team_summary(tool_input: Any) -> str:
    """
    Get high-level summary of your FPL team including rank, points, and value.
    Accepts JSON, dict, or scalar inputs for the team ID.
    """
    params, error = parse_tool_input(
        tool_input,
        TeamIdParams,
        primary_field="team_id",
        example='{"team_id": 7798096}',
    )
    if error:
        return error

    team_id = params.team_id
    bootstrap, manager_api = _get_apis()
    
    try:
        summary = manager_api.get_team_summary(team_id)
        history_data = manager_api.get_manager_history(team_id)
        current_season = history_data.get('current', [])
        
        result = f"📊 **FPL Team Summary**\n\n"
        result += f"**Team Name:** {summary.get('team_name', 'Unknown')}\n"
        result += f"**Manager:** {summary.get('manager_name', 'Unknown')}\n\n"
        
        result += f"**Overall Performance:**\n"
        result += f"• Total Points: {summary.get('total_points', 0):,}\n"
        result += f"• Overall Rank: {summary.get('overall_rank', 0):,}\n"
        result += f"• Current Gameweek: {summary.get('current_gw', 0)}\n\n"
        
        result += f"**Team Value:**\n"
        result += f"• Squad Value: £{summary.get('team_value', 0)}m\n"
        result += f"• In Bank: £{summary.get('bank', 0)}m\n"
        result += f"• Total Transfers: {summary.get('total_transfers', 0)}\n\n"
        
        # Recent form (last 5 gameweeks)
        if current_season and len(current_season) >= 1:
            recent = current_season[-5:]  # Last 5 gameweeks
            recent_points = [gw.get('points', 0) for gw in recent]
            avg_recent = sum(recent_points) / len(recent_points) if recent_points else 0
            
            result += f"**Recent Form (Last {len(recent)} GWs):**\n"
            result += f"• Points: {' | '.join(map(str, recent_points))}\n"
            result += f"• Average: {avg_recent:.1f} pts per GW\n"
            
            # Rank movement
            if len(current_season) >= 2:
                prev_rank = current_season[-2].get('overall_rank', 0)
                curr_rank = current_season[-1].get('overall_rank', 0)
                rank_change = prev_rank - curr_rank
                
                if rank_change > 0:
                    result += f"• Rank Change: ⬆️ +{rank_change:,} (improved)\n"
                elif rank_change < 0:
                    result += f"• Rank Change: ⬇️ {rank_change:,} (dropped)\n"
                else:
                    result += f"• Rank Change: ➡️ No change\n"
        
        return result
        
    except Exception as e:
        return f"Error fetching team summary: {str(e)}"


@tool
def get_my_transfers(tool_input: Any) -> str:
    """
    Show recent transfers made by your FPL team.
    Accepts JSON, dict, or scalar inputs with team ID and optional limit.
    """
    params, error = parse_tool_input(
        tool_input,
        TeamTransfersParams,
        primary_field="team_id",
        example='{"team_id": 7798096, "limit": 5}',
    )
    if error:
        return error

    team_id = params.team_id
    limit = params.limit
    bootstrap, manager_api = _get_apis()
    
    try:
        transfers = manager_api.get_manager_transfers(team_id)
        
        if not transfers:
            return "No transfers made this season yet."
        
        # Get all players for name lookups
        all_players = {p['id']: p for p in bootstrap.get_all_players()}
        
        # Limit and reverse (most recent first)
        recent_transfers = transfers[-limit:][::-1]
        
        result = f"🔄 **Recent Transfers (Last {len(recent_transfers)})**\n\n"
        
        for i, transfer in enumerate(recent_transfers, 1):
            player_in_id = transfer.get('element_in')
            player_out_id = transfer.get('element_out')
            cost = transfer.get('element_in_cost', 0) / 10
            gw = transfer.get('event')
            
            player_in = all_players.get(player_in_id, {})
            player_out = all_players.get(player_out_id, {})
            
            in_name = f"{player_in.get('first_name', '')} {player_in.get('second_name', 'Unknown')}"
            out_name = f"{player_out.get('first_name', '')} {player_out.get('second_name', 'Unknown')}"
            
            in_team = _get_team_short_name(player_in.get('team', 0), bootstrap) if player_in else 'UNK'
            out_team = _get_team_short_name(player_out.get('team', 0), bootstrap) if player_out else 'UNK'
            
            result += f"**GW{gw}:** {out_name} ({out_team}) ➡️ {in_name} ({in_team}) - £{cost}m\n"
        
        return result
        
    except Exception as e:
        return f"Error fetching transfers: {str(e)}"


@tool
def analyze_my_team_performance(tool_input: Any) -> str:
    """
    Analyze your team's performance over recent gameweeks with trends and insights.
    Accepts JSON, dict, or scalar inputs with team ID and optional week window.
    """
    params, error = parse_tool_input(
        tool_input,
        TeamPerformanceParams,
        primary_field="team_id",
        example='{"team_id": 7798096, "last_n_weeks": 5}',
    )
    if error:
        return error

    team_id = params.team_id
    last_n_weeks = params.last_n_weeks
    bootstrap, manager_api = _get_apis()
    
    try:
        history_data = manager_api.get_manager_history(team_id)
        current_season = history_data.get('current', [])
        
        if not current_season:
            return "No gameweek history available yet."
        
        # Get recent gameweeks
        recent = current_season[-last_n_weeks:] if len(current_season) >= last_n_weeks else current_season
        
        result = f"📈 **Team Performance Analysis (Last {len(recent)} Gameweeks)**\n\n"
        
        # Points analysis
        points = [gw.get('points', 0) for gw in recent]
        avg_points = sum(points) / len(points) if points else 0
        total_points = sum(points)
        best_gw = max(points) if points else 0
        worst_gw = min(points) if points else 0
        
        result += f"**Points Summary:**\n"
        result += f"• Total: {total_points} pts\n"
        result += f"• Average: {avg_points:.1f} pts/GW\n"
        result += f"• Best GW: {best_gw} pts\n"
        result += f"• Worst GW: {worst_gw} pts\n\n"
        
        # Compare to average
        avg_scores = [gw.get('event_average', 0) for gw in recent]
        avg_league = sum(avg_scores) / len(avg_scores) if avg_scores else 0
        
        if avg_league > 0:
            diff = avg_points - avg_league
            if diff > 0:
                result += f"• Performance: ⬆️ {diff:.1f} pts above average\n\n"
            else:
                result += f"• Performance: ⬇️ {abs(diff):.1f} pts below average\n\n"
        
        # Rank movement
        if len(recent) >= 2:
            start_rank = recent[0].get('overall_rank', 0)
            end_rank = recent[-1].get('overall_rank', 0)
            rank_change = start_rank - end_rank
            
            result += f"**Rank Movement:**\n"
            result += f"• Starting Rank: {start_rank:,}\n"
            result += f"• Current Rank: {end_rank:,}\n"
            
            if rank_change > 0:
                result += f"• Change: ⬆️ Improved by {rank_change:,} places\n\n"
            elif rank_change < 0:
                result += f"• Change: ⬇️ Dropped {abs(rank_change):,} places\n\n"
            else:
                result += f"• Change: ➡️ No change\n\n"
        
        # Points on bench
        bench_points = [gw.get('points_on_bench', 0) for gw in recent]
        total_bench = sum(bench_points)
        avg_bench = total_bench / len(bench_points) if bench_points else 0
        
        result += f"**Bench Analysis:**\n"
        result += f"• Total Points Left on Bench: {total_bench} pts\n"
        result += f"• Average per GW: {avg_bench:.1f} pts\n\n"
        
        # Gameweek breakdown
        result += f"**Gameweek Breakdown:**\n"
        for gw in recent:
            gw_num = gw.get('event')
            gw_pts = gw.get('points', 0)
            gw_avg = gw.get('event_average', 0)
            diff_symbol = '✅' if gw_pts >= gw_avg else '⚠️'
            result += f"• GW{gw_num}: {gw_pts} pts (avg: {gw_avg}) {diff_symbol}\n"
        
        return result
        
    except Exception as e:
        return f"Error analyzing performance: {str(e)}"


@tool
def get_team_value_breakdown(tool_input: Any) -> str:
    """
    Break down team value by position and identify budget allocation.
    Accepts JSON, dict, or scalar inputs for the team ID.
    """
    params, error = parse_tool_input(
        tool_input,
        TeamIdParams,
        primary_field="team_id",
        example='{"team_id": 7798096}',
    )
    if error:
        return error

    team_id = params.team_id
    bootstrap, manager_api = _get_apis()
    
    try:
        # Get current gameweek
        current_gw = bootstrap.get_current_gameweek()
        gameweek = current_gw.get('id', 1)
        
        # Get team picks
        team_data = manager_api.get_manager_team(team_id, gameweek)
        picks = team_data.get('picks', [])
        entry_history = team_data.get('entry_history', {})
        
        if not picks:
            return f"No team data found for Team ID {team_id}"
        
        # Get all players data
        all_players = {p['id']: p for p in bootstrap.get_all_players()}
        
        # Analyze by position
        position_data = {
            1: {'name': 'Goalkeepers', 'count': 0, 'total_value': 0, 'total_points': 0, 'players': []},
            2: {'name': 'Defenders', 'count': 0, 'total_value': 0, 'total_points': 0, 'players': []},
            3: {'name': 'Midfielders', 'count': 0, 'total_value': 0, 'total_points': 0, 'players': []},
            4: {'name': 'Forwards', 'count': 0, 'total_value': 0, 'total_points': 0, 'players': []}
        }
        
        for pick in picks:
            player = all_players.get(pick['element'])
            if player:
                pos = player['element_type']
                value = player['now_cost'] / 10
                points = player['total_points']
                
                position_data[pos]['count'] += 1
                position_data[pos]['total_value'] += value
                position_data[pos]['total_points'] += points
                position_data[pos]['players'].append({
                    'name': f"{player['first_name']} {player['second_name']}",
                    'value': value,
                    'points': points,
                    'team': _get_team_short_name(player['team'], bootstrap)
                })
        
        result = f"💰 **Team Value Breakdown**\n\n"
        
        total_squad_value = sum(pos['total_value'] for pos in position_data.values())
        bank = entry_history.get('bank', 0) / 10
        
        result += f"**Overall:**\n"
        result += f"• Squad Value: £{total_squad_value:.1f}m\n"
        result += f"• In Bank: £{bank}m\n"
        result += f"• Total Budget: £{total_squad_value + bank:.1f}m\n\n"
        
        # Breakdown by position
        for pos_id in [1, 2, 3, 4]:
            pos = position_data[pos_id]
            emoji = _get_position_emoji(pos_id)
            
            result += f"{emoji} **{pos['name']}** ({pos['count']} players):\n"
            result += f"• Total Value: £{pos['total_value']:.1f}m ({pos['total_value']/total_squad_value*100:.1f}%)\n"
            result += f"• Total Points: {pos['total_points']} pts\n"
            result += f"• Avg Value: £{pos['total_value']/pos['count']:.1f}m per player\n"
            
            # Sort players by value (most expensive first)
            pos['players'].sort(key=lambda x: x['value'], reverse=True)
            
            result += f"• Players:\n"
            for p in pos['players']:
                result += f"  - {p['name']} ({p['team']}): £{p['value']}m, {p['points']} pts\n"
            
            result += "\n"
        
        # Identify most expensive players
        all_squad = []
        for pos in position_data.values():
            all_squad.extend(pos['players'])
        
        all_squad.sort(key=lambda x: x['value'], reverse=True)
        
        result += f"**💎 Most Expensive Players:**\n"
        for i, p in enumerate(all_squad[:3], 1):
            result += f"{i}. {p['name']} - £{p['value']}m\n"
        
        result += f"\n**💵 Budget Players:**\n"
        for i, p in enumerate(all_squad[-3:][::-1], 1):
            result += f"{i}. {p['name']} - £{p['value']}m ({p['points']} pts)\n"
        
        return result
        
    except Exception as e:
        return f"Error fetching value breakdown: {str(e)}"
