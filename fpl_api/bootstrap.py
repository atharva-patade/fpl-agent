"""
Bootstrap API - handles bootstrap-static endpoint for all game data.
"""
from typing import Dict, List, Any
from fpl_api.client import FPLClient


class BootstrapAPI:
    """API client for bootstrap-static data (players, teams, events, etc)."""
    
    def __init__(self, client: FPLClient):
        """
        Initialize Bootstrap API.
        
        Args:
            client: FPL API client instance
        """
        self.client = client
        self._data = None
    
    def get_bootstrap_data(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get all bootstrap-static data.
        
        Args:
            force_refresh: Force refresh cached data
            
        Returns:
            Complete bootstrap data dictionary
        """
        if force_refresh or self._data is None:
            self._data = self.client.get("bootstrap-static/")
        return self._data
    
    def get_all_players(self) -> List[Dict[str, Any]]:
        """Get all PL players (elements)."""
        data = self.get_bootstrap_data()
        return data.get('elements', [])
    
    def get_all_teams(self) -> List[Dict[str, Any]]:
        """Get all 20 PL teams."""
        data = self.get_bootstrap_data()
        return data.get('teams', [])
    
    def get_all_gameweeks(self) -> List[Dict[str, Any]]:
        """Get all 38 gameweeks (events)."""
        data = self.get_bootstrap_data()
        return data.get('events', [])
    
    def get_current_gameweek(self) -> Dict[str, Any]:
        """Get the current active gameweek."""
        events = self.get_all_gameweeks()
        for event in events:
            if event.get('is_current'):
                return event
        return {}
    
    def get_next_gameweek(self) -> Dict[str, Any]:
        """Get the next upcoming gameweek."""
        events = self.get_all_gameweeks()
        for event in events:
            if event.get('is_next'):
                return event
        return {}
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """Get all FPL positions (element_types)."""
        data = self.get_bootstrap_data()
        return data.get('element_types', [])
    
    def get_game_settings(self) -> Dict[str, Any]:
        """Get FPL game settings."""
        data = self.get_bootstrap_data()
        return data.get('game_settings', {})
    
    def get_phases(self) -> List[Dict[str, Any]]:
        """Get season phases."""
        data = self.get_bootstrap_data()
        return data.get('phases', [])
    
    def get_total_players(self) -> int:
        """Get total number of FPL users."""
        data = self.get_bootstrap_data()
        return data.get('total_players', 0)
    
    def get_element_stats(self) -> List[Dict[str, Any]]:
        """Get list of tracked player stats."""
        data = self.get_bootstrap_data()
        return data.get('element_stats', [])
    
    def get_player_by_id(self, player_id: int) -> Dict[str, Any]:
        """
        Get player by FPL player ID.
        
        Args:
            player_id: FPL player ID
            
        Returns:
            Player data dictionary or empty dict if not found
        """
        players = self.get_all_players()
        for player in players:
            if player.get('id') == player_id:
                return player
        return {}
    
    def get_player_by_name(self, name: str) -> List[Dict[str, Any]]:
        """
        Search players by name (case-insensitive partial match).
        
        Args:
            name: Player name or partial name
            
        Returns:
            List of matching players
        """
        players = self.get_all_players()
        name_lower = name.lower()
        return [
            p for p in players
            if name_lower in f"{p.get('first_name', '')} {p.get('second_name', '')}".lower()
        ]
    
    def get_team_by_id(self, team_id: int) -> Dict[str, Any]:
        """
        Get team by ID (1-20).
        
        Args:
            team_id: Team ID
            
        Returns:
            Team data dictionary or empty dict if not found
        """
        teams = self.get_all_teams()
        for team in teams:
            if team.get('id') == team_id:
                return team
        return {}
