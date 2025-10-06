# FPL Agent Evaluation Framework

## Overview

This evaluation framework tests whether the FPL Agent correctly selects the appropriate tools for different types of queries. It validates tool selection behavior without relying on specific data values (which can change over time).

## Files

```
evals/
├── test_cases.yaml          # Test cases with queries and expected tools
├── eval_runner.py           # Main evaluation script
├── failed_queries.jsonl     # Log of failed queries from /log command
└── reports/                 # Generated evaluation reports
    └── eval_report_*.json   # Timestamped JSON reports
```

## Test Cases Structure

The `test_cases.yaml` file contains evaluation test cases structured as:

```yaml
test_cases:
  - id: "test_id"                    # Unique test identifier
    category: "category_name"        # Test category
    query: "User query text"         # Query to test
    expected_tools:                  # List of tools that should be called
      - "tool_name_1"
      - "tool_name_2"
    description: "Test description"  # What this test validates
    requires_team_id: true/false    # Optional: requires team ID
    notes: "Additional notes"        # Optional: extra information
```

## Available Categories

- `player_search` - Basic player name searches
- `player_stats` - Detailed player statistics requests
- `player_comparison` - Comparing two players
- `find_best_players` - Finding players by position/budget
- `gameweek_current` - Current gameweek information
- `gameweek_next` - Next gameweek information
- `gameweek_specific` - Specific gameweek lookup
- `season_overview` - Season progress information
- `team_info` - User's team information (requires team_id)
- `team_analysis` - User's team analysis (requires team_id)
- `team_value` - User's team value (requires team_id)
- `multi_tool` - Complex queries requiring multiple tools

## Running Evaluations

### Basic Usage

```bash
# Run all evaluation tests
python evals/eval_runner.py

# Run with verbose output (shows each test)
python evals/eval_runner.py --verbose

# Run specific category only
python evals/eval_runner.py --category player_search

# Include team-specific tests (requires team ID)
python evals/eval_runner.py --team-id 7798096

# Custom output location
python evals/eval_runner.py --output my_report.json
```

### Quick Runner

Use the `run_evals.py` script for common configurations:

```bash
# Run all tests (simple command)
python run_evals.py

# Run specific category
python run_evals.py --category gameweek

# Run with team ID
python run_evals.py --team-id 7798096

# Verbose mode
python run_evals.py --verbose
```

### Examples

```bash
# Test only player-related queries
python run_evals.py --category player

# Test gameweek queries with detailed output
python run_evals.py --category gameweek --verbose

# Test everything including team tools
python run_evals.py --team-id 7798096 --verbose
```

## Understanding Results

### Pass/Fail Criteria

A test **PASSES** if:
- All expected tools are called by the agent
- No errors occur during execution

A test **FAILS** if:
- Any expected tool is NOT called
- An error occurs during execution
- The test requires team_id but none is provided

**Note:** The agent may call additional tools beyond the expected ones, and that's fine. We only check that the expected tools are included.

### Report Output

The evaluation generates two types of output:

#### 1. Terminal Display

```
📊 Evaluation Summary
┌─────────────────────┬─────────┐
│ Metric              │ Value   │
├─────────────────────┼─────────┤
│ Total Tests         │ 35      │
│ Passed              │ ✅ 32   │
│ Failed              │ ❌ 3    │
│ Pass Rate           │ 91.4%   │
│ Avg Execution Time  │ 2.45s   │
└─────────────────────┴─────────┘

📂 Results by Category
┌──────────────────┬───────┬────────┬────────┬───────────┐
│ Category         │ Total │ Passed │ Failed │ Pass Rate │
├──────────────────┼───────┼────────┼────────┼───────────┤
│ player_search    │ 3     │ 3      │ 0      │ 100.0%    │
│ player_stats     │ 4     │ 4      │ 0      │ 100.0%    │
│ find_best_players│ 5     │ 4      │ 1      │ 80.0%     │
└──────────────────┴───────┴────────┴────────┴───────────┘
```

#### 2. JSON Report File

Saved to `evals/reports/eval_report_<timestamp>.json`:

```json
{
  "summary": {
    "total_tests": 35,
    "passed": 32,
    "failed": 3,
    "pass_rate": 91.4,
    "avg_execution_time": 2.45
  },
  "category_stats": {
    "player_search": {
      "total": 3,
      "passed": 3,
      "failed": 0
    }
  },
  "results": [
    {
      "test_id": "player_search_001",
      "category": "player_search",
      "query": "Find Mohamed Salah",
      "expected_tools": ["search_player_by_name"],
      "actual_tools": ["search_player_by_name"],
      "passed": true,
      "error": null,
      "execution_time": 2.3
    }
  ]
}
```

## Adding New Test Cases

To add new test cases, edit `evals/test_cases.yaml`:

```yaml
test_cases:
  # ... existing tests ...
  
  - id: "my_new_test_001"
    category: "my_category"
    query: "What is my query?"
    expected_tools:
      - "tool_that_should_be_called"
    description: "Description of what this tests"
    requires_team_id: false  # Optional
    notes: "Any additional notes"  # Optional
```

### Best Practices for Test Cases

1. **Clear Intent**: Make the query clear about what information is needed
2. **Single Responsibility**: Each test should focus on one type of query pattern
3. **Realistic Queries**: Use natural language that real users would type
4. **Expected Tools**: List the minimum set of tools required
5. **Categories**: Group similar tests together
6. **Edge Cases**: Include variations in phrasing for the same intent

### Example: Adding a Captain Recommendation Test

```yaml
- id: "captain_recommendation_001"
  category: "captain_strategy"
  query: "Who should I captain this week?"
  expected_tools:
    - "get_current_gameweek_info"
    - "get_player_detailed_stats"
  description: "Captain recommendation with current gameweek context"
  notes: "May also call find_best_players_by_position for alternatives"
```

## Interpreting Failed Tests

When tests fail, check:

1. **Missing Tool Calls**: Did the agent skip a necessary tool?
   - Review the agent's prompt to ensure it knows when to use the tool
   - Check if the tool description is clear

2. **Wrong Tool Selection**: Did the agent call a different tool?
   - The query might be ambiguous
   - Tool descriptions might overlap

3. **Errors**: Did the agent encounter an error?
   - Check the error message in the report
   - Verify API connectivity and authentication

## Continuous Evaluation

### After Prompt Changes

Run evaluations after modifying agent prompts:

```bash
# Test that prompt changes don't break tool selection
python run_evals.py --verbose
```

### After Adding New Tools

Add corresponding test cases for new tools:

```bash
# Test only the new tool category
python run_evals.py --category new_category
```

### Before Deployment

Always run full evaluation suite:

```bash
# Full test with team ID
python run_evals.py --team-id YOUR_TEAM_ID
```

## Integration with Failed Queries

The `/log` command in the main agent saves failed queries to `failed_queries.jsonl`. You can:

1. Review failed queries from real usage
2. Convert them into test cases in `test_cases.yaml`
3. Fix the issues that caused failures
4. Run evals to verify the fixes

Example workflow:

```bash
# 1. Use agent and log failures with /log command
python main.py

# 2. Review failed queries
cat evals/failed_queries.jsonl

# 3. Add patterns to test_cases.yaml
# ... edit test_cases.yaml ...

# 4. Run evaluations
python run_evals.py --verbose

# 5. Fix issues and repeat
```

## Performance Benchmarking

Use evaluation reports to track performance over time:

```bash
# Run baseline evaluation
python run_evals.py > baseline_results.txt

# Make improvements...

# Run new evaluation
python run_evals.py > improved_results.txt

# Compare pass rates and execution times
diff baseline_results.txt improved_results.txt
```

## Troubleshooting

### "Test file not found" Error

```bash
# Make sure you're in the FPL-Agent directory
cd /path/to/FPL-Agent
python run_evals.py
```

### Azure OpenAI Authentication Errors

Check your `.env` file has correct credentials:

```env
OPENAI_API_KEY=your_key
OPENAI_API_HOST=https://your-resource.openai.azure.com/
OPENAI_DEPLOYMENT=gpt-4.1
OPENAI_API_VERSION=2024-07-01-preview
```

### Rate Limiting

If you hit rate limits, reduce test load:

```bash
# Run smaller category
python run_evals.py --category player_search

# Or add delays in eval_runner.py (modify the code)
```

### Team Tests Skipped

Provide team ID to run team-specific tests:

```bash
python run_evals.py --team-id YOUR_TEAM_ID
```

## Advanced Usage

### Custom Test File

```bash
python evals/eval_runner.py --test-file my_custom_tests.yaml
```

### Programmatic Usage

```python
from evals.eval_runner import FPLAgentEvaluator, load_test_cases

# Load tests
test_cases = load_test_cases(Path("evals/test_cases.yaml"))

# Run evaluator
evaluator = FPLAgentEvaluator(team_id=7798096, verbose=True)
evaluator.run_all_tests(test_cases, category_filter="player")

# Get report
report = evaluator.generate_report()
print(f"Pass rate: {report['summary']['pass_rate']}%")
```

## Future Enhancements

- [ ] Add response quality evaluation (not just tool selection)
- [ ] Performance regression testing
- [ ] A/B testing different prompts
- [ ] Automated evaluation on PR/commit
- [ ] Evaluation dashboard/visualization
- [ ] Cost tracking per evaluation run

## Summary

The evaluation framework helps ensure that:
1. ✅ The agent selects the right tools for different queries
2. ✅ Changes to prompts or tools don't break existing functionality
3. ✅ New features work as expected
4. ✅ Performance remains consistent over time

Run `python run_evals.py` regularly to maintain agent quality! 🚀
