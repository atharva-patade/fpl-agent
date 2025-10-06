#!/usr/bin/env python3
"""
FPL Agent - Interactive CLI
Main entry point for the FPL AI Agent
"""

import sys
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm
from rich.table import Table

from langchain_openai import AzureChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.callbacks.base import BaseCallbackHandler
from langchain.callbacks import get_openai_callback

# Import configuration
from config.settings import Settings

# Import API clients
from fpl_api.client import FPLClient
from fpl_api.managers import ManagerAPI

# Import tools
from tools.player_tools import (
    search_player_by_name,
    get_player_detailed_stats,
    compare_two_players,
    find_best_players_by_position
)
from tools.general_tools import (
    get_current_gameweek_info,
    get_next_gameweek_info,
    get_gameweek_by_number,
    get_season_overview
)


class StreamingCallbackHandler(BaseCallbackHandler):
    """Custom callback handler for streaming agent output"""
    
    def __init__(self, console: Console):
        self.console = console
        self.total_tokens = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0
        
    def on_tool_start(self, serialized: dict, input_str: str, **kwargs):
        """Called when tool starts executing"""
        tool_name = serialized.get("name", "Unknown")
        self.console.print(f"\n🔧 [cyan]Using tool:[/cyan] {tool_name}", style="dim")
        
    def on_tool_end(self, output: str, **kwargs):
        """Called when tool finishes executing"""
        self.console.print("✓ [green]Tool completed[/green]", style="dim")
        
    def on_agent_action(self, action, **kwargs):
        """Called when agent takes an action"""
        pass
        
    def on_agent_finish(self, finish, **kwargs):
        """Called when agent finishes"""
        pass
    
    def on_llm_end(self, response, **kwargs):
        """Called when LLM finishes - track token usage"""
        if hasattr(response, 'llm_output') and response.llm_output:
            token_usage = response.llm_output.get('token_usage', {})
            if token_usage:
                self.total_tokens += token_usage.get('total_tokens', 0)
                self.prompt_tokens += token_usage.get('prompt_tokens', 0)
                self.completion_tokens += token_usage.get('completion_tokens', 0)
    
    def get_token_summary(self) -> dict:
        """Get token usage summary"""
        return {
            'total_tokens': self.total_tokens,
            'prompt_tokens': self.prompt_tokens,
            'completion_tokens': self.completion_tokens
        }
    
    def reset_tokens(self):
        """Reset token counters"""
        self.total_tokens = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0


class FPLAgentCLI:
    """Interactive CLI for FPL Agent"""
    
    def __init__(self):
        self.console = Console()
        self.settings = Settings()
        self.team_id: Optional[int] = None
        self.fpl_client = FPLClient()
        self.manager_api = ManagerAPI(self.fpl_client)
        self.agent_executor: Optional[AgentExecutor] = None
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        # Token tracking
        self.streaming_handler = StreamingCallbackHandler(self.console)
        # Failed queries log
        self.failed_queries_log = []
        self.failed_queries_file = Path("evals/failed_queries.jsonl")
        self.last_query = None
        self.last_response = None
        
    def display_welcome(self):
        """Display welcome banner"""
        welcome_text = """
# 🏆 FPL AI Agent

Your intelligent Fantasy Premier League assistant powered by Azure OpenAI.

## Features
- 🔍 Player search and analysis
- 📊 Player comparison and statistics
- 💰 Value discovery by position
- 🎯 Transfer recommendations
- 📈 Team performance tracking

## Commands
- `/team` - Set or view your FPL team ID
- `/help` - Show available commands
- `/clear` - Clear conversation history
- `/log` - Log current query as failed for review
- `/tokens` - Show total token usage for this session
- `/exit` - Exit the agent

---
        """
        self.console.print(Panel(Markdown(welcome_text), border_style="green"))
        
    def initialize_agent(self):
        """Initialize the LangChain ReAct agent"""
        # Initialize Azure OpenAI
        llm = AzureChatOpenAI(
            azure_endpoint=self.settings.openai_api_host,
            api_key=self.settings.openai_api_key,
            api_version=self.settings.openai_api_version,
            deployment_name=self.settings.openai_deployment,
            temperature=0.7,
            streaming=True,
            callbacks=[self.streaming_handler],
            max_retries=3,
            request_timeout=60
        )
        
        # Define tools
        tools = [
            search_player_by_name,
            get_player_detailed_stats,
            compare_two_players,
            find_best_players_by_position,
            get_current_gameweek_info,
            get_next_gameweek_info,
            get_gameweek_by_number,
            get_season_overview
        ]
        
        # Create custom prompt
        prompt = self._create_agent_prompt()
        
        # Create ReAct agent
        agent = create_react_agent(
            llm=llm,
            tools=tools,
            prompt=prompt
        )
        
        # Create agent executor with increased limits
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=10,  # Increased from 5 to 10
            max_execution_time=120  # 2 minutes timeout
        )
        
        self.console.print("✅ [green]Agent initialized successfully![/green]\n")
        
    def _create_agent_prompt(self) -> PromptTemplate:
        """Create custom prompt template with dynamic team context"""
        
        # Dynamic team context based on whether team ID is set
        team_context = ""
        if self.team_id:
            team_context = f"\n\n**USER'S TEAM ID:** {self.team_id}\nYou can access their team information when needed."
        else:
            team_context = "\n\n**USER'S TEAM ID:** Not provided yet.\nIf the user asks team-specific questions (e.g., 'analyze my team', 'what transfers should I make'), politely ask them to provide their FPL Team ID using the `/team` command."
        
        template = f"""You are an expert Fantasy Premier League (FPL) advisor with deep knowledge of football statistics, player performance, and FPL strategy.

**CURRENT CONTEXT:**{team_context}

**YOUR ROLE:**
- Provide data-driven insights using the available tools
- Help users make informed decisions about transfers, captaincy, and team selection
- Explain your reasoning clearly and concisely
- Use statistics to back up your recommendations

**GUIDELINES:**
1. **When asked about the user's team:** If Team ID is NOT provided, ask them to set it using `/team` command
2. **For general questions:** Use the tools to gather information and provide analysis
3. **Always use tools:** Don't make up statistics - use the tools to get real data
4. **Be concise:** Provide clear, actionable advice
5. **Explain your reasoning:** Show the data behind your recommendations

You have access to the following tools:

{{tools}}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{{tool_names}}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {{input}}
Thought:{{agent_scratchpad}}"""
        
        return PromptTemplate(
            template=template,
            input_variables=["input", "agent_scratchpad", "tools", "tool_names"]
        )
        
    def set_team_id(self, team_id: Optional[int] = None):
        """Set or update the user's FPL team ID"""
        if team_id is None:
            team_id_str = Prompt.ask("\n[cyan]Enter your FPL Team ID[/cyan]")
            try:
                team_id = int(team_id_str)
            except ValueError:
                self.console.print("❌ [red]Invalid Team ID. Please enter a number.[/red]")
                return False
                
        # Validate team ID by fetching manager info
        self.console.print(f"�� Validating Team ID {team_id}...")
        
        try:
            manager_info = self.manager_api.get_manager_info(team_id)
            team_name = manager_info.get("name", "Unknown Team")
            player_name = f"{manager_info.get('player_first_name', '')} {manager_info.get('player_last_name', '')}".strip()
            
            # Display team info
            table = Table(title=f"✅ Team Found!", show_header=True, header_style="bold cyan")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Team Name", team_name)
            table.add_row("Manager", player_name)
            table.add_row("Team ID", str(team_id))
            
            self.console.print(table)
            
            # Confirm and set
            confirm = Confirm.ask(f"\n[cyan]Is this your team?[/cyan]", default=True)
            if confirm:
                self.team_id = team_id
                self.console.print(f"✅ [green]Team ID set to {team_id}[/green]")
                
                # Reinitialize agent with team context
                self.console.print("🔄 Updating agent with your team information...")
                self.initialize_agent()
                return True
            else:
                self.console.print("❌ Team ID not set. Please try again.")
                return False
                
        except Exception as e:
            self.console.print(f"❌ [red]Error validating Team ID: {str(e)}[/red]")
            self.console.print("[yellow]Please check your Team ID and try again.[/yellow]")
            return False
            
    def process_command(self, user_input: str) -> bool:
        """Process special commands. Returns True if command was processed."""
        if not user_input.startswith("/"):
            return False
            
        command = user_input.lower().strip()
        
        if command == "/exit" or command == "/quit":
            self.console.print("\n👋 [yellow]Goodbye! Good luck with your FPL team![/yellow]\n")
            return True
            
        elif command == "/help":
            help_text = """
## Available Commands

- `/team` - Set or view your FPL team ID
- `/help` - Show this help message
- `/clear` - Clear conversation history
- `/log` - Log the last query as failed for later review
- `/tokens` - Show token usage and estimated cost
- `/exit` - Exit the agent

## Example Questions

- "What gameweek are we in?"
- "Who should I captain this week?"
- "Compare Haaland and Kane"
- "Find best midfielders under £8m"
- "What are Salah's stats?"
- "Analyze my team" (requires team ID)
            """
            self.console.print(Panel(Markdown(help_text), title="Help", border_style="blue"))
            return False
            
        elif command == "/team":
            if self.team_id:
                self.console.print(f"\n📋 [cyan]Current Team ID:[/cyan] {self.team_id}")
                change = Confirm.ask("Would you like to change it?", default=False)
                if change:
                    self.set_team_id()
            else:
                self.set_team_id()
            return False
            
        elif command == "/clear":
            self.memory.clear()
            self.console.clear()
            self.display_welcome()
            self.console.print("✅ [green]Conversation history cleared![/green]\n")
            return False
            
        elif command == "/log":
            self.log_failed_query()
            return False
            
        elif command == "/tokens":
            tokens = self.streaming_handler.get_token_summary()
            self.console.print("\n📊 [bold cyan]Token Usage Summary[/bold cyan]")
            self.console.print(f"   Total Tokens: [green]{tokens['total_tokens']:,}[/green]")
            self.console.print(f"   Prompt Tokens: [yellow]{tokens['prompt_tokens']:,}[/yellow]")
            self.console.print(f"   Completion Tokens: [blue]{tokens['completion_tokens']:,}[/blue]")
            
            # Calculate approximate cost (Azure OpenAI GPT-4 pricing)
            # These are example rates - adjust based on your actual pricing
            prompt_cost = (tokens['prompt_tokens'] / 1000) * 0.03  # $0.03 per 1K tokens
            completion_cost = (tokens['completion_tokens'] / 1000) * 0.06  # $0.06 per 1K tokens
            total_cost = prompt_cost + completion_cost
            
            self.console.print(f"   Estimated Cost: [magenta]${total_cost:.4f}[/magenta]")
            self.console.print("[dim]   (Based on standard GPT-4 pricing)[/dim]\n")
            return False
            
        else:
            self.console.print(f"❌ [red]Unknown command: {command}[/red]")
            self.console.print("[yellow]Type /help to see available commands[/yellow]\n")
            return False
    
    def log_failed_query(self):
        """Log the last query as failed for review and evaluation"""
        if not self.last_query:
            self.console.print("❌ [red]No query to log. Ask a question first![/red]")
            return
        
        # Create evals directory if it doesn't exist
        self.failed_queries_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Prepare log entry
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "query": self.last_query,
            "response": self.last_response.get("output", "") if self.last_response else "",
            "team_id_set": self.team_id is not None,
            "team_id": self.team_id,
            "tools_used": [],
            "status": "failed",
            "notes": ""
        }
        
        # Extract tools used if available
        if self.last_response and 'intermediate_steps' in self.last_response:
            for step in self.last_response['intermediate_steps']:
                if isinstance(step, tuple) and len(step) >= 1:
                    action = step[0]
                    if hasattr(action, 'tool'):
                        log_entry["tools_used"].append(action.tool)
        
        # Append to JSONL file
        with open(self.failed_queries_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        self.console.print("✅ [green]Query logged to failed_queries.jsonl[/green]")
        self.console.print(f"   Query: \"{self.last_query}\"")
        self.console.print("[dim]   You can review failed queries later to improve the agent.[/dim]")
            
    def chat(self):
        """Main chat loop"""
        self.console.print("[bold cyan]Let's get started! Ask me anything about FPL.[/bold cyan]\n")
        
        while True:
            try:
                # Get user input
                user_input = Prompt.ask("\n[bold green]You[/bold green]")
                
                if not user_input.strip():
                    continue
                    
                # Check for special commands
                if self.process_command(user_input):
                    # /exit command returns True
                    if user_input.lower().strip() in ["/exit", "/quit"]:
                        break
                    continue
                    
                # Process with agent
                self.console.print("\n[bold cyan]Agent[/bold cyan]:")
                
                # Store query for logging
                self.last_query = user_input
                
                # Reset token counter for this query
                self.streaming_handler.reset_tokens()
                
                try:
                    response = self.agent_executor.invoke({
                        "input": user_input
                    })
                    
                    # Store response for logging
                    self.last_response = response
                    
                    # Display final answer
                    final_answer = response.get("output", "I couldn't generate a response.")
                    self.console.print(Panel(
                        Markdown(final_answer),
                        border_style="cyan",
                        padding=(1, 2)
                    ))
                    
                    # Display token usage
                    tokens = self.streaming_handler.get_token_summary()
                    if tokens['total_tokens'] > 0:
                        self.console.print(
                            f"\n[dim]📊 Tokens: {tokens['total_tokens']:,} total "
                            f"({tokens['prompt_tokens']:,} prompt + {tokens['completion_tokens']:,} completion)[/dim]"
                        )
                    
                except Exception as e:
                    self.console.print(f"❌ [red]Error processing request: {str(e)}[/red]")
                    self.console.print("[yellow]Please try rephrasing your question.[/yellow]")
                    self.console.print("[dim]Tip: Use /log to save this failed query for review.[/dim]")
                    
            except KeyboardInterrupt:
                self.console.print("\n\n👋 [yellow]Goodbye! Good luck with your FPL team![/yellow]\n")
                break
            except EOFError:
                break
                
    def run(self):
        """Main entry point"""
        self.console.clear()
        self.display_welcome()
        
        # Ask for team ID (optional)
        self.console.print("[bold cyan]Welcome to FPL Agent![/bold cyan]")
        self.console.print("You can explore FPL data without a team ID, or provide yours for personalized advice.\n")
        
        wants_team_id = Confirm.ask(
            "[cyan]Do you want to provide your FPL Team ID now?[/cyan]",
            default=False
        )
        
        if wants_team_id:
            self.set_team_id()
        else:
            self.console.print("\n✅ [green]No problem! You can explore without a team ID.[/green]")
            self.console.print("[dim]You can set it later using the /team command if you want personalized advice.[/dim]\n")
            
        # Initialize agent
        self.console.print("🚀 Initializing agent...")
        self.initialize_agent()
        
        # Start chat loop
        self.chat()


def main():
    """Main function"""
    try:
        agent = FPLAgentCLI()
        agent.run()
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
