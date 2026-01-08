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
            
            with st.expander("🔑 Comptes de Démonstration (Demo)"):
                st.markdown("""
                | Rôle | Email | Password |
                | :--- | :--- | :--- |
                | **Directeur** | `admin@univ.edu` | `admin` |
                | **Vice-Doyen** | `doyen@univ.edu` | `doyen123` |
                | **Chef Dept (Chimie)** | `chef.chimie@univ.edu` | `chef123` |
                | **Professeur** | `bouchenak_0@univ.edu` | `password123` |
                | **Étudiant (Chimie)** | `e202400074@student.edu` | `password123` |
                """)
                st.info("💡 Les étudiants ne voient leur planning qu'après validation par leur Chef de Département.")
            
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
from frontend.views.dept_preview import show_dept_preview

# -----------------------------------------------------------------------------
if not st.session_state.user:
    login_page()
else:
    role = st.session_state.user['type_utilisateur']
    user_name = st.session_state.get('user_name', 'Utilisateur')
    
    # SIDEBAR NAVIGATION
    with st.sidebar:
        st.title("🎓 UMBB EXAM")
        st.caption("Sciences Portal")
        st.divider()
        
        # Define menu based on role
        if role == 'vice_doyen':
            page_options = ["📊 Tableau de Bord", "📅 Planning Global", "🛡️ Audit & Qualité"]
        elif role == 'admin_examens':
            page_options = ["📊 Tableau de Bord", "⚙️ Générateur", "📅 Planning Global", "🛡️ Audit & Qualité"]
        elif role == 'chef_departement':
            page_options = ["📊 Tableau de Bord", "🔍 Aperçu Département", "📅 Planning Global", "🛡️ Audit & Qualité"]
        elif role in ['professeur', 'etudiant']:
            page_options = ["🎓 Mes Examens", "📅 Planning Global"]
        else:
            page_options = []
        
        # Navigation
        selected_page = st.radio("Navigation", page_options, label_visibility="collapsed")
        
        st.divider()
        st.caption(f"👤 {user_name}")
        
        if st.button("🚪 Déconnexion", use_container_width=True):
            st.session_state.user = None
            st.session_state.authenticated = False
            st.query_params.clear()
            st.rerun()
    
    # RENDER SELECTED PAGE
    if selected_page == "📊 Tableau de Bord":
        show_dashboard()
    elif selected_page == "⚙️ Générateur":
        show_generate()
    elif selected_page == "📅 Planning Global":
        show_timetable()
    elif selected_page == "🛡️ Audit & Qualité":
        show_audit()
    elif selected_page == "🎓 Mes Examens":
        show_my_exams()
    elif selected_page == "🔍 Aperçu Département":
        show_dept_preview()
    else:
        st.error("Page non trouvée")

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
