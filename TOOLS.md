# FPL Agent Tools

This document lists all the tools available to the FPL AI Agent.

## Overview

The agent has access to **8 specialized tools** organized into two categories:

- **4 Player Analysis Tools** - For searching, analyzing, and comparing players
- **4 Gameweek Tools** - For tracking gameweek progress and season status

---

## 🎯 Player Analysis Tools

### 1. `search_player_by_name`

**Purpose**: Search for FPL players by name

**Use Cases**:
- Find players by first name, last name, or partial matches
- Get basic player information (team, position, price)
- Discover player IDs for detailed analysis

**Example Queries**:
- "Find Haaland"
- "Search for players named Salah"
- "Who is Son?"

**Returns**: List of matching players with team, position, price, and form

---

### 2. `get_player_detailed_stats`

**Purpose**: Get comprehensive statistics for a specific player

**Use Cases**:
- Analyze player performance metrics
- Check current form and fixtures
- Review recent game statistics
- Assess value for money

**Example Queries**:
- "Tell me about Erling Haaland's stats"
- "How is Salah performing?"
- "Show me detailed stats for Bruno Fernandes"

**Returns**: 
- Basic info (name, team, position, price)
- Performance metrics (total points, form, points per game)
- Ownership and selection percentage
- Recent fixtures and scores
- Expected stats (xG, xA)

---

### 3. `compare_players`

**Purpose**: Compare statistics between two players

**Use Cases**:
- Make transfer decisions
- Choose between similar players
- Compare value for money
- Analyze differential picks

**Example Queries**:
- "Compare Haaland and Darwin Nunez"
- "Who is better between Saka and Palmer?"
- "Compare Salah vs Son"

**Returns**: Side-by-side comparison of:
- Price and value metrics
- Points and performance
- Form and consistency
- Expected stats (xG, xA)
- Fixtures difficulty

---

### 4. `find_best_players_by_position`

**Purpose**: Discover top-performing players in a specific position

**Use Cases**:
- Find the best value picks
- Identify form players
- Discover differential options
- Plan team structure

**Arguments**:
- `position`: GKP, DEF, MID, or FWD
- `limit`: Number of players to return (default: 10)
- `sort_by`: Metric to sort by (default: "total_points")
  - Options: total_points, form, value, points_per_game

**Example Queries**:
- "Show me the best midfielders"
- "Find top 5 forwards by form"
- "Best value defenders"
- "Top goalkeepers this season"

**Returns**: Ranked list of players with key metrics

---

## 📅 Gameweek Tools

### 5. `get_current_gameweek_info`

**Purpose**: Get information about the current FPL gameweek

**Use Cases**:
- Check which gameweek is currently active
- See current gameweek deadline
- View average scores and statistics
- Confirm gameweek status

**Example Queries**:
- "What gameweek are we in?"
- "What's the current gameweek?"
- "When is the next deadline?"
- "What's the average score this week?"

**Returns**:
- Current gameweek ID and name
- Deadline time
- Status (In Progress/Finished/Upcoming)
- Average entry score (if available)
- Highest score (if available)

---

### 6. `get_next_gameweek_info`

**Purpose**: Get information about the next upcoming gameweek

**Use Cases**:
- Plan ahead for transfers
- Check upcoming deadline
- Prepare team selections

**Example Queries**:
- "When is the next gameweek?"
- "What's the next deadline?"
- "Tell me about gameweek 8"

**Returns**:
- Next gameweek ID and name
- Deadline time
- Status

---

### 7. `get_gameweek_by_number`

**Purpose**: Get detailed information about a specific gameweek

**Arguments**:
- `gameweek_number`: Integer from 1-38

**Use Cases**:
- Review historical gameweek performance
- Check specific gameweek deadlines
- Analyze past scores and statistics

**Example Queries**:
- "Tell me about gameweek 5"
- "What happened in GW3?"
- "Show me gameweek 10 stats"

**Returns**:
- Gameweek details (ID, name, deadline)
- Status (Current/Next/Finished/Upcoming)
- Statistics (average score, highest score) if finished

---

### 8. `get_season_overview`

**Purpose**: Get overview of the current FPL season

**Use Cases**:
- Check season progress
- See how many gameweeks remain
- Understand season timeline

**Example Queries**:
- "How many gameweeks are left?"
- "What's the season progress?"
- "Give me a season overview"
- "How far through the season are we?"

**Returns**:
- Total gameweeks (38)
- Current gameweek number
- Gameweeks finished count
- Gameweeks remaining count
- Progress percentage

---

## Tool Usage Notes

### How the Agent Uses Tools

1. **Automatic Selection**: The agent automatically selects the most appropriate tool(s) based on your query
2. **Multi-Tool Queries**: Complex queries may use multiple tools in sequence
3. **Intelligent Fallbacks**: If a tool fails, the agent will try alternative approaches
4. **Real-Time Data**: All tools fetch live data from the FPL API

### Tool Visibility

When the agent uses a tool, you'll see:
- 🔧 **Tool name** being executed
- ⏳ **Processing indicator** while fetching data
- ✅ **Results** formatted for readability

### Tool Reliability

- **Retry Logic**: All API calls have automatic retry on failure (3 attempts)
- **Caching**: Results cached for 15 minutes to improve performance
- **Error Handling**: Graceful degradation with helpful error messages

---

## Adding New Tools

To extend the agent with new tools:

1. **Player Tools**: Add to `tools/player_tools.py`
2. **Gameweek Tools**: Add to `tools/general_tools.py`
3. **New Category**: Create new file in `tools/` directory
4. **Register**: Import in `tools/__init__.py`
5. **Connect**: Add to agent initialization in `main.py`

Each tool should:
- Use the `@tool` decorator from LangChain
- Have a clear, descriptive docstring
- Include use case examples
- Handle errors gracefully
- Return formatted strings for readability

---

## Tool Testing

Test individual tools:

```bash
# Test player tools
python demo_tools.py

# Test gameweek tools
python test_gameweek_tools.py

# Test all basic functionality
python test_basic.py
```

---

## Future Tool Ideas

Potential tools to add:

- [ ] **Fixture Difficulty**: Analyze upcoming fixture difficulty for teams
- [ ] **Transfer Suggestions**: AI-powered transfer recommendations based on team
- [ ] **Captain Picks**: Suggest optimal captain choices for upcoming gameweek
- [ ] **Differential Finder**: Find low-ownership high-performing players
- [ ] **Team Optimizer**: Suggest optimal team structure and formations
- [ ] **Injury Tracker**: Monitor player injuries and availability
- [ ] **Price Change Predictor**: Predict upcoming price changes
- [ ] **Chip Strategy**: Recommend when to use chips (Wildcard, Triple Captain, etc.)

---

Last Updated: October 5, 2025
