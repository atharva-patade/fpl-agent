# 🏆 FPL Agent - Your AI-Powered Fantasy Premier League Assistant

An intelligent AI agent built with LangChain and Azure OpenAI to help you dominate your Fantasy Premier League (FPL) leagues. Get data-driven insights, transfer recommendations, and strategic advice to maximize your points every gameweek.

## 🎯 Features

- **🤖 Intelligent Chat Interface**: Natural language conversations powered by Azure OpenAI (GPT-4)
- **🔍 Player Search & Analysis**: Search players, get detailed stats, and compare performance
- **📊 8 Specialized Tools**: 4 player analysis tools + 4 gameweek tracking tools
- **📅 Gameweek Tracking**: Real-time current gameweek info, deadlines, and season progress
- **💡 Smart Recommendations**: AI-powered insights based on real FPL data
- **🎨 Beautiful Terminal UI**: Rich interface with panels, tables, and formatted output
- **🆔 Optional Team ID**: Explore FPL data without a team or get personalized advice with your ID
- **💾 Conversation Memory**: Context-aware responses that remember your previous questions
- **📝 Query Logging**: Track and review queries with `/log` command for continuous improvement

## 🏗️ Architecture

```
FPL-Agent/
├── config/          # Configuration and settings
├── fpl_api/         # FPL API client modules
├── models/          # Data models
├── agents/          # LangChain agent implementation
├── tools/           # LangChain tools for the agent
├── strategies/      # Advanced analysis modules
└── utils/           # Helper utilities
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Azure OpenAI API access
- FPL Team ID

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/atharva-patade/fpl-agent.git
cd fpl-agent
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_azure_openai_key
OPENAI_API_HOST=https://your-resource.openai.azure.com/
OPENAI_DEPLOYMENT=gpt-4.1
OPENAI_API_VERSION=2024-07-01-preview
```

### Usage

**Interactive Mode (Recommended):**
```bash
python main.py
```

The agent will:
1. Display a welcome banner with features and commands
2. Ask if you want to provide your FPL Team ID (optional)
3. Validate your team ID and show team information
4. Start an interactive chat session

**Special Commands:**
- `/team` - Set or view your FPL team ID
- `/help` - Show available commands and example questions
- `/clear` - Clear conversation history
- `/log` - Log current query as failed for review (saves to `evals/failed_queries.jsonl`)
- `/exit` - Exit the agent

**Note:** You can explore FPL data without a team ID. The agent will only prompt for it when you ask team-specific questions.

**Example Questions to Try:**
- "What gameweek are we in?"
- "Find me the best midfielders under £8m"
- "Compare Haaland and Watkins"
- "Show me Salah's detailed stats"
- "What's the season progress?"

## 💬 Example Conversations

```
You: What gameweek are we in?

🔧 Using tool: get_current_gameweek_info

🤖 Agent: We are currently in Gameweek 7 of the 2024/25 season.

**Current Gameweek: 7**
- Name: Gameweek 7
- Deadline: 2025-10-03T17:30:00Z
- Status: In Progress
- Average Score: 60 points
- Highest Score: 135 points

---

You: Find me the best midfielders under £8m

🔧 Using tool: find_best_players_by_position

🤖 Agent: Here are the best midfielders under £8.0m based on points per million:

1. **Bryan Mbeumo** (£7.5m) - 52 pts, 6.93 PPM, Form: 5.8
2. **Bukayo Saka** (£7.9m) - 48 pts, 6.08 PPM, Form: 4.8
...

---

You: Compare Haaland and Watkins

🔧 Using tool: compare_two_players

🤖 Agent: Here's a detailed comparison:

**Erling Haaland vs Ollie Watkins**

Price: £15.1m vs £8.8m
Total Points: 68 vs 42
Points per Game: 11.3 vs 6.0
Form: 7.8 vs 4.2

Haaland is significantly more expensive but delivers nearly double the points...

---

You: Show me Salah's detailed stats

🔧 Using tool: get_player_detailed_stats

🤖 Agent: Here's Mohamed Salah's comprehensive analysis:

**Mohamed Salah** - Liverpool Midfielder
Price: £12.5m | Selected by: 45.2%

**Season Performance:**
- Total Points: 56
- Points per Game: 8.0
- Goals: 4 | Assists: 4
- Bonus: 8
...
```

## 🛠️ API Modules

### Bootstrap API
Access to game-wide data:
- All players and their stats
- All 20 Premier League teams
- Gameweek information
- Game settings and rules

### Manager API
Your team information:
- Team details and value
- Transfer history
- Gameweek picks
- Performance history

### Player API
Player-specific data:
- Detailed statistics
- Upcoming fixtures
- Historical performance
- Live gameweek data

### Fixtures API
Match information:
- All season fixtures
- Gameweek-specific fixtures
- Team-specific fixtures
- Fixture difficulty

## 🤖 LangChain Tools

The agent has access to **8 specialized tools** for comprehensive FPL analysis. All tools are located in the `tools/` directory and are decorated with `@tool` for LangChain integration.

📚 **[See TOOLS.md for complete tool documentation](TOOLS.md)**

### Player Analysis Tools (4 tools)
**Location:** `tools/player_tools.py`

#### `search_player_by_name(name: str)`
**Use Cases:**
- Quickly find a player's basic information
- Get player ID for further analysis
- Check current price and ownership
- Verify player exists before detailed analysis

**Returns:** Player name, ID, team, position, price, total points, form, and ownership percentage

**Example:** `search_player_by_name("Salah")` → Find Mohamed Salah's current stats

---

#### `get_player_detailed_stats(player_name: str)`
**Use Cases:**
- Deep dive into a player's season performance
- Analyze recent form (last 5 gameweeks)
- Review upcoming fixture difficulty
- Calculate value metrics (points per million)
- Make informed transfer decisions

**Returns:** Comprehensive analysis including:
- Basic info (position, team, price, ownership)
- Season performance (total points, PPG, form, goals, assists, clean sheets)
- Recent form with points breakdown
- Next 5 fixtures with difficulty ratings
- Value metrics (points per £1m, ICT index)

**Example:** `get_player_detailed_stats("Haaland")` → Full analysis of Erling Haaland

---

#### `compare_two_players(player1_name: str, player2_name: str)`
**Use Cases:**
- Make transfer decisions between two options
- Compare premium vs budget options
- Evaluate similar players in same position
- Determine better value for money

**Returns:** Side-by-side comparison of:
- Price
- Total points and points per game
- Form and ownership
- Goals, assists, clean sheets
- Value analysis (points per £1m)

**Example:** `compare_two_players("Haaland", "Watkins")` → Head-to-head striker comparison

---

#### `find_best_players_by_position(position: str, max_price: float = 15.0, min_minutes: int = 200)`
**Use Cases:**
- Find transfer targets within budget
- Discover differential picks (low ownership, high value)
- Identify best value players by position
- Build your initial squad
- Find bench fodder (low price, guaranteed minutes)

**Parameters:**
- `position`: "Goalkeeper", "Defender", "Midfielder", or "Forward"
- `max_price`: Maximum price in millions (e.g., 8.5)
- `min_minutes`: Minimum minutes played (filters out non-starters)

**Returns:** Top 10 players sorted by points per million with:
- Full name and price
- Total points, PPM, and form
- Ownership percentage and minutes played

**Example:** `find_best_players_by_position("midfielder", 8.0, 300)` → Best midfielders under £8m with 300+ minutes

---

### Gameweek Tools (4 tools)
**Location:** `tools/general_tools.py`

#### `get_current_gameweek_info()`
**Use Cases:**
- Check which gameweek is currently active
- View current gameweek deadline and status
- See average scores and highest score

**Returns:** Current gameweek ID, name, deadline, status, and statistics

**Example:** Ask "What gameweek are we in?" → Returns GW7 with deadline and scores

---

#### `get_next_gameweek_info()`
**Use Cases:**
- Plan ahead for upcoming gameweek
- Check next deadline
- Prepare transfer strategy

**Returns:** Next gameweek ID, name, and deadline

**Example:** Ask "When is the next gameweek?" → Returns GW8 deadline

---

#### `get_gameweek_by_number(gameweek_number: int)`
**Use Cases:**
- Review specific gameweek statistics
- Analyze historical performance
- Check past deadlines

**Parameters:**
- `gameweek_number`: Integer from 1-38

**Returns:** Specific gameweek details, status, and statistics if finished

**Example:** `get_gameweek_by_number(5)` → Returns GW5 information

---

#### `get_season_overview()`
**Use Cases:**
- Check season progress
- See how many gameweeks remain
- Understand timeline for planning

**Returns:** Total gameweeks, current GW, finished/remaining counts, progress percentage

**Example:** Ask "How far through the season are we?" → Returns 18% complete (7/38 GWs)

---

### Future Tool Categories *(Coming Soon)*

#### Team Analysis Tools - `tools/team_tools.py`
- `analyze_my_team`: Comprehensive squad analysis
- `identify_underperforming_players`: Find players not delivering
- `get_team_value_and_bank`: Check budget and team value
- `optimize_lineup_for_gameweek`: Best 11 and captain selection

#### Fixture Analysis Tools - `tools/fixture_tools.py`
- `analyze_upcoming_fixtures`: Fixture difficulty analysis
- `get_fixtures_for_gameweek`: All matches in specific GW
- `find_teams_with_best_fixtures`: Identify favorable schedules
- `get_double_gameweek_teams`: Find teams with multiple fixtures

#### Transfer Strategy Tools - `tools/transfer_tools.py`
- `suggest_transfers`: AI-powered recommendations
- `calculate_transfer_impact`: Predict points gain/loss
- `get_price_change_predictions`: Track price movements
- `get_differential_picks`: High-value, low-owned players

---

### 🧪 Testing the Tools

**Test Player Tools:**
```bash
python demo_tools.py
```

**Test Gameweek Tools:**
```bash
python test_gameweek_tools.py
```

**Test All Basic Functionality:**
```bash
python test_basic.py
```

**Run Complete Test Suite:**
```bash
# All 8 tests should pass
python test_basic.py

# Expected output:
# ✅ Configuration loads successfully
# ✅ FPL Client initialized
# ✅ Bootstrap API - Current gameweek: 7
# ✅ Manager API - Team 7798096 found
# ✅ Player API - Haaland found
# ✅ Fixtures API - 380 fixtures loaded
# ✅ Player tools working
# ✅ Gameweek tools working
```

## 📊 Project Status

**Current Phase**: Phase 1 - Core Infrastructure ✅

### Completed ✅
- [x] Project structure with OOP architecture
- [x] Configuration management with Pydantic
- [x] API client with caching and error handling
- [x] Bootstrap API module (players, teams, gameweeks)
- [x] Manager API module (team info, history, transfers)
- [x] Player API module (detailed stats, fixtures, history)
- [x] Fixtures API module (all matches, by GW, by team)
- [x] **LangChain Player Tools (4 tools)** - `tools/player_tools.py`
  - search_player_by_name
  - get_player_detailed_stats
  - compare_two_players
  - find_best_players_by_position
- [x] Comprehensive testing suite
- [x] Demo scripts and documentation

### Completed ✅ (Phase 2 - Interactive CLI & Tools)
- [x] **Interactive CLI** - `main.py`
  - LangChain ReAct agent with custom prompts
  - Optional team ID on startup (flexible exploration mode)
  - Dynamic context engineering (adapts prompt based on team ID)
  - Team ID validation and display
  - Special commands (/team, /help, /clear, /log, /exit)
  - Rich terminal UI with panels, tables, and markdown
  - Conversation memory and streaming callbacks
  - Error handling and graceful exits
  - Query logging for evaluation and improvement
- [x] **Gameweek Tools (4 tools)** - `tools/general_tools.py`
  - get_current_gameweek_info
  - get_next_gameweek_info
  - get_gameweek_by_number
  - get_season_overview
- [x] **Complete Documentation**
  - README.md with full project details
  - TOOLS.md with comprehensive tool documentation
  - TESTING_GUIDE.md for development workflow
  - READY_TO_TEST.md for quick start testing

### In Progress 🚧
- [ ] **Evaluation Framework** - `evals/`
  - Behavior-based test cases (YAML)
  - Automated evaluation runner
  - Failed query tracking and analysis
  - Performance metrics and reporting

### Upcoming 📋
- [ ] **Additional Tool Categories**
  - Team analysis tools - `tools/team_tools.py`
  - Fixture analysis tools - `tools/fixture_tools.py`
  - Transfer strategy tools - `tools/transfer_tools.py`
  - Statistical analysis tools - `tools/statistics_tools.py`
- [ ] **Advanced Features**
  - Strategy modules (predictions, recommendations)
  - Gameweek briefings automation
  - Price change tracking and alerts
  - Chip strategy recommendations
- [ ] **Agent Improvements**
  - Prompt optimization - `agents/prompts.py`
  - Multi-agent workflows
  - RAG integration for historical data

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

MIT License

## 🙏 Acknowledgments

- Fantasy Premier League API
- LangChain framework
- Azure OpenAI

## 📧 Contact

For questions or suggestions, please open an issue on GitHub.

---

**Built with ❤️ for FPL managers who want to climb the ranks**
