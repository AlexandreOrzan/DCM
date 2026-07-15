#!/usr/bin/env python3
"""Run the full-cohort MIPLAB PEB analysis directly from Python.

This wrapper verifies that all expected subject-level DCMs exist, writes the
MATLAB/SPM PEB batch script, and optionally launches MATLAB.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent if ROOT.name == "src" else ROOT
DEFAULT_MODEL = "SENSORY_RELAY__UNC_FLEX"
TASKS = ("MDOD", "MDOG", "MGOD", "MGOG")

SUBJECT_GROUP = {
    "sub-03": "TDC",
    "sub-04": "CCD",
    "sub-06": "CCD",
    "sub-07": "CCD",
    "sub-08": "TDC",
    "sub-13": "TDC",
    "sub-14": "TDC",
    "sub-19": "TDC",
    "sub-20": "TDC",
    "sub-26": "TDC",
    "sub-31": "CCD",
    "sub-32": "CCD",
    "sub-34": "TDC",
    "sub-41": "TDC",
    "sub-42": "TDC",
    "sub-43": "TDC",
    "sub-45": "TDC",
    "sub-51": "TDC",
    "sub-52": "CCD",
    "sub-54": "TDC",
    "sub-55": "TDC",
    "sub-56": "TDC",
    "sub-58": "TDC",
    "sub-63": "CCD",
    "sub-64": "CCD",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify and run the full-cohort PEB analysis from Python."
    )
    parser.add_argument(
        "--data-root",
        type=Path,
        default=Path("/Volumes/T7 Shield/derivatives_MNIcohort3"),
    )
    parser.add_argument("--out-dir", type=Path, default=Path("group_peb_full_cohort"))
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument(
        "--fields",
        nargs="*",
        default=["A", "B"],
        help="DCM parameter fields passed to spm_dcm_peb. Default: A B.",
    )
    parser.add_argument("--matlab-cmd", default="")
    parser.add_argument("--spm-path", default="")
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only verify inputs and print the command without launching MATLAB.",
    )
    return parser.parse_args()


def resolve_data_root(requested: Path) -> Path:
    candidates = [
        requested.expanduser(),
        Path("/Volumes/T7 Shield/derivatives_MNIcohort3"),
        Path("/media/lea/T7 Shield/derivatives_MNIcohort3"),
        Path("/run/media/lea/T7 Shield/derivatives_MNIcohort3"),
        Path('/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3')
    ]
    return next((path.resolve() for path in candidates if path.exists()), requested.resolve())


def resolve_matlab(requested: str) -> Path:
    candidates = [
        Path(requested).expanduser() if requested else None,
        Path(shutil.which("matlab")) if shutil.which("matlab") else None,
        Path("/home/lea/MATLAB/R2025b/bin/matlab"),
        Path("/home/lea/Matlab/R2025b/bin/matlab"),
        Path("/usr/local/MATLAB/R2025b/bin/matlab"),
        Path("/Applications/MATLAB_R2025a.app/bin/matlab"),
    ]
    matlab = next((path.resolve() for path in candidates if path and path.exists()), None)
    if matlab is None:
        raise FileNotFoundError(
            "MATLAB executable not found. Pass --matlab-cmd /path/to/matlab."
        )
    return matlab


def resolve_spm(requested: str) -> Path:
    candidates = [
        Path(requested).expanduser() if requested else None,
        Path("/home/lea/MATLAB/spm"),
        Path("/home/lea/MATLAB/spm12"),
        Path("/home/lea/spm12"),
        Path.home() / "spm",
        Path.home() / "Documents" / "MATLAB" / "spm",
    ]
    spm = next((path.resolve() for path in candidates if path and path.exists()), None)
    if spm is None:
        raise FileNotFoundError("SPM directory not found. Pass --spm-path /path/to/spm.")
    return spm


def dcm_file(data_root: Path, subject: str, task: str, model: str) -> Path:
    return (
            data_root
            / subject
            / "func"
            / "dcm_results"
            / "spm_dcm_specs"
            / "pathway_models"
            / model
            / task
            / f"DCM_{subject}_{task}_{model}.mat"
    )


def collect_inputs(data_root: Path, model: str) -> pd.DataFrame:
    rows = []
    for subject, group in sorted(SUBJECT_GROUP.items()):
        group_code = 1 if group == "CCD" else -1
        for task in TASKS:
            path = dcm_file(data_root, subject, task, model)
            rows.append(
                {
                    "Subject": subject,
                    "Group": group,
                    "GroupCode": group_code,
                    "Task": task,
                    "Model": model,
                    "DCMFile": str(path),
                    "Exists": path.exists(),
                }
            )
    return pd.DataFrame(rows)


def matlab_cellstr(items: list[str]) -> str:
    quoted = [f"'{item.replace(chr(39), chr(39) + chr(39))}'" for item in items]
    return "{" + "; ".join(quoted) + "}"


def matlab_rowvec(values: list[int | float]) -> str:
    return "[" + " ".join(str(value) for value in values) + "]"


def generate_matlab_script(
        df: pd.DataFrame,
        peb_dir: Path,
        model: str,
        spm_path: Path | None,
        fields: list[str],
) -> str:
    spm_setup = ""
    if spm_path is not None:
        spm_setup = f"addpath(genpath('{str(spm_path).replace(chr(39), chr(39) + chr(39))}'));"
    lines = [
        "% Auto-generated PEB script for MIPLAB DCM group analysis",
        "% PEB question: which DCM parameters differ between CCD and TDC?",
        "% Group coding: TDC = -1, CCD = +1, so column 2 is CCD minus TDC.",
        "",
        "clear; clc;",
        spm_setup,
        "spm('Defaults','fMRI');",
        "spm_jobman('initcfg');",
        "",
        f"model_name = '{model}';",
        f"tasks = {matlab_cellstr(list(TASKS))};",
        f"peb_fields = {matlab_cellstr(fields)};",
        f"out_dir = '{str(peb_dir.resolve()).replace(chr(39), chr(39) + chr(39))}';",
        "if ~exist(out_dir, 'dir'), mkdir(out_dir); end",
        "",
    ]

    for task in TASKS:
        task_df = df[(df["Task"] == task) & (df["Exists"])].copy()
        subjects = task_df["Subject"].tolist()
        groups = task_df["Group"].tolist()
        group_code = task_df["GroupCode"].tolist()
        files = task_df["DCMFile"].tolist()

        lines.extend(
            [
                "% -------------------------------------------------------------------------",
                f"% Task: {task}",
                "% -------------------------------------------------------------------------",
                f"subjects_{task} = {matlab_cellstr(subjects)};",
                f"groups_{task} = {matlab_cellstr(groups)};",
                f"group_code_{task} = {matlab_rowvec(group_code)}';",
                f"dcm_files_{task} = {matlab_cellstr(files)};",
                f"GCM_{task} = cell(numel(dcm_files_{task}), 1);",
                f"for i = 1:numel(dcm_files_{task})",
                f"    S = load(dcm_files_{task}{{i}});",
                "    if isfield(S, 'DCM_est')",
                "        DCM = S.DCM_est;",
                "    elseif isfield(S, 'DCM')",
                "        DCM = S.DCM;",
                "    else",
                f"        error('No DCM_est or DCM variable found in %s', dcm_files_{task}{{i}});",
                "    end",
                f"    GCM_{task}{{i}} = DCM;",
                "end",
                "",
                f"M_{task} = struct();",
                f"M_{task}.X = [ones(numel(group_code_{task}), 1), group_code_{task}];",
                f"M_{task}.Xnames = {{'Mean', 'CCD_minus_TDC'}};",
                f"M_{task}.Q = 'all';",
                "",
                f"[PEB_{task}, DCM_{task}] = spm_dcm_peb(GCM_{task}, M_{task}, peb_fields);",
                f"BMA_{task} = spm_dcm_peb_bmc(PEB_{task});",
                f"save(fullfile(out_dir, 'PEB_{task}_{model}.mat'), 'PEB_{task}', 'BMA_{task}', 'DCM_{task}', 'M_{task}', 'subjects_{task}', 'groups_{task}', 'dcm_files_{task}', 'model_name', 'peb_fields');",
                f"fprintf('Saved PEB results for {task}: %s\\n', fullfile(out_dir, 'PEB_{task}_{model}.mat'));",
                "",
            ]
        )

    lines.append("fprintf('\\nPEB group analysis complete. Results saved in: %s\\n', out_dir);")
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    data_root = resolve_data_root(args.data_root)
    out_dir = (PROJECT_ROOT / args.out_dir).resolve() if not args.out_dir.is_absolute() else args.out_dir.resolve()

    # Création dynamique du sous-dossier PEB_results
    peb_results_dir = out_dir / "PEB_results"

    inputs = collect_inputs(data_root, args.model)

    # On s'assure que out_dir et le sous-dossier PEB_results existent physiquement
    out_dir.mkdir(parents=True, exist_ok=True)
    peb_results_dir.mkdir(parents=True, exist_ok=True)

    inputs.to_csv(out_dir / f"peb_inputs_{args.model}.csv", index=False)

    # --- FILTRE DES MANQUANTS ---
    missing = [Path(path) for path in inputs.loc[~inputs["Exists"], "DCMFile"]]
    if missing:
        print(f"⚠️ Information : {len(missing)} fichiers DCM manquants (tâches non calculées pour ces sujets) :")
        for path in missing:
            print(f"  - {path.parent.name}/{path.name}")
        print("  -> Ces tâches spécifiques seront ignorées par SPM pour ces sujets lors du PEB.\n")

    n_subjects = inputs["Subject"].nunique()
    n_files_found = inputs["Exists"].sum()
    print(f"Sujets identifiés : {n_subjects} | Fichiers DCM valides trouvés : {n_files_found} / {len(inputs)}.")

    spm = None if args.verify_only else resolve_spm(args.spm_path)
    matlab_script = out_dir / f"run_peb_{args.model}.m"

    # On passe peb_results_dir pour la génération du script MATLAB
    matlab_script.write_text(
        generate_matlab_script(inputs, peb_results_dir, args.model, spm, list(args.fields)),
        encoding="utf-8",
    )

    if args.verify_only:
        print(f"PEB input table: {out_dir / f'peb_inputs_{args.model}.csv'}")
        print(f"MATLAB PEB script: {matlab_script}")
        print("Verification complete. MATLAB was not launched.")
        return

    matlab = resolve_matlab(args.matlab_cmd)
    print(f"MATLAB: {matlab}")
    print(f"SPM:    {spm}")
    print(f"MATLAB PEB script: {matlab_script}")
    print("Launching full-cohort PEB from Python...")
    cmd = [str(matlab), "-batch", f"run('{matlab_script.resolve()}')"]

    subprocess.run(cmd, check=True, cwd=PROJECT_ROOT)

    print("\nFull-cohort PEB complete.")
    print(f"Results saved in: {peb_results_dir}")


if __name__ == "__main__":
    main()