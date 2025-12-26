import streamlit as st
import pandas as pd
from backend.db import run_query

def show_timetable():
    st.title("📅 Planning Global des Examens")

    def get_exams():
        query = """
        SELECT 
            e.date_examen as Date,
            e.heure_debut as Heure,
            m.code_module as Code,
            m.nom as Module,
            f.nom as Formation,
            CONCAT(p.prenom, ' ', p.nom) as Surveillant,
            s.nom as Salle
        FROM examen e
        JOIN module m ON e.id_module = m.id_module
        JOIN formation f ON m.id_formation = f.id_formation
        JOIN professeur p ON e.id_professeur = p.id_professeur
        JOIN salle s ON e.id_salle = s.id_salle
        ORDER BY e.date_examen, e.heure_debut
        """
        data = run_query(query)
        return pd.DataFrame(data)

    df = get_exams()

    if df.empty:
        st.info("Aucun examen programmé pour le moment.")
    else:
        # Filters
        with st.expander("Filtres", expanded=True):
            col1, col2 = st.columns(2)
            all_formations = sorted(df['Formation'].unique())
            selected_formation = col1.multiselect("Formation", all_formations)
            
            all_dates = sorted(df['Date'].unique())
            # selected_date = col2.date_input("Date", [])

        if selected_formation:
            df = df[df['Formation'].isin(selected_formation)]

        st.dataframe(
            df,
            column_config={
                "Date": st.column_config.DateColumn("Date", format="DD/MM/YYYY"),
                "Heure": st.column_config.TimeColumn("Heure", format="HH:mm"),
            },
            use_container_width=True,
            hide_index=True
        )
