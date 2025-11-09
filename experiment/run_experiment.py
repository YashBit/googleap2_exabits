#!/usr/bin/env python3
"""
AP2 Agent Failure Detection Experiment - Complete Version
Using real AP2 agent architecture with TQDM progress bars
"""

import argparse
import json
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from tqdm import tqdm

from agent_orchestrator import AgentOrchestrator
from ap2_transaction import AP2TransactionExecutor


@dataclass
class TransactionMetrics:
    """Metrics for a single transaction"""
    scenario: str
    transaction_id: int
    duration: float
    success: bool
    steps: int = 0
    error_message: str = ""


class ExperimentRunner:
    """Run AP2 experiments with real agent infrastructure"""
    
    def __init__(self, ap2_path, output_dir="results"):
        self.ap2_path = Path(ap2_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.metrics = []
        self.executor = AP2TransactionExecutor()
    
    def run_experiment(self, scenarios, runs_per_scenario):
        """Run complete experiment with agent orchestration"""
        
        print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║  AP2 Agent Failure Detection Experiment                      ║
    ║  Using Real AP2 Agent Architecture                           ║
    ╚══════════════════════════════════════════════════════════════╝
        """)
        
        # Start all agents
        with AgentOrchestrator(self.ap2_path) as orchestrator:
            
            # Run each scenario
            for scenario in scenarios:
                self._run_scenario(scenario, runs_per_scenario[scenario])
        
        print("\n✅ Experiment complete!")
        print(f"\nResults saved to: {self.output_dir}/")
        
        # Print summary
        self._print_summary()
    
    def _run_scenario(self, scenario: str, num_runs: int):
        """Run a specific scenario multiple times"""
        print(f"\n{'='*60}")
        print(f"Scenario: {scenario}")
        print(f"Runs: {num_runs}")
        print(f"{'='*60}\n")
        
        # Create progress bar
        pbar = tqdm(range(num_runs), desc=f"{scenario:20s}", unit="run")
        
        for i in pbar:
            try:
                result = self.executor.execute_transaction(scenario)
                
                metrics = TransactionMetrics(
                    scenario=scenario,
                    transaction_id=i,
                    duration=result['duration'],
                    success=result['success'],
                    steps=result['steps'],
                    error_message=result.get('error', '')
                )
                
                self.metrics.append(metrics)
                
                # Update progress bar with status
                status = "✅" if metrics.success else "❌"
                pbar.set_postfix({
                    'status': status,
                    'duration': f"{metrics.duration:.2f}s",
                    'steps': metrics.steps
                })
                
            except Exception as e:
                pbar.set_postfix({'status': '❌', 'error': str(e)[:30]})
                self.metrics.append(TransactionMetrics(
                    scenario=scenario,
                    transaction_id=i,
                    duration=0,
                    success=False,
                    error_message=str(e)
                ))
        
        pbar.close()
        self._save_results()
    
    def _save_results(self):
        """Save metrics to JSON"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = self.output_dir / f"metrics_{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump([asdict(m) for m in self.metrics], f, indent=2)
        
        print(f"\n💾 Results saved: {output_file}")
    
    def _print_summary(self):
        """Print experiment summary"""
        print("\n" + "="*60)
        print("EXPERIMENT SUMMARY")
        print("="*60)
        
        # Group by scenario
        scenarios = {}
        for m in self.metrics:
            if m.scenario not in scenarios:
                scenarios[m.scenario] = []
            scenarios[m.scenario].append(m)
        
        for scenario, metrics in scenarios.items():
            total = len(metrics)
            successes = sum(1 for m in metrics if m.success)
            avg_duration = sum(m.duration for m in metrics) / total if total > 0 else 0
            avg_steps = sum(m.steps for m in metrics) / total if total > 0 else 0
            
            print(f"\n{scenario.upper()}")
            print(f"  Total runs:     {total}")
            print(f"  Successes:      {successes} ({successes/total*100:.1f}%)")
            print(f"  Failures:       {total - successes}")
            print(f"  Avg duration:   {avg_duration:.2f}s")
            print(f"  Avg steps:      {avg_steps:.1f}")
        
        print("\n" + "="*60)


def main():
    parser = argparse.ArgumentParser(
        description="Run AP2 Agent Failure Detection Experiment"
    )
    parser.add_argument(
        "--scenario",
        choices=["normal", "infinite_loop", "retry_storm", "all"],
        default="all",
        help="Which scenario to run"
    )
    parser.add_argument(
        "--num-runs",
        type=int,
        default=3,
        help="Number of runs per scenario"
    )
    parser.add_argument(
        "--ap2-path",
        default="../AP2",
        help="Path to AP2 repository"
    )
    parser.add_argument(
        "--output-dir",
        default="results",
        help="Output directory for results"
    )
    
    args = parser.parse_args()
    
    ap2_path = Path(args.ap2_path).resolve()
    if not ap2_path.exists():
        print(f"❌ Error: AP2 path not found: {ap2_path}")
        sys.exit(1)
    
    runner = ExperimentRunner(
        ap2_path=ap2_path,
        output_dir=args.output_dir
    )
    
    if args.scenario == "all":
        scenarios = ["normal", "infinite_loop", "retry_storm"]
        runs_per_scenario = {s: args.num_runs for s in scenarios}
    else:
        scenarios = [args.scenario]
        runs_per_scenario = {args.scenario: args.num_runs}
    
    runner.run_experiment(scenarios, runs_per_scenario)


if __name__ == "__main__":
    main()