# Quick Start: FPL Agent Evaluation Framework

## ✅ What You Have Now

Your evaluation framework is ready! Here's what was created:

1. **`evals/test_cases.yaml`** - 35 test cases covering all tool categories
2. **`evals/eval_runner.py`** - Main evaluation engine
3. **`run_evals.py`** - Quick runner script
4. **`evals/README.md`** - Comprehensive documentation
5. **`evals/reports/`** - Directory for evaluation reports

## 🚀 Quick Test

Try it out right now:

```bash
# Test a small category first (3 tests)
python run_evals.py --category player_search

# If that works, try a bigger category (5 tests)
python run_evals.py --category find_best_players

# Run all tests (35 tests)
python run_evals.py
```

## 📊 What Gets Tested

The framework tests whether your agent calls the **correct tools** for different queries:

### Player Analysis (16 tests)
- Player search: "Find Mohamed Salah"
- Detailed stats: "Show me Salah's stats"
- Comparisons: "Compare Haaland and Kane"
- Best players: "Find best midfielders under £8m"

### Gameweek Info (9 tests)
- Current GW: "What gameweek are we in?"
- Next GW: "When is the next deadline?"
- Specific GW: "Show me gameweek 5"
- Season: "How far through the season are we?"

### Team Analysis (5 tests - require team ID)
- Team info: "Show me my team"
- Performance: "Analyze my team"
- Value: "What's my team value?"

### Multi-Tool (5 tests)
- Complex: "Compare Haaland and Kane, then find other forwards under £10m"

## 📝 Example Run

```bash
$ python run_evals.py --category player_search

🚀 Running command: python evals/eval_runner.py --category player_search

📂 Loading test cases from: evals/test_cases.yaml
✅ Loaded 3 test cases

🚀 Running 3 evaluation tests...

📊 Evaluation Summary
┌─────────────────────┬─────────┐
│ Metric              │ Value   │
├─────────────────────┼─────────┤
│ Total Tests         │ 3       │
│ Passed              │ ✅ 3    │
│ Failed              │ ❌ 0    │
│ Pass Rate           │ 100.0%  │
│ Avg Execution Time  │ 2.34s   │
└─────────────────────┴─────────┘

💾 Report saved to: evals/reports/eval_report_20250106_143022.json
```

## 🎯 Understanding Results

### ✅ PASS = Agent called the right tool(s)

Example:
```
Query: "Find Mohamed Salah"
Expected: search_player_by_name
Actual: search_player_by_name
Result: ✅ PASS
```

### ❌ FAIL = Agent didn't call expected tool

Example:
```
Query: "Compare Haaland and Kane"
Expected: compare_two_players
Actual: search_player_by_name, search_player_by_name
Result: ❌ FAIL (missing compare_two_players)
```

## 🛠️ Common Commands

```bash
# Run all tests
python run_evals.py

# Run with verbose output (see each test)
python run_evals.py --verbose

# Run specific category
python run_evals.py --category player_search
python run_evals.py --category gameweek
python run_evals.py --category find_best_players

# Include team tests (needs your team ID)
python run_evals.py --team-id 7798096

# Combination
python run_evals.py --category player --verbose
```

## 📈 Adding Your Own Tests

Edit `evals/test_cases.yaml` and add:

```yaml
test_cases:
  # ... existing tests ...
  
  - id: "my_test_001"
    category: "my_category"
    query: "Your test query here"
    expected_tools:
      - "tool_name_that_should_be_called"
    description: "What this test validates"
```

Then run:

```bash
python run_evals.py --category my_category
```

## 🔍 Reviewing Results

### Terminal Output
See results immediately in your terminal with colored tables

### JSON Report
Detailed results saved to `evals/reports/eval_report_TIMESTAMP.json`

```bash
# View latest report
cat evals/reports/eval_report_*.json | jq .summary
```

## 💡 Tips

1. **Start Small**: Test one category first
2. **Use Verbose**: Add `--verbose` to see what's happening
3. **Check Reports**: Review JSON reports for detailed analysis
4. **Failed Queries**: Use `/log` in main agent to capture real failures
5. **Iterate**: Add failed patterns to test_cases.yaml

## 🎓 Next Steps

1. **Run your first evaluation**:
   ```bash
   python run_evals.py --category player_search --verbose
   ```

2. **If all pass, run full suite**:
   ```bash
   python run_evals.py
   ```

3. **Review any failures** and iterate

4. **Add your own test cases** based on real usage

5. **Run regularly** after making changes to prompts or tools

## 📚 Full Documentation

See `evals/README.md` for complete documentation.

## ❓ Troubleshooting

**"Test file not found"**: Make sure you're in the FPL-Agent directory

**"No tests match category"**: Check spelling - use `--category player` not `--category players`

**"Authentication error"**: Check your `.env` file has valid Azure OpenAI credentials

**"Requires team_id"**: Some tests need `--team-id YOUR_ID`

---

**Ready to test?** Run: `python run_evals.py --category player_search --verbose` 🚀
