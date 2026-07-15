import os
import glob
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.ticker import MultipleLocator

PEB_RESULTS_DIR = "/Users/alex/university/Neuroscience_Master/short-term internship/group_peb_full_cohort/PEB_results"
BASE_PATH = "/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3"


SUBJECTS = {
    "sub-03": "TDC", "sub-04": "CCD", "sub-06": "CCD", "sub-07": "CCD", "sub-08": "TDC",
    "sub-13": "TDC", "sub-14": "TDC", "sub-19": "TDC", "sub-20": "TDC", "sub-26": "TDC",
    "sub-31": "CCD", "sub-32": "CCD", "sub-34": "TDC", "sub-41": "TDC", "sub-42": "TDC",
    "sub-43": "TDC", "sub-45": "TDC", "sub-51": "TDC", "sub-52": "CCD", "sub-54": "TDC",
    "sub-55": "TDC", "sub-56": "TDC", "sub-58": "TDC", "sub-63": "CCD", "sub-64": "CCD",
}

N_PARTICIPANTS = len(SUBJECTS)

REGIONS = {1: 'M1_L', 2: 'M1_R', 3: 'A1_L', 4: 'A1_R', 5: 'V1_L', 6: 'V1_R'}

CONDITIONS_B = {
    1: 'visual L, uncrossed',
    2: 'auditory L, uncrossed',
    3: 'visual R, uncrossed',
    4: 'auditory R, uncrossed',
    5: 'auditory R, crossed',
    6: 'visual L, crossed',
    7: 'auditory L, crossed',
    8: 'visual R, crossed'
}

TASKS = ['MDOD', 'MDOG', 'MGOD', 'MGOG']



def load_group_results():
    """Charge tous les fichiers CSV et extrait la tâche du nom de fichier."""
    files = glob.glob(os.path.join(PEB_RESULTS_DIR, 'resultats_comparaison_groupes_DCM_*.csv'))
    if not files:
        print(f"Warning: No group comparison CSVs found in {PEB_RESULTS_DIR}")
        return pd.DataFrame()

    dfs = []
    for f in files:
        filename = os.path.basename(f)

        task = "UNKNOWN"
        for t in ['MGOD', 'MDOG', 'MDOD', 'MGOG']:
            if t in filename:
                task = t
                break

        df = pd.read_csv(f)
        df_sig = df[df['Significatif_95'] == True].copy()
        df_sig['Task'] = task
        dfs.append(df_sig)
    return pd.concat(dfs, ignore_index=True)


def parse_connection_label(row):
    conn = row['Connexion']
    task = row['Task']

    # Matrice A (Intrisinc)
    match_a = re.match(r'A\((\d+),(\d+)\)', conn)
    if match_a:
        de, vers = int(match_a.group(2)), int(match_a.group(1))
        r_from, r_to = REGIONS.get(de, f'R{de}'), REGIONS.get(vers, f'R{vers}')
        if de == vers:
            return f"{task} | {r_from} → {r_to} | self-connection"
        return f"{task} | {r_from} → {r_to}"

    # Matrice B (Task-modulated)
    match_b = re.match(r'B\((\d+),(\d+),(\d+)\)', conn)
    if match_b:
        de, vers, cond_idx = int(match_b.group(2)), int(match_b.group(1)), int(match_b.group(3))
        r_from, r_to = REGIONS.get(de, f'R{de}'), REGIONS.get(vers, f'R{vers}')
        cond = CONDITIONS_B.get(cond_idx, f'condition {cond_idx}')
        return f"{task} | {r_from} → {r_to} | {cond}"

    return f"{task} | {conn}"


def is_intra_hemisphere(conn_str):
    indices = [int(n) for n in re.findall(r'\d+', conn_str)]
    if len(indices) < 2:
        return True

    gauche = {1, 3, 5}
    droite = {2, 4, 6}

    de_gauche = indices[1] in gauche
    vers_gauche = indices[0] in gauche
    de_droite = indices[1] in droite
    vers_droite = indices[0] in droite

    if (de_gauche and vers_gauche) or (de_droite and vers_droite):
        return True
    return False


def load_bms_summaries():
    records = []
    for sub, group in SUBJECTS.items():
        path = os.path.join(BASE_PATH, sub, "func", "dcm_results", "bms_8model_summary.csv")
        if not os.path.exists(path):
            print(f"Missing file for {sub}: {path}")
            continue
        try:
            df = pd.read_csv(path)
            for _, row in df.iterrows():
                record = {
                    'Subject': sub,
                    'Group': group,
                    'Task': row['Task'],
                    'Winner_Raw': row['Winner']
                }
                for col in df.columns:
                    if col not in ['Task', 'Winner', 'WinnerPosterior']:
                        record[col] = row[col]
                records.append(record)
        except Exception as e:
            print(f"Error parsing {sub}: {e}")
    return pd.DataFrame(records)


# GRAPHS

def plot_peb_connectivity(df, out_path):
    df_plot = df.copy()

    df_plot['Label_Graphique'] = df_plot.apply(parse_connection_label, axis=1)

    tasks_order = ['MGOG', 'MGOD', 'MDOG', 'MDOD']
    df_plot['Task'] = pd.Categorical(df_plot['Task'], categories=tasks_order, ordered=True)

    df_A = df_plot[df_plot['Connexion'].str.startswith('A')].sort_values(['Task', 'Difference_Groupe_Beta'],
                                                                         ascending=[False, True])
    df_B = df_plot[df_plot['Connexion'].str.startswith('B')].sort_values(['Task', 'Difference_Groupe_Beta'],
                                                                         ascending=[False, True])

    h_A = max(2, len(df_A) * 0.45)
    h_B = max(2, len(df_B) * 0.45)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, h_A + h_B + 4), gridspec_kw={'height_ratios': [h_A, h_B]})

    c_blue = '#2b7bba'
    c_orange = '#d35400'
    c_A = [c_orange if x > 0 else c_blue for x in df_A['Difference_Groupe_Beta']]
    c_B = [c_orange if x > 0 else c_blue for x in df_B['Difference_Groupe_Beta']]

    bars1 = ax1.barh(df_A['Label_Graphique'], df_A['Difference_Groupe_Beta'], color=c_A, edgecolor='#222222',
                     height=0.55, zorder=3)
    ax1.set_title("A. Intrinsic connectivity", loc='left', fontweight='bold', fontsize=13, pad=15)
    ax1.axvline(0, color='black', linewidth=1, zorder=4)

    for bar, pp in zip(bars1, df_A['Probabilite_Posterior_Pp']):
        w = bar.get_width()
        if w >= 0:
            ha = 'left'
            offset = 0.02 if w < 0.82 else -0.15
            color = 'black' if w < 0.82 else 'white'
        else:
            ha = 'right'
            offset = -0.02 if w > -0.82 else 0.15
            color = 'black' if w > -0.82 else 'white'

        ax1.text(w + offset, bar.get_y() + bar.get_height() / 2, f'Pp={pp:.2f}',
                 va='center', ha=ha, fontweight='bold', fontsize=9.5, color=color)

    bars2 = ax2.barh(df_B['Label_Graphique'], df_B['Difference_Groupe_Beta'], color=c_B, edgecolor='#222222',
                     height=0.55, zorder=3)
    ax2.set_title("B. Task-modulated connectivity", loc='left', fontweight='bold', fontsize=13, pad=15)
    ax2.axvline(0, color='black', linewidth=1, zorder=4)

    for bar, pp in zip(bars2, df_B['Probabilite_Posterior_Pp']):
        w = bar.get_width()
        if w >= 0:
            ha = 'left'
            offset = 0.02 if w < 0.82 else -0.15
            color = 'black' if w < 0.82 else 'white'
        else:
            ha = 'right'
            offset = -0.02 if w > -0.82 else 0.15
            color = 'black' if w > -0.82 else 'white'

        ax2.text(w + offset, bar.get_y() + bar.get_height() / 2, f'Pp={pp:.2f}',
                 va='center', ha=ha, fontweight='bold', fontsize=9.5, color=color)

    for ax in [ax1, ax2]:
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.grid(axis='x', linestyle='-', color='#e5e5e5', alpha=0.6, zorder=0)

        ax.set_xlim(-1.0, 1.0)
        ax.xaxis.set_major_locator(MultipleLocator(0.2))

        ax.tick_params(axis='y', which='both', length=0, labelsize=9.5)
        ax.tick_params(axis='x', labelsize=10)

    ax2.set_xlabel("PEB group-effect estimate (CCD minus TDC)", fontsize=11, labelpad=10)

    fig.text(0.30, 0.98, "Stronger / more positive in TDC", color=c_blue, fontweight='bold', fontsize=11, ha='left')
    fig.text(0.90, 0.98, "Stronger / more positive in CCD", color=c_orange, fontweight='bold', fontsize=11, ha='right')

    footnote = r"Only credible group effects (Pp $\geq$ 0.95). For self-connections, positive estimates indicate increased self-inhibition in CCD."
    fig.text(0.5, 0.01, footnote, ha='center', fontsize=9.5, fontstyle='italic', color='#333333')

    plt.tight_layout(rect=[0, 0.03, 1, 0.96])
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_connection_classes(df, out_path):
    df_class = df.copy()
    df_class['Class'] = df_class['Connexion'].apply(lambda x: 'Intra' if is_intra_hemisphere(x) else 'Inter')
    df_class['Matrice'] = df_class['Connexion'].apply(
        lambda x: 'Intrinsic A' if x.startswith('A') else 'Task-modulated B')
    df_class['Direction'] = df_class['Difference_Groupe_Beta'].apply(lambda x: 'CCD' if x > 0 else 'TDC')

    def get_counts(matrix_name):
        sub = df_class[df_class['Matrice'] == matrix_name]
        intra_ccd = len(sub[(sub['Class'] == 'Intra') & (sub['Direction'] == 'CCD')])
        intra_tdc = len(sub[(sub['Class'] == 'Intra') & (sub['Direction'] == 'TDC')])
        inter_ccd = len(sub[(sub['Class'] == 'Inter') & (sub['Direction'] == 'CCD')])
        inter_tdc = len(sub[(sub['Class'] == 'Inter') & (sub['Direction'] == 'TDC')])
        return np.array([intra_ccd, inter_ccd]), np.array([intra_tdc, inter_tdc])

    ccd_A, tdc_A = get_counts('Intrinsic A')
    ccd_B, tdc_B = get_counts('Task-modulated B')

    categories = ['Intra', 'Inter']
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 6.5), sharey=True)

    c_ccd, c_tdc = '#d35400', '#16a085'

    ax1.bar(categories, ccd_A, color=c_ccd, edgecolor='black', lw=0.6, width=0.5)
    ax1.bar(categories, tdc_A, bottom=ccd_A, color=c_tdc, edgecolor='black', lw=0.6, width=0.5)
    for i in range(2):
        if ccd_A[i] > 0:
            ax1.text(i, ccd_A[i] / 2, str(ccd_A[i]), ha='center', va='center', color='white', fontweight='bold',
                     fontsize=14)
        if tdc_A[i] > 0:
            ax1.text(i, ccd_A[i] + tdc_A[i] / 2, str(tdc_A[i]), ha='center', va='center', color='white',
                     fontweight='bold', fontsize=14)

    ax1.set_title('Intrinsic A', fontweight='bold', fontsize=16, pad=20)
    ax1.set_xlabel('Connection class', fontsize=13, labelpad=8)
    ax1.set_ylabel('Credible group effects (Pp $\geq$ 0.95)', fontsize=13, labelpad=10)

    ax2.bar(categories, ccd_B, color=c_ccd, edgecolor='black', lw=0.6, width=0.5)
    ax2.bar(categories, tdc_B, bottom=ccd_B, color=c_tdc, edgecolor='black', lw=0.6, width=0.5)
    for i in range(2):
        if ccd_B[i] > 0:
            ax2.text(i, ccd_B[i] / 2, str(ccd_B[i]), ha='center', va='center', color='white', fontweight='bold',
                     fontsize=14)
        if tdc_B[i] > 0:
            ax2.text(i, ccd_B[i] + tdc_B[i] / 2, str(tdc_B[i]), ha='center', va='center', color='white',
                     fontweight='bold', fontsize=14)

    ax2.set_title('Task-modulated B', fontweight='bold', fontsize=16, pad=20)
    ax2.set_xlabel('Connection class', fontsize=13, labelpad=8)

    for ax in [ax1, ax2]:
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='y', linestyle=':', alpha=0.4)
        ax.tick_params(labelsize=12)
        ax.yaxis.set_major_locator(MultipleLocator(2))

    fig.legend(['More positive in CCD', 'More positive in TDC'], loc='upper center', bbox_to_anchor=(0.5, 0.93), ncol=2,
               frameon=False, fontsize=12)
    fig.suptitle('Credible PEB group effects by connection class', fontweight='bold', fontsize=18, y=1.02)

    footnote = f"Full cohort: {N_PARTICIPANTS} participants. Self-connections are classified as intra-hemispheric; their sign reflects self-inhibition."
    fig.text(0.05, -0.05, footnote, fontsize=10, ha='left', fontstyle='italic')

    plt.tight_layout(rect=[0, 0, 1, 0.85])
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_subject_architectures(df, out_path):
    sub_data = []
    models = [c for c in df.columns if c not in ['Subject', 'Group', 'Task', 'Winner_Raw']]

    for sub in df['Subject'].unique():
        df_sub = df[df['Subject'] == sub]
        group = df_sub['Group'].iloc[0]

        mean_p = df_sub[models].mean()
        best_model = mean_p.idxmax()
        best_prob = mean_p.max() * 100

        label_short = 'SR' if 'SENSORY_RELAY' in best_model else 'Relay'
        label_full = 'SENSORY_RELAY / FLEX' if 'SENSORY_RELAY' in best_model else 'RELAY / FLEX'

        sub_data.append({
            'Subject': sub, 'Group': group, 'Label': f"{sub} {group}",
            'Winner': label_short, 'Winner_Full': label_full, 'Probability': best_prob
        })

    df_results = pd.DataFrame(sub_data)
    df_ccd = df_results[df_results['Group'] == 'CCD'].sort_values('Subject')
    df_tdc = df_results[df_results['Group'] == 'TDC'].sort_values('Subject')
    df_plot = pd.concat([df_ccd, df_tdc], ignore_index=True)

    n_ccd, n_tdc = len(df_ccd), len(df_tdc)
    c_sr, c_relay = '#4fa0c0', '#d96b15'

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 8), gridspec_kw={'width_ratios': [1.8, 1]})

    bar_colors = [c_relay if r['Winner'] == 'Relay' else c_sr for _, r in df_plot.iterrows()]
    bars = ax1.barh(df_plot['Label'], df_plot['Probability'], color=bar_colors, edgecolor='black', lw=0.5, height=0.7)
    ax1.invert_yaxis()
    ax1.set_xlabel('Mean posterior probability of subject winner (%)', fontsize=12, labelpad=10)
    ax1.set_xlim(0, 108)
    ax1.grid(axis='x', linestyle=':', alpha=0.5)

    for bar, row in zip(bars, df_plot.itertuples()):
        w = bar.get_width()
        ax1.text(w + 1.5, bar.get_y() + bar.get_height() / 2, row.Winner, ha='left', va='center', fontsize=9,
                 fontweight='bold', color='#444444')

    ax1.axhline(y=n_ccd - 0.5, color='#555555', linestyle='--', lw=1.2)
    ax1.text(106, n_ccd / 2 - 0.5, f'CCD (n={n_ccd})', va='center', ha='right', fontsize=13, fontweight='bold',
             color='#222222')
    ax1.text(106, n_ccd + n_tdc / 2 - 0.5, f'TDC (n={n_tdc})', va='center', ha='right', fontsize=13, fontweight='bold',
             color='#222222')

    ccd_sr = len(df_ccd[df_ccd['Winner'] == 'SR'])
    ccd_relay = len(df_ccd[df_ccd['Winner'] == 'Relay'])
    tdc_sr = len(df_tdc[df_tdc['Winner'] == 'SR'])
    tdc_relay = len(df_tdc[df_tdc['Winner'] == 'Relay'])

    ccd_tot, tdc_tot = ccd_sr + ccd_relay, tdc_sr + tdc_relay
    ccd_sr_pct = (ccd_sr / ccd_tot) * 100 if ccd_tot > 0 else 0
    ccd_relay_pct = (ccd_relay / ccd_tot) * 100 if ccd_tot > 0 else 0
    tdc_sr_pct = (tdc_sr / tdc_tot) * 100 if tdc_tot > 0 else 0
    tdc_relay_pct = (tdc_relay / tdc_tot) * 100 if tdc_tot > 0 else 0

    labels = [f"CCD\n(n={n_ccd})", f"TDC\n(n={n_tdc})"]
    ax2.bar(labels, [ccd_sr_pct, tdc_sr_pct], color=c_sr, edgecolor='black', lw=0.5, width=0.65)
    ax2.bar(labels, [ccd_relay_pct, tdc_relay_pct], bottom=[ccd_sr_pct, tdc_sr_pct], color=c_relay, edgecolor='black',
            lw=0.5, width=0.65)

    for i, (sr, relay, sr_pct) in enumerate([(ccd_sr, ccd_relay, ccd_sr_pct), (tdc_sr, tdc_relay, tdc_sr_pct)]):
        if sr > 0:
            ax2.text(i, sr_pct / 2, str(sr), ha='center', va='center', color='white', fontweight='bold', fontsize=14)
        if relay > 0:
            ax2.text(i, sr_pct + (100 - sr_pct) / 2, str(relay), ha='center', va='center', color='white',
                     fontweight='bold', fontsize=14)

    ax2.set_ylabel('Subjects with this winning model (%)', fontsize=12, labelpad=8)
    ax2.set_ylim(0, 100)
    ax2.grid(axis='y', linestyle=':', alpha=0.5)

    p_sr = mpatches.Patch(facecolor=c_sr, label='SENSORY_RELAY / FLEX', edgecolor='black', lw=0.5)
    p_relay = mpatches.Patch(facecolor=c_relay, label='RELAY / FLEX', edgecolor='black', lw=0.5)
    fig.legend(handles=[p_sr, p_relay], loc='upper center', bbox_to_anchor=(0.5, 1.05), ncol=2, frameon=False,
               fontsize=14)

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_task_architectures(df, out_path):
    mapping = {
        'SENSORY_RELAY__UNC_FLEX': 'SENSORY RELAY / UNC FLEX',
        'RELAY__UNC_FLEX': 'RELAY / UNC FLEX',
        'NULL__UNC_FLEX': 'NULL / UNC FLEX',
        'DIRECT__UNC_FLEX': 'DIRECT / UNC FLEX',
        'SENSORY_RELAY__UNC_INTRA_ONLY': 'SENSORY RELAY / UNC INTRA ONLY',
        'RELAY__UNC_INTRA_ONLY': 'RELAY / UNC INTRA ONLY',
        'NULL__UNC_INTRA_ONLY': 'NULL / UNC INTRA ONLY',
        'DIRECT__UNC_INTRA_ONLY': 'DIRECT / UNC INTRA ONLY',
    }

    order = [
        'SENSORY RELAY / UNC FLEX', 'RELAY / UNC FLEX', 'NULL / UNC FLEX', 'DIRECT / UNC FLEX',
        'SENSORY RELAY / UNC INTRA ONLY', 'RELAY / UNC INTRA ONLY', 'NULL / UNC INTRA ONLY'
    ]

    palette = {
        'SENSORY RELAY / UNC FLEX': '#2980b9', 'RELAY / UNC FLEX': '#d35400',
        'NULL / UNC FLEX': '#7474b4', 'DIRECT / UNC FLEX': '#d81b60',
        'SENSORY RELAY / UNC INTRA ONLY': '#7fb3d5',
        'RELAY / UNC INTRA ONLY': '#f5b041', 'NULL / UNC INTRA ONLY': '#bb8fce'
    }

    df_clean = df.copy()
    df_clean['Winner_Clean'] = df_clean['Winner_Raw'].map(mapping).fillna(df_clean['Winner_Raw'])

    fig, axes = plt.subplots(2, 2, figsize=(15, 10), sharey=True)
    axes = axes.flatten()

    for idx, task in enumerate(TASKS):
        ax = axes[idx]
        df_task = df_clean[df_clean['Task'] == task]

        n_ccd = df_task[df_task['Group'] == 'CCD']['Subject'].nunique()
        n_tdc = df_task[df_task['Group'] == 'TDC']['Subject'].nunique()

        counts = df_task.groupby(['Group', 'Winner_Clean']).size().unstack(fill_value=0)
        for m in order:
            if m not in counts.columns:
                counts[m] = 0

        groups = ['CCD', 'TDC']
        labels = [f"CCD\n(n={n_ccd})", f"TDC\n(n={n_tdc})"]
        totals = {'CCD': n_ccd, 'TDC': n_tdc}
        bottoms = np.zeros(2)

        for m in order:
            raw = np.array([counts.loc['CCD', m] if 'CCD' in counts.index else 0,
                            counts.loc['TDC', m] if 'TDC' in counts.index else 0])

            pct = np.zeros(2)
            for g_idx, g_name in enumerate(groups):
                if totals[g_name] > 0:
                    pct[g_idx] = (raw[g_idx] / totals[g_name]) * 100

            if np.any(raw > 0):
                bars = ax.bar(groups, pct, bottom=bottoms, color=palette.get(m, '#333333'), edgecolor='black', lw=0.5,
                              width=0.55)
                for b_idx, bar in enumerate(bars):
                    val = raw[b_idx]
                    if val > 0:
                        y_pos = bar.get_y() + bar.get_height() / 2
                        ax.text(bar.get_x() + bar.get_width() / 2, y_pos, str(val), ha='center', va='center',
                                color='white', fontweight='bold', fontsize=12)

            bottoms += pct

        ax.set_title(task, fontweight='bold', fontsize=15, pad=12)
        ax.set_xticklabels(labels, fontsize=12)
        ax.set_ylabel("Subjects with this winning architecture (%)", fontsize=11, labelpad=8)
        ax.set_ylim(0, 105)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='y', linestyle=':', alpha=0.3)

    fig.suptitle('Winning DCM architectures by task and group', fontweight='bold', fontsize=18, y=0.98)
    handles = [plt.Rectangle((0, 0), 1, 1, color=palette[m], ec='k', lw=0.5) for m in order]
    fig.legend(handles, order, loc='lower center', bbox_to_anchor=(0.5, -0.08), ncol=3, frameon=False, fontsize=11)

    footnote = "Numbers inside bars indicate subject counts. Percentages are computed within each group for each task dynamically based on data availability."
    fig.text(0.5, -0.12, footnote, ha='center', fontsize=10.5, fontstyle='italic')

    plt.tight_layout(rect=[0, 0, 1, 0.94])
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()



def main():
    out_dir = "graphs"
    os.makedirs(out_dir, exist_ok=True)

    df_peb = load_group_results()
    if not df_peb.empty:
        plot_peb_connectivity(df_peb, os.path.join(out_dir, 'peb_effective_connectivity_clean.png'))
        plot_connection_classes(df_peb, os.path.join(out_dir, 'peb_distributions_classes_clean.png'))
    else:
        print("Skipped PEB graphs: group-level data empty or missing.")

    df_bms = load_bms_summaries()
    if not df_bms.empty:
        plot_subject_architectures(df_bms, os.path.join(out_dir, 'winning_architecture_summary_dynamic.png'))
        plot_task_architectures(df_bms, os.path.join(out_dir, 'winning_architecture_by_task_group_dynamic.png'))
    else:
        print("Skipped BMS graphs: individual summary data empty.")

    print(f"\nPipeline finished. Figures saved in: {os.path.abspath(out_dir)}")


if __name__ == '__main__':
    main()