"""
Managers API - handles FPL manager/team endpoints.
"""
from typing import Dict, List, Any
from fpl_api.client import FPLClient


class ManagerAPI:
    """API client for FPL manager/team data."""
    
    def __init__(self, client: FPLClient):
        """
        Initialize Manager API.
        
        Args:
            client: FPL API client instance
        """
        self.client = client
    
    def get_manager_info(self, manager_id: int) -> Dict[str, Any]:
        """
        Get basic information about an FPL manager.
        
        Args:
            manager_id: FPL manager/entry ID
            
        Returns:
            Manager info including team name, points, rank, etc.
        """
        return self.client.get(f"entry/{manager_id}/")
    
    def get_manager_history(self, manager_id: int) -> Dict[str, Any]:
        """
        Get manager's full history for current season.
        
        Args:
            manager_id: FPL manager/entry ID
            
        Returns:
            Dict with current season history, past seasons, chips used
        """
        return self.client.get(f"entry/{manager_id}/history/")
    
    def get_manager_transfers(self, manager_id: int) -> List[Dict[str, Any]]:
        """
        Get all transfers made by manager this season.
        
        Args:
            manager_id: FPL manager/entry ID
            
        Returns:
            List of all transfers
        """
        return self.client.get(f"entry/{manager_id}/transfers/")
    
    def get_manager_team(self, manager_id: int, gameweek: int) -> Dict[str, Any]:
        """
        Get manager's team selection for a specific gameweek.
        
        Args:
            manager_id: FPL manager/entry ID
            gameweek: Gameweek number
            
        Returns:
            Team picks, captain, vice-captain, bench, chips used
        """
        return self.client.get(f"entry/{manager_id}/event/{gameweek}/picks/")
    
    def get_team_summary(self, manager_id: int) -> Dict[str, Any]:
        """
        Get a summary of manager's key information.
        
        Args:
            manager_id: FPL manager/entry ID
            
        Returns:
            Formatted summary dict
        """
        info = self.get_manager_info(manager_id)
        return {
            'team_id': info.get('id'),
            'team_name': info.get('name'),
            'manager_name': f"{info.get('player_first_name', '')} {info.get('player_last_name', '')}",
            'total_points': info.get('summary_overall_points'),
            'overall_rank': info.get('summary_overall_rank'),
            'current_gw': info.get('current_event'),
            'team_value': info.get('last_deadline_value', 0) / 10,
            'bank': info.get('last_deadline_bank', 0) / 10,
            'total_transfers': info.get('last_deadline_total_transfers'),
        }
