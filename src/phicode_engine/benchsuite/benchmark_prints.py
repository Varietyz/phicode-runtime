
def print_benchsuite_entry(discovered, ENGINE, SYMBOL):
    print(f"{ENGINE} Self-Validation")
    print("=" * 30)
    print(f"Auto-discovered benchmarks:")
    print(f"  ✅ Engine self-benchmarks ({len(discovered['engine'])} {SYMBOL} files)")
    print(f"  ✅ Simulation benchmarks ({len(discovered['simulation'])} {SYMBOL} files)")
    print(f"  ✅ Project benchmarks ({len(discovered['project'])} {SYMBOL} files)")
    print("\nSelect benchmarks to run:")
    print("1. Engine Self-Validation\n2. Project Performance Analysis")
    print("3. Combined Analysis\n4. Quick Performance Check")
    print("5. Workload Simulation")