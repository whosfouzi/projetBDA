import streamlit as st
import pandas as pd
import traceback

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
# Wrap in try-except to prevent crashes during app initialization
if not st.session_state.user:
    try:
        params = st.query_params
        if "user_email" in params:
            # Try to restore the session from stored email
            try:
                from backend.auth import restore_session, get_user_name
                user = restore_session(params["user_email"])
                if user:
                    try:
                        st.session_state.user = user
                        st.session_state.authenticated = True
                        user_name = get_user_name(
                            user.get('type_utilisateur', ''),
                            user.get('id_professeur'),
                            user.get('id_etudiant')
                        )
                        st.session_state.user_name = user_name
                    except Exception as e:
                        print(f"Warning: Could not restore session state: {e}")
            except Exception as e:
                print(f"Warning: Could not restore session: {e}")
                # Don't crash - just continue without restored session
    except Exception as e:
        print(f"Warning: Session restore check failed: {e}")
        # Don't crash - just continue

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
            
            st.markdown("""
            <div style="background-color: rgba(59, 130, 246, 0.1); padding: 15px; border-radius: 10px; border-left: 5px solid #3b82f6; margin-bottom: 20px;">
                <h4 style="margin-top:0; color:#3b82f6;">🔑 Comptes de Démonstration (Demo)</h4>
                <div style="max-height: 250px; overflow-y: auto;">
                    <table style="width:100%; font-size: 0.85rem; border-collapse: collapse;">
                        <tr style="border-bottom: 1px solid rgba(0,0,0,0.1);">
                            <th style="padding: 5px; text-align: left;">Rôle</th>
                            <th style="padding: 5px; text-align: left;">Email</th>
                            <th style="padding: 5px; text-align: left;">Password</th>
                        </tr>
                        <tr><td>👤 Directeur</td><td><code>admin@univ.edu</code></td><td><code>admin</code></td></tr>
                        <tr><td>🏛️ Vice-Doyen</td><td><code>doyen@univ.edu</code></td><td><code>doyen123</code></td></tr>
                        <tr style="background-color: rgba(59, 130, 246, 0.05);"><td colspan="3" style="font-weight: bold; padding: 5px; font-size: 0.75rem;">CHEFS DE DÉPARTEMENT (Valideurs)</td></tr>
                        <tr><td>🧪 Chimie</td><td><code>chef.chimie@univ.edu</code></td><td><code>chef123</code></td></tr>
                        <tr><td>💻 Info</td><td><code>chef.info@univ.edu</code></td><td><code>chef123</code></td></tr>
                        <tr><td>📐 Maths</td><td><code>chef.maths@univ.edu</code></td><td><code>chef123</code></td></tr>
                        <tr><td>⚡ Physique</td><td><code>chef.phys@univ.edu</code></td><td><code>chef123</code></td></tr>
                        <tr><td>🔬 Bio</td><td><code>chef.bio@univ.edu</code></td><td><code>chef123</code></td></tr>
                        <tr><td>🚜 Agro</td><td><code>chef.agro@univ.edu</code></td><td><code>chef123</code></td></tr>
                        <tr><td>🏃 STAPS</td><td><code>chef.staps@univ.edu</code></td><td><code>chef123</code></td></tr>
                        <tr style="background-color: rgba(59, 130, 246, 0.05);"><td colspan="3" style="font-weight: bold; padding: 5px; font-size: 0.75rem;">AUTRES ACTEURS</td></tr>
                        <tr><td>👨‍🏫 Professeur</td><td><code>amine.ziani@univ.edu</code></td><td><code>password123</code></td></tr>
                        <tr><td>🎓 Étudiant</td><td><code>sarah.toumi@student.edu</code></td><td><code>password123</code></td></tr>
                    </table>
                </div>
                <p style="font-size: 0.8rem; margin-top: 10px; color: #1e40af;">
                    🛡️ Les étudiants/profs accèdent au planning après validation du Chef.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            email = st.text_input("Email")
            password = st.text_input("Mot de passe", type="password")
            submit = st.form_submit_button("Se connecter", use_container_width=True)
            
            if submit:
                # CRITICAL: Wrap EVERYTHING in try-except to prevent server crash
                # This is the outermost safety net - no exception can escape
                try:
                    # Import safely - wrap in try-except
                    check_login_func = None
                    get_user_name_func = None
                    
                    try:
                        from backend.auth import check_login as _check_login, get_user_name as _get_user_name
                        check_login_func = _check_login
                        get_user_name_func = _get_user_name
                    except Exception as e:
                        error_msg = f"Erreur d'importation: {str(e)}"
                        print(f"ERROR: Import failed: {e}")
                        traceback.print_exc()
                        try:
                            st.error(f"❌ {error_msg}")
                        except:
                            pass
                        # Stop here if imports fail - don't continue
                        check_login_func = None
                    
                    # If imports failed, stop here
                    if check_login_func is None or get_user_name_func is None:
                        return
                    
                    # Validate inputs first
                    if not email or not password:
                        try:
                            st.error("Veuillez remplir tous les champs.")
                        except:
                            pass
                    else:
                        # Execute login check - check_login NEVER raises, always returns (user, err)
                        user = None
                        err = None
                        
                        # Don't use st.spinner in form context - it can cause issues
                        # Just call check_login directly - it's safe
                        try:
                            # check_login is safe - it never raises exceptions
                            user, err = check_login_func(email, password)
                        except Exception as e:
                            # This should never happen, but safety first
                            error_msg = f"Erreur lors de la vérification: {type(e).__name__}: {str(e)}"
                            print(f"CRITICAL ERROR: check_login raised exception: {error_msg}")
                            traceback.print_exc()
                            try:
                                st.error(f"❌ {error_msg}")
                            except:
                                pass
                            user, err = None, error_msg
                        
                        # Process login result
                        if user:
                            # Login successful - set session state safely
                            try:
                                # Set session state one by one to catch any issues
                                st.session_state.user = user
                                st.session_state.authenticated = True
                                
                                # Get user name safely
                                try:
                                    user_name = get_user_name_func(
                                        user.get('type_utilisateur', ''),
                                        user.get('id_professeur'),
                                        user.get('id_etudiant')
                                    )
                                    st.session_state.user_name = user_name
                                except Exception as e:
                                    print(f"Warning: Could not get user name: {e}")
                                    traceback.print_exc()
                                    try:
                                        st.session_state.user_name = user.get('email', 'Utilisateur')
                                    except:
                                        pass
                                
                                # Set query params safely
                                try:
                                    st.query_params["user_email"] = email
                                except Exception as e:
                                    print(f"Warning: Could not set query params: {e}")
                                
                                # Show success message safely
                                try:
                                    st.success("Connexion réussie !")
                                except:
                                    pass
                                
                                # Rerun safely - wrap in try-except
                                try:
                                    st.rerun()
                                except Exception as e:
                                    print(f"Warning: st.rerun() failed: {e}")
                                    traceback.print_exc()
                                    # If rerun fails, don't crash - just continue
                                    # The page will refresh on next interaction
                                    
                            except Exception as e:
                                # Critical: If session state setting fails, show error but don't crash
                                error_msg = f"Erreur lors de l'initialisation de la session: {type(e).__name__}: {str(e)}"
                                st.error(f"❌ {error_msg}")
                                print(f"ERROR: Session initialization failed: {error_msg}")
                                traceback.print_exc()
                        else:
                            # Login failed - show appropriate error
                            try:
                                if err:
                                    # Check if it's a database connection error
                                    err_lower = err.lower()
                                    if any(keyword in err_lower for keyword in ["connection", "timeout", "database", "mysql", "erreur"]):
                                        st.error(f"❌ {err}")
                                        st.warning("💡 Vérifiez que:\n- Le serveur MySQL est démarré sur le port 3307\n- Les identifiants dans `.streamlit/secrets.toml` sont corrects\n- Le serveur est accessible depuis votre machine")
                                    else:
                                        st.error(err)
                                else:
                                    st.error("Erreur inconnue lors de la connexion")
                            except Exception as e:
                                # Even error display can fail - log it
                                print(f"ERROR: Failed to display error message: {e}")
                                st.error("Une erreur s'est produite. Consultez les logs du serveur.")
                                
                except Exception as e:
                    # CRITICAL: This is the absolute last line of defense
                    # If we reach here, something very unexpected happened
                    error_msg = f"Erreur critique lors de la connexion: {type(e).__name__}: {str(e)}"
                    print(f"CRITICAL ERROR in login handler: {error_msg}")
                    traceback.print_exc()
                    
                    # Try to show error to user, but don't fail if this also fails
                    try:
                        st.error(f"❌ {error_msg}")
                        st.warning("💡 Le serveur de base de données peut être inaccessible. Vérifiez votre configuration.")
                    except Exception:
                        # If even error display fails, just log it
                        print("CRITICAL: Could not display error message to user")
        
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
        
        # Display Student Info
        if role == 'etudiant':
             spec = st.session_state.user.get('spec_nom', 'N/A')
             grp = st.session_state.user.get('groupe_nom', 'N/A')
             st.info(f"📚 {spec}\n\n👥 {grp}")

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
