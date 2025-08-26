# Copyright 2025 Baleine Jay
# Licensed under the Phicode Non-Commercial License (https://banes-lab.com/licensing)
# Commercial use requires a paid license. See link for details.
import json
import sys
import subprocess
import os
from datetime import datetime
from phicode_engine.config.config import BADGE, BENCHMARK_FOLDER_PATH, SECONDARY_FILE_TYPE, MAIN_FILE_TYPE, ENGINE, SYMBOL
from phicode_engine.core.phicode_logger import logger

def _find_files(directory, prefix, suffix):
    try:
        return [os.path.join(directory, entry.name)
                for entry in os.scandir(directory)
                if entry.is_file() and
                    entry.name.startswith(prefix) and
                    entry.name.endswith(suffix)]
    except OSError:
        return []

def discover_benchmarks():
    benchsuite_dir = os.path.dirname(__file__)

    engine_phi = _find_files(benchsuite_dir, "bench_", MAIN_FILE_TYPE)

    simulation_dir = os.path.join(benchsuite_dir, "simulation")
    simulation_phi = _find_files(simulation_dir, "simulate_", MAIN_FILE_TYPE) if os.path.exists(simulation_dir) else []

    project_phi = _find_files(BENCHMARK_FOLDER_PATH, "", MAIN_FILE_TYPE) if os.path.exists(BENCHMARK_FOLDER_PATH) else []
    project_py = _find_files(BENCHMARK_FOLDER_PATH, "", SECONDARY_FILE_TYPE) if os.path.exists(BENCHMARK_FOLDER_PATH) else []

    return {
        "engine": engine_phi,
        "simulation": simulation_phi,
        "project": project_phi + project_py,
        "all": engine_phi + simulation_phi + project_phi + project_py
    }

def execute_benchmark_file(file_path: str):
    try:
        name = os.path.splitext(os.path.basename(file_path))[0]
        benchsuite_dir = os.path.dirname(file_path)

        intesive_benchmarks = ["extreme", "crash", "phimmuno"]

        if any(keyword in name for keyword in intesive_benchmarks):
            timeout = 5*60
        else:
            timeout = 60

        result = subprocess.run([sys.executable, '-m', 'phicode_engine', name], capture_output=True, text=True, cwd=benchsuite_dir, timeout=timeout)

        return {"status": "completed" if result.returncode == 0 else "error", "output": result.stdout, "error": result.stderr if result.returncode != 0 else None}
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "error": f"Benchmark timeout ({timeout}s)"}
    except Exception as e:
        return {"status": "failed", "error": str(e)}

def run_json_benchmarks():
    discovered = discover_benchmarks()
    results = {}
    for benchmark in discovered['all']:
        name = os.path.splitext(os.path.basename(benchmark))[0]
        results[name] = execute_benchmark_file(benchmark)
    logger.info(json.dumps(results, indent=2))

def run_full_benchmark_report():
    from phicode_engine.benchsuite.benchmark_visualizer import generate_visualization_report, export_results_csv
    from phicode_engine.benchsuite.system_info import format_system_report

    logger.info("🔄 Running full benchmark suite...")

    results = {}
    for benchmark in discover_benchmarks()['all']:
        name = os.path.splitext(os.path.basename(benchmark))[0]
        logger.info(f"⚡ Executing {name}...")
        results[name] = execute_benchmark_file(benchmark)

    now = datetime.now()
    timestamp = now.strftime("%Y%m%d%H%M%S")
    hour_dir = os.path.join(BENCHMARK_FOLDER_PATH, now.strftime("%Y%m%d"), now.strftime("%H"))
    os.makedirs(hour_dir, exist_ok=True)

    # Write all outputs
    files = {
        f"{BADGE}bench_results_{timestamp}.json": lambda f: json.dump({"system": format_system_report(), "results": results}, f, indent=2),
        f"{BADGE}bench_results_{timestamp}.csv": lambda f: f.write(export_results_csv(results)),
        f"{BADGE}bench_results_{timestamp}.md": lambda f: f.write(generate_visualization_report(results))
    }

    for name, func in files.items():
        with open(os.path.join(hour_dir, name), "w") as f:
            func(f)

    logger.info(f"✅ Complete report package generated in {hour_dir}")
    logger.info(" → 📄 benchmark_results.json")
    logger.info(" → 📊 benchmark_results.csv")
    logger.info(" → 📈 benchmark_report.md (with Mermaid diagrams)")

def run_interactive_benchmarks():
    discovered = discover_benchmarks()

    from .benchmark_prints import print_benchsuite_entry
    print_benchsuite_entry(discovered, ENGINE, SYMBOL)

    selection = input("\nEnter selection (1-5): ").strip()
    logger.info(f"> Auto-executing discovered {SYMBOL} files...")

    if selection == "1":
        benchmarks = discovered['engine']
    elif selection == "2":
        benchmarks = discovered['project'] or []
    elif selection == "3":
        benchmarks = discovered['all']
    elif selection == "5":
        benchmarks = discovered['simulation']
    else:
        benchmarks = discovered['engine'][:2]

    for benchmark in benchmarks:
        result = execute_benchmark_file(benchmark)
        logger.info(result["output"])

    logger.info("💡 Additional options: --json --full")