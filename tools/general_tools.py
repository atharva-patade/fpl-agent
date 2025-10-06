"""
General FPL Tools - gameweek info, season overview, general FPL data
"""
from langchain.tools import tool
from fpl_api.client import FPLClient
from fpl_api.bootstrap import BootstrapAPI


# Lazy initialization
_bootstrap_api = None

def get_bootstrap_api() -> BootstrapAPI:
    """Get or create BootstrapAPI instance."""
    global _bootstrap_api
    if _bootstrap_api is None:
        client = FPLClient()
        _bootstrap_api = BootstrapAPI(client)
    return _bootstrap_api


@tool
def get_current_gameweek_info() -> str:
    """
    Get information about the current FPL gameweek.
    Use this tool when users ask about the current gameweek, what week it is, current GW, or which gameweek we're in.
    
    Returns:
        Current gameweek ID, name, deadline, and status information with average scores if available
    """
    api = get_bootstrap_api()
    current_gw = api.get_current_gameweek()
    
    if not current_gw:
        return "No current gameweek found. The season may not have started or may be finished."
    
    gw_id = current_gw.get('id', 'N/A')
    name = current_gw.get('name', 'N/A')
    deadline = current_gw.get('deadline_time', 'N/A')
    is_finished = current_gw.get('finished', False)
    
    # Get average score if available
    avg_score = current_gw.get('average_entry_score', 0)
    highest_score = current_gw.get('highest_score', 0)
    
    result = f"""**Current Gameweek: {gw_id}**
- Name: {name}
- Deadline: {deadline}
- Status: {'Finished' if is_finished else 'In Progress' if avg_score > 0 else 'Upcoming'}
"""
    
    if avg_score > 0:
        result += f"- Average Score: {avg_score} points\n"
        result += f"- Highest Score: {highest_score} points\n"
    
    return result


@tool
def get_next_gameweek_info() -> str:
    """
    Get information about the next upcoming FPL gameweek.
    Use this when users ask about the next gameweek, upcoming deadline, next GW, or when the next deadline is.
    
    Returns:
        Next gameweek ID, name, and deadline information
    """
    api = get_bootstrap_api()
    next_gw = api.get_next_gameweek()
    
    if not next_gw:
        return "No next gameweek found. This may be the end of the season."
    
    gw_id = next_gw.get('id', 'N/A')
    name = next_gw.get('name', 'N/A')
    deadline = next_gw.get('deadline_time', 'N/A')
    
    result = f"""**Next Gameweek: {gw_id}**
- Name: {name}
- Deadline: {deadline}
- Status: Upcoming
"""
    
    return result


@tool
def get_gameweek_by_number(gameweek_number: int) -> str:
    """
    Get detailed information about a specific gameweek by its number.
    Use this when users ask about a specific gameweek (e.g., "Tell me about gameweek 10" or "What happened in GW5").
    
    Args:
        gameweek_number: The gameweek number (1-38)
        
    Returns:
        Gameweek information including deadline, scores, and status
    """
    api = get_bootstrap_api()
    all_gws = api.get_all_gameweeks()
    
    # Find the specific gameweek
    gw = next((g for g in all_gws if g.get('id') == gameweek_number), None)
    
    if not gw:
        return f"Gameweek {gameweek_number} not found. Valid gameweeks are 1-38."
    
    gw_id = gw.get('id', 'N/A')
    name = gw.get('name', 'N/A')
    deadline = gw.get('deadline_time', 'N/A')
    is_finished = gw.get('finished', False)
    is_current = gw.get('is_current', False)
    is_next = gw.get('is_next', False)
    
    avg_score = gw.get('average_entry_score', 0)
    highest_score = gw.get('highest_score', 0)
    
    status = "Current" if is_current else "Next" if is_next else "Finished" if is_finished else "Upcoming"
    
    result = f"""**Gameweek {gw_id}: {name}**
- Deadline: {deadline}
- Status: {status}
"""
    
    if is_finished and avg_score > 0:
        result += f"\n**Statistics:**\n"
        result += f"- Average Score: {avg_score} points\n"
        result += f"- Highest Score: {highest_score} points\n"
    
    return result


@tool
def get_season_overview() -> str:
    """
    Get overview of the current FPL season including total gameweeks and current progress.
    Use this when users ask about the season, how many gameweeks are left, season status, or season progress.
    
    Returns:
        Season overview with gameweek progress and completion percentage
    """
    api = get_bootstrap_api()
    all_gws = api.get_all_gameweeks()
    current_gw = api.get_current_gameweek()
    
    total_gws = len(all_gws)
    current_gw_id = current_gw.get('id', 0) if current_gw else 0
    
    finished_gws = sum(1 for gw in all_gws if gw.get('finished', False))
    remaining_gws = total_gws - current_gw_id if current_gw_id > 0 else total_gws
    
    result = f"""**FPL Season Overview**
- Total Gameweeks: {total_gws}
- Current Gameweek: {current_gw_id}
- Gameweeks Finished: {finished_gws}
- Gameweeks Remaining: {remaining_gws}
- Progress: {current_gw_id}/{total_gws} ({int(current_gw_id/total_gws*100)}% complete)
"""
    
    return result
