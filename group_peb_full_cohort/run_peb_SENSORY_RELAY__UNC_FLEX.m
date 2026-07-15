% Auto-generated PEB script for MIPLAB DCM group analysis
% PEB question: which DCM parameters differ between CCD and TDC?
% Group coding: TDC = -1, CCD = +1, so column 2 is CCD minus TDC.

clear; clc;
addpath(genpath('/Users/alex/Documents/MATLAB/spm'));
spm('Defaults','fMRI');
spm_jobman('initcfg');

model_name = 'SENSORY_RELAY__UNC_FLEX';
tasks = {'MDOD'; 'MDOG'; 'MGOD'; 'MGOG'};
peb_fields = {'A'; 'B'};
out_dir = '/Users/alex/university/Neuroscience_Master/short-term internship/group_peb_full_cohort/PEB_results';
if ~exist(out_dir, 'dir'), mkdir(out_dir); end

% -------------------------------------------------------------------------
% Task: MDOD
% -------------------------------------------------------------------------
subjects_MDOD = {'sub-03'; 'sub-04'; 'sub-06'; 'sub-07'; 'sub-08'; 'sub-13'; 'sub-14'; 'sub-19'; 'sub-26'; 'sub-31'; 'sub-34'; 'sub-41'; 'sub-42'; 'sub-43'; 'sub-51'; 'sub-52'; 'sub-54'; 'sub-55'; 'sub-56'; 'sub-58'; 'sub-64'};
groups_MDOD = {'TDC'; 'CCD'; 'CCD'; 'CCD'; 'TDC'; 'TDC'; 'TDC'; 'TDC'; 'TDC'; 'CCD'; 'TDC'; 'TDC'; 'TDC'; 'TDC'; 'TDC'; 'CCD'; 'TDC'; 'TDC'; 'TDC'; 'TDC'; 'CCD'};
group_code_MDOD = [-1 1 1 1 -1 -1 -1 -1 -1 1 -1 -1 -1 -1 -1 1 -1 -1 -1 -1 1]';
dcm_files_MDOD = {'/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-03/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MDOD/DCM_sub-03_MDOD_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-04/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MDOD/DCM_sub-04_MDOD_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-06/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MDOD/DCM_sub-06_MDOD_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-07/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MDOD/DCM_sub-07_MDOD_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-08/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MDOD/DCM_sub-08_MDOD_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-13/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MDOD/DCM_sub-13_MDOD_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-14/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MDOD/DCM_sub-14_MDOD_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-19/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MDOD/DCM_sub-19_MDOD_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-26/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MDOD/DCM_sub-26_MDOD_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-31/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MDOD/DCM_sub-31_MDOD_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-34/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MDOD/DCM_sub-34_MDOD_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-41/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MDOD/DCM_sub-41_MDOD_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-42/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MDOD/DCM_sub-42_MDOD_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-43/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MDOD/DCM_sub-43_MDOD_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-51/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MDOD/DCM_sub-51_MDOD_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-52/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MDOD/DCM_sub-52_MDOD_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-54/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MDOD/DCM_sub-54_MDOD_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-55/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MDOD/DCM_sub-55_MDOD_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-56/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MDOD/DCM_sub-56_MDOD_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-58/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MDOD/DCM_sub-58_MDOD_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-64/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MDOD/DCM_sub-64_MDOD_SENSORY_RELAY__UNC_FLEX.mat'};
GCM_MDOD = cell(numel(dcm_files_MDOD), 1);
for i = 1:numel(dcm_files_MDOD)
    S = load(dcm_files_MDOD{i});
    if isfield(S, 'DCM_est')
        DCM = S.DCM_est;
    elseif isfield(S, 'DCM')
        DCM = S.DCM;
    else
        error('No DCM_est or DCM variable found in %s', dcm_files_MDOD{i});
    end
    GCM_MDOD{i} = DCM;
end

M_MDOD = struct();
M_MDOD.X = [ones(numel(group_code_MDOD), 1), group_code_MDOD];
M_MDOD.Xnames = {'Mean', 'CCD_minus_TDC'};
M_MDOD.Q = 'all';

[PEB_MDOD, DCM_MDOD] = spm_dcm_peb(GCM_MDOD, M_MDOD, peb_fields);
BMA_MDOD = spm_dcm_peb_bmc(PEB_MDOD);
save(fullfile(out_dir, 'PEB_MDOD_SENSORY_RELAY__UNC_FLEX.mat'), 'PEB_MDOD', 'BMA_MDOD', 'DCM_MDOD', 'M_MDOD', 'subjects_MDOD', 'groups_MDOD', 'dcm_files_MDOD', 'model_name', 'peb_fields');
fprintf('Saved PEB results for MDOD: %s\n', fullfile(out_dir, 'PEB_MDOD_SENSORY_RELAY__UNC_FLEX.mat'));

% -------------------------------------------------------------------------
% Task: MDOG
% -------------------------------------------------------------------------
subjects_MDOG = {'sub-03'; 'sub-04'; 'sub-06'; 'sub-07'; 'sub-08'; 'sub-13'; 'sub-14'; 'sub-19'; 'sub-20'; 'sub-26'; 'sub-31'; 'sub-32'; 'sub-34'; 'sub-41'; 'sub-42'; 'sub-43'; 'sub-51'; 'sub-52'; 'sub-54'; 'sub-55'; 'sub-56'; 'sub-63'; 'sub-64'};
groups_MDOG = {'TDC'; 'CCD'; 'CCD'; 'CCD'; 'TDC'; 'TDC'; 'TDC'; 'TDC'; 'TDC'; 'TDC'; 'CCD'; 'CCD'; 'TDC'; 'TDC'; 'TDC'; 'TDC'; 'TDC'; 'CCD'; 'TDC'; 'TDC'; 'TDC'; 'CCD'; 'CCD'};
group_code_MDOG = [-1 1 1 1 -1 -1 -1 -1 -1 -1 1 1 -1 -1 -1 -1 -1 1 -1 -1 -1 1 1]';
dcm_files_MDOG = {'/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-03/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MDOG/DCM_sub-03_MDOG_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-04/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MDOG/DCM_sub-04_MDOG_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-06/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MDOG/DCM_sub-06_MDOG_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-07/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MDOG/DCM_sub-07_MDOG_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-08/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MDOG/DCM_sub-08_MDOG_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-13/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MDOG/DCM_sub-13_MDOG_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-14/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MDOG/DCM_sub-14_MDOG_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-19/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MDOG/DCM_sub-19_MDOG_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-20/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MDOG/DCM_sub-20_MDOG_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-26/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MDOG/DCM_sub-26_MDOG_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-31/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MDOG/DCM_sub-31_MDOG_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-32/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MDOG/DCM_sub-32_MDOG_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-34/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MDOG/DCM_sub-34_MDOG_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-41/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MDOG/DCM_sub-41_MDOG_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-42/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MDOG/DCM_sub-42_MDOG_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-43/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MDOG/DCM_sub-43_MDOG_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-51/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MDOG/DCM_sub-51_MDOG_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-52/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MDOG/DCM_sub-52_MDOG_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-54/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MDOG/DCM_sub-54_MDOG_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-55/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MDOG/DCM_sub-55_MDOG_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-56/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MDOG/DCM_sub-56_MDOG_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-63/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MDOG/DCM_sub-63_MDOG_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-64/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MDOG/DCM_sub-64_MDOG_SENSORY_RELAY__UNC_FLEX.mat'};
GCM_MDOG = cell(numel(dcm_files_MDOG), 1);
for i = 1:numel(dcm_files_MDOG)
    S = load(dcm_files_MDOG{i});
    if isfield(S, 'DCM_est')
        DCM = S.DCM_est;
    elseif isfield(S, 'DCM')
        DCM = S.DCM;
    else
        error('No DCM_est or DCM variable found in %s', dcm_files_MDOG{i});
    end
    GCM_MDOG{i} = DCM;
end

M_MDOG = struct();
M_MDOG.X = [ones(numel(group_code_MDOG), 1), group_code_MDOG];
M_MDOG.Xnames = {'Mean', 'CCD_minus_TDC'};
M_MDOG.Q = 'all';

[PEB_MDOG, DCM_MDOG] = spm_dcm_peb(GCM_MDOG, M_MDOG, peb_fields);
BMA_MDOG = spm_dcm_peb_bmc(PEB_MDOG);
save(fullfile(out_dir, 'PEB_MDOG_SENSORY_RELAY__UNC_FLEX.mat'), 'PEB_MDOG', 'BMA_MDOG', 'DCM_MDOG', 'M_MDOG', 'subjects_MDOG', 'groups_MDOG', 'dcm_files_MDOG', 'model_name', 'peb_fields');
fprintf('Saved PEB results for MDOG: %s\n', fullfile(out_dir, 'PEB_MDOG_SENSORY_RELAY__UNC_FLEX.mat'));

% -------------------------------------------------------------------------
% Task: MGOD
% -------------------------------------------------------------------------
subjects_MGOD = {'sub-04'; 'sub-06'; 'sub-07'; 'sub-08'; 'sub-13'; 'sub-14'; 'sub-19'; 'sub-20'; 'sub-26'; 'sub-31'; 'sub-32'; 'sub-34'; 'sub-41'; 'sub-42'; 'sub-43'; 'sub-45'; 'sub-51'; 'sub-54'; 'sub-55'; 'sub-56'; 'sub-58'; 'sub-63'; 'sub-64'};
groups_MGOD = {'CCD'; 'CCD'; 'CCD'; 'TDC'; 'TDC'; 'TDC'; 'TDC'; 'TDC'; 'TDC'; 'CCD'; 'CCD'; 'TDC'; 'TDC'; 'TDC'; 'TDC'; 'TDC'; 'TDC'; 'TDC'; 'TDC'; 'TDC'; 'TDC'; 'CCD'; 'CCD'};
group_code_MGOD = [1 1 1 -1 -1 -1 -1 -1 -1 1 1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 1 1]';
dcm_files_MGOD = {'/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-04/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MGOD/DCM_sub-04_MGOD_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-06/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MGOD/DCM_sub-06_MGOD_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-07/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MGOD/DCM_sub-07_MGOD_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-08/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MGOD/DCM_sub-08_MGOD_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-13/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MGOD/DCM_sub-13_MGOD_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-14/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MGOD/DCM_sub-14_MGOD_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-19/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MGOD/DCM_sub-19_MGOD_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-20/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MGOD/DCM_sub-20_MGOD_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-26/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MGOD/DCM_sub-26_MGOD_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-31/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MGOD/DCM_sub-31_MGOD_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-32/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MGOD/DCM_sub-32_MGOD_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-34/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MGOD/DCM_sub-34_MGOD_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-41/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MGOD/DCM_sub-41_MGOD_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-42/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MGOD/DCM_sub-42_MGOD_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-43/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MGOD/DCM_sub-43_MGOD_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-45/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MGOD/DCM_sub-45_MGOD_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-51/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MGOD/DCM_sub-51_MGOD_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-54/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MGOD/DCM_sub-54_MGOD_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-55/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MGOD/DCM_sub-55_MGOD_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-56/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MGOD/DCM_sub-56_MGOD_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-58/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MGOD/DCM_sub-58_MGOD_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-63/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MGOD/DCM_sub-63_MGOD_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-64/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MGOD/DCM_sub-64_MGOD_SENSORY_RELAY__UNC_FLEX.mat'};
GCM_MGOD = cell(numel(dcm_files_MGOD), 1);
for i = 1:numel(dcm_files_MGOD)
    S = load(dcm_files_MGOD{i});
    if isfield(S, 'DCM_est')
        DCM = S.DCM_est;
    elseif isfield(S, 'DCM')
        DCM = S.DCM;
    else
        error('No DCM_est or DCM variable found in %s', dcm_files_MGOD{i});
    end
    GCM_MGOD{i} = DCM;
end

M_MGOD = struct();
M_MGOD.X = [ones(numel(group_code_MGOD), 1), group_code_MGOD];
M_MGOD.Xnames = {'Mean', 'CCD_minus_TDC'};
M_MGOD.Q = 'all';

[PEB_MGOD, DCM_MGOD] = spm_dcm_peb(GCM_MGOD, M_MGOD, peb_fields);
BMA_MGOD = spm_dcm_peb_bmc(PEB_MGOD);
save(fullfile(out_dir, 'PEB_MGOD_SENSORY_RELAY__UNC_FLEX.mat'), 'PEB_MGOD', 'BMA_MGOD', 'DCM_MGOD', 'M_MGOD', 'subjects_MGOD', 'groups_MGOD', 'dcm_files_MGOD', 'model_name', 'peb_fields');
fprintf('Saved PEB results for MGOD: %s\n', fullfile(out_dir, 'PEB_MGOD_SENSORY_RELAY__UNC_FLEX.mat'));

% -------------------------------------------------------------------------
% Task: MGOG
% -------------------------------------------------------------------------
subjects_MGOG = {'sub-03'; 'sub-04'; 'sub-07'; 'sub-08'; 'sub-13'; 'sub-14'; 'sub-19'; 'sub-20'; 'sub-31'; 'sub-32'; 'sub-34'; 'sub-41'; 'sub-42'; 'sub-43'; 'sub-51'; 'sub-52'; 'sub-54'; 'sub-55'; 'sub-56'; 'sub-58'; 'sub-63'; 'sub-64'};
groups_MGOG = {'TDC'; 'CCD'; 'CCD'; 'TDC'; 'TDC'; 'TDC'; 'TDC'; 'TDC'; 'CCD'; 'CCD'; 'TDC'; 'TDC'; 'TDC'; 'TDC'; 'TDC'; 'CCD'; 'TDC'; 'TDC'; 'TDC'; 'TDC'; 'CCD'; 'CCD'};
group_code_MGOG = [-1 1 1 -1 -1 -1 -1 -1 1 1 -1 -1 -1 -1 -1 1 -1 -1 -1 -1 1 1]';
dcm_files_MGOG = {'/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-03/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MGOG/DCM_sub-03_MGOG_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-04/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MGOG/DCM_sub-04_MGOG_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-07/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MGOG/DCM_sub-07_MGOG_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-08/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MGOG/DCM_sub-08_MGOG_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-13/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MGOG/DCM_sub-13_MGOG_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-14/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MGOG/DCM_sub-14_MGOG_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-19/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MGOG/DCM_sub-19_MGOG_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-20/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MGOG/DCM_sub-20_MGOG_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-31/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MGOG/DCM_sub-31_MGOG_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-32/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MGOG/DCM_sub-32_MGOG_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-34/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MGOG/DCM_sub-34_MGOG_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-41/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MGOG/DCM_sub-41_MGOG_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-42/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MGOG/DCM_sub-42_MGOG_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-43/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MGOG/DCM_sub-43_MGOG_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-51/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MGOG/DCM_sub-51_MGOG_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-52/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MGOG/DCM_sub-52_MGOG_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-54/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MGOG/DCM_sub-54_MGOG_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-55/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MGOG/DCM_sub-55_MGOG_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-56/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MGOG/DCM_sub-56_MGOG_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-58/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MGOG/DCM_sub-58_MGOG_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-63/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MGOG/DCM_sub-63_MGOG_SENSORY_RELAY__UNC_FLEX.mat'; '/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/sub-64/func/dcm_results/spm_dcm_specs/pathway_models/SENSORY_RELAY__UNC_FLEX/MGOG/DCM_sub-64_MGOG_SENSORY_RELAY__UNC_FLEX.mat'};
GCM_MGOG = cell(numel(dcm_files_MGOG), 1);
for i = 1:numel(dcm_files_MGOG)
    S = load(dcm_files_MGOG{i});
    if isfield(S, 'DCM_est')
        DCM = S.DCM_est;
    elseif isfield(S, 'DCM')
        DCM = S.DCM;
    else
        error('No DCM_est or DCM variable found in %s', dcm_files_MGOG{i});
    end
    GCM_MGOG{i} = DCM;
end

M_MGOG = struct();
M_MGOG.X = [ones(numel(group_code_MGOG), 1), group_code_MGOG];
M_MGOG.Xnames = {'Mean', 'CCD_minus_TDC'};
M_MGOG.Q = 'all';

[PEB_MGOG, DCM_MGOG] = spm_dcm_peb(GCM_MGOG, M_MGOG, peb_fields);
BMA_MGOG = spm_dcm_peb_bmc(PEB_MGOG);
save(fullfile(out_dir, 'PEB_MGOG_SENSORY_RELAY__UNC_FLEX.mat'), 'PEB_MGOG', 'BMA_MGOG', 'DCM_MGOG', 'M_MGOG', 'subjects_MGOG', 'groups_MGOG', 'dcm_files_MGOG', 'model_name', 'peb_fields');
fprintf('Saved PEB results for MGOG: %s\n', fullfile(out_dir, 'PEB_MGOG_SENSORY_RELAY__UNC_FLEX.mat'));

fprintf('\nPEB group analysis complete. Results saved in: %s\n', out_dir);