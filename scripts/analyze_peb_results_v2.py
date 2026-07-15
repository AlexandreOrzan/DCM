#!/usr/bin/env python3
"""Analyze PEB results from MATLAB/SPM group-level output.

Extracts and displays the group comparison parameters showing which DCM
connections differ between CCD and TDC groups.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.io import loadmat


TASKS = ("MDOD", "MDOG", "MGOD", "MGOG")
DEFAULT_MODEL = "SENSORY_RELAY__UNC_FLEX"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze PEB group comparison results.")
    parser.add_argument(
        "--peb-dir",
        type=Path,
        default=Path("group_peb"),
        help="Directory containing PEB .mat files.",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help="DCM model name matching the PEB files.",
    )
    parser.add_argument(
        "--tasks",
        nargs="*",
        default=list(TASKS),
        help="Tasks to analyze.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Output directory for analysis results.",
    )
    return parser.parse_args()


def load_and_analyze_peb(peb_file: Path, task: str) -> dict:
    """Load a PEB result file and extract summaries."""
    result = {"Task": task, "File": str(peb_file)}

    if not peb_file.exists():
        result["error"] = "File not found"
        return result

    try:
        mat = loadmat(str(peb_file), squeeze_me=False)
    except Exception as e:
        result["error"] = f"Failed to load: {e}"
        return result

    peb_key = f"PEB_{task}"
    bma_key = f"BMA_{task}"
    m_key = f"M_{task}"
    dcm_key = f"DCM_{task}"

    # Get design matrix info
    if m_key in mat:
        m_obj = mat[m_key]
        if isinstance(m_obj, np.ndarray) and m_obj.ndim == 2 and m_obj.shape[0] > 0:
            if m_obj.dtype.names:  # Structured array
                if "X" in m_obj.dtype.names:
                    x = m_obj["X"][0, 0]
                    result["n_subjects"] = x.shape[0] if hasattr(x, "shape") else 1
                if "Xnames" in m_obj.dtype.names:
                    xnames = m_obj["Xnames"][0, 0]
                    if isinstance(xnames, np.ndarray):
                        # Flatten and convert to strings
                        names = []
                        for item in xnames.flat:
                            if isinstance(item, np.ndarray):
                                names.append("".join(item.flatten().astype(str)))
                            else:
                                names.append(str(item))
                        result["design_columns"] = names

    # Get PEB results (posterior means and standard deviations)
    if peb_key in mat:
        peb_obj = mat[peb_key]
        if isinstance(peb_obj, np.ndarray) and peb_obj.ndim == 2 and peb_obj.shape[0] > 0:
            if peb_obj.dtype.names:  # Structured array
                peb_struct = peb_obj[0, 0]  # Get first (only) element

                # Extract Ep (posterior means)
                if "Ep" in peb_obj.dtype.names:
                    ep = peb_struct[peb_obj.dtype.names.index("Ep")]
                    if isinstance(ep, np.ndarray):
                        result["posterior_means"] = ep.flatten()

                # Extract Cp (posterior covariance) for standard deviations
                if "Cp" in peb_obj.dtype.names:
                    cp = peb_struct[peb_obj.dtype.names.index("Cp")]
                    if isinstance(cp, np.ndarray) and cp.ndim == 2:
                        result["posterior_std"] = np.sqrt(np.diag(cp))

    # Get BMA results
    if bma_key in mat:
        bma_obj = mat[bma_key]
        if isinstance(bma_obj, np.ndarray) and bma_obj.size > 0:
            result["has_bma"] = True

    # Get GCM (group canonical model - DCM results)
    if dcm_key in mat:
        dcm_obj = mat[dcm_key]
        if isinstance(dcm_obj, np.ndarray):
            result["n_dcm_subjects"] = dcm_obj.shape[0]

    return result


def create_report(all_results: list[dict], model: str) -> str:
    """Create a summary report from all task results."""
    lines = [
        "=" * 90,
        "PEB GROUP COMPARISON ANALYSIS",
        "=" * 90,
        "",
        "Research Question:",
        "  Which DCM connectivity parameters differ between CCD and TDC groups?",
        "",
        "Encoding:",
        "  TDC group = -1  (typically healthy/control)",
        "  CCD group = +1  (typically patient/case)",
        "  Intercept = grand mean across groups",
        "  Column 2 (CCD_minus_TDC) = group contrast effect",
        "",
        "=" * 90,
    ]

    for result in all_results:
        task = result.get("Task", "UNKNOWN")
        lines.append(f"\nTASK: {task}")
        lines.append("-" * 90)

        if "error" in result:
            lines.append(f"  ERROR: {result['error']}")
            continue

        # Subject count
        if "n_subjects" in result:
            lines.append(f"  N subjects: {result['n_subjects']}")
        if "n_dcm_subjects" in result:
            lines.append(f"  N DCM subject results: {result['n_dcm_subjects']}")

        # Design matrix columns
        if "design_columns" in result:
            cols = result["design_columns"]
            lines.append(f"  Design columns: {', '.join(cols)}")

        # PEB results - the key output!
        if "posterior_means" in result:
            means = result["posterior_means"]
            stds = result.get("posterior_std", np.ones(len(means)))

            lines.append("\n  POSTERIOR ESTIMATES:")
            lines.append("  " + "-" * 86)

            # Always show intercept if available
            if len(means) > 0:
                col_name = result.get("design_columns", ["Intercept"])[0] if result.get("design_columns") else "Intercept"
                lines.append(f"    {col_name:20s}  Mean: {means[0]:9.4f}  Std: {stds[0]:9.4f}")

            # Show group effect (column 2 if it exists)
            if len(means) > 1:
                col_name = result.get("design_columns", ["?", "Group_Effect"])[1] if len(result.get("design_columns", [])) > 1 else "Group_Effect"
                lines.append(f"    {col_name:20s}  Mean: {means[1]:9.4f}  Std: {stds[1]:9.4f}  ← MAIN GROUP CONTRAST")

            # Show next few parameters
            if len(means) > 6:
                lines.append(f"\n    {len(means)} total parameters estimated")
                lines.append(f"    First 6 parameter estimates shown above, remaining: {len(means) - 2}")
            else:
                for i in range(2, len(means)):
                    param_name = result.get("design_columns", [""] * len(means))[i] if len(result.get("design_columns", [])) > i else f"Param_{i}"
                    lines.append(f"    {param_name:20s}  Mean: {means[i]:9.4f}  Std: {stds[i]:9.4f}")

        if result.get("has_bma"):
            lines.append("\n  ✓ BMA (Bayesian Model Averaging) results available")

    lines.extend([
        "",
        "=" * 90,
        "INTERPRETATION GUIDE:",
        "",
        "  1. GROUP EFFECT (CCD_minus_TDC):",
        "     - If Mean ≠ 0 with small Std → group difference likely",
        "     - Positive = CCD group has stronger parameter",
        "     - Negative = TDC group has stronger parameter",
        "",
        "  2. FURTHER ANALYSIS IN MATLAB:",
        f"     load('group_peb/PEB_MDOD_{model}.mat')",
        "     spm_dcm_peb_review(BMA_MDOD, GCM_MDOD)  % Interactive inspection",
        "",
        "  3. STATISTICAL INFERENCE:",
        "     - Use BMA output for family-wise inference",
        "     - Check Bayes factors for parameter importance",
        "     - Consider posterior probabilities > 0.95 as credible effects",
        "",
        "=" * 90,
    ])

    return "\n".join(lines)


def run() -> None:
    args = parse_args()
    peb_dir = args.peb_dir.resolve()
    out_dir = (args.out_dir or peb_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nAnalyzing PEB results from: {peb_dir}")
    print(f"Model: {args.model}\n")

    # Load and analyze each task
    results = []
    for task in args.tasks:
        peb_file = peb_dir / f"PEB_{task}_{args.model}.mat"
        print(f"  {task}...", end=" ")
        result = load_and_analyze_peb(peb_file, task)
        results.append(result)
        status = "✓" if "error" not in result else "✗"
        print(status)

    # Generate and print report
    report = create_report(results, args.model)
    print("\n" + report)

    # Save report
    report_file = out_dir / "peb_analysis_report.txt"
    with open(report_file, "w") as f:
        f.write(report)
    print(f"\nReport saved to: {report_file}")

    # Save CSV summary
    df_rows = []
    for result in results:
        row = {
            "Task": result.get("Task", ""),
            "N_subjects": result.get("n_subjects", ""),
            "Status": "OK" if "error" not in result else f"Error: {result['error']}"
        }
        if "posterior_means" in result:
            means = result["posterior_means"]
            row["Intercept"] = means[0] if len(means) > 0 else ""
            row["Group_Effect"] = means[1] if len(means) > 1 else ""
        df_rows.append(row)

    df = pd.DataFrame(df_rows)
    csv_file = out_dir / "peb_summary.csv"
    df.to_csv(csv_file, index=False)
    print(f"Summary table saved to: {csv_file}\n")


if __name__ == "__main__":
    run()
