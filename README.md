# I didn't code all this, this is a small rework of a huge project of another student, credit to Neila Benlamri


# DCM for children with callosal dysgenesis

This repository contains the analysis code used to run Dynamic Causal Modelling
(DCM) for a pediatric task-fMRI project comparing typically developing children
(TDC) and children with corpus callosum dysgenesis or agenesis (CCD).

The dataset used in this project comes from the **Translational Machine Learning
Lab** and the Swiss Pre- to Postnatal Neurodevelopmental Cohort. The data are
expected to be available locally in BIDS-derivatives style, for example:

```text
derivatives_MNIcohort3/
  mask/
      M1_L_sphere.nii.gz
      M1_R_sphere.nii.gz
      A1_L_sphere.nii.gz
      A1_R_sphere.nii.gz
      V1_L_sphere.nii.gz
      V1_R_sphere.nii.gz
  sub-XX/
    func/
      sub-XX_task-MDOD_..._bold.nii.gz
      sub-XX_task_MDOD.csv
      ...
  ...
        
```

Raw MRI data, preprocessed NIfTI files, subject-level DCM `.mat` files, and PEB
`.mat` files are intentionally not versioned in Git.

## Analysis overview

The full pipeline is:

```text
subject-level DCM estimation
  -> random-effects Bayesian model selection (RFX BMS)
  -> Parametric Empirical Bayes (PEB)
  -> result decoding and plotting
```

The subject-level model space contains eight candidate DCM architectures:

```text
4 crossed-transfer hypotheses x 2 uncrossed configurations = 8 models
```

Crossed-transfer hypotheses:

- `NULL`
- `RELAY`
- `DIRECT`
- `SENSORY_RELAY`

Uncrossed configurations:

- `INTRA_ONLY`
- `FLEX`

The full-cohort analysis used 26 subjects:

- CCD: `sub-04`, `sub-05`, `sub-06`, `sub-07`, `sub-31`, `sub-32`, `sub-55`, `sub-58`
- TDC: `sub-03`, `sub-08`, `sub-13`, `sub-14`, `sub-19`, `sub-20`, `sub-26`, `sub-33`, `sub-34`, `sub-41`, `sub-42`, `sub-43`, `sub-45`, `sub-51`, `sub-52`, `sub-54`, `sub-56`, `sub-63`

Group labels are stored in [`subject_group_mapping.json`](subject_group_mapping.json).

## Requirements

Python dependencies:

```bash
pip install -r requirements.txt
```

External software:

- MATLAB
- SPM12 on the MATLAB path
- Jupyter/nbconvert for executing `src/DCM.ipynb`

The scripts try to resolve the cohort path automatically across macOS and Linux:

- macOS: `/Volumes/T7 Shield/derivatives_MNIcohort3`
- Linux: `/media/lea/T7 Shield/derivatives_MNIcohort3`

You can always override the location with `--data-root`.

## 1. Run subject-level DCM

First check which subjects are ready:

```bash
python src/run_dcm_all_subjects.py --data-root "/Volumes/T7 Shield/derivatives_MNIcohort3" --dry-run
```

Run all ready subjects and execute the MATLAB/SPM cells inside the notebook:

```bash
python src/run_dcm_all_subjects.py --data-root "/Volumes/T7 Shield/derivatives_MNIcohort3" --run-matlab
```

Linux example:

```bash
cd "/media/lea/T7 Shield/PycharmProjects/MIPLAB" && python src/run_dcm_all_subjects.py --data-root "/media/lea/T7 Shield/derivatives_MNIcohort3" --run-matlab
```

The script executes a parameterized copy of [`src/DCM.ipynb`](src/DCM.ipynb) for each
subject and writes subject-level outputs under:

```text
sub-XX/func/dcm_results/sub-XX/
```

## 2. Run RFX BMS group comparison

After all subject-level `F_values.mat` files are present, run:

```bash
python src/dcm_multi_subject_comparison.py --data-root "/Volumes/T7 Shield/derivatives_MNIcohort3" --out-dir group_dcm_comparison
```

Linux example:

```bash
cd "/media/lea/T7 Shield/PycharmProjects/MIPLAB" && python src/dcm_multi_subject_comparison.py --data-root "/media/lea/T7 Shield/derivatives_MNIcohort3" --out-dir group_dcm_comparison
```

This creates model-level and family-level RFX BMS summaries in
[`group_dcm_comparison`](group_dcm_comparison).

Main full-cohort result:

- Winning model family: `SENSORY_RELAY__UNC_FLEX`
- Uncrossed family: `FLEX`
- All dominant subject-level winners belonged to the `UNC_FLEX` family.

## 3. Run full-cohort PEB

The Python wrapper verifies that all expected DCM files exist and launches the
MATLAB/SPM PEB script.

macOS example:

```bash
python src/run_full_cohort_peb.py --data-root "/Volumes/T7 Shield/derivatives_MNIcohort3" --out-dir group_peb_full_cohort --model SENSORY_RELAY__UNC_FLEX --matlab-cmd "/Applications/MATLAB_R2025b.app/bin/matlab" --spm-path "$HOME/spm12"
```

Linux example:

```bash
cd "/media/lea/T7 Shield/PycharmProjects/MIPLAB" && python src/run_full_cohort_peb.py --data-root "/media/lea/T7 Shield/derivatives_MNIcohort3" --out-dir group_peb_full_cohort --model SENSORY_RELAY__UNC_FLEX --matlab-cmd "/home/lea/MATLAB/R2025b/bin/matlab" --spm-path "/home/lea/MATLAB/spm"
```

To verify inputs without launching MATLAB:

```bash
python src/run_full_cohort_peb.py --data-root "/Volumes/T7 Shield/derivatives_MNIcohort3" --out-dir group_peb_full_cohort --model SENSORY_RELAY__UNC_FLEX --verify-only
```

## 4. Decode PEB results

Decode the MATLAB/SPM PEB outputs:

```bash
python src/analyze_peb_results_v2.py --peb-dir group_peb_full_cohort --model SENSORY_RELAY__UNC_FLEX --out-dir group_peb_full_cohort
```

## Reproduced full-cohort results

The current full-cohort outputs are stored as lightweight CSV/JSON/figure files:

- [`group_dcm_comparison`](group_dcm_comparison): RFX BMS model and family summaries
- [`group_peb_full_cohort`](group_peb_full_cohort): decoded PEB CSV summaries and figures
- [`figures`](figures): final report/presentation figures

PEB tested 152 `CCD_minus_TDC` parameters across the four tasks. In the current
full-cohort output, 27 parameters showed strong posterior evidence for a group
effect (`Pp >= 0.95`):

- 16 intrinsic `A` effects, all intra-hemispheric
- 11 task-modulated `B` effects
- intrinsic effects were mostly more positive in CCD, consistent with stronger
  modelled within-hemisphere coupling in the specified intrinsic pathways

## Key scripts

- [`src/DCM.ipynb`](src/DCM.ipynb): subject-level DCM pipeline
- [`src/run_dcm_all_subjects.py`](src/run_dcm_all_subjects.py): execute `src/DCM.ipynb` across subjects
- [`src/dcm_multi_subject_comparison.py`](src/dcm_multi_subject_comparison.py): RFX BMS and family comparison
- [`src/run_full_cohort_peb.py`](src/run_full_cohort_peb.py): launch PEB from Python
- [`src/analyze_peb_results_v2.py`](src/analyze_peb_results_v2.py): decode PEB outputs

## Notes

The repository is designed to reproduce the analysis once the user has access to
the local dataset and SPM12. The dataset itself should not be committed to Git.
