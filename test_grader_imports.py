#!/usr/bin/env python
"""Test if validator can import graders via string-based import."""

grader_specs = [
    'task_1_basic_ram_reduction_grader',
    'task_2_energy_optimization_grader',
    'task_3_balanced_optimization_grader',
    'task_4_advanced_efficiency_grader',
    'task_5_expert_optimization_grader',
]

print("Testing string-based grader imports (openenv.yaml format):")
success_count = 0
for grader_name in grader_specs:
    try:
        module = __import__('task_graders')
        grader_func = getattr(module, grader_name)
        is_callable = callable(grader_func)
        print(f"✅ {grader_name} - callable: {is_callable}")
        if is_callable:
            success_count += 1
    except Exception as e:
        print(f"❌ {grader_name} - ERROR: {type(e).__name__}: {e}")

print(f"\n📊 Result: {success_count}/5 graders imported successfully")
