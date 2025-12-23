"""
Tableau de Bord Principal (Dashboard)

Ce module sert de point d'entrée pour l'application Planificateur d'Examens.
Il gère l'authentification simulée (RBAC) via un sélecteur de rôle en barre latérale.
"""

import streamlit as st
import pandas as pd
from utils.fake_data import get_stats_data, get_exams_data

# Configuration de la page
st.set_page_config(
    page_title="Planificateur d'Examens",
    page_icon="📅",
    layout="wide"
)

def load_css():
    """Charge le fichier de style personnalisé."""
    with open("frontend/assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def render_sidebar_auth():
    """Gère le sélecteur de rôle et la simulation d'authentification."""
    load_css()
    st.sidebar.title("Connexion")
    st.sidebar.caption("Simulation d'Accès Sécurisé")
    
    # Sélecteur de rôle
    role = st.sidebar.selectbox(
        "Sélectionnez votre profil",
        [
            "Étudiant / Professeur",
            "Chef de Département",
            "Vice-Doyen / Doyen",
            "Administrateur d'Examens"
        ],
        index=3  # Par défaut Administrateur pour la démo
    )
    
    # Store in session state for cross-page access
    st.session_state['user_role'] = role
    
    st.sidebar.divider()
    
    # Affichage contextuel basé sur le rôle
    if role == "Administrateur d'Examens":
        st.sidebar.success("✅ Accès Complet")
        # PLACEHOLDER: Auth Backend
        # cursor.execute("SELECT * FROM administrators WHERE username = %s", (username,))
    
    elif role == "Vice-Doyen / Doyen":
        st.sidebar.info("Statistics & Vue Globale")
        # PLACEHOLDER: Auth Backend
        # cursor.execute("SELECT * FROM deans WHERE username = %s", (username,))
        
    elif role == "Chef de Département":
        st.sidebar.warning("Vue Départementale Uniquement")
        # PLACEHOLDER: Auth Backend
        # cursor.execute("SELECT department_id FROM heads_of_department WHERE username = %s")
        # st.session_state['dept_id'] = result['department_id']
        
    else:
        st.sidebar.write("Vue Limitée")
        # PLACEHOLDER: Auth Backend
        # cursor.execute("SELECT * FROM users WHERE username = %s", (username,))

    return role

def main():
    """Fonction principale pour rendre le tableau de bord."""
    
    # Initialisation de l'authentification
    current_role = render_sidebar_auth()

    # En-tête principal
    st.title("📅 Tableau de Bord")
    st.markdown("""
    Bienvenue sur la **Plateforme de Planification des Examens Universitaires**. 
    Cette interface permet aux acteurs académiques de superviser le processus de planification.
    """)
    
    st.info(f"Connecté en tant que : **{current_role}**")

    # Chargement des données simulées
    stats = get_stats_data()
    exams = get_exams_data()

    # Section Indicateurs Clés (KPIs) - Visibilité selon Rôle
    st.subheader("Situation Actuelle")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(label="Total Examens Prévus", value=stats['total_exams'])

    with col2:
        st.metric(label="Total Étudiants", value=stats['total_students'])
        
    with col3:
        # Seuls les admins et doyens voient les alertes critiques
        if current_role in ["Administrateur d'Examens", "Vice-Doyen / Doyen"]:
            st.metric(
                label="Conflits Détectés", 
                value=stats['conflicts'], 
                delta_color="inverse", 
                delta="-2" if stats['conflicts'] > 0 else "0"
            )
        else:
            st.metric(label="Conflits Détectés", value="Masqué")

    with col4:
        st.metric(label="Salles Utilisées", value=f"{stats['rooms_utilized']}%")

    st.divider()

    # Section Activité Récente (Visible par tous)
    st.subheader("📆 Examens à Venir (7 Prochains Jours)")
    
    if not exams.empty:
        upcoming_exams = exams.sort_values(by='Date').head(5)
        st.dataframe(
            upcoming_exams[['Date', 'Heure', 'Cours', 'Département', 'Salle', 'Formation']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Aucun examen prévu pour le moment.")

    st.divider()

    # Section Actions Rapides (Contextuel)
    st.subheader("⚡ Actions Rapides")
    c1, c2, c3 = st.columns(3)

    if current_role == "Administrateur d'Examens":
        with c1:
            if st.button("Générer un Nouvel Emploi du Temps", use_container_width=True):
                st.switch_page("pages/1_Generate_Timetable.py")

    with c2:
        if st.button("Voir l'Emploi du Temps Complet", use_container_width=True):
            st.switch_page("pages/2_View_Timetable.py")
            
    if current_role in ["Administrateur d'Examens", "Vice-Doyen / Doyen"]:
        with c3:
            if st.button("Télécharger le Rapport", use_container_width=True):
                st.toast("Rapport téléchargé avec succès !")

if __name__ == "__main__":
    main()
