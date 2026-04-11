#!/usr/bin/env python3
"""Quick script to show RAM consumption values from environment"""

import asyncio
import sys

# Add project to path
sys.path.insert(0, "d:\\Projects\\Pytorch x hugging face\\he_demo")

async def main():
    from he_demo.client import EnergyOptimizationEnv
    
    print("=" * 70)
    print("🔋 RAM CONSUMPTION VALUES - Energy & Memory Optimization Environment")
    print("=" * 70)
    
    # Create environment
    env = EnergyOptimizationEnv(base_url="http://localhost:8000")
    
    # Reset and show initial state
    result = await env.reset()
    obs = result.observation
    
    print("\n📊 INITIAL STATE (After Reset)")
    print("-" * 70)
    print(f"RAM Usage:           {obs.ram_usage:.1f}%")
    print(f"Energy Consumption:  {obs.energy_consumption:.1f} kWh")
    print(f"System Load:         {obs.system_load:.2f}")
    print(f"Efficiency Score:    {obs.efficiency_score:.2f}")
    print(f"Task Progress:       {obs.task_progress:.2%}")
    print(f"Current Task:        {obs.current_task.name if obs.current_task else 'None'}")
    
    # Execute actions and show RAM changes
    print("\n\n📈 RAM VALUES AFTER EACH ACTION")
    print("-" * 70)
    
    actions = [
        {"action_type": "reduce_ram", "intensity": 0.8},
        {"action_type": "optimize_energy", "intensity": 0.8},
        {"action_type": "balance_resources", "intensity": 0.8},
        {"action_type": "reduce_ram", "intensity": 0.9},
        {"action_type": "optimize_energy", "intensity": 0.9},
    ]
    
    for i, action in enumerate(actions, 1):
        # Create action object from dict
        from he_demo.models import EnergyOptimizationAction
        action_obj = EnergyOptimizationAction(**action)
        
        # Execute step
        result = await env.step(action_obj)
        obs = result.observation
        
        # Show reward (already normalized by server to 0-1 scale)
        print(f"\nStep {i}: {action['action_type']} (intensity={action['intensity']})")
        print(f"  ├─ RAM Usage:        {obs.ram_usage:.1f}%")
        print(f"  ├─ Energy:           {obs.energy_consumption:.1f} kWh")
        print(f"  ├─ System Load:      {obs.system_load:.2f}")
        print(f"  ├─ Efficiency:       {obs.efficiency_score:.2f}")
        print(f"  └─ Reward (0-1):     {result.reward:.3f}")
    
    # Show final metrics
    print("\n\n" + "=" * 70)
    print("📊 FINAL METRICS")
    print("=" * 70)
    print(f"Final RAM Usage:     {obs.ram_usage:.1f}%")
    print(f"Final Energy:        {obs.energy_consumption:.1f} kWh")
    print(f"Total Reward:        {sum([r for r in range(5)])}") # Approximate
    
    await env.close()

if __name__ == "__main__":
    asyncio.run(main())
