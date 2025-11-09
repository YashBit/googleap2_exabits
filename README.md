I'll help you implement the experiment code. First, let me create a focused README with the initial strategy, then we'll work through the code implementation.

# AP2 Agent Failure Detection Experiment - README

## Quick Start Strategy

### Goal
Prove that Exabits infrastructure can detect AP2 agent misbehavior patterns through GPU-level telemetry in <10 seconds with ≥80% accuracy.

### Approach
1. **Local Testing First** - Verify AP2 SDK works, understand the agent flow
2. **Instrumentation** - Add monitoring to capture GPU metrics during agent execution
3. **Failure Injection** - Create three scenarios: Normal, Infinite Loop, Retry Storm
4. **Analysis** - Generate visualizations and metrics for CIO decision

### Budget
- **Cost**: $24 (8 hours RTX 4090 @ $3/hour)
- **Time**: 2-3 days
- **Outcome**: GO/NO-GO decision on $350K investment

---

## Phase 1: Local Setup & SDK Understanding (Today)

### What We Need to See First

To implement this efficiently, I need to see:

1. **AP2 Sample Structure** - Show me one working scenario
2. **Agent Execution Flow** - How agents interact in the sample
3. **Where to Inject Failures** - Identify instrumentation points

### Steps

```bash
# 1. Clone AP2 repository
git clone https://github.com/google-agentic-commerce/AP2.git
cd AP2

# 2. Install dependencies
uv pip install git+https://github.com/google-agentic-commerce/AP2.git@main

# 3. Set up authentication
export GOOGLE_API_KEY='your-key-here'

# 4. Test a sample scenario
cd samples/python/scenarios
ls  # Show me what scenarios are available
```

---

## What to Share Next

Please share:

### 1. Available Scenarios
```bash
cd AP2/samples/python/scenarios
ls -la
```

### 2. Pick One Scenario (Preferably Simple)
Show me the contents of ONE scenario:
```bash
# Example: if there's a "basic_purchase" scenario
cd basic_purchase
ls -la
cat README.md
```

### 3. Sample Code Structure
```bash
cd AP2/samples/python/src
ls -la
# Show me the main agent files
```

---

## Implementation Plan (After We See SDK)

Once I understand the SDK structure, we'll build:

### `src/instrumented_runner.py` (Core)
- Wraps AP2 scenario execution
- Captures GPU metrics every 100ms
- Saves transaction data to JSON

### `src/failure_injectors.py` (Scenarios)
- `create_contradictory_mandate()` - Infinite loop trigger
- `inject_payment_failures()` - Retry storm trigger
- `normal_baseline()` - Control group

### `utils/gpu_monitor.py` (Monitoring)
- Background thread sampling GPU via nvidia-smi
- Memory + utilization tracking

### `scripts/run_experiment.sh` (Execution)
- Runs all three scenarios sequentially
- Saves results to `data/results/`

### `scripts/analyze.py` (Analysis)
- Generates visualizations
- Calculates detection accuracy
- Creates CIO summary

---

## Next Steps

**Please provide:**

1. List of available scenarios in `AP2/samples/python/scenarios/`
2. Contents of ONE simple scenario (preferably a basic purchase example)
3. Confirm you can run `samples/python/scenarios/[scenario-name]/run.sh` successfully

Once I see the actual SDK structure, I'll write focused, working code that integrates cleanly with the AP2 framework.

---

## Expected Timeline

- **Today**: Understand SDK, write instrumentation wrapper
- **Tomorrow**: Test locally, debug, add failure injection
- **Day 3**: Run on GPU, generate results, create CIO summary

**Key Principle**: Keep it simple. We're proving a concept, not building production software.


API Key: AIzaSyC7UfNDQZo7IlaoYX976BpSATQl5n_ii7A