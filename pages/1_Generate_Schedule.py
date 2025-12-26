import streamlit as st
import pandas as pd
from datetime import datetime, date

st.set_page_config(page_title="Générateur de Planning", page_icon="⚙️", layout="wide")

# Check Auth
if 'user' not in st.session_state or not st.session_state.user:
    st.error("Veuillez vous connecter.")
    st.stop()

# Check Role
if st.session_state.user['type_utilisateur'] not in ['admin_examens', 'vice_doyen']:
    st.error("⛔ Accès refusé. Cette page est réservée aux administrateurs.")
    st.stop()

st.title("⚙️ Générateur Automatique")
st.markdown("Algorithme d'optimisation d'emploi du temps.")

with st.form("config_gen"):
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Date de début des examens", date.today())
    with col2:
        days = st.number_input("Durée de la session (jours)", min_value=1, max_value=30, value=14)
        
    submit = st.form_submit_button("Lancer la Génération", type="primary")

if submit:
    st.info("🚀 Démarrage de l'algorithme...")
    
    from backend.scheduler import GreedyScheduler
    
    try:
        # Init Scheduler
        scheduler = GreedyScheduler(start_date=start_date, days=days)
        
        with st.spinner("Calcul en cours (Analyse des conflits, disponibilités, etc.)..."):
            scheduler.solve()
            results = scheduler.save()
        
        st.success("✅ Planning généré et sauvegardé !")
        st.balloons()
        
        # Results
        m1, m2 = st.columns(2)
        m1.metric("Examens Placés", results['assigned'])
        m2.metric("Non Placés", len(results['unscheduled']))
        
        if results['unscheduled']:
            st.warning(f"⚠️ Modules non planifiés : {results['unscheduled']}")
            
        st.caption("Les données sont maintenant visibles dans l'Explorateur de Base de Données (Table 'examen').")
            
    except Exception as e:
        st.error(f"Erreur technique : {e}")
