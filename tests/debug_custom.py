#!/usr/bin/env python
"""Debug script to test custom rules"""

import traceback
from run_demo import test_custom_rules, generate_sample_data

print("Generating sample data...")
data = generate_sample_data(500, 'ES')

print("\n" + "="*70)
print("Testing custom rules...")
print("="*70)

try:
    result = test_custom_rules(data)
    print(f"\n✅ Test completed")
    print(f"Passed: {result.get('passed')}")
    print(f"Reason: {result.get('reason')}")
    
    if result.get('error'):
        print(f"\n⚠️  Error occurred during backtest:")
        print(result['error'][:1000])
        
except Exception as e:
    print(f"\n❌ Exception during test:")
    print(f"Error: {e}")
    traceback.print_exc()
