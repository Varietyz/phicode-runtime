# Copyright 2025 Baleine Jay
# Licensed under the Phicode Non-Commercial License (https://banes-lab.com/licensing)
# Commercial use requires a paid license. See link for details.
import sys
import platform
from typing import Dict, Optional

def get_system_fingerprint() -> Dict[str, str]:
    try:
        import psutil
        memory_gb = round(psutil.virtual_memory().total / (1024**3), 1)
        cpu_count = psutil.cpu_count(logical=False)
        cpu_logical = psutil.cpu_count(logical=True)
    except ImportError:
        memory_gb = "unknown"
        cpu_count = "unknown"
        cpu_logical = "unknown"

    return {
        "os": f"{platform.system()} {platform.release()}",
        "python": f"{sys.implementation.name} {sys.version_info.major}.{sys.version_info.minor}",
        "cpu_physical": str(cpu_count),
        "cpu_logical": str(cpu_logical),
        "memory_gb": str(memory_gb),
        "arch": platform.machine()
    }

def get_performance_baseline() -> float:
    import time

    start = time.perf_counter()
    total = 0
    for i in range(100000):
        total += i * i
    end = time.perf_counter()

    baseline = 100000 / (end - start)
    return round(baseline, 0)

def normalize_result(raw_result: float, baseline: Optional[float] = None) -> float:
    if baseline is None:
        baseline = get_performance_baseline()

    reference_baseline = 1000000.0
    normalized = raw_result * (reference_baseline / baseline)
    return round(normalized, 2)

def format_system_report() -> str:
    info = get_system_fingerprint()
    baseline = get_performance_baseline()

    report = f"""System Information:
  OS: {info['os']}
  Python: {info['python']}
  CPU: {info['cpu_physical']} cores ({info['cpu_logical']} logical)
  Memory: {info['memory_gb']} GB
  Architecture: {info['arch']}
  Performance Baseline: {baseline:,.0f} ops/sec"""

    return report

def get_reproducibility_hash() -> str:
    import hashlib

    info = get_system_fingerprint()
    stable_info = f"{info['os']}-{info['python']}-{info['cpu_physical']}-{info['arch']}"
    return hashlib.md5(stable_info.encode()).hexdigest()[:8]