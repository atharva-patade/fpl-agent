"""
Players API - handles player-specific endpoints.
"""
from typing import Dict, List, Any
from fpl_api.client import FPLClient


class PlayerAPI:
    """API client for player-specific data."""
    
    def __init__(self, client: FPLClient):
        """
        Initialize Player API.
        
        Args:
            client: FPL API client instance
        """
        self.client = client
    
    def get_player_summary(self, player_id: int) -> Dict[str, Any]:
        """
        Get detailed player summary including fixtures and history.
        
        Args:
            player_id: FPL player ID
            
        Returns:
            Player summary with fixtures, history, past seasons
        """
        return self.client.get(f"element-summary/{player_id}/")
    
    def get_player_fixtures(self, player_id: int) -> List[Dict[str, Any]]:
        """
        Get remaining fixtures for a player.
        
        Args:
            player_id: FPL player ID
            
        Returns:
            List of upcoming fixtures
        """
        summary = self.get_player_summary(player_id)
        return summary.get('fixtures', [])
    
    def get_player_history(self, player_id: int) -> List[Dict[str, Any]]:
        """
        Get player's gameweek-by-gameweek history this season.
        
        Args:
            player_id: FPL player ID
            
        Returns:
            List of gameweek performances
        """
        summary = self.get_player_summary(player_id)
        return summary.get('history', [])
    
    def get_player_past_seasons(self, player_id: int) -> List[Dict[str, Any]]:
        """
        Get player's performance in past seasons.
        
        Args:
            player_id: FPL player ID
            
        Returns:
            List of past season summaries
        """
        summary = self.get_player_summary(player_id)
        return summary.get('history_past', [])
    
    def get_gameweek_live_data(self, gameweek: int) -> Dict[str, Any]:
        """
        Get live stats for all players in a specific gameweek.
        
        Args:
            gameweek: Gameweek number
            
        Returns:
            Live player stats for the gameweek
        """
        return self.client.get(f"event/{gameweek}/live/", use_cache=False)
    
    @staticmethod
    def get_player_photo_url(player: Dict[str, Any]) -> str:
        """
        Get URL for player's photo.
        
        Args:
            player: Player data dict from bootstrap
            
        Returns:
            URL to player photo (110x140 PNG)
        """
        photo = player.get('photo', '')
        if not photo:
            return ""
        code = photo.split('.')[0]
        return f"https://resources.premierleague.com/premierleague25/photos/players/110x140/{code}.png"
