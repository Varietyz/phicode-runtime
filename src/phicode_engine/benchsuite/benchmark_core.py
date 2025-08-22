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

        if "crash" in name:
            timeout = 120
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

    discovered = discover_benchmarks()
    results = {}
    for benchmark in discovered['all']:
        name = os.path.splitext(os.path.basename(benchmark))[0]
        logger.info(f"⚡ Executing {name}...")
        results[name] = execute_benchmark_file(benchmark)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    datestamp = datetime.now().strftime("%Y%m%d")

    logger.info("📊 Generating complete benchmark report...")

    results_dir = BENCHMARK_FOLDER_PATH
    os.makedirs(results_dir, exist_ok=True)

    datestamp_dir = os.path.join(results_dir, datestamp)
    os.makedirs(datestamp_dir, exist_ok=True)

    with open(os.path.join(datestamp_dir, f"{BADGE}bench_results_{timestamp}.json"), "w") as f:
        json.dump({"system": format_system_report(), "results": results}, f, indent=2)

    with open(os.path.join(datestamp_dir, f"{BADGE}bench_results_{timestamp}.csv"), "w") as f:
        f.write(export_results_csv(results))

    with open(os.path.join(datestamp_dir, f"{BADGE}bench_results_{timestamp}.md"), "w") as f:
        f.write(generate_visualization_report(results))

    logger.info("✅ Complete report package generated in {datestamp_dir}")
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