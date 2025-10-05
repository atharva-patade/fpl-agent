# 🏆 FPL Agent - Your AI-Powered Fantasy Premier League Assistant

An intelligent AI agent built with LangChain and Azure OpenAI to help you dominate your Fantasy Premier League (FPL) leagues. Get data-driven insights, transfer recommendations, and strategic advice to maximize your points every gameweek.

## 🎯 Features

- **Intelligent Chat Interface**: Natural language conversations about your FPL team
- **Transfer Recommendations**: AI-powered suggestions based on form, fixtures, and value
- **Player Analysis**: Deep dive into player statistics, form, and upcoming fixtures
- **Team Optimization**: Get lineup suggestions for maximum points
- **Captain Selection**: Data-driven captaincy recommendations
- **Fixture Analysis**: Understand fixture difficulty and plan ahead
- **League Tracking**: Monitor your position across all your leagues
- **Gameweek Briefings**: Automated summaries of key information before each gameweek

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

```bash
python main.py --team-id YOUR_FPL_TEAM_ID
```

Example:
```bash
python main.py --team-id 7798096
```

## 💬 Example Conversations

```
> What transfers should I make this week?

🤔 Analyzing your team...

Based on my analysis of your team, form, fixtures, and budget:

📊 Current Issues:
- Player X has tough fixtures (AVG FDR: 4.2) for next 3 GWs
- You're lacking midfield coverage from top teams
- £2.5M in the bank

💡 Recommended Transfers:
1. OUT: Player X → IN: Player Y (Expected gain: +12 pts over 3 GWs)
   Reason: Player Y has excellent fixtures, in top form

> Who should captain this week?

🎯 Captain Recommendation for GW 15:
Captain: Haaland (vs Fulham H)
Reasoning: Home fixture, scored in last 3 home games, FDR 2

> Show my team performance

📊 Your Team: "Team Name"
Current GW: 15
Overall Rank: 182,456 (↑ 12,340 from last GW)
Total Points: 734
GW Points: 52

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

The agent has access to powerful tools for comprehensive FPL analysis. All tools are located in the `tools/` directory and are decorated with `@tool` for LangChain integration.

### Player Analysis Tools
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

### Team Analysis Tools
**Location:** `tools/team_tools.py` *(Coming Soon)*

- `analyze_my_team`: Comprehensive analysis of your current squad
- `identify_underperforming_players`: Find players not delivering points
- `get_team_value_and_bank`: Check team value and available budget
- `optimize_lineup_for_gameweek`: Best 11 players and captain for upcoming GW

### Fixture Analysis Tools
**Location:** `tools/fixture_tools.py` *(Coming Soon)*

- `analyze_upcoming_fixtures`: Fixture difficulty for teams over next N gameweeks
- `get_fixtures_for_gameweek`: All matches in a specific gameweek
- `find_teams_with_best_fixtures`: Identify teams with favorable schedules
- `get_double_gameweek_teams`: Find teams with multiple fixtures in one GW

### Transfer Strategy Tools
**Location:** `tools/transfer_tools.py` *(Coming Soon)*

- `suggest_transfers`: AI-powered transfer recommendations
- `calculate_transfer_impact`: Predict points gain/loss from specific transfer
- `get_price_change_predictions`: Players likely to rise/fall in price
- `get_differential_picks`: High-value, low-owned players for rank climbing

### Statistical Analysis Tools
**Location:** `tools/statistics_tools.py` *(Coming Soon)*

- `get_top_scorers`: Highest scoring players overall or by position
- `get_most_selected_players`: Most owned players across all managers
- `calculate_effective_ownership`: Adjusted ownership including captaincy
- `get_form_table`: Players ranked by recent form

---

### 🧪 Testing the Tools

Run the demo script to see all tools in action:
```bash
python demo_tools.py
```

Run the test suite to verify all components:
```bash
python test_basic.py
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

### In Progress 🚧
- [ ] Team analysis tools - `tools/team_tools.py`
- [ ] Fixture analysis tools - `tools/fixture_tools.py`
- [ ] Transfer strategy tools - `tools/transfer_tools.py`
- [ ] Statistical analysis tools - `tools/statistics_tools.py`

### Upcoming 📋
- [ ] ReAct agent implementation - `agents/fpl_agent.py`
- [ ] Custom prompts for FPL context - `agents/prompts.py`
- [ ] CLI interface - `main.py`
- [ ] Strategy modules (predictions, recommendations)
- [ ] Advanced features (gameweek briefings, price tracking)

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
