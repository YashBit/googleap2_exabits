# AP2 Agent Failure Detection Experiment - README

## Quick Start Strategy

### Goal
Prove that Exabits infrastructure can detect AP2 agent misbehavior patterns through GPU-level telemetry in <10 seconds with ≥80% accuracy.

### Approach
1. **Local Testing First** - Verify AP2 SDK works, understand the agent flow
2. **Instrumentation** - Add monitoring to capture GPU metrics during agent execution
3. **Failure Injection** - Create three scenarios: Normal, Infinite Loop, Retry Storm
4. **Analysis** - Generate visualizations and metrics for CIO decision


