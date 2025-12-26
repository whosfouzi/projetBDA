import streamlit as st
import pandas as pd
from datetime import datetime
from backend.auth import authenticate, get_user_role_label
from backend.db import run_query

# Configuration de la page (Doit être la première commande Streamlit)
st.set_page_config(
    page_title="Planificateur d'Examens",
    page_icon="📅",
    layout="wide"
)

def load_css():
    """Charge le fichier de style personnalisé."""
    with open("frontend/assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def init_session_state():
    """Initialise les variables de session."""
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None

def render_sidebar_auth():
    """Gère l'authentification réelle via DB."""
    load_css()
    st.sidebar.title("Connexion")
    
    if st.session_state.role:
        st.sidebar.success(f"Connecté : {get_user_role_label(st.session_state.role)}")
        st.sidebar.info(f"User : {st.session_state.user_info.get('email', 'N/A')}")
        if st.sidebar.button("Déconnexion"):
            st.session_state.role = None
            st.session_state.user_info = None
            st.rerun()
    else:
        email = st.sidebar.text_input("Email")
        password = st.sidebar.text_input("Mot de passe", type="password")
        
        if st.sidebar.button("Se Connecter"):
            user = authenticate(email, password)
            if user:
                st.session_state.role = user['type_utilisateur']
                st.session_state.user_info = user
                st.rerun()
            else:
                st.sidebar.error("Identifiants invalides")
        
        with st.sidebar.expander("Aide Connexion"):
             st.write("Admin: admin@univ.edu / admin")

def get_dashboard_metrics():
    """Récupère les KPIs réels depuis la base de données."""
    try:
        # Counters simple
        total_exams = run_query("SELECT COUNT(*) as val FROM examen")[0]['val']
        total_students = run_query("SELECT COUNT(*) as val FROM etudiant")[0]['val']
        
        # Conflits: Vérifier si la vue existe, sinon 0
        conflicts = 0
        try:
            res = run_query("SELECT COUNT(*) as val FROM vue_etudiants_conflits")
            if res:
                conflicts = res[0]['val']
        except:
            pass # Vue peut-être pas encore créée
        
        # Usage Salles
        used_rooms = run_query("SELECT COUNT(DISTINCT id_salle) as val FROM examen")[0]['val']
        total_rooms = run_query("SELECT COUNT(*) as val FROM salle")[0]['val']
        room_usage = round((used_rooms / total_rooms * 100) if total_rooms > 0 else 0)
        
        return total_exams, total_students, conflicts, room_usage
    except Exception as e:
        # Fallback pour ne pas crasher tout le dashboard
        return 0, 0, 0, 0

def get_upcoming_exams():
    """Récupère les 5 prochains examens."""
    query = """
    SELECT 
        e.date_examen AS Date, 
        TIME_FORMAT(e.heure_debut, '%H:%i') AS Heure,
        m.nom AS Cours,
        d.nom AS Département,
        s.nom AS Salle,
        f.nom AS Formation
    FROM examen e
    JOIN module m ON e.id_module = m.id_module
    JOIN formation f ON m.id_formation = f.id_formation
    JOIN departement d ON f.id_departement = d.id_dep
    LEFT JOIN salle s ON e.id_salle = s.id_salle
    WHERE e.date_examen >= CURDATE()
    ORDER BY e.date_examen, e.heure_debut
    LIMIT 5
    """
    data = run_query(query)
    return pd.DataFrame(data)

def main():
    init_session_state()
    render_sidebar_auth()
    
    st.title("Tableau de Bord")
    
    if not st.session_state.role:
        st.warning("Veuillez vous connecter pour accéder au tableau de bord.")
        st.stop()

    # Récupération des données réelles
    total_exams, total_students, conflicts, room_usage = get_dashboard_metrics()
    
    # KPIs with standard Metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Examens", total_exams)
    with col2:
        st.metric("Étudiants", total_students)
    with col3:
        st.metric("Conflits", conflicts, delta="-2" if conflicts > 0 else None, delta_color="inverse")
    with col4:
        st.metric("Utilisation Salles", f"{room_usage}%")

    # Aperçu du Planning
    st.subheader("🗓️ Prochains Examens")
    upcoming_exams = get_upcoming_exams()
    
    if not upcoming_exams.empty:
        st.dataframe(
            upcoming_exams,
            width="stretch",
            hide_index=True
        )
    else:
        st.info("Aucun examen prévu prochainement.")

    # Quick Actions (Role based)
    st.subheader("⚡ Actions Rapides")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.session_state.role == 'admin_examens':
            if st.button("𝗚énérer Planning"):
                st.switch_page("pages/1_Generate_Timetable.py")
        else:
            st.button("Générer (Restreint)", disabled=True)
            
    with col2:
        if st.button("Voir Emploi du Temps"):
            st.switch_page("pages/2_View_Timetable.py")
            
    with col3:
        if st.button("Exporter Données"):
            st.toast("Export CSV en cours... (Simulé)")

if __name__ == "__main__":
    main()
