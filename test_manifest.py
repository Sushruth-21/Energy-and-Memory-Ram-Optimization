#!/usr/bin/env python
"""Quick test of grader manifest."""

from he_demo.grader_manifest import GRADERS_MANIFEST, is_validator_satisfied

print('✓ Manifest imported')
print(f'✓ Total graders: {GRADERS_MANIFEST["validation"]["actual_count"]}')
print(f'✓ Validator satisfied: {is_validator_satisfied()}')
print(f'✓ Grader names: {[g["name"] for g in GRADERS_MANIFEST["graders"]]}')
print(f'✓ Grader IDs: {[g["id"] for g in GRADERS_MANIFEST["graders"]]}')
