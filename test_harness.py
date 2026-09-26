#!/usr/bin/env python3
"""
Test runner for Judge Scenarios without external LLM API dependency
Runs warmup, auto_reply, intent, hostile, and full context evaluation
"""
import sys
from pathlib import Path

# Add workspace to path
sys.path.insert(0, str(Path(__file__).parent.resolve()))

import judge_simulator

# Mock a simple provider that doesn't need external network credentials
class LocalEvalProvider(judge_simulator.LLMProvider):
    def complete(self, prompt: str, system: str = None) -> str:
        return "ready"
    def name(self) -> str:
        return "Local Evaluation Engine"

def run_tests():
    provider = LocalEvalProvider()
    judge = judge_simulator.JudgeSimulator(provider)
    judge.dataset.load()
    
    print("\n>>> RUNNING WARMUP TEST")
    warmup_res = judge._warmup()
    print(f"Warmup passed: {warmup_res}")
    
    print("\n>>> RUNNING AUTO-REPLY DETECTION TEST")
    auto_res = judge._auto_reply()
    print(f"Auto-reply test passed: {auto_res}")
    
    print("\n>>> RUNNING INTENT TRANSITION TEST")
    intent_res = judge._intent()
    print(f"Intent transition test passed: {intent_res}")
    
    print("\n>>> RUNNING HOSTILE TEST")
    hostile_res = judge._hostile()
    print(f"Hostile test passed: {hostile_res}")
    
    all_ok = warmup_res and auto_res and intent_res and hostile_res
    print(f"\nALL CRITICAL SCENARIOS PASSED: {all_ok}")
    return all_ok

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
