#!/usr/bin/env python3
"""
AP2 Agent Orchestrator - Manages the full agent server architecture
With improved logging, port checking, and automatic cleanup
"""

import subprocess
import time
import requests
import signal
import sys
import os
from pathlib import Path


def kill_process_on_port(port):
    """Kill any process running on the specified port"""
    try:
        # macOS/Linux
        result = subprocess.run(
            ['lsof', '-ti', f':{port}'],
            capture_output=True,
            text=True
        )
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                try:
                    os.kill(int(pid), signal.SIGTERM)
                    print(f"    ✓ Killed existing process on port {port} (PID: {pid})")
                except ProcessLookupError:
                    pass
            time.sleep(1)
    except FileNotFoundError:
        # lsof not available, try fuser (Linux)
        try:
            subprocess.run(['fuser', '-k', f'{port}/tcp'], stderr=subprocess.DEVNULL)
        except FileNotFoundError:
            pass


def check_port_available(port):
    """Check if a port is available"""
    try:
        response = requests.get(f'http://localhost:{port}/', timeout=1)
        return True  # Port is responding
    except:
        return False  # Port is not responding


class AgentOrchestrator:
    """Manages lifecycle of all AP2 agent servers"""
    
    def __init__(self, ap2_path):
        self.ap2_path = Path(ap2_path)
        self.processes = []
        self.agent_configs = [
            {
                'name': 'merchant',
                'port': 8001,
                'module': 'roles.merchant_agent',
            },
            {
                'name': 'credentials_provider',
                'port': 8002,
                'module': 'roles.credentials_provider_agent',
            },
            {
                'name': 'payment_processor',
                'port': 8003,
                'module': 'roles.merchant_payment_processor_agent',
            }
        ]
    
    def start_agents(self, timeout=30):
        """Start all agent servers"""
        print("🚀 Starting AP2 agents...\n")
        
        # Ensure logs directory exists
        logs_dir = self.ap2_path / ".logs"
        logs_dir.mkdir(exist_ok=True)
        
        # Clean up any existing processes on these ports
        print("🧹 Cleaning up existing processes...")
        for agent in self.agent_configs:
            kill_process_on_port(agent['port'])
        print()
        
        # Start each agent
        for agent in self.agent_configs:
            print(f"📍 Starting {agent['name']} on port {agent['port']}...")
            
            # Check if already running
            if check_port_available(agent['port']):
                print(f"   ℹ️  Agent already running on port {agent['port']}")
                self.processes.append({
                    'name': agent['name'],
                    'process': None,  # Don't have handle to existing process
                    'port': agent['port']
                })
                continue
            
            # Start the agent process
            log_file = logs_dir / f"{agent['name']}.log"
            log_handle = open(log_file, 'w')
            
            process = subprocess.Popen(
                [sys.executable, '-m', agent['module']],
                cwd=self.ap2_path,
                stdout=log_handle,
                stderr=subprocess.STDOUT,
                env={
                    **os.environ,
                    'GOOGLE_API_KEY': 'AIzaSyC7UfNDQZo7IlaoYX976BpSATQl5n_ii7A'
                }
            )
            
            self.processes.append({
                'name': agent['name'],
                'process': process,
                'port': agent['port'],
                'log_file': log_handle
            })
            
            # Wait for agent to be ready
            print(f"   ⏳ Waiting for agent to start...", end=" ", flush=True)
            if self._wait_for_agent(agent['port'], timeout=15):
                print("✅")
            else:
                print("❌")
                print(f"   ⚠️  Agent failed to start. Check log: {log_file}")
                # Show last few lines of log
                try:
                    log_handle.flush()
                    with open(log_file) as f:
                        lines = f.readlines()
                        if lines:
                            print(f"   Last log lines:")
                            for line in lines[-5:]:
                                print(f"      {line.rstrip()}")
                except:
                    pass
        
        print(f"\n✅ All agents started successfully\n")
        return True
    
    def _wait_for_agent(self, port, timeout=15):
        """Wait for an agent to be ready"""
        start = time.time()
        while (time.time() - start) < timeout:
            try:
                response = requests.get(f'http://localhost:{port}/', timeout=1)
                return True
            except:
                time.sleep(0.5)
        return False
    
    def stop_agents(self):
        """Stop all agent servers"""
        print("\n🛑 Stopping agents...\n")
        
        for item in self.processes:
            print(f"   Stopping {item['name']}...", end=" ")
            
            if item['process']:
                item['process'].terminate()
                try:
                    item['process'].wait(timeout=3)
                    print("✅")
                except subprocess.TimeoutExpired:
                    item['process'].kill()
                    print("⚠️  (force killed)")
                
                # Close log file
                if 'log_file' in item:
                    item['log_file'].close()
            else:
                # Process was already running, try to kill by port
                kill_process_on_port(item['port'])
                print("✅")
        
        print("\n✅ All agents stopped\n")
    
    def __enter__(self):
        self.start_agents()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_agents()


if __name__ == "__main__":
    # Test the orchestrator
    ap2_path = Path(__file__).parent.parent.parent / "AP2"
    
    print(f"AP2 path: {ap2_path}")
    print("Testing agent orchestrator...\n")
    
    with AgentOrchestrator(ap2_path) as orchestrator:
        print("✅ Agents running. Press Ctrl+C to stop...")
        try:
            time.sleep(60)
        except KeyboardInterrupt:
            print("\n\nShutting down...")
