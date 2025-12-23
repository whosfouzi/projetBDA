"""
Module de Statistiques et Analyses.

ACCÈS CONDITIONNEL (RBAC) : 
- Étudiants / Professeurs : Accès Refusé.
- Chef de Département : Vue filtrée sur leur département.
- Doyens / Administrateurs : Accès Global.
"""

import streamlit as st
import pandas as pd
import altair as alt
from utils.fake_data import get_exams_data, get_rooms_data

st.set_page_config(page_title="Statistiques", page_icon="📊", layout="wide")

def check_access_and_filter(exams_df):
    """
    Vérifie les droits d'accès et filtre les données si nécessaire.
    Renvoie le DataFrame filtré ou arrête l'exécution.
    """
    role = st.session_state.get('user_role', 'Invité')
    
    # 1. Restriction Totale
    if role == "Étudiant / Professeur":
        st.error("⛔ Accès Non Autorisé")
        st.markdown(f"""
        Les étudiants et professeurs n'ont pas accès aux statistiques globales.
        Veuillez contacter votre **Chef de Département** pour toute demande d'information.
        """)
        st.stop()

    # 2. Filtrage Partiel
    if role == "Chef de Département":
        # PLACEHOLDER: SELECT department_name FROM departments WHERE head_id = current_user_id
        target_dept = "Informatique" # Simulation
        st.info(f"🔒 Vue restreinte au département : **{target_dept}**")
        return exams_df[exams_df['Département'] == target_dept]

    # 3. Accès Global (Admin, Doyen)
    return exams_df

def main():
    """Rendu de la page de statistiques."""
    role = st.session_state.get('user_role', 'Invité')
    st.title("📊 Analyses & Statistiques")
    st.caption(f"Profil actif : {role}")

    # Chargement
    exams = get_exams_data()
    rooms = get_rooms_data()

    # Application de la Sécurité
    filtered_exams = check_access_and_filter(exams)

    st.markdown("""
    Tableau de bord analytique pour visualiser la distribution de la charge d'examen
    et l'optimisation des espaces physiques.
    """)

    # Section 1: Répartition Académique
    st.header("1. Répartition Académique")
    
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Charge par Département")
        if not filtered_exams.empty:
            chart_dept = alt.Chart(filtered_exams).mark_bar().encode(
                x=alt.X('Département', sort='-y', title="Département"),
                y=alt.Y('count()', title="Nombre d'Examens"),
                color=alt.Color('Département', legend=None),
                tooltip=['Département', 'count()']
            ).properties(height=350)
            st.altair_chart(chart_dept, use_container_width=True)
        else:
            st.info("Aucune donnée disponible pour votre sélection.")

    with col2:
        st.subheader("Répartition Temporelle")
        if not filtered_exams.empty:
            chart_time = alt.Chart(filtered_exams).mark_arc(innerRadius=50).encode(
                theta=alt.Theta('count()', stack=True),
                color=alt.Color('Heure', title="Créneau Horaire"),
                tooltip=['Heure', 'count()']
            ).properties(height=350)
            st.altair_chart(chart_time, use_container_width=True)
        else:
            st.info("Aucune donnée disponible")


    st.divider()

    # Section 2: Logistique
    st.header("2. Analyse Logistique")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Taux d'Occupation des Salles")
        if not filtered_exams.empty:
            room_counts = filtered_exams['Salle'].value_counts().reset_index()
            room_counts.columns = ['Salle', 'Examens Hébergés']

            chart_rooms = alt.Chart(room_counts).mark_bar().encode(
                x=alt.X('Salle', sort='-y', title="Salle d'Examen"),
                y=alt.Y('Examens Hébergés', title="Volume d'Activité"),
                color=alt.value("#4c78a8"),
                tooltip=['Salle', 'Examens Hébergés']
            ).properties(height=300)

            st.altair_chart(chart_rooms, use_container_width=True)
        else:
            st.info("Aucune donnée d'utilisation des salles disponible")

    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True) 
        st.info("""
        **Note d'interprétation :**
        Ces données reflètent uniquement les examens relevant de votre périmètre de gestion.
        """)


    st.divider()

    # Section 3: Démographie
    st.header("3. Démographie Étudiante")
    st.subheader("Densité des Effectifs par Examen")
    
    if not filtered_exams.empty:
        chart_students = alt.Chart(filtered_exams).mark_area(
            opacity=0.6,
            interpolate='monotone',
            color='lightgreen'
        ).encode(
            alt.X('Étudiants', bin=alt.Bin(maxbins=15), title="Nombre d'Étudiants par Examen"),
            alt.Y('count()', title="Fréquence"),
        ).properties(height=300)
        st.altair_chart(chart_students, use_container_width=True)
    else:
        st.info("Aucune donnée étudiante disponible")

if __name__ == "__main__":
    main()
