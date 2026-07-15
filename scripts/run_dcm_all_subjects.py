#!/usr/bin/env python3
"""Run DCM.ipynb for all available subjects in derivatives_MNIcohort3.

The notebook is currently a subject-level pipeline. This runner makes a
temporary parameterized copy for each subject, executes it, and writes the
executed notebook into that subject's dcm_results folder.

Typical use after adding the events files:

    python run_dcm_all_subjects.py --dry-run
    python run_dcm_all_subjects.py --run-matlab
    python run_dcm_all_subjects.py --no-run-matlab

Use --force to rerun subjects that already have bms_8model_summary.csv.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


TASKS = ("MDOD", "MDOG", "MGOD", "MGOG")
ROI_NAMES = ("M1_L", "M1_R", "A1_L", "A1_R", "V1_L", "V1_R")
ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent if ROOT.name == "src" else ROOT


def resolve_data_root(requested_root: Path) -> Path:
    """Resolve cohort root across macOS/Linux mount conventions."""
    requested_root = requested_root.expanduser()
    if requested_root.exists():
        return requested_root.resolve()

    candidate_roots = [
        Path("/Volumes/T7 Shield/derivatives_MNIcohort3"),
        Path("/media") / "*" / "T7 Shield" / "derivatives_MNIcohort3",
        Path("/run/media") / "*" / "T7 Shield" / "derivatives_MNIcohort3",
        Path('/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3')

    ]

    for candidate in candidate_roots:
        if "*" in str(candidate):
            for matched in sorted(Path("/").glob(str(candidate).lstrip("/"))):
                if matched.exists():
                    return matched.resolve()
        elif candidate.exists():
            return candidate.resolve()

    return requested_root.resolve()


@dataclass(frozen=True)
class SubjectCheck:
    subject: str
    ok: bool
    missing: tuple[str, ...]
    output_dir: Path
    summary_csv: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Execute DCM.ipynb across all cohort subjects.")
    parser.add_argument(
        "--data-root",
        type=Path,
        default=Path("/Volumes/T7 Shield/derivatives_MNIcohort3"),
        help="Root containing sub-* folders.",
    )
    parser.add_argument(
        "--notebook",
        type=Path,
        default=PROJECT_ROOT / "src" / "DCM.ipynb",
        help="Subject-level DCM notebook to execute.",
    )
    parser.add_argument(
        "--subjects",
        nargs="*",
        default=None,
        help="Optional subject subset, e.g. sub-03 sub-04 32.",
    )
    parser.add_argument(
        "--tasks",
        nargs="*",
        default=list(TASKS),
        help="Tasks expected per subject.",
    )
    parser.add_argument(
        "--run-matlab",
        action=argparse.BooleanOptionalAction,
        default=None,
        help=(
            "Override RUN_MATLAB in the temporary notebook. "
            "Default preserves the notebook's existing RUN_MATLAB value."
        ),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Rerun even if bms_8model_summary.csv already exists.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only report what would run.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=0,
        help="Notebook execution timeout in seconds. 0 means no timeout.",
    )
    parser.add_argument(
        "--kernel",
        default="python3",
        help="Jupyter kernel name.",
    )
    return parser.parse_args()


def normalise_subject(subject: str) -> str:
    subject = str(subject)
    return subject if subject.startswith("sub-") else f"sub-{int(subject):02d}"


def discover_subjects(data_root: Path) -> list[str]:
    return sorted(p.name for p in data_root.glob("sub-*") if p.is_dir())


def bold_candidates(func_dir: Path, subject: str, task: str) -> list[Path]:
    preferred = sorted(func_dir.glob(f"{subject}_task-{task}*_desc-preproc_bold.nii.gz"))
    if preferred:
        return preferred

    # Some cohort folders contain preprocessed 4D BOLD files without the
    # desc-preproc entity. Keep boldref files out: they are single-volume
    # references and cannot be used for ROI time-series extraction.
    fallback = [
        path
        for path in func_dir.glob(f"{subject}_task-{task}*_bold.nii.gz")
        if "boldref" not in path.name
    ]
    return sorted(fallback)


def check_subject(data_root: Path, subject: str, tasks: list[str]) -> SubjectCheck:
    func_dir = data_root / subject / "func"
    output_dir = func_dir / "dcm_results"
    summary_csv = output_dir / "bms_8model_summary.csv"
    missing: list[str] = []

    if not func_dir.exists():
        missing.append(f"missing func directory: {func_dir}")

    has_at_least_one_task = False
    for task in tasks:
        bold_files = bold_candidates(func_dir, subject, task)
        event_file = func_dir / f"{subject}_task_{task}.csv"

        if bold_files and event_file.exists():
            has_at_least_one_task = True
        else:
            pass

    if not has_at_least_one_task:
        missing.append("Aucune tâche fMRI valide et complète (BOLD + CSV) trouvée pour ce sujet.")

    glm_dir = data_root / "mask"
    for roi in ROI_NAMES:
        roi_file = glm_dir / f"{roi}_sphere.nii.gz"
        if not roi_file.exists():
            missing.append(f"missing ROI mask central: {roi_file.name} dans {glm_dir}")

    return SubjectCheck(
        subject=subject,
        ok=not missing,
        missing=tuple(missing),
        output_dir=output_dir,
        summary_csv=summary_csv,
    )


def patch_parameter_cell(source: str, subject: str, data_root: Path, run_matlab: bool | None) -> str:
    replacements = {
        "subject_id =": f'subject_id = "{subject}"',
    }
    if run_matlab is not None:
        replacements["RUN_MATLAB ="] = f"RUN_MATLAB = {str(bool(run_matlab))}"

    patched_lines = []
    for line in source.splitlines():
        stripped = line.strip()
        replaced = False
        for prefix, replacement in replacements.items():
            if stripped.startswith(prefix):
                indent = line[: len(line) - len(line.lstrip())]
                patched_lines.append(indent + replacement)
                replaced = True
                break
        if not replaced:
            patched_lines.append(line)

    patched = "\n".join(patched_lines)
    root_literal = f'Path("{data_root}")'
    if root_literal not in patched:
        patched = patched.replace(
            "candidate_roots = [",
            f"candidate_roots = [\n    {root_literal},",
            1,
        )
    return patched


def make_subject_notebook(
    notebook: Path,
    subject: str,
    data_root: Path,
    run_matlab: bool | None,
    tmp_dir: Path,
) -> Path:
    with open(notebook, "r", encoding="utf-8") as f:
        nb = json.load(f)

    patched = False
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        source = "".join(cell.get("source", []))
        if "subject_id =" in source and "candidate_roots" in source:
            new_source = patch_parameter_cell(source, subject, data_root, run_matlab)
            cell["source"] = [line + "\n" for line in new_source.splitlines()]
            patched = True
            break

    if not patched:
        raise RuntimeError("Could not find the DCM.ipynb setup cell containing subject_id and candidate_roots.")

    tmp_notebook = tmp_dir / f"DCM_{subject}.ipynb"
    with open(tmp_notebook, "w", encoding="utf-8") as f:
        json.dump(nb, f)
    return tmp_notebook


def execute_notebook(tmp_notebook: Path, output_notebook: Path, kernel: str, timeout: int) -> None:
    output_notebook.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        "-m",
        "jupyter",
        "nbconvert",
        "--to",
        "notebook",
        "--execute",
        str(tmp_notebook),
        "--output",
        str(output_notebook),
        "--ExecutePreprocessor.kernel_name",
        kernel,
    ]
    if timeout > 0:
        cmd.extend(["--ExecutePreprocessor.timeout", str(timeout)])
    else:
        cmd.extend(["--ExecutePreprocessor.timeout", "-1"])

    subprocess.run(cmd, check=True, cwd=str(tmp_notebook.parent))


def run() -> None:
    args = parse_args()
    data_root = resolve_data_root(args.data_root)
    notebook = args.notebook.expanduser().resolve()

    if args.subjects is None:
        subjects = discover_subjects(data_root)
    else:
        subjects = [normalise_subject(s) for s in args.subjects]

    checks = [check_subject(data_root, subject, args.tasks) for subject in subjects]
    runnable = [
        check
        for check in checks
        if check.ok and (args.force or not check.summary_csv.exists())
    ]
    skipped_done = [
        check
        for check in checks
        if check.ok and check.summary_csv.exists() and not args.force
    ]
    blocked = [check for check in checks if not check.ok]

    print(f"Data root : {data_root}")
    print(f"Notebook  : {notebook}")
    if args.run_matlab is None:
        print("MATLAB    : preserve notebook RUN_MATLAB")
    else:
        print(f"MATLAB    : force RUN_MATLAB={args.run_matlab}")
    print(f"Subjects  : {len(subjects)} found/requested")
    print(f"Runnable  : {len(runnable)}")
    print(f"Done      : {len(skipped_done)} already have bms_8model_summary.csv")
    print(f"Blocked   : {len(blocked)} missing inputs")

    if blocked:
        print("\nBlocked subjects")
        for check in blocked:
            print(f"  {check.subject}")
            for item in check.missing:
                print(f"    - {item}")

    if skipped_done:
        print("\nAlready done")
        for check in skipped_done:
            print(f"  {check.subject}: {check.summary_csv}")

    if not runnable:
        print("\nNo subjects to run.")
        return

    print("\nWill run")
    for check in runnable:
        print(f"  {check.subject}")

    if args.dry_run:
        print("\nDry run only. Add events/inputs, then run without --dry-run.")
        return

    with tempfile.TemporaryDirectory(prefix="miplab_dcm_") as tmp:
        tmp_dir = Path(tmp)
        failed: list[tuple[str, str]] = []
        for check in runnable:
            print(f"\n=== Running {check.subject} ===")
            tmp_notebook = make_subject_notebook(
                notebook=notebook,
                subject=check.subject,
                data_root=data_root,
                run_matlab=args.run_matlab,
                tmp_dir=tmp_dir,
            )
            output_notebook = check.output_dir / f"DCM_executed_{check.subject}.ipynb"
            try:
                execute_notebook(tmp_notebook, output_notebook, args.kernel, args.timeout)
                print(f"Saved executed notebook: {output_notebook}")
            except subprocess.CalledProcessError as exc:
                failed.append((check.subject, str(exc)))
                print(f"FAILED {check.subject}: notebook execution returned non-zero status")

    if failed:
        print("\nSome subjects failed")
        for subject, reason in failed:
            print(f"  {subject}: {reason}")
        print("\nTip: if F_values.mat is missing, run with --run-matlab to execute MATLAB/SPM cells.")
        raise SystemExit(1)

    print("\nAll requested runnable subjects completed.")


if __name__ == "__main__":
    run()
