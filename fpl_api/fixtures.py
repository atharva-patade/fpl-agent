"""
Fixtures API - handles fixture/match data.
"""
from typing import Dict, List, Any
from fpl_api.client import FPLClient


class FixturesAPI:
    """API client for fixtures data."""
    
    def __init__(self, client: FPLClient):
        """
        Initialize Fixtures API.
        
        Args:
            client: FPL API client instance
        """
        self.client = client
    
    def get_all_fixtures(self) -> List[Dict[str, Any]]:
        """
        Get all 380 fixtures for the season.
        
        Returns:
            List of all fixtures
        """
        return self.client.get("fixtures/")
    
    def get_fixtures_by_gameweek(self, gameweek: int) -> List[Dict[str, Any]]:
        """
        Get fixtures for a specific gameweek.
        
        Args:
            gameweek: Gameweek number
            
        Returns:
            List of fixtures in that gameweek
        """
        all_fixtures = self.get_all_fixtures()
        return [f for f in all_fixtures if f.get('event') == gameweek]
    
    def get_fixtures_by_team(self, team_id: int, upcoming_only: bool = False) -> List[Dict[str, Any]]:
        """
        Get fixtures for a specific team.
        
        Args:
            team_id: Team ID (1-20)
            upcoming_only: If True, only return unplayed fixtures
            
        Returns:
            List of team's fixtures
        """
        all_fixtures = self.get_all_fixtures()
        team_fixtures = [
            f for f in all_fixtures
            if f.get('team_h') == team_id or f.get('team_a') == team_id
        ]
        
        if upcoming_only:
            team_fixtures = [f for f in team_fixtures if not f.get('finished')]
        
        return team_fixtures
    
    def get_upcoming_fixtures(self, num_gameweeks: int = 5) -> List[Dict[str, Any]]:
        """
        Get upcoming fixtures for next N gameweeks.
        
        Args:
            num_gameweeks: Number of gameweeks to look ahead
            
        Returns:
            List of upcoming fixtures
        """
        all_fixtures = self.get_all_fixtures()
        upcoming = [f for f in all_fixtures if not f.get('finished')]
        
        # Get unique gameweek numbers and sort
        gws = sorted(set(f.get('event') for f in upcoming if f.get('event')))[:num_gameweeks]
        
        return [f for f in upcoming if f.get('event') in gws]
