"""
Test Team Tools
Quick verification that team tools work correctly
"""
from tools.team_tools import (
    get_my_team,
    get_my_team_summary,
    get_my_transfers,
    analyze_my_team_performance,
    get_team_value_breakdown
)

# Test team ID from failed_queries.jsonl
TEST_TEAM_ID = 7798096


def test_get_my_team():
    """Test getting team squad"""
    print("\n" + "="*80)
    print("TEST: get_my_team")
    print("="*80)
    
    result = get_my_team.invoke('{"team_id": %d}' % TEST_TEAM_ID)
    print(result)
    assert "Formation" in result
    assert "Goalkeeper" in result or "🥅" in result
    print("\n✅ PASSED: get_my_team")


def test_get_my_team_summary():
    """Test getting team summary"""
    print("\n" + "="*80)
    print("TEST: get_my_team_summary")
    print("="*80)
    
    result = get_my_team_summary.invoke('{"team_id": %d}' % TEST_TEAM_ID)
    print(result)
    assert "Team Name" in result or "Overall" in result
    print("\n✅ PASSED: get_my_team_summary")


def test_get_my_transfers():
    """Test getting transfer history"""
    print("\n" + "="*80)
    print("TEST: get_my_transfers")
    print("="*80)
    
    result = get_my_transfers.invoke('{"team_id": %d, "limit": 5}' % TEST_TEAM_ID)
    print(result)
    assert "Transfer" in result or "No transfers" in result
    print("\n✅ PASSED: get_my_transfers")


def test_analyze_performance():
    """Test performance analysis"""
    print("\n" + "="*80)
    print("TEST: analyze_my_team_performance")
    print("="*80)
    
    result = analyze_my_team_performance.invoke('{"team_id": %d, "last_n_weeks": 3}' % TEST_TEAM_ID)
    print(result)
    assert "Performance" in result or "Points" in result
    print("\n✅ PASSED: analyze_my_team_performance")


def test_value_breakdown():
    """Test value breakdown"""
    print("\n" + "="*80)
    print("TEST: get_team_value_breakdown")
    print("="*80)
    
    result = get_team_value_breakdown.invoke('{"team_id": %d}' % TEST_TEAM_ID)
    print(result)
    assert "Value" in result or "Squad" in result
    print("\n✅ PASSED: get_team_value_breakdown")


if __name__ == "__main__":
    print("\n🏆 FPL Team Tools Test Suite")
    print(f"Testing with Team ID: {TEST_TEAM_ID}\n")
    
    try:
        test_get_my_team()
        test_get_my_team_summary()
        test_get_my_transfers()
        test_analyze_performance()
        test_value_breakdown()
        
        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED!")
        print("="*80)
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
