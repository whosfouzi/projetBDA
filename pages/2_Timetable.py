import streamlit as st
import pandas as pd
from backend.db import run_query

st.set_page_config(page_title="Emploi du Temps Global", page_icon="📅", layout="wide")

st.title("📅 Planning Global des Examens")

# Check permissions? No, public view usually, or at least logged in.
if 'user' not in st.session_state or not st.session_state.user:
    st.warning("Veuillez vous connecter pour voir le planning.")
    st.stop()

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
    # 1. Filters
    st.sidebar.header("Filtres")
    
    # Filter by Formation
    all_formations = sorted(df['Formation'].unique())
    selected_formation = st.sidebar.multiselect("Formation", all_formations)
    
    # Filter by Date
    all_dates = sorted(df['Date'].unique())
    selected_date = st.sidebar.date_input("Date", [])
    
    # Apply Filters
    if selected_formation:
        df = df[df['Formation'].isin(selected_formation)]
        
    if selected_date:
        # Handle date_input returning a tuple/list
        if isinstance(selected_date, (list, tuple)):
             if len(selected_date) > 0:
                 pass 
        else:
             df = df[df['Date'] == selected_date]

    # 2. Display
    st.dataframe(
        df,
        column_config={
            "Date": st.column_config.DateColumn("Date", format="DD/MM/YYYY"),
            "Heure": st.column_config.TimeColumn("Heure", format="HH:mm"),
        },
        use_container_width=True,
        hide_index=True
    )
    
    st.caption(f"Total: {len(df)} examens affichés.")
