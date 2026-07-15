#!/usr/bin/env python3
"""Multi-subject DCM model comparison for MIPLAB cohort 3.

This script aggregates the first-level DCM model evidence files produced by
DCM.ipynb and performs group-level Bayesian model selection (BMS). It is
designed for the current 8-model space:

    crossed pathway: NULL, RELAY, DIRECT, SENSORY_RELAY
    uncrossed policy: INTRA_ONLY, FLEX

The group comparison follows the logic used in DCM group analyses: compare
model evidence at the subject level, and summarize families of models when the
scientific question is about a shared feature rather than one exact model.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.io import loadmat
from scipy.special import digamma, logsumexp, softmax


TASKS = ("MDOD", "MDOG", "MGOD", "MGOG")
CROSSED_PATHWAYS = ("NULL", "RELAY", "DIRECT", "SENSORY_RELAY")
UNCROSSED_POLICIES = ("INTRA_ONLY", "FLEX")
DEFAULT_MODEL_LABELS = tuple(
    f"{pathway}__UNC_{policy}"
    for pathway in CROSSED_PATHWAYS
    for policy in UNCROSSED_POLICIES
)


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
class DCMRecord:
    subject: str
    task: str
    labels: tuple[str, ...]
    log_evidence: np.ndarray
    source: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Group-level Bayesian model comparison for DCM cohort results."
    )
    parser.add_argument(
        "--data-root",
        type=Path,
        default=Path("/Volumes/T7 Shield/derivatives_MNIcohort3"),
        help="Root containing sub-*/func/dcm_results/sub-* directories.",
    )
    parser.add_argument(
        "--subjects",
        nargs="*",
        default=None,
        help="Subjects to include, e.g. sub-03 sub-04 sub-32 sub-33 sub-41. "
        "If omitted, all subjects with DCM results are included.",
    )
    parser.add_argument(
        "--tasks",
        nargs="*",
        default=list(TASKS),
        help="Tasks to include. Default: MDOD MDOG MGOD MGOG.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Output directory. Default: ./group_dcm_comparison.",
    )
    parser.add_argument(
        "--n-samples",
        type=int,
        default=100_000,
        help="Dirichlet samples used for exceedance probabilities.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=13,
        help="Random seed for exceedance probability sampling.",
    )
    return parser.parse_args()


def normalise_subject(subject: str) -> str:
    subject = str(subject)
    return subject if subject.startswith("sub-") else f"sub-{int(subject):02d}"


def decode_matlab_strings(value) -> tuple[str, ...] | None:
    arr = np.asarray(value).squeeze()
    if arr.size == 0:
        return None
    labels = []
    for item in arr.flat:
        if isinstance(item, str):
            labels.append(item)
        elif isinstance(item, np.ndarray):
            labels.append("".join(str(x) for x in item.squeeze().flat))
        else:
            labels.append(str(item))
    return tuple(label.strip() for label in labels if label.strip())


def bms_file_for(data_root: Path, subject: str, task: str) -> Path:
    return (
        data_root
        / subject
        / "func"
        / "dcm_results"
        / "spm_dcm_specs"
        / "pathway_models"
        / task
        / "BMS_unique"
        / "F_values.mat"
    )


def summary_file_for(data_root: Path, subject: str) -> Path:
    return (
        data_root
        / subject
        / "func"
        / "dcm_results"
        / "bms_8model_summary.csv"
    )


def discover_subjects(data_root: Path) -> list[str]:
    return sorted(
        p.name
        for p in data_root.glob("sub-*")
        if p.is_dir() and summary_file_for(data_root, p.name).exists()
    )


def load_record(data_root: Path, subject: str, task: str) -> DCMRecord | None:
    f_file = bms_file_for(data_root, subject, task)
    if not f_file.exists():
        return None

    mat = loadmat(str(f_file))
    if "F_values" not in mat:
        raise KeyError(f"{f_file} does not contain F_values")

    log_evidence = np.asarray(mat["F_values"], dtype=float).flatten()
    labels = decode_matlab_strings(mat.get("models")) or DEFAULT_MODEL_LABELS

    if len(labels) != len(log_evidence):
        raise ValueError(
            f"{f_file} has {len(log_evidence)} F values but {len(labels)} labels"
        )

    return DCMRecord(
        subject=subject,
        task=task,
        labels=tuple(labels),
        log_evidence=log_evidence,
        source=f_file,
    )


def collect_records(
    data_root: Path, subjects: list[str] | None, tasks: list[str]
) -> tuple[list[DCMRecord], list[dict]]:
    if subjects is None:
        subjects = discover_subjects(data_root)
    else:
        subjects = [normalise_subject(s) for s in subjects]

    records: list[DCMRecord] = []
    missing: list[dict] = []

    for subject in subjects:
        if not (data_root / subject).exists():
            missing.append({"Subject": subject, "Task": "ALL", "Reason": "missing subject directory"})
            continue

        for task in tasks:
            record = load_record(data_root, subject, task)
            if record is None:
                missing.append({"Subject": subject, "Task": task, "Reason": "missing F_values.mat"})
                continue
            records.append(record)

    return records, missing


def align_log_evidence(records: list[DCMRecord]) -> tuple[np.ndarray, list[str], pd.DataFrame]:
    labels = list(records[0].labels)
    rows = []
    meta = []

    for record in records:
        if set(record.labels) != set(labels):
            raise ValueError(f"Model labels differ in {record.source}")
        order = [record.labels.index(label) for label in labels]
        rows.append(record.log_evidence[order])
        meta.append({"Subject": record.subject, "Task": record.task, "Source": str(record.source)})

    return np.vstack(rows), labels, pd.DataFrame(meta)


def rfx_bms(
    log_evidence: np.ndarray,
    alpha0: float = 1.0,
    tol: float = 1e-8,
    max_iter: int = 10_000,
) -> dict:
    """Variational random-effects BMS with a Dirichlet population model."""
    n_obs, n_models = log_evidence.shape
    prior = np.full(n_models, alpha0, dtype=float)
    alpha = prior.copy()

    for _ in range(max_iter):
        log_u = log_evidence + digamma(alpha) - digamma(np.sum(alpha))
        responsibilities = softmax(log_u, axis=1)
        next_alpha = prior + responsibilities.sum(axis=0)
        if np.max(np.abs(next_alpha - alpha)) < tol:
            alpha = next_alpha
            break
        alpha = next_alpha

    return {
        "alpha": alpha,
        "expected_frequency": alpha / np.sum(alpha),
        "responsibilities": responsibilities,
        "n_observations": n_obs,
    }


def exceedance_probability(alpha: np.ndarray, n_samples: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    samples = rng.dirichlet(alpha, size=n_samples)
    winners = np.argmax(samples, axis=1)
    return np.bincount(winners, minlength=len(alpha)) / n_samples


def family_labels(model_labels: list[str], family: str) -> list[str]:
    out = []
    for label in model_labels:
        crossed, policy = label.split("__UNC_")
        if family == "crossed_pathway":
            out.append(crossed)
        elif family == "uncrossed_policy":
            out.append(policy)
        else:
            raise ValueError(f"Unknown family: {family}")
    return out


def family_log_evidence(log_evidence: np.ndarray, model_labels: list[str], family: str):
    labels = family_labels(model_labels, family)
    unique = list(dict.fromkeys(labels))
    out = np.zeros((log_evidence.shape[0], len(unique)))

    for j, name in enumerate(unique):
        cols = [i for i, label in enumerate(labels) if label == name]
        out[:, j] = logsumexp(log_evidence[:, cols], axis=1)

    return out, unique


def bms_table(
    labels: list[str],
    bms: dict,
    xp: np.ndarray,
    ffx_posterior: np.ndarray | None = None,
) -> pd.DataFrame:
    rows = []
    for i, label in enumerate(labels):
        row = {
            "Label": label,
            "RFX_ExpectedFrequency": bms["expected_frequency"][i],
            "RFX_ExceedanceProbability": xp[i],
            "DirichletAlpha": bms["alpha"][i],
        }
        if ffx_posterior is not None:
            row["FFX_Posterior"] = ffx_posterior[i]
        rows.append(row)
    return pd.DataFrame(rows).sort_values("RFX_ExceedanceProbability", ascending=False)


def model_posterior_rows(records: list[DCMRecord]) -> pd.DataFrame:
    rows = []
    for record in records:
        post = softmax(record.log_evidence)
        winner_idx = int(np.argmax(post))
        row = {
            "Subject": record.subject,
            "Task": record.task,
            "Winner": record.labels[winner_idx],
            "WinnerPosterior": float(post[winner_idx]),
        }
        row.update({label: float(value) for label, value in zip(record.labels, post)})
        rows.append(row)
    return pd.DataFrame(rows)


def save_barplot(df: pd.DataFrame, title: str, value_col: str, path: Path) -> None:
    plot_df = df.sort_values(value_col, ascending=True)
    fig, ax = plt.subplots(figsize=(10, max(4, 0.45 * len(plot_df))))
    colors = ["#d95f02" if i == len(plot_df) - 1 else "#2e86ab" for i in range(len(plot_df))]
    ax.barh(plot_df["Label"], plot_df[value_col] * 100, color=colors, edgecolor="black", alpha=0.88)
    ax.set_xlabel(value_col.replace("_", " ") + " (%)")
    ax.set_title(title)
    ax.grid(axis="x", alpha=0.25)
    ax.set_xlim(0, 100)
    plt.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def save_heatmap(posterior_df: pd.DataFrame, model_labels: list[str], path: Path) -> None:
    labels = posterior_df["Subject"] + " " + posterior_df["Task"]
    matrix = posterior_df[model_labels].to_numpy(dtype=float) * 100

    fig, ax = plt.subplots(figsize=(12, max(5, 0.35 * len(posterior_df))))
    image = ax.imshow(matrix, aspect="auto", cmap="viridis", vmin=0, vmax=100)
    ax.set_xticks(range(len(model_labels)))
    ax.set_xticklabels(model_labels, rotation=35, ha="right")
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels)
    ax.set_title("Subject-task model posterior probabilities")

    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            value = matrix[i, j]
            if value >= 1:
                ax.text(j, i, f"{value:.0f}", ha="center", va="center", fontsize=7, color="white" if value < 55 else "black")

    fig.colorbar(image, ax=ax, label="Posterior (%)")
    plt.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def run() -> None:
    args = parse_args()
    data_root = resolve_data_root(args.data_root)
    out_dir = args.out_dir or Path.cwd() / "group_dcm_comparison"
    out_dir.mkdir(parents=True, exist_ok=True)

    records, missing = collect_records(data_root, args.subjects, args.tasks)
    if not records:
        raise RuntimeError(f"No DCM F_values.mat files found under {data_root}")

    log_evidence, model_labels, meta_df = align_log_evidence(records)
    posterior_df = model_posterior_rows(records)

    ffx_posterior = softmax(np.sum(log_evidence, axis=0))
    model_bms = rfx_bms(log_evidence)
    model_xp = exceedance_probability(model_bms["alpha"], args.n_samples, args.seed)
    model_df = bms_table(model_labels, model_bms, model_xp, ffx_posterior)

    outputs = {
        "data_root": str(data_root),
        "out_dir": str(out_dir),
        "n_records": len(records),
        "n_subjects": posterior_df["Subject"].nunique(),
        "subjects": sorted(posterior_df["Subject"].unique().tolist()),
        "tasks": sorted(posterior_df["Task"].unique().tolist()),
    }

    posterior_df.to_csv(out_dir / "subject_task_model_posteriors.csv", index=False)
    meta_df.to_csv(out_dir / "included_f_values_files.csv", index=False)
    model_df.to_csv(out_dir / "group_bms_models.csv", index=False)

    if missing:
        pd.DataFrame(missing).to_csv(out_dir / "missing_subject_task_results.csv", index=False)

    family_outputs = {}
    for family in ("crossed_pathway", "uncrossed_policy"):
        fam_lme, fam_labels = family_log_evidence(log_evidence, model_labels, family)
        fam_bms = rfx_bms(fam_lme)
        fam_xp = exceedance_probability(fam_bms["alpha"], args.n_samples, args.seed + len(family))
        fam_ffx = softmax(np.sum(fam_lme, axis=0))
        fam_df = bms_table(fam_labels, fam_bms, fam_xp, fam_ffx)
        fam_df.to_csv(out_dir / f"group_bms_family_{family}.csv", index=False)
        family_outputs[family] = fam_df.iloc[0].to_dict()
        save_barplot(
            fam_df,
            title=f"Group RFX BMS by {family.replace('_', ' ')}",
            value_col="RFX_ExceedanceProbability",
            path=out_dir / f"group_bms_family_{family}.png",
        )

    save_barplot(
        model_df,
        title="Group RFX BMS: 8 DCM models",
        value_col="RFX_ExceedanceProbability",
        path=out_dir / "group_bms_models.png",
    )
    save_heatmap(posterior_df, model_labels, out_dir / "subject_task_model_posteriors.png")

    outputs["model_winner"] = model_df.iloc[0].to_dict()
    outputs["family_winners"] = family_outputs
    outputs["missing"] = missing

    with open(out_dir / "group_dcm_comparison_summary.json", "w", encoding="utf-8") as f:
        json.dump(outputs, f, indent=2)

    print("\nGroup DCM comparison complete")
    print(f"Included records : {len(records)}")
    print(f"Included subjects: {', '.join(outputs['subjects'])}")
    if missing:
        print(f"Missing results  : {len(missing)} entries (see missing_subject_task_results.csv)")
    print("\nModel-level RFX BMS")
    print(model_df[["Label", "RFX_ExpectedFrequency", "RFX_ExceedanceProbability", "FFX_Posterior"]].to_string(index=False))
    print("\nOutputs saved to:", out_dir)


if __name__ == "__main__":
    run()
