#!/usr/bin/env python3
"""Skill Description Optimization Loop.

Automates the process of optimizing a skill's description:
1. Run trigger eval on current description (train set)
2. Call Claude to generate an improved description based on failures
3. Repeat for N iterations, keeping track of the best description
4. Final validation on a hold-out test set (optional)
"""

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

from scripts.improve_description import improve_description
from scripts.run_eval import run_eval
from scripts.utils import parse_skill_md


def main():
    parser = argparse.ArgumentParser(description="Skill Description Optimization Loop")
    parser.add_argument("--skill-path", required=True, help="Path to skill directory")
    parser.add_argument("--train-set", required=True, help="Path to training eval set JSON")
    parser.add_argument("--test-set", default=None, help="Optional path to hold-out test set JSON")
    parser.add_argument("--iterations", type=int, default=5, help="Number of optimization iterations")
    parser.add_argument("--workers", type=int, default=10, help="Number of parallel workers for eval")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout per query in seconds")
    parser.add_argument("--runs-per-query", type=int, default=3, help="Number of runs per query")
    parser.add_argument("--model", default=None, help="Model to use (default: user configured)")
    parser.add_argument("--out-dir", type=Path, default=None, help="Directory for logs and results")
    args = parser.parse_args()

    skill_path = Path(args.skill_path)
    if not (skill_path / "SKILL.md").exists():
        print(f"Error: No SKILL.md found at {skill_path}")
        sys.exit(1)

    train_set = json.loads(Path(args.train_set).read_text())
    test_set = json.loads(Path(args.test_set).read_text()) if args.test_set else None

    # Setup output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = args.out_dir or (Path.cwd() / f"optimization_{timestamp}")
    out_dir.mkdir(parents=True, exist_ok=True)
    log_dir = out_dir / "logs"
    log_dir.mkdir(exist_ok=True)

    name, original_description, skill_content = parse_skill_md(skill_path)
    from scripts.run_eval import find_project_root
    project_root = find_project_root()

    current_description = original_description
    best_description = original_description
    best_score = -1.0
    history = []

    print(f"\n🚀 Starting optimization loop for skill: {name}")
    print(f"   Initial description: \"{current_description}\"")
    print(f"   Output directory: {out_dir}\n")

    for i in range(args.iterations):
        print(f"--- Iteration {i+1}/{args.iterations} ---")
        
        # 1. Run eval
        print(f"   Running eval on train set ({len(train_set)} queries)...")
        results = run_eval(
            eval_set=train_set,
            skill_name=name,
            description=current_description,
            num_workers=args.workers,
            timeout=args.timeout,
            project_root=project_root,
            runs_per_query=args.runs_per_query,
            model=args.model,
        )
        
        passed = results["summary"]["passed"]
        total = results["summary"]["total"]
        score = passed / total
        print(f"   Score: {passed}/{total} ({score*100:.1f}%)")

        # Track history for context
        history.append({
            "iteration": i,
            "description": current_description,
            "passed": passed,
            "total": total,
            "results": results["results"]
        })

        if score > best_score:
            best_score = score
            best_description = current_description
            print(f"   ✨ New best score!")

        # 2. Improve description (unless it's the last iteration)
        if i < args.iterations - 1:
            print(f"   Calling Claude to improve description...")
            current_description = improve_description(
                skill_name=name,
                skill_content=skill_content,
                current_description=current_description,
                eval_results=results,
                history=history[-3:],  # Give recent context
                model=args.model,
                log_dir=log_dir,
                iteration=i
            )
            print(f"   Next description: \"{current_description}\"")
        print()

    # 3. Final validation on test set
    test_results = None
    if test_set:
        print(f"--- Final Validation on Test Set ---")
        print(f"   Testing best description: \"{best_description}\"")
        test_results = run_eval(
            eval_set=test_set,
            skill_name=name,
            description=best_description,
            num_workers=args.workers,
            timeout=args.timeout,
            project_root=project_root,
            runs_per_query=args.runs_per_query,
            model=args.model,
        )
        t_passed = test_results["summary"]["passed"]
        t_total = test_results["summary"]["total"]
        print(f"   Test Score: {t_passed}/{t_total} ({ (t_passed/t_total)*100:.1f}%)\n")

    # 4. Save results
    final_data = {
        "skill_name": name,
        "original_description": original_description,
        "best_description": best_description,
        "best_score": best_score,
        "train_size": len(train_set),
        "test_size": len(test_set) if test_set else 0,
        "iterations_run": args.iterations,
        "history": history,
    }
    if test_results:
        final_data["test_results"] = test_results

    result_file = out_dir / "optimization_results.json"
    result_file.write_text(json.dumps(final_data, indent=2))
    
    # Also generate a report.html for final state
    from scripts.generate_report import generate_html_report
    # We fake a grading.json-like structure so generate_html_report can read it
    temp_grading = {
        "skill_name": name,
        "summary": test_results["summary"] if test_results else history[-1]["summary"],
        "expectations": [], # Trigger eval doesn't have expectations in the same way
        "best_description": best_description,
        "original_description": original_description,
        "best_score": best_score,
        "iterations_run": args.iterations,
        "train_size": len(train_set),
        "test_size": len(test_set) if test_set else 0,
    }
    # Map results to something report-like
    plot_results = test_results["results"] if test_results else history[-1]["results"]
    for r in plot_results:
        status = "✅ PASS" if r["pass"] else "❌ FAIL"
        temp_grading["expectations"].append({
            "text": f"[{status}] Query: {r['query']}",
            "passed": r["pass"],
            "evidence": f"Trigger rate: {r['trigger_rate']*100:.0f}% ({r['triggers']}/{r['runs']})"
        })
    
    (out_dir / "grading.json").write_text(json.dumps(temp_grading))
    generate_html_report(out_dir)

    print(f"✅ Optimization complete!")
    print(f"   Best description: \"{best_description}\"")
    print(f"   Results saved to: {out_dir}\n")


if __name__ == "__main__":
    main()
