#!/usr/bin/env python3
"""
Test script for the improved find_best_players_by_position tool
"""

import json
import sys
from tools.player_tools import find_best_players_by_position

def test_json_input():
    """Test with JSON input (as LangChain would pass it)"""
    print("=" * 80)
    print("TEST 1: JSON input - Forwards under £10m")
    print("=" * 80)
    
    json_input = json.dumps({
        "position": "Forward",
        "max_price": 10.0
    })
    
    result = find_best_players_by_position.invoke(json_input)
    print(result)
    print("\n")

def test_json_input_with_min_price():
    """Test with min and max price"""
    print("=" * 80)
    print("TEST 2: JSON input - Midfielders £6m-£8m")
    print("=" * 80)
    
    json_input = json.dumps({
        "position": "Midfielder",
        "max_price": 8.0,
        "min_price": 6.0,
        "min_minutes": 300
    })
    
    result = find_best_players_by_position.invoke(json_input)
    print(result)
    print("\n")

def test_simple_string_input():
    """Test with simple string input (legacy support)"""
    print("=" * 80)
    print("TEST 3: Simple string input - Defenders")
    print("=" * 80)
    
    result = find_best_players_by_position.invoke("Defender")
    print(result)
    print("\n")

def test_dict_input():
    """Test with dict input (as LangChain sometimes passes it)"""
    print("=" * 80)
    print("TEST 4: Dict input - Goalkeepers under £5m")
    print("=" * 80)
    
    # When passing dict to a LangChain tool, convert to JSON string
    dict_input = {
        "position": "Goalkeeper",
        "max_price": 5.0
    }
    
    result = find_best_players_by_position.invoke(json.dumps(dict_input))
    print(result)
    print("\n")

def test_position_aliases():
    """Test with position aliases"""
    print("=" * 80)
    print("TEST 5: Position aliases - 'Striker' should work like 'Forward'")
    print("=" * 80)
    
    json_input = json.dumps({
        "position": "Striker",
        "max_price": 9.0
    })
    
    result = find_best_players_by_position.invoke(json_input)
    print(result)
    print("\n")

def test_invalid_position():
    """Test error handling for invalid position"""
    print("=" * 80)
    print("TEST 6: Invalid position error handling")
    print("=" * 80)
    
    json_input = json.dumps({
        "position": "InvalidPosition",
        "max_price": 10.0
    })
    
    result = find_best_players_by_position.invoke(json_input)
    print(result)
    print("\n")

def test_invalid_json():
    """Test error handling for invalid JSON"""
    print("=" * 80)
    print("TEST 7: Invalid JSON error handling")
    print("=" * 80)
    
    result = find_best_players_by_position.invoke("{invalid json")
    print(result)
    print("\n")

def main():
    """Run all tests"""
    print("\n")
    print("*" * 80)
    print("TESTING find_best_players_by_position TOOL")
    print("*" * 80)
    print("\n")
    
    try:
        test_json_input()
        test_json_input_with_min_price()
        test_simple_string_input()
        test_dict_input()
        test_position_aliases()
        test_invalid_position()
        test_invalid_json()
        
        print("=" * 80)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED WITH ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
