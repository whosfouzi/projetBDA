import streamlit as st
import pandas as pd
import altair as alt
from backend.db import run_query

st.set_page_config(page_title="Statistiques", page_icon="📊", layout="wide")

def load_css():
    """Charge le fichier de style personnalisé."""
    with open("frontend/assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

st.title("📊 Analyse & Statistiques")

# Query Data for Stats
def get_stats_real():
    # 1. Exams per Dept
    q_dept = """
        SELECT d.nom as Département, COUNT(e.id_examen) as count
        FROM examen e
        JOIN module m ON e.id_module = m.id_module
        JOIN formation f ON m.id_formation = f.id_formation
        JOIN departement d ON f.id_departement = d.id_dep
        GROUP BY d.nom
    """
    df_dept = pd.DataFrame(run_query(q_dept))

    # 2. Exams per Hour
    q_time = """
        SELECT TIME_FORMAT(heure_debut, '%H:%i') as Heure, COUNT(*) as count
        FROM examen
        GROUP BY heure_debut
    """
    df_time = pd.DataFrame(run_query(q_time))

    # 3. Room Usage
    q_room = """
        SELECT s.nom as Salle, COUNT(e.id_examen) as count
        FROM examen e
        JOIN salle s ON e.id_salle = s.id_salle
        GROUP BY s.nom
        ORDER BY count DESC
        LIMIT 10
    """
    df_room = pd.DataFrame(run_query(q_room))
    
    return df_dept, df_time, df_room

df_dept, df_time, df_room = get_stats_real()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Répartition par Département")
    if not df_dept.empty:
        chart = alt.Chart(df_dept).mark_bar().encode(
            x='Département',
            y='count',
            color='Département'
        ).properties(height=300)
        st.altair_chart(chart, width="stretch")
    else:
        st.info("Pas assez de données pour les départements.")

with col2:
    st.subheader("Distribution Horaire")
    if not df_time.empty:
        chart = alt.Chart(df_time).mark_arc().encode(
            theta='count',
            color='Heure'
        ).properties(height=300)
        st.altair_chart(chart, width="stretch")
    else:
        st.info("Pas assez de données horaires.")

st.subheader("Top 10 Salles les plus utilisées")
if not df_room.empty:
    chart = alt.Chart(df_room).mark_bar().encode(
        x='Salle',
        y='count'
    ).properties(height=300)
    st.altair_chart(chart, width="stretch")
else:
    st.info("Pas assez de données de salles.")
