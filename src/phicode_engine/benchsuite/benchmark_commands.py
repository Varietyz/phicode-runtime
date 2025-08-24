# Copyright 2025 Baleine Jay
# Licensed under the Phicode Non-Commercial License (https://banes-lab.com/licensing)
# Commercial use requires a paid license. See link for details.
import sys
import os

def parse_benchmark_command():
    try:
        from phicode_engine.core.importing.phicode_importer import install_phicode_importer
        benchsuite_dir = os.path.dirname(__file__)
        install_phicode_importer(benchsuite_dir)
    except ImportError:
        pass

    if "--simulation" in sys.argv:
        from phicode_engine.benchsuite.simulation import run_simulations
        run_simulations.main()
        return True

    if "--full" in sys.argv:
        from phicode_engine.benchsuite.benchmark_core import run_full_benchmark_report
        run_full_benchmark_report()
        return True

    if "--json" in sys.argv:
        from phicode_engine.benchsuite.benchmark_core import run_json_benchmarks
        run_json_benchmarks()
        return True

    from phicode_engine.benchsuite.benchmark_core import run_interactive_benchmarks
    run_interactive_benchmarks()
    return True