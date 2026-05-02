#!/usr/bin/env python3
"""
Generate a human-readable evaluation report from grading.json files.

Usage:
    python scripts/generate_report.py <run_dir> [output_file]
"""

import argparse
import html
import json
import sys
from datetime import datetime
from pathlib import Path


def generate_html_report(run_dir: Path, output_file: Path | None = None) -> Path:
    """Generate an HTML report for an eval run."""
    grading_file = run_dir / "grading.json"
    if not grading_file.exists():
        print(f"Error: {grading_file} not found")
        sys.exit(1)

    try:
        data = json.loads(grading_file.read_text())
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {grading_file}: {e}")
        sys.exit(1)

    summary = data.get("summary", {})
    metrics = data.get("execution_metrics", {})
    timing = data.get("timing", {})
    expectations = data.get("expectations", [])
    
    # Optimization data if present
    best_test_score = data.get("best_test_score")
    title_prefix = f"[{data['skill_name']}] " if "skill_name" in data else ""

    report_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title_prefix}Evaluation Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; max-width: 1000px; margin: 0 auto; padding: 2rem; background: #f5f7f9; }}
        h1, h2, h3 {{ color: #2c3e50; }}
        .card {{ background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); padding: 1.5rem; margin-bottom: 1.5rem; }}
        .header {{ display: flex; justify-content: space-between; align-items: baseline; border-bottom: 2px solid #edf2f7; margin-bottom: 1.5rem; padding-bottom: 0.5rem; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 1rem; }}
        .stat {{ border-left: 4px solid #3498db; padding-left: 1rem; }}
        .stat-label {{ font-size: 0.85rem; color: #7f8c8d; text-transform: uppercase; letter-spacing: 1px; }}
        .stat-value {{ font-size: 1.5rem; font-weight: bold; }}
        .pass {{ border-color: #2ecc71; }}
        .fail {{ border-color: #e74c3c; }}
        .expectation {{ border-bottom: 1px solid #edf2f7; padding: 1rem 0; }}
        .expectation:last-child {{ border-bottom: none; }}
        .badge {{ display: inline-block; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-weight: bold; text-transform: uppercase; margin-right: 0.5rem; }}
        .badge-pass {{ background: #d4edda; color: #155724; }}
        .badge-fail {{ background: #f8d7da; color: #721c24; }}
        .evidence {{ background: #f8f9fa; border-radius: 4px; padding: 0.75rem; margin-top: 0.5rem; font-size: 0.9rem; font-style: italic; border-left: 3px solid #dee2e6; }}
        pre {{ background: #2c3e50; color: #ecf0f1; padding: 1rem; border-radius: 4px; overflow-x: auto; font-size: 0.85rem; }}
        .opt-meta {{ font-size: 0.9rem; color: #666; margin-top: -1rem; margin-bottom: 1rem; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Evaluation Report</h1>
        <div>{datetime.now().strftime("%Y-%m-%d %H:%M")}</div>
    </div>

    {f'''<div class="opt-meta">
        # """ + title_prefix + """Skill Description Optimization<br>
        Original: {html.escape(data.get('original_description', 'N/A'))}<br>
        Best: {html.escape(data.get('best_description', 'N/A'))}<br>
        Best Score: {data.get('best_score', 'N/A')} {'(test)' if best_test_score else '(train)'}<br>
        Iterations: {data.get('iterations_run', 0)} | Train: {data.get('train_size', '?')} | Test: {data.get('test_size', '?')}
    </div>''' if 'best_description' in data else ''}

    <div class="stats-grid">
        <div class="stat pass">
            <div class="stat-label">Pass Rate</div>
            <div class="stat-value">{summary.get('pass_rate', 0)*100:.1f}%</div>
        </div>
        <div class="stat">
            <div class="stat-label">Score</div>
            <div class="stat-value">{summary.get('passed', 0)} / {summary.get('total', 0)}</div>
        </div>
        <div class="stat">
            <div class="stat-label">Duration</div>
            <div class="stat-value">{timing.get('total_duration_seconds', 0.0):.1f}s</div>
        </div>
        <div class="stat">
            <div class="stat-label">Tool Calls</div>
            <div class="stat-value">{metrics.get('total_tool_calls', 0)}</div>
        </div>
    </div>

    <div class="card">
        <h2>Expectations</h2>
        {"".join([f'''
        <div class="expectation">
            <div>
                <span class="badge badge-{"pass" if exp.get("passed") else "fail"}">{"Pass" if exp.get("passed") else "Fail"}</span>
                <strong>{html.escape(exp.get("text", ""))}</strong>
            </div>
            {f'<div class="evidence">{html.escape(exp.get("evidence", ""))}</div>' if exp.get("evidence") else ""}
        </div>
        ''' for exp in expectations])}
    </div>

    {f'''
    <div class="card">
        <h2>Execution Metrics</h2>
        <div class="stats-grid">
            <div class="stat">
                <div class="stat-label">Steps</div>
                <div class="stat-value">{metrics.get('total_steps', 0)}</div>
            </div>
            <div class="stat">
                <div class="stat-label">Output Chars</div>
                <div class="stat-value">{metrics.get('output_chars', 0)}</div>
            </div>
            <div class="stat">
                <div class="stat-label">Errors</div>
                <div class="stat-value">{metrics.get('errors_encountered', 0)}</div>
            </div>
        </div>
        <h3>Tool Breakdown</h3>
        <pre>{json.dumps(metrics.get('tool_calls', {}), indent=2)}</pre>
    </div>
    ''' if metrics else ""}

</body>
</html>
"""
    if not output_file:
        output_file = run_dir / "report.html"
    
    output_file.write_text(report_html)
    return output_file


def main():
    parser = argparse.ArgumentParser(description="Generate human-readable evaluation report")
    parser.add_argument("run_dir", type=Path, help="Directory containing grading.json")
    parser.add_argument("output", type=Path, nargs="?", help="Output HTML file path")
    args = parser.parse_args()

    if not args.run_dir.exists():
        print(f"Directory not found: {args.run_dir}")
        sys.exit(1)

    report_path = generate_html_report(args.run_dir, args.output)
    print(f"Generated report: {report_path}")


if __name__ == "__main__":
    main()
