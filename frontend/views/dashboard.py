import streamlit as st
import pandas as pd
from backend.db import run_query

def show_dashboard():
    st.title("📊 Tableau de Bord")
    
    # 1. KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    # Total Exams
    res_exams = run_query("SELECT COUNT(*) as c FROM examen")
    nb_exams = res_exams[0]['c'] if res_exams else 0
    col1.metric("Examens Planifiés", nb_exams)
    
    # Upcoming
    res_up = run_query("SELECT COUNT(*) as c FROM examen WHERE date_examen >= CURDATE()")
    nb_up = res_up[0]['c'] if res_up else 0
    col2.metric("À Venir", nb_up)
    
    # Students
    res_stud = run_query("SELECT COUNT(*) as c FROM etudiant")
    nb_stud = res_stud[0]['c'] if res_stud else 0
    col3.metric("Étudiants", nb_stud)
    
    # Conflicts
    # For now static, ideally dynamic
    col4.metric("Conflits Détectés", "0", delta="OK", delta_color="normal")

    st.markdown("### Accès Rapide")
    c1, c2 = st.columns(2)
    with c1:
        st.info("📅 **Planning Global**: Consultez l'emploi du temps complet.")
    with c2:
        st.info("🎓 **Mes Examens**: Votre emploi du temps personnalisé.")

    # Recent Activity
    st.markdown("### Prochains Examens")
    df_recent = pd.DataFrame(run_query("""
        SELECT e.date_examen, m.nom as Module, s.nom as Salle 
        FROM examen e 
        JOIN module m ON e.id_module = m.id_module
        JOIN salle s ON e.id_salle = s.id_salle
        WHERE e.date_examen >= CURDATE()
        ORDER BY e.date_examen ASC 
        LIMIT 5
    """))
    if not df_recent.empty:
        st.dataframe(df_recent, use_container_width=True, hide_index=True)
    else:
        st.caption("Aucun examen à venir.")
