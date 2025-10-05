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

The agent has access to powerful tools:

- `analyze_player_form`: Analyze recent player performance
- `compare_players`: Compare two players across metrics
- `find_best_players_by_position`: Find top performers within budget
- `analyze_my_team`: Comprehensive team analysis
- `suggest_transfers`: AI-powered transfer recommendations
- `analyze_upcoming_fixtures`: Fixture difficulty analysis
- `optimize_team_for_gameweek`: Best lineup suggestions
- `get_differential_picks`: Find high-value, low-owned players

## 📊 Project Status

**Current Phase**: Phase 1 - Core Infrastructure ✅

- [x] Project structure
- [x] API client with caching and error handling
- [x] Bootstrap API module
- [x] Manager API module
- [x] Player API module
- [x] Fixtures API module
- [ ] LangChain tools implementation
- [ ] ReAct agent setup
- [ ] CLI interface
- [ ] Strategy modules
- [ ] Testing suite

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
