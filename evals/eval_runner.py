#!/usr/bin/env python3
"""
FPL Agent Evaluation Runner

This script runs evaluation tests to verify that the agent calls the correct tools
for different types of queries. It loads test cases from test_cases.yaml and
validates tool selection behavior.

Usage:
    python evals/eval_runner.py                    # Run all tests
    python evals/eval_runner.py --category player  # Run specific category
    python evals/eval_runner.py --verbose          # Show detailed output
"""

import sys
import os
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# Add parent directory to path to import FPL Agent modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import Settings
from fpl_api.client import FPLClient
from fpl_api.managers import ManagerAPI
from langchain_openai import AzureChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.callbacks.base import BaseCallbackHandler

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
from tools.team_tools import (
    get_my_team,
    get_my_team_summary,
    get_my_transfers,
    analyze_my_team_performance,
    get_team_value_breakdown
)


@dataclass
class EvalResult:
    """Results from a single evaluation test"""
    test_id: str
    category: str
    query: str
    expected_tools: List[str]
    actual_tools: List[str] = field(default_factory=list)
    passed: bool = False
    error: Optional[str] = None
    response: Optional[str] = None
    execution_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


class ToolTrackingCallback(BaseCallbackHandler):
    """Callback handler to track which tools are called during agent execution"""
    
    def __init__(self, verbose: bool = False):
        self.tools_called: List[str] = []
        self.verbose = verbose
        
    def on_tool_start(self, serialized: dict, input_str: str, **kwargs):
        """Track when a tool is called"""
        tool_name = serialized.get("name", "Unknown")
        self.tools_called.append(tool_name)
        
    def reset(self):
        """Reset the tools list"""
        self.tools_called = []


class FPLAgentEvaluator:
    """Evaluator for FPL Agent tool selection"""
    
    def __init__(self, team_id: Optional[int] = None, verbose: bool = False):
        self.console = Console()
        self.verbose = verbose
        self.team_id = team_id
        self.settings = Settings()
        
        # Initialize FPL client
        self.fpl_client = FPLClient()
        self.manager_api = ManagerAPI(self.fpl_client)
        
        # Initialize tool tracker with verbose flag
        self.tool_tracker = ToolTrackingCallback(verbose=verbose)
        
        # Initialize agent
        self.agent_executor = self._initialize_agent()
        
        # Results storage
        self.results: List[EvalResult] = []
        
    def _initialize_agent(self) -> AgentExecutor:
        """Initialize the LangChain agent with tool tracking"""
        # Initialize Azure OpenAI
        llm = AzureChatOpenAI(
            azure_endpoint=self.settings.openai_api_host,
            api_key=self.settings.openai_api_key,
            api_version=self.settings.openai_api_version,
            deployment_name=self.settings.openai_deployment,
            temperature=0.7,
            max_retries=3,
            request_timeout=60
        )
        
        # Define tools
        tools = [
            # Player analysis tools
            search_player_by_name,
            get_player_detailed_stats,
            compare_two_players,
            find_best_players_by_position,
            # Gameweek tools
            get_current_gameweek_info,
            get_next_gameweek_info,
            get_gameweek_by_number,
            get_season_overview,
            # Team tools
            get_my_team,
            get_my_team_summary,
            get_my_transfers,
            analyze_my_team_performance,
            get_team_value_breakdown
        ]
        
        # Create simple prompt for evaluation
        prompt = self._create_agent_prompt()
        
        # Create ReAct agent
        agent = create_react_agent(
            llm=llm,
            tools=tools,
            prompt=prompt
        )
        
        # Create agent executor with callback
        return AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=self.verbose,
            handle_parsing_errors=True,
            max_iterations=10,
            max_execution_time=120,
            callbacks=[self.tool_tracker]
        )
    
    def _create_agent_prompt(self) -> PromptTemplate:
        """Create agent prompt template"""
        team_context = ""
        if self.team_id:
            team_context = f"\n\n**USER'S TEAM ID:** {self.team_id}"
        else:
            team_context = "\n\n**USER'S TEAM ID:** Not provided."
        
        template = """You are an expert Fantasy Premier League (FPL) advisor.""" + team_context + """

Use the available tools to answer questions. Be concise and data-driven.

**IMPORTANT:** For tools with multiple parameters (like compare_two_players), you MUST use JSON format for Action Input.
Example: Action Input: {{"player1_name": "Haaland", "player2_name": "Kane"}}

You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action (use JSON format for multiple parameters)
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}"""
        
        return PromptTemplate(
            template=template,
            input_variables=["input", "agent_scratchpad", "tools", "tool_names"]
        )
    
    def run_test(self, test_case: Dict[str, Any]) -> EvalResult:
        """Run a single evaluation test"""
        test_id = test_case['id']
        query = test_case['query']
        expected_tools = test_case['expected_tools']
        category = test_case['category']
        
        # Check if test requires team_id
        requires_team_id = test_case.get('requires_team_id', False)
        if requires_team_id and not self.team_id:
            return EvalResult(
                test_id=test_id,
                category=category,
                query=query,
                expected_tools=expected_tools,
                passed=False,
                error="Test requires team_id but none provided"
            )
        
        # Reset tool tracker
        self.tool_tracker.reset()
        
        # Run the query with callback
        start_time = datetime.now()
        try:
            response = self.agent_executor.invoke(
                {"input": query},
                config={"callbacks": [self.tool_tracker]}
            )
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Get tools that were called
            actual_tools = self.tool_tracker.tools_called
            
            # Check if expected tools were called
            # Allow subset matching - if all expected tools were called, it's a pass
            # (agent might call additional tools, which is fine)
            passed = all(tool in actual_tools for tool in expected_tools)
            
            return EvalResult(
                test_id=test_id,
                category=category,
                query=query,
                expected_tools=expected_tools,
                actual_tools=actual_tools,
                passed=passed,
                response=response.get("output", ""),
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return EvalResult(
                test_id=test_id,
                category=category,
                query=query,
                expected_tools=expected_tools,
                actual_tools=self.tool_tracker.tools_called,
                passed=False,
                error=str(e),
                execution_time=execution_time
            )
    
    def run_all_tests(
        self, 
        test_cases: List[Dict[str, Any]],
        category_filter: Optional[str] = None
    ) -> List[EvalResult]:
        """Run all evaluation tests"""
        # Filter by category if specified
        if category_filter:
            test_cases = [
                tc for tc in test_cases 
                if category_filter.lower() in tc['category'].lower()
            ]
        
        self.console.print(f"\n🚀 Running {len(test_cases)} evaluation tests...\n")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Running tests...", total=len(test_cases))
            
            for test_case in test_cases:
                if self.verbose:
                    self.console.print(f"\n[cyan]Running: {test_case['id']}[/cyan]")
                    self.console.print(f"Query: {test_case['query']}")
                
                result = self.run_test(test_case)
                self.results.append(result)
                
                if self.verbose:
                    status = "✅ PASS" if result.passed else "❌ FAIL"
                    self.console.print(f"Result: {status}")
                    self.console.print(f"Expected: {result.expected_tools}")
                    self.console.print(f"Actual: {result.actual_tools}")
                
                progress.update(task, advance=1)
        
        return self.results
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate evaluation report"""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        failed_tests = total_tests - passed_tests
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Group by category
        category_stats = {}
        for result in self.results:
            if result.category not in category_stats:
                category_stats[result.category] = {'total': 0, 'passed': 0, 'failed': 0}
            
            category_stats[result.category]['total'] += 1
            if result.passed:
                category_stats[result.category]['passed'] += 1
            else:
                category_stats[result.category]['failed'] += 1
        
        # Calculate average execution time
        avg_execution_time = sum(r.execution_time for r in self.results) / total_tests if total_tests > 0 else 0
        
        return {
            'summary': {
                'total_tests': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'pass_rate': pass_rate,
                'avg_execution_time': avg_execution_time
            },
            'category_stats': category_stats,
            'results': [r.to_dict() for r in self.results]
        }
    
    def display_report(self, report: Dict[str, Any]):
        """Display evaluation report in terminal"""
        summary = report['summary']
        category_stats = report['category_stats']
        
        # Summary table
        summary_table = Table(title="📊 Evaluation Summary", show_header=True, header_style="bold cyan")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="green")
        
        summary_table.add_row("Total Tests", str(summary['total_tests']))
        summary_table.add_row("Passed", f"✅ {summary['passed']}")
        summary_table.add_row("Failed", f"❌ {summary['failed']}")
        summary_table.add_row("Pass Rate", f"{summary['pass_rate']:.1f}%")
        summary_table.add_row("Avg Execution Time", f"{summary['avg_execution_time']:.2f}s")
        
        self.console.print("\n")
        self.console.print(summary_table)
        
        # Category breakdown
        category_table = Table(title="📂 Results by Category", show_header=True, header_style="bold cyan")
        category_table.add_column("Category", style="cyan")
        category_table.add_column("Total", justify="center")
        category_table.add_column("Passed", justify="center", style="green")
        category_table.add_column("Failed", justify="center", style="red")
        category_table.add_column("Pass Rate", justify="center")
        
        for category, stats in sorted(category_stats.items()):
            pass_rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
            category_table.add_row(
                category,
                str(stats['total']),
                str(stats['passed']),
                str(stats['failed']),
                f"{pass_rate:.1f}%"
            )
        
        self.console.print("\n")
        self.console.print(category_table)
        
        # Failed tests details
        failed_tests = [r for r in self.results if not r.passed]
        if failed_tests:
            self.console.print("\n")
            self.console.print(Panel("[bold red]Failed Tests Details[/bold red]", style="red"))
            
            for result in failed_tests:
                self.console.print(f"\n[red]❌ {result.test_id}[/red] - {result.category}")
                self.console.print(f"   Query: \"{result.query}\"")
                self.console.print(f"   Expected tools: {result.expected_tools}")
                self.console.print(f"   Actual tools: {result.actual_tools}")
                if result.error:
                    self.console.print(f"   Error: {result.error}")
    
    def save_report(self, report: Dict[str, Any], output_file: Path):
        """Save evaluation report to JSON file"""
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.console.print(f"\n💾 Report saved to: {output_file}")


def load_test_cases(yaml_file: Path) -> List[Dict[str, Any]]:
    """Load test cases from YAML file"""
    with open(yaml_file, 'r') as f:
        data = yaml.safe_load(f)
    
    return data.get('test_cases', [])


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run FPL Agent evaluation tests")
    parser.add_argument(
        '--test-file',
        type=str,
        default='evals/test_cases.yaml',
        help='Path to test cases YAML file'
    )
    parser.add_argument(
        '--category',
        type=str,
        default=None,
        help='Filter tests by category (e.g., player_search, gameweek)'
    )
    parser.add_argument(
        '--team-id',
        type=int,
        default=None,
        help='FPL Team ID for team-specific tests'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed output for each test'
    )
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Output file for JSON report (default: evals/reports/eval_report_TIMESTAMP.json)'
    )
    
    args = parser.parse_args()
    
    # Load test cases
    console = Console()
    test_file = Path(args.test_file)
    
    if not test_file.exists():
        console.print(f"[red]❌ Test file not found: {test_file}[/red]")
        sys.exit(1)
    
    console.print(f"📂 Loading test cases from: {test_file}")
    test_cases = load_test_cases(test_file)
    console.print(f"✅ Loaded {len(test_cases)} test cases")
    
    # Initialize evaluator
    evaluator = FPLAgentEvaluator(
        team_id=args.team_id,
        verbose=args.verbose
    )
    
    # Run tests
    evaluator.run_all_tests(test_cases, category_filter=args.category)
    
    # Generate report
    report = evaluator.generate_report()
    
    # Display report
    evaluator.display_report(report)
    
    # Save report
    if args.output:
        output_file = Path(args.output)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = Path(f"evals/reports/eval_report_{timestamp}.json")
    
    evaluator.save_report(report, output_file)
    
    # Exit with appropriate code
    sys.exit(0 if report['summary']['failed'] == 0 else 1)


if __name__ == "__main__":
    main()
