import streamlit as st
from datetime import date
from backend.scheduler import GreedyScheduler

def show_generate():
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
        try:
            scheduler = GreedyScheduler(start_date=start_date, days=days)
            with st.spinner("Calcul en cours..."):
                scheduler.solve()
                results = scheduler.save()
            
            st.success("✅ Planning généré et sauvegardé !")
            m1, m2 = st.columns(2)
            m1.metric("Examens Placés", results['assigned'])
            m2.metric("Non Placés", len(results['unscheduled']))
            
            if results['unscheduled']:
                st.warning(f"⚠️ Modules non planifiés : {results['unscheduled']}")
                
        except Exception as e:
            st.error(f"Erreur technique : {e}")
