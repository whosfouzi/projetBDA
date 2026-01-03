import streamlit as st
import pandas as pd

st.set_page_config(page_title="Exam Scheduler", layout="wide", page_icon="🎓", initial_sidebar_state="expanded")

def load_css():
    try:
        with open("assets/style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

load_css()

# Session State Init & Persistent Login
if 'user' not in st.session_state:
    st.session_state.user = None
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Auto-restore session from query params (for persistence across refreshes)
if not st.session_state.user:
    params = st.query_params
    if "user_email" in params:
        # Try to restore the session from stored email
        from backend.auth import restore_session
        user = restore_session(params["user_email"])
        if user:
            from backend.auth import get_user_name
            st.session_state.user = user
            st.session_state.authenticated = True
            st.session_state.user_name = get_user_name(user['type_utilisateur'], user['id_professeur'], user['id_etudiant'])

def login_page():
    st.markdown("""
    <div style='text-align: center; margin-top: 50px;'>
        <h1>🏫 Exam Scheduler</h1>
        <p style='color: #6b7280;'>Système de gestion des examens universitaires</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.form("login_form"):
            st.subheader("Connexion")
            st.caption("Admin: admin@univ.edu / admin")
            st.caption("Prof: nom_numero@univ.edu (ex: bouchenak_0) / password123")
            st.caption("Etudiant: e1@student.edu / password123")
            
            email = st.text_input("Email")
            password = st.text_input("Mot de passe", type="password")
            submit = st.form_submit_button("Se connecter", use_container_width=True)
            
            if submit:
                from backend.auth import check_login, get_user_name
                user, err = check_login(email, password)
                if user:
                    st.session_state.user = user
                    st.session_state.authenticated = True
                    st.session_state.user_name = get_user_name(user['type_utilisateur'], user['id_professeur'], user['id_etudiant'])
                    # Store email in query params for persistence
                    st.query_params["user_email"] = email
                    st.success("Connexion réussie !")
                    st.rerun()
                else:
                    st.error(err)
        
        # --- RESCUE MODE: For when utilisateur table is empty ---
        st.divider()
        with st.expander("🔧 Mode Récupération (Base de données vide ?)"):
            st.warning("⚠️ Cela va effacer et recréer toutes les données !")
            if st.button("🌱 Réinitialiser la Base de Données"):
                from backend.seed import seed_database
                with st.spinner("Réinitialisation..."):
                    success, msg = seed_database()
                if success:
                    st.success(f"{msg}")
                    st.info("Vous pouvez maintenant vous connecter avec admin@univ.edu / admin")
                else:
                    st.error(f"Erreur : {msg}")

# def main_dashboard(): ... (Kept as is, but we need to call login_page now)


# -----------------------------------------------------------------------------
# Views Import
# -----------------------------------------------------------------------------
from frontend.views.dashboard import show_dashboard
from frontend.views.generate import show_generate
from frontend.views.timetable import show_timetable
from frontend.views.my_exams import show_my_exams
from frontend.views.audit import show_audit

# -----------------------------------------------------------------------------
# Navigation Logic
# -----------------------------------------------------------------------------
if not st.session_state.user:
    login_page()
else:
    role = st.session_state.user['type_utilisateur']
    
    # Define Permissions
    # Label -> Function
    menus = {}

    # 1. Vice-Dean / Dean (Strategic)
    if role == 'vice_doyen':
        menus = {
            "📊 Tableau de Bord": show_dashboard,
            "📅 Planning Global": show_timetable,
            "🛡️ Audit & Qualité": show_audit
        }

    # 2. Admin (Operational)
    elif role == 'admin_examens':
        menus = {
            "📊 Tableau de Bord": show_dashboard,
            "⚙️ Générateur": show_generate,
            "📅 Planning Global": show_timetable,
            "🛡️ Audit & Qualité": show_audit
        }

    # 3. Head of Dept (Validation)
    elif role == 'chef_departement':
        menus = {
            "📊 Tableau de Bord": show_dashboard,
            "📅 Planning Global": show_timetable,
            "🛡️ Audit & Qualité": show_audit
        }

    # 4. Student / Prof (Consultation)
    elif role in ['professeur', 'etudiant']:
        menus = {
            "🎓 Mes Examens": show_my_exams,
            "📅 Planning Global": show_timetable
        }

    # Render Navigation (Navbar)
    if menus:
        from frontend.components.navbar import Navbar
        page_func = Navbar(menus)
        page_func()
    else:
        st.error("Aucun menu disponible pour ce rôle.")

    # -----------------------------------------------------------------------------
    # Global Tools available to Admins
    # -----------------------------------------------------------------------------
    if role in ['admin_examens', 'vice_doyen']:
        with st.sidebar:
            st.markdown("<br><br>", unsafe_allow_html=True)
            with st.expander("🔧 Zone Admin"):
                if st.button("🌱 Réinitialiser Données", help="Reset DB"):
                    from backend.seed import seed_database
                    with st.spinner("Réinitialisation..."):
                        success, msg = seed_database()
                        if success:
                            st.success("✅ Données réinitialisées!")
                            st.rerun()
                        else:
                            st.error(f"❌ Erreur: {msg}")
