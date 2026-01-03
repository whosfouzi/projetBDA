import streamlit as st

def Navbar(menu_dict):
    """
    Renders an Aside (Sidebar) navigation bar.
    """
    with st.sidebar:
        # Branding
        st.markdown("""
            <div class='sidebar-header'>
                <h1 style='color: white !important; font-size: 1.5rem !important; margin: 0 !important;'>🎓 UMBB EXAM</h1>
                <p style='color: #94a3b8; font-size: 0.8rem;'>Sciences Portal</p>
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
        
        st.markdown("<div style='flex-grow: 1;'></div>", unsafe_allow_html=True)
        
        # User & Logout
        st.markdown(f"""
            <div class='sidebar-user'>
                <div style='font-size: 0.8rem; opacity: 0.7;'>Connecté en tant que</div>
                <div style='font-weight: 600;'>{st.session_state.get('user_name', 'Utilisateur')}</div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("Déconnexion", use_container_width=True):
            st.session_state.user = None
            st.session_state.authenticated = False
            st.query_params.clear()
            st.rerun()
            
    return menu_dict[selected_label]
