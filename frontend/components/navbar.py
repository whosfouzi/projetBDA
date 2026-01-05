import streamlit as st

def Navbar(menu_dict):
    """
    Renders an Aside (Sidebar) navigation bar compatible with all users.
    """
    role_map = {
        'vice_doyen': ('Vice-Doyen', 'admin'),
        'admin_examens': ('Admin Examens', 'admin'),
        'chef_departement': ('Chef Dept', 'admin'),
        'professeur': ('Enseignant', 'prof'),
        'etudiant': ('Étudiant', 'student')
    }
    
    user = st.session_state.get('user', {})
    internal_role = user.get('type_utilisateur', 'guest')
    role_label, role_class = role_map.get(internal_role, ('Utilisateur', 'neutral'))

    with st.sidebar:
        # Branding
        st.markdown(f"""
            <div class='sidebar-header'>
                <h1 style='color: white !important; font-size: 1.5rem !important; margin: 0 !important;'>🎓 UMBB EXAM</h1>
                <p style='color: #94a3b8; font-size: 0.8rem;'>Sciences Portal • Faculty of Sciences</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Navigation
        selected_label = st.radio(
            "Navigation",
            options=list(menu_dict.keys()),
            label_visibility="collapsed",
            key="navbar_selection"
        )
        
        st.markdown("<div style='flex-grow: 1; height: 100px;'></div>", unsafe_allow_html=True)
        
        # User & Logout
        st.markdown(f"""
            <div class='sidebar-user'>
                <div style='display: flex; flex-direction: column; gap: 4px;'>
                    <span class="role-badge {role_class}" style="position: static; margin-bottom: 8px; width: fit-content;">{role_label}</span>
                    <div style='font-size: 0.8rem; opacity: 0.7;'>Connecté en tant que</div>
                    <div style='font-weight: 600; font-size: 1rem;'>{st.session_state.get('user_name', 'Utilisateur')}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("Déconnexion", use_container_width=True):
            st.session_state.user = None
            st.session_state.authenticated = False
            st.query_params.clear()
            st.rerun()
            
    return menu_dict[selected_label]
