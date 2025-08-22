import os
from phicode_engine.core.importing.phicode_importer import install_phicode_importer
from .benchmark_cli import run_benchmarks
from phicode_engine.core.phicode_logger import logger

install_phicode_importer(os.path.dirname(__file__))

def get_system_info():
    try:
        from .system_info import get_system_fingerprint
        return get_system_fingerprint()
    except ImportError:
        return {"error": "system_info module not available"}

def generate_performance_chart(results):
    try:
        from .benchmark_visualizer import generate_mermaid_performance_chart
        return generate_mermaid_performance_chart(results)
    except ImportError:
        return "benchmark_visualizer module not available"

def report(name: str, result):
    logger.info(f"📊 {name}: {result}")

__all__ = ["run_benchmarks", "get_system_info", "generate_performance_chart", "report"]