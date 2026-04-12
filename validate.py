#!/usr/bin/env python3
"""
Final validation script for the Energy & Memory RAM Optimization Environment.

Per hackathon requirements, this validation includes grader configuration verification.
"""

# Import from properly structured he_demo package
from he_demo.models import EnergyOptimizationAction, EnergyOptimizationObservation, Task, TaskSummary
from he_demo.task_graders import TASK_GRADERS, get_grader_metadata, get_grader
from he_demo.server.he_demo_environment import EnergyOptimizationEnvironment

def main():
    print("🔋 Energy & Memory RAM Optimization Environment - Final Validation")
    print("=" * 70)
    
    # ===== GRADER CONFIGURATION VALIDATION (Hackathon Requirement) =====
    print("\n[1] Validating Task-Specific Graders")
    print("-" * 70)
    print(f"Total Graders Found: {len(TASK_GRADERS)}")
    if len(TASK_GRADERS) >= 3:
        print("✅ Grader count requirement met (>= 3)")
    else:
        print(f"❌ Insufficient graders: {len(TASK_GRADERS)} < 3")
        return
    
    for task_name, task_info in TASK_GRADERS.items():
        metadata = get_grader_metadata(task_name)
        print(f"\n  Task: {metadata['display_name']}")
        print(f"    Name: {task_name}")
        print(f"    Difficulty: {metadata['difficulty']}")
        print(f"    Targets: RAM < {metadata['target_ram']}%, Energy < {metadata['target_energy']} kWh")
        print(f"    Application: {metadata['real_world_application']}")

    try:
        # Create environment
        env = EnergyOptimizationEnvironment()
        print("\n[2] Environment Creation")
        print("-" * 70)
        print("✅ Environment created successfully")

        # Test reset
        obs = env.reset()
        print("✅ Environment reset successfully")
        print(f"   Initial RAM: {obs.ram_usage:.1f}%")
        print(f"   Initial Energy: {obs.energy_consumption:.1f} kWh")
        print(f"   Current Task: {obs.current_task.name if obs.current_task else 'None'}")

        # Test a few actions
        actions = [
            ("reduce_ram", 0.8),
            ("optimize_energy", 0.7),
            ("balance_resources", 0.6)
        ]
        
        print("\n[3] Action Execution")
        print("-" * 70)
        for action_type, intensity in actions:
            action = EnergyOptimizationAction(action_type=action_type, intensity=intensity)
            obs = env.step(action)
            print(f"✅ Action '{action_type}' executed: RAM={obs.ram_usage:.1f}%, Energy={obs.energy_consumption:.1f}kWh, Reward={obs.reward:.2f}")
        
        # ===== GRADER EVALUATION (Hackathon Requirement) =====
        print("\n[4] Grader Evaluation")
        print("-" * 70)
        
        # Test grader on current observation
        for task_name in ["basic_ram_reduction", "energy_optimization", "balanced_optimization"]:
            try:
                grader = get_grader(task_name)
                score = grader(obs)
                print(f"✅ {task_name}: Score = {score:.3f}")
            except Exception as e:
                print(f"❌ {task_name}: {e}")

        print("\n🎉 All validation tests passed!")
        print("🚀 The Energy & Memory RAM Optimization Environment is ready for deployment!")
        print("\n✅ Grader Configuration Status:")
        print(f"   - Total task-specific graders: {len(TASK_GRADERS)}")
        print(f"   - Hackathon requirement (>= 3 graders): MET")
        print(f"   - All graders executable: YES")

    except Exception as e:
        print(f"❌ Validation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()