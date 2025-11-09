#!/usr/bin/env python3
"""
AP2 Agent Failure Detection Experiment
Simple version - no GPU monitoring yet
"""

import argparse
import json
import time
import subprocess
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path


@dataclass
class TransactionMetrics:
    """Metrics for a single transaction"""
    scenario: str
    transaction_id: int
    start_time: float
    end_time: float
    duration: float
    success: bool
    error_message: str = ""


class ExperimentRunner:
    """Run AP2 experiments with instrumentation"""
    
    def __init__(self, output_dir="results", use_gpu=False):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.use_gpu = use_gpu
        self.metrics = []
    
    def run_scenario(self, scenario: str, num_runs: int):
        """Run a specific scenario multiple times"""
        print(f"\n{'='*60}")
        print(f"Scenario: {scenario}")
        print(f"Runs: {num_runs}")
        print(f"{'='*60}\n")
        
        for i in range(num_runs):
            print(f"Run {i+1}/{num_runs}...", end=" ", flush=True)
            
            try:
                metrics = self._run_single_transaction(scenario, i)
                self.metrics.append(metrics)
                
                status = "✅" if metrics.success else "❌"
                print(f"{status} ({metrics.duration:.2f}s)")
                
            except Exception as e:
                print(f"❌ ERROR: {e}")
                self.metrics.append(TransactionMetrics(
                    scenario=scenario,
                    transaction_id=i,
                    start_time=time.time(),
                    end_time=time.time(),
                    duration=0,
                    success=False,
                    error_message=str(e)
                ))
        
        self._save_results()
    
    def _run_single_transaction(self, scenario: str, tx_id: int) -> TransactionMetrics:
        """Run one transaction"""
        start_time = time.time()
        
        # For now, just simulate a transaction
        # We'll implement actual AP2 execution next
        if scenario == "normal":
            time.sleep(0.5)  # Simulate normal execution
            success = True
            error = ""
        elif scenario == "infinite_loop":
            time.sleep(2)  # Simulate longer execution
            success = False
            error = "Timeout: contradictory mandate"
        elif scenario == "retry_storm":
            time.sleep(1.5)  # Simulate retry delays
            success = False
            error = "Payment retry limit exceeded"
        else:
            raise ValueError(f"Unknown scenario: {scenario}")
        
        end_time = time.time()
        
        return TransactionMetrics(
            scenario=scenario,
            transaction_id=tx_id,
            start_time=start_time,
            end_time=end_time,
            duration=end_time - start_time,
            success=success,
            error_message=error
        )
    
    def _save_results(self):
        """Save metrics to JSON"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = self.output_dir / f"metrics_{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump([asdict(m) for m in self.metrics], f, indent=2)
        
        print(f"\n💾 Results saved: {output_file}")


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
        default=5,
        help="Number of runs per scenario"
    )
    parser.add_argument(
        "--use-gpu",
        action="store_true",
        help="Enable GPU monitoring (for Exabits VM)"
    )
    parser.add_argument(
        "--output-dir",
        default="results",
        help="Output directory for results"
    )
    
    args = parser.parse_args()
    
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║  AP2 Agent Failure Detection Experiment                      ║
    ║  Exabits Infrastructure Validation                           ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    runner = ExperimentRunner(
        output_dir=args.output_dir,
        use_gpu=args.use_gpu
    )
    
    if args.scenario == "all":
        scenarios = ["normal", "infinite_loop", "retry_storm"]
        runs_per_scenario = {
            "normal": args.num_runs,
            "infinite_loop": args.num_runs,
            "retry_storm": args.num_runs
        }
    else:
        scenarios = [args.scenario]
        runs_per_scenario = {args.scenario: args.num_runs}
    
    for scenario in scenarios:
        runner.run_scenario(scenario, runs_per_scenario[scenario])
    
    print("\n✅ Experiment complete!")
    print(f"\nResults saved to: {args.output_dir}/")


if __name__ == "__main__":
    main()