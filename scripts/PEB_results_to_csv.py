import os
import glob
import re
import numpy as np
import pandas as pd
from scipy.io import loadmat


DOSSIER_SOURCE = '/Users/alex/university/Neuroscience_Master/short-term internship/group_peb_full_cohort/PEB_results'
DOSSIER_CIBLE = '/Users/alex/university/Neuroscience_Master/short-term internship/group_peb_full_cohort/PEB_results'

os.makedirs(DOSSIER_CIBLE, exist_ok=True)

def vers_tableau_plat(variable):
    """Convertit n'importe quel format (sparse ou dense) en tableau 1D classique."""
    if hasattr(variable, 'toarray'):
        return variable.toarray().flatten()
    return np.array(variable).flatten()


fichiers_mat = glob.glob(os.path.join(DOSSIER_SOURCE, '*.mat'))

if not fichiers_mat:
    print(f"Aucun fichier .mat trouvé dans le dossier : {DOSSIER_SOURCE}")
    exit()

print(f"🔍 {len(fichiers_mat)} fichier(s) .mat détecté(s). Début du traitement...\n")

for chemin_mat in fichiers_mat:
    nom_fichier_mat = os.path.basename(chemin_mat)
    nom_base = os.path.splitext(nom_fichier_mat)[0]  # Ex: 'BMA_PEB_MGOD_SENSORY_RELAY__UNC_FLEX'

    try:
        mat_data = loadmat(chemin_mat)
        cles_bma = [k for k in mat_data.keys() if k.startswith('BMA_')]
        if not cles_bma:
            print(f"Clé 'BMA_' introuvable dans {nom_fichier_mat}. Fichier ignoré.")
            continue
        cle_active = cles_bma[0]

        # Noms des connexions (38 noms)
        pnames_raw = mat_data[cle_active]['Pnames'][0, 0]
        noms_connexions = [str(p[0][0]) if len(p[0]) > 0 else f"Connexion_{i + 1}" for i, p in enumerate(pnames_raw)]

        # Ep et Pp
        ep_raw = mat_data[cle_active]['Ep'][0, 0]
        pp_raw = mat_data[cle_active]['Pp'][0, 0]

        ep_values = vers_tableau_plat(ep_raw)
        pp_values = vers_tableau_plat(pp_raw)

        effet_moyen_connexion = ep_values[0:38]
        difference_groupe_connexion = ep_values[38:76]
        probabilite_bayesienne = pp_values[38:76]

        df_resultats = pd.DataFrame({
            'Connexion': noms_connexions,
            'Moyenne_Generale': effet_moyen_connexion,
            'Difference_Groupe_Beta': difference_groupe_connexion,
            'Probabilite_Posterior_Pp': probabilite_bayesienne
        })

        df_resultats['Significatif_95'] = df_resultats['Probabilite_Posterior_Pp'] > 0.95
        df_resultats = df_resultats.sort_values(by='Difference_Groupe_Beta', key=abs, ascending=False)

        # Extraction propre du nom de la tâche pour formater le fichier CSV de sortie
        task = "UNKNOWN"
        for t in ['MGOD', 'MDOG', 'MDOD', 'MGOG']:
            if t in nom_base:
                task = t
                break

        # On nettoie le suffixe en enlevant le préfixe BMA_ et le nom de la tâche s'il y est déjà
        suffixe_propre = nom_base.replace('BMA_', '')
        if task != "UNKNOWN":
            # On retire temporairement le nom de la tâche du suffixe pour éviter de l'avoir en doublon
            suffixe_propre = re.sub(rf'_?{task}_?', '_', suffixe_propre).strip('_')
            # Format standardisé : resultats_comparaison_groupes_DCM_TACHE_description.csv
            nom_csv = f"resultats_comparaison_groupes_DCM_{task}_{suffixe_propre}.csv"
        else:
            nom_csv = f"resultats_comparaison_groupes_DCM_{suffixe_propre}.csv"

        chemin_csv_complet = os.path.join(DOSSIER_CIBLE, nom_csv)
        df_resultats.to_csv(chemin_csv_complet, index=False)
        print(f"{nom_fichier_mat} traité -> Sauvegardé : {nom_csv}")

    except Exception as e:
        print(f"Erreur lors du traitement de {nom_fichier_mat} : {str(e)}")

print("\nTous les fichiers ont été traités avec succès !")