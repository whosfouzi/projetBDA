import streamlit as st

def Navbar(menu_dict):
    """
    Renders navigation in the sidebar using native Streamlit components.
    """
    with st.sidebar:
        # Header
        st.title("🎓 UMBB EXAM")
        st.caption("Sciences Portal")
        
        st.divider()
        
        # Navigation Menu
        st.subheader("Navigation")
        
        # Use buttons for each menu item
        for menu_label in menu_dict.keys():
            if st.button(menu_label, use_container_width=True, key=f"nav_{menu_label}"):
                st.session_state['selected_page'] = menu_label
        
        # Set default if not set
        if 'selected_page' not in st.session_state or st.session_state['selected_page'] not in menu_dict:
            st.session_state['selected_page'] = list(menu_dict.keys())[0]
        
        st.divider()
        
        # User Info
        user_name = st.session_state.get('user_name', 'Utilisateur')
        st.caption(f"👤 {user_name}")
        
        # Logout
        if st.button("🚪 Déconnexion", use_container_width=True, type="secondary"):
            st.session_state.user = None
            st.session_state.authenticated = False
            st.session_state.pop('selected_page', None)
            st.query_params.clear()
            st.rerun()
    
    # Return the selected page function
    selected_label = st.session_state.get('selected_page', list(menu_dict.keys())[0])
    return menu_dict[selected_label]
