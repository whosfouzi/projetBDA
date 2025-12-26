import streamlit as st
import pandas as pd
from backend.db import run_query

st.set_page_config(page_title="Emploi du Temps", page_icon="📅", layout="wide")

def load_css():
    """Charge le fichier de style personnalisé."""
    with open("frontend/assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

def get_real_exams():
    """Récupère tous les examens depuis la BDD."""
    query = """
    SELECT 
        e.id_examen,
        e.date_examen AS Date, 
        TIME_FORMAT(e.heure_debut, '%H:%i') AS Heure,
        m.nom AS Cours,
        d.nom AS Département,
        s.nom AS Salle,
        f.nom AS Formation
    FROM examen e
    JOIN module m ON e.id_module = m.id_module
    JOIN formation f ON m.id_formation = f.id_formation
    JOIN departement d ON f.id_departement = d.id_dep
    LEFT JOIN salle s ON e.id_salle = s.id_salle
    ORDER BY e.date_examen, e.heure_debut
    """
    data = run_query(query)
    # Convert dates to datetime for filtering compatibility
    df = pd.DataFrame(data)
    if not df.empty:
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date']).dt.date
    return df

st.title("📅 Emploi du Temps Global")

# Check Auth
if 'role' not in st.session_state or not st.session_state.role:
    st.warning("Veuillez vous connecter sur le Dashboard.")
    st.stop()

# Load Data
df = get_real_exams()

if df.empty:
    st.info("Aucun examen trouvé dans la base de données.")
    st.stop()

# Sidebar Filters
st.sidebar.header("Filtres")
dept_filter = st.sidebar.multiselect("Département", options=df['Département'].unique())
formation_filter = st.sidebar.multiselect("Formation", options=df['Formation'].unique())

filtered_df = df.copy()

if dept_filter:
    filtered_df = filtered_df[filtered_df['Département'].isin(dept_filter)]
if formation_filter:
    filtered_df = filtered_df[filtered_df['Formation'].isin(formation_filter)]

# Display
st.metric("Examens Affichés", len(filtered_df))

if not filtered_df.empty:
    st.dataframe(
        filtered_df[['Date', 'Heure', 'Cours', 'Département', 'Salle', 'Formation']],
        width="stretch",
        height=600,
        hide_index=True
    )
    
    # Export
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Télécharger en CSV",
        data=csv,
        file_name='emploi_du_temps_reel.csv',
        mime='text/csv',
    )
else:
    st.info("Aucun examen trouvé pour ces critères.")
