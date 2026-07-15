# PEB Analysis Instructions - Updated for 26 Subjects

## Summary of Updates

- **Subjects**: 26 total (CCD=8, TDC=18)
- **Tasks**: MDOD, MDOG, MGOD, MGOG (4 tasks per subject)
- **Model**: SENSORY_RELAY__UNC_FLEX
- **Total observations**: 26 × 4 = 104

### Subject Group Assignments (from demographic_data.pdf)

**CCD (N=8)**: sub-04, sub-05, sub-06, sub-07, sub-31, sub-32, sub-55, sub-58

**TDC (N=18)**: sub-03, sub-08, sub-13, sub-14, sub-19, sub-20, sub-26, sub-33, sub-34, sub-41, sub-42, sub-43, sub-45, sub-51, sub-52, sub-54, sub-56, sub-63

## Group Design Matrix

```
X = [ones(26,1) group_codes]
```

Where:
- Column 1: Grand mean (intercept)
- Column 2: Group contrast (CCD=+1, TDC=-1, centered)

This allows testing of:
1. **Intercept**: Average DCM parameter value across all subjects
2. **Group effect**: DCM parameter differences between CCD and TDC children

## Files Generated

1. **Input data**: `group_peb_full_cohort/peb_inputs_SENSORY_RELAY__UNC_FLEX.csv`
   - 104 rows (all subjects × tasks)
   - All DCM files verified to exist

2. **MATLAB script**: `group_peb_full_cohort/run_peb_SENSORY_RELAY__UNC_FLEX.m`
   - Runs PEB for each of the 4 tasks
   - Tests group differences in A and B parameters

## How to Run PEB

### Option 1: From Python

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

## Expected Outputs

After PEB completes, you should see:
- `PEB_*.mat` files for each task-model combination
- Summary statistics of group effects
- Parameter estimates comparing CCD vs TDC

## Notes

- All 26 subjects have verified DCM files
- Group coding is centered (TDC=-1, CCD=+1) for interpretable intercepts
- PEB tests both A (connectivity) and B (modulatory) parameters
