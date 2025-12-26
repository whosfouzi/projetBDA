import streamlit as st
import pandas as pd
from datetime import time, datetime

st.set_page_config(page_title="Générateur Auto", page_icon="⚙️", layout="wide")

def load_css():
    """Charge le fichier de style personnalisé."""
    with open("frontend/assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

st.title("⚙️ Génération d'Emploi du Temps")
st.markdown("Configurez les contraintes et lancez l'algorithme d'optimisation.")

# Check Permissions
if 'role' not in st.session_state or st.session_state.role != 'admin_examens':
    st.error("⛔ Accès refusé. Réservé aux administrateurs.")
    st.stop()

# Formulaire de Configuration
with st.form("generation_config"):
    col1, col2 = st.columns(2)
    
    with col1:
        session_name = st.text_input("Nom de la Session", value="Session Hiver 2024")
        dept_select = st.multiselect("Départements Concernés", ["Informatique", "Mathématiques", "Physique", "Biologie"])
        
    with col2:
        date_range = st.date_input("Période d'Examens", [])
        
    st.subheader("Contraintes")
    c1, c2 = st.columns(2)
    with c1:
        max_exams_student = st.number_input("Max examens/étudiant/jour", 1, 3, 2)
    with c2:
        min_surveillance = st.number_input("Min surveillants/salle", 1, 5, 2)
        
    submit = st.form_submit_button("Lancer la Génération")

if submit:
    st.info("🚀 Démarrage de l'algorithme d'optimisation (Greedy)...")
    st.caption("Cette opération peut prendre quelques instants...")
    
    from backend.scheduler import GreedyScheduler
    
    # Init Scheduler
    start_date = date_range[0] if date_range else datetime.now().date()
    scheduler = GreedyScheduler(start_date=start_date, days=14)
    
    # Run
    try:
        with st.spinner("Calcul du planning en cours..."):
            scheduler.solve()
            results = scheduler.save()
            
        st.success(f"✅ Génération terminée ! {results['assigned']} examens planifiés.")
        st.balloons()
        
        # Stats
        st.subheader("📊 Résultats")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Examens Placés", results['assigned'])
        with col2:
            st.metric("Non Planifiés", len(results['unscheduled']))
            
        if results['unscheduled']:
            st.warning(f"⚠️ Impossible de placer : {', '.join(results['unscheduled'])}")
            
        st.caption("Les données ont été sauvegardées dans la base de données MySQL.")
        
    except Exception as e:
        st.error(f"Erreur durant l'exécution : {e}")
