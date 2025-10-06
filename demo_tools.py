"""
Demo script to showcase FPL Agent LangChain tools.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.player_tools import (
    search_player_by_name,
    get_player_detailed_stats,
    compare_two_players,
    find_best_players_by_position
)

print("🏆 FPL Agent - Tool Demonstration\n")
print("=" * 80)

# Demo 1: Search for a player
print("\n📌 DEMO 1: Search for 'Haaland'")
print("-" * 80)
result = search_player_by_name.invoke("Haaland")
print(result)

# Demo 2: Get detailed stats
print("\n📌 DEMO 2: Detailed stats for 'Salah'")
print("-" * 80)
result = get_player_detailed_stats.invoke("Salah")
print(result)

# Demo 3: Compare players
print("\n📌 DEMO 3: Compare 'Haaland' vs 'Watkins'")
print("-" * 80)
result = compare_two_players.invoke('{"player1_name": "Haaland", "player2_name": "Watkins"}')
print(result)

# Demo 4: Find best midfielders under 8m
print("\n📌 DEMO 4: Top Midfielders under £8m")
print("-" * 80)
result = find_best_players_by_position.invoke('{"position": "midfielder", "max_price": 8.0, "min_minutes": 300}')
print(result)

print("\n" + "=" * 80)
print("✨ Demo Complete! These tools are ready for the LangChain agent.\n")
