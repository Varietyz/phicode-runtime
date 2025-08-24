# Copyright 2025 Baleine Jay
# Licensed under the Phicode Non-Commercial License (https://banes-lab.com/licensing)
# Commercial use requires a paid license. See link for details.
import json
from typing import Dict

def generate_mermaid_performance_chart(results: Dict) -> str:
    chart_lines = ["graph TD"]

    for name, data in results.items():
        if data.get("status") != "completed":
            continue

        output = data.get("output", "")
        if "chars/sec" in output:
            speed = _extract_metric(output, "chars/sec")
            chart_lines.append(f'    {name}["{name}<br/>{speed} chars/sec"]')
        elif "Hit Rate" in output:
            rate = _extract_metric(output, "Hit Rate")
            chart_lines.append(f'    {name}["{name}<br/>Hit Rate: {rate}"]')
        elif "MB" in output:
            memory = _extract_metric(output, "MB")
            chart_lines.append(f'    {name}["{name}<br/>{memory}MB"]')
        else:
            chart_lines.append(f'    {name}["{name}<br/>✓ Completed"]')

    return "\n".join(chart_lines)

def create_performance_summary_chart(results: Dict) -> str:
    passed = sum(1 for r in results.values() if r.get("status") == "completed")
    total = len(results)

    chart = f"""flowchart LR
    A[Φ Engine Benchmarks] --> B["{passed}/{total} Passed"]
    B --> C[Performance Validated]

    style A fill:#e1f5fe
    style B fill:#c8e6c9
    style C fill:#dcedc8"""

    return chart

def export_results_csv(results: Dict) -> str:
    lines = ["Benchmark,Status,Output"]

    for name, data in results.items():
        status = data.get("status", "unknown")
        output = data.get("output", "").replace("\n", " | ").replace(",", ";")
        lines.append(f"{name},{status},{output}")

    return "\n".join(lines)

def _extract_metric(text: str, metric: str) -> str:
    lines = text.split("\n")
    for line in lines:
        if metric in line:
            parts = line.split(metric)[0].split()
            if parts:
                return parts[-1].replace(":", "")
    return "N/A"

def generate_visualization_report(results: Dict, format: str = "mermaid") -> str:
    if format == "mermaid":
        performance_chart = generate_mermaid_performance_chart(results)
        summary_chart = create_performance_summary_chart(results)

        return f"""# Φ Engine Performance Report

## Summary
```mermaid
{summary_chart}
```

## Detailed Performance
```mermaid
{performance_chart}
```

## Results Data
{len(results)} benchmarks executed
"""

    elif format == "csv":
        return export_results_csv(results)

    else:
        return json.dumps(results, indent=2)