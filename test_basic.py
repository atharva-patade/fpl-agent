"""
Basic test script to verify FPL Agent core functionality.
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("🧪 Testing FPL Agent Core Components\n")
print("=" * 60)

# Test 1: Configuration
print("\n1️⃣ Testing Configuration...")
try:
    from config.settings import settings
    print(f"✅ Configuration loaded")
    print(f"   - FPL Base URL: {settings.fpl_base_url}")
    print(f"   - Cache enabled: {settings.enable_cache}")
    print(f"   - OpenAI configured: {'Yes' if settings.openai_api_key else 'No'}")
except Exception as e:
    print(f"❌ Configuration failed: {e}")

# Test 2: FPL Client
print("\n2️⃣ Testing FPL API Client...")
try:
    from fpl_api.client import FPLClient
    client = FPLClient()
    print(f"✅ FPL Client initialized")
    print(f"   - Base URL: {client.base_url}")
except Exception as e:
    print(f"❌ Client initialization failed: {e}")

# Test 3: Bootstrap API
print("\n3️⃣ Testing Bootstrap API...")
try:
    from fpl_api.bootstrap import BootstrapAPI
    bootstrap = BootstrapAPI(client)
    
    # Test getting current gameweek
    current_gw = bootstrap.get_current_gameweek()
    print(f"✅ Bootstrap API working")
    print(f"   - Current Gameweek: {current_gw.get('id', 'N/A')}")
    print(f"   - GW Name: {current_gw.get('name', 'N/A')}")
    
    # Test getting total players
    total_players = bootstrap.get_total_players()
    print(f"   - Total FPL Users: {total_players:,}")
    
    # Test getting all teams
    teams = bootstrap.get_all_teams()
    print(f"   - Premier League Teams: {len(teams)}")
    
    # Test getting all players
    players = bootstrap.get_all_players()
    print(f"   - Total PL Players: {len(players)}")
    
except Exception as e:
    print(f"❌ Bootstrap API failed: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Player Search
print("\n4️⃣ Testing Player Search...")
try:
    # Search for Salah
    salah = bootstrap.get_player_by_name("Salah")
    if salah:
        player = salah[0]
        print(f"✅ Player search working")
        print(f"   - Found: {player['first_name']} {player['second_name']}")
        print(f"   - Price: £{player['now_cost']/10}m")
        print(f"   - Total Points: {player['total_points']}")
        print(f"   - Form: {player['form']}")
    else:
        print(f"⚠️  Player 'Salah' not found")
except Exception as e:
    print(f"❌ Player search failed: {e}")

# Test 5: Manager API
print("\n5️⃣ Testing Manager API...")
try:
    from fpl_api.managers import ManagerAPI
    manager_api = ManagerAPI(client)
    
    # Use your team ID
    team_id = 7798096
    team_summary = manager_api.get_team_summary(team_id)
    
    print(f"✅ Manager API working")
    print(f"   - Team: {team_summary.get('team_name')}")
    print(f"   - Manager: {team_summary.get('manager_name')}")
    print(f"   - Total Points: {team_summary.get('total_points')}")
    print(f"   - Overall Rank: {team_summary.get('overall_rank'):,}")
    print(f"   - Team Value: £{team_summary.get('team_value')}m")
    print(f"   - Bank: £{team_summary.get('bank')}m")
    
except Exception as e:
    print(f"❌ Manager API failed: {e}")
    import traceback
    traceback.print_exc()

# Test 6: Fixtures API
print("\n6️⃣ Testing Fixtures API...")
try:
    from fpl_api.fixtures import FixturesAPI
    fixtures_api = FixturesAPI(client)
    
    all_fixtures = fixtures_api.get_all_fixtures()
    print(f"✅ Fixtures API working")
    print(f"   - Total Fixtures: {len(all_fixtures)}")
    
    # Get current GW fixtures
    if current_gw.get('id'):
        gw_fixtures = fixtures_api.get_fixtures_by_gameweek(current_gw['id'])
        print(f"   - GW{current_gw['id']} Fixtures: {len(gw_fixtures)}")
    
except Exception as e:
    print(f"❌ Fixtures API failed: {e}")

# Test 7: Player API
print("\n7️⃣ Testing Player API...")
try:
    from fpl_api.players import PlayerAPI
    player_api = PlayerAPI(client)
    
    # Get Salah's detailed stats
    if salah:
        player_id = salah[0]['id']
        player_summary = player_api.get_player_summary(player_id)
        
        print(f"✅ Player API working")
        print(f"   - Player ID: {player_id}")
        print(f"   - History records: {len(player_summary.get('history', []))}")
        print(f"   - Upcoming fixtures: {len(player_summary.get('fixtures', []))}")
    
except Exception as e:
    print(f"❌ Player API failed: {e}")

# Test 8: LangChain Tools
print("\n8️⃣ Testing LangChain Tools...")
try:
    from tools.player_tools import (
        search_player_by_name,
        get_player_detailed_stats,
        compare_two_players,
        find_best_players_by_position
    )
    
    print(f"✅ LangChain tools imported successfully")
    print(f"   - search_player_by_name: ✓")
    print(f"   - get_player_detailed_stats: ✓")
    print(f"   - compare_two_players: ✓")
    print(f"   - find_best_players_by_position: ✓")
    
    # Test a simple tool call
    print("\n   Testing search_player_by_name tool:")
    result = search_player_by_name.invoke({"name": "Haaland"})
    print(f"   {result[:200]}..." if len(result) > 200 else f"   {result}")
    
except Exception as e:
    print(f"❌ LangChain tools failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("\n✨ Testing Complete!\n")
