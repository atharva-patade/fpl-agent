#!/usr/bin/env python3
"""
Quick Eval Runner

Run evaluations quickly with common configurations.

Usage:
    python run_evals.py                           # Run all tests
    python run_evals.py --quick                   # Run quick subset (10 tests)
    python run_evals.py --category player         # Run specific category
    python run_evals.py --team-id 7798096         # Include team tests
"""

import sys
import subprocess
from pathlib import Path

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Quick evaluation runner")
    parser.add_argument(
        '--quick',
        action='store_true',
        help='Run quick subset of tests (first 10)'
    )
    parser.add_argument(
        '--category',
        type=str,
        default=None,
        help='Filter by category'
    )
    parser.add_argument(
        '--team-id',
        type=int,
        default=None,
        help='Team ID for team-specific tests'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed output'
    )
    
    args = parser.parse_args()
    
    # Build command
    cmd = [sys.executable, 'evals/eval_runner.py']
    
    if args.category:
        cmd.extend(['--category', args.category])
    
    if args.team_id:
        cmd.extend(['--team-id', str(args.team_id)])
    
    if args.verbose:
        cmd.append('--verbose')
    
    # Run the evaluator
    print(f"🚀 Running command: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(cmd, check=False)
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        print("\n\n⚠️  Evaluation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error running evaluation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
