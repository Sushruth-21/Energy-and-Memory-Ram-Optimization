#!/usr/bin/env python3
"""Direct test of environment state persistence"""

from he_demo.server.he_demo_environment import EnergyOptimizationEnvironment
from he_demo.models import EnergyOptimizationAction

env = EnergyOptimizationEnvironment()

# Test 1: Reset
print("=" * 70)
print("TEST 1: RESET")
print("=" * 70)
obs = env.reset()
print(f"Initial state:")
print(f"  RAM: {obs.ram_usage}%")
print(f"  Energy: {obs.energy_consumption} kWh")
print(f"  Reward: {obs.reward}")

# Test 2: Step 1
print("\n" + "=" * 70)
print("TEST 2: STEP 1 - reduce_ram intensity=0.8")
print("=" * 70)
action1 = EnergyOptimizationAction(action_type="reduce_ram", intensity=0.8)
obs1 = env.step(action1)
print(f"After step 1:")
print(f"  RAM: {obs1.ram_usage}% (should be ~72% if reduced by 8%)")
print(f"  Energy: {obs1.energy_consumption} kWh")
print(f"  Reward: {obs1.reward} (should be 0.080)")
print(f"  Step count: {obs1.steps_taken}")

# Test 3: Step 2
print("\n" + "=" * 70)
print("TEST 3: STEP 2 - reduce_ram intensity=0.8 again")
print("=" * 70)
action2 = EnergyOptimizationAction(action_type="reduce_ram", intensity=0.8)
obs2 = env.step(action2)
print(f"After step 2:")
print(f"  RAM: {obs2.ram_usage}% (should be ~64% if reduced by another 8%)")
print(f"  Energy: {obs2.energy_consumption} kWh")
print(f"  Reward: {obs2.reward} (should be 0.080)")
print(f"  Step count: {obs2.steps_taken}")

print("\n" + "=" * 70)
print("VERIFICATION")
print("=" * 70)
if obs1.ram_usage != obs.ram_usage:
    print("✅ RAM is UPDATING correctly between steps")
else:
    print("❌ RAM is NOT updating - state persistence issue!")

if obs2.ram_usage != obs1.ram_usage:
    print("✅ RAM continues to update")
else:
    print("❌ RAM stopped updating after second step")
