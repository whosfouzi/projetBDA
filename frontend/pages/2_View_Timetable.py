"""
Visualiseur d'Emploi du Temps.

Ce module est accessible à tous les rôles simulés (Étudiant, Professeur, Admin, etc.).
Dans un système réel, la vue pourrait être pré-filtrée selon l'ID de l'étudiant ou du professeur connecté.
"""

import streamlit as st
import pandas as pd
from utils.fake_data import get_exams_data

st.set_page_config(page_title="Voir Emploi du Temps", page_icon="📅", layout="wide")

def apply_role_constraints(df):
    """
    Applique des filtres automatiques basés sur le rôle de l'utilisateur.
    """
    role = st.session_state.get('user_role', 'Invité')
    
    if role == "Chef de Département":
        # Simulation: Le Chef de Département info ne voit que 'Informatique' par défaut
        # PLACEHOLDER: SELECT department FROM heads_of_department WHERE id = current_user_id
        st.info(f"Filtre Automatique ({role}): Focus sur le département Informatique")
        return df[df['Département'] == 'Informatique']
    
    if role == "Étudiant / Professeur":
        # Dans un vrai cas, on filtrerait sur les cours inscrits
        # PLACEHOLDER: SELECT * FROM exams WHERE course_id IN (SELECT course_id FROM enrollments...)
        pass
        
    return df

def main():
    """Rendu de la page de consultation."""
    role = st.session_state.get('user_role', 'Invité')
    st.title("📅 Consultation de l'Emploi du Temps")
    
    st.markdown(f"""
    Connecté en tant que : **{role}**
    """)

    # Chargement des données
    df = get_exams_data()
    
    # Application des contraintes de rôle (optionnel pour la démo, mais bonne pratique)
    # df = apply_role_constraints(df) # Commenté pour laisser la liberté de filtrage dans la démo

    # Zone de Filtrage
    with st.expander("🔎 Critères de Recherche", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            dept_filter = st.multiselect(
                "Département",
                options=df['Département'].unique(),
                default=df['Département'].unique(),
                help="Sélectionnez un ou plusieurs départements."
            )
            
        with col2:
            # Filtrage contextuel des formations
            available_formations = df[df['Département'].isin(dept_filter)]['Formation'].unique()
            formation_filter = st.multiselect(
                "Formation / Année",
                options=available_formations,
                default=available_formations,
                help="Filtrer par niveau d'étude ou groupe."
            )
            
        with col3:
            date_range = st.date_input(
                "Période",
                value=(pd.to_datetime(df['Date'].min()), pd.to_datetime(df['Date'].max())),
                help="Sélectionnez la plage de dates à afficher."
            )

    # Application des filtres UI
    if not df.empty:
        mask = (
            df['Département'].isin(dept_filter) &
            df['Formation'].isin(formation_filter)
        )
        
        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_date, end_date = date_range
            mask = mask & (pd.to_datetime(df['Date']).dt.date >= start_date) & (pd.to_datetime(df['Date']).dt.date <= end_date)

        filtered_df = df[mask]
    else:
        filtered_df = df


    # Affichage des Résultats
    st.divider()
    st.subheader(f"Résultats de la Recherche ({len(filtered_df)} examens)")

    # Fonction de stylisation conditionnelle
    def highlight_time(val):
        """Colore les cellules selon l'heure (Matin/Après-midi)."""
        color = '#e6f3ff' if val == '09:00' else '#fff0e6' 
        return f'background-color: {color}'

    st.dataframe(
        filtered_df.style.applymap(highlight_time, subset=['Heure']),
        use_container_width=True,
        height=600
    )
    st.caption("Légende : Bleu = Matin (09:00), Orange = Après-midi (14:00)")

    # Options d'Exportation
    col1, col2 = st.columns([1, 4])
    with col1:
        st.download_button(
            label="📥 Exporter en CSV",
            data=filtered_df.to_csv(index=False),
            file_name='emploi_du_temps_export.csv',
            mime='text/csv',
            help="Télécharger la vue actuelle au format CSV compatible Excel."
        )

if __name__ == "__main__":
    main()
