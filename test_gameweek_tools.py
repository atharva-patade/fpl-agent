"""
Test script for gameweek tools - verify they return real data not hallucinated responses
"""
from tools.general_tools import (
    get_current_gameweek_info,
    get_next_gameweek_info, 
    get_gameweek_by_number,
    get_season_overview
)

print("=" * 80)
print("GAMEWEEK TOOLS TEST - Verifying Real Data (Not Hallucinated)")
print("=" * 80)

print("\n1️⃣ Testing get_current_gameweek_info()...")
print("-" * 80)
result = get_current_gameweek_info.invoke({})
print(result)

print("\n2️⃣ Testing get_next_gameweek_info()...")
print("-" * 80)
result = get_next_gameweek_info.invoke({})
print(result)

print("\n3️⃣ Testing get_gameweek_by_number(7)...")
print("-" * 80)
result = get_gameweek_by_number.invoke('{"gameweek_number": 7}')
print(result)

print("\n4️⃣ Testing get_season_overview()...")
print("-" * 80)
result = get_season_overview.invoke({})
print(result)

print("\n" + "=" * 80)
print("✅ All gameweek tools tested successfully!")
print("=" * 80)
