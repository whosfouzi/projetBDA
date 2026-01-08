import streamlit as st
import pandas as pd
from backend.db import run_query

def show_dept_preview():
    user = st.session_state.user
    if user['type_utilisateur'] != 'chef_departement':
        st.error("Accès réservé aux Chefs de Département.")
        return

    # 1. Fetch Dept Info
    dept_info = run_query(f"""
        SELECT d.id_dep, d.nom 
        FROM professeur p 
        JOIN departement d ON p.id_departement = d.id_dep 
        WHERE p.id_professeur = {user['id_professeur']}
    """)
    if not dept_info:
        st.error("Impossible de récupérer les informations du département.")
        return
    
    dept_id = dept_info[0]['id_dep']
    dept_name = dept_info[0]['nom']

    st.title(f"🔍 Aperçu du Planning : {dept_name}")
    st.markdown("Examinez le planning généré par l'administration avant de procéder à la validation officielle.")

    # 2. Fetch Exams for this Dept
    query = """
    SELECT 
        e.date_examen as Date,
        e.heure_debut as Heure,
        m.code_module as Code,
        m.nom as Module,
        s.nom as Salle,
        spec.nom as Spécialité,
        CONCAT(p.prenom, ' ', p.nom) as Surveillant
    FROM examen e
    JOIN module m ON e.id_module = m.id_module
    JOIN specialite spec ON m.id_spec = spec.id_spec
    JOIN annee_etude a ON spec.id_annee = a.id_annee
    JOIN salle s ON e.id_salle = s.id_salle
    LEFT JOIN professeur p ON e.id_professeur = p.id_professeur
    WHERE a.id_dep = %s
    ORDER BY e.date_examen, e.heure_debut
    """
    data = run_query(query, (dept_id,))
    
    if not data:
        st.info("Aucun examen n'est encore planifié pour votre département.")
    else:
        df = pd.DataFrame(data)
        
        # Filters
        st.sidebar.subheader("Filtres d'aperçu")
        all_specs = sorted(df['Spécialité'].unique())
        selected_spec = st.sidebar.multiselect("Filtrer par Spécialité", all_specs, default=all_specs)
        
        filtered_df = df[df['Spécialité'].isin(selected_spec)]
        
        st.markdown(f"**Total : {len(filtered_df)} examens dans l'aperçu.**")
        
        # Formatting Time
        def format_time(t):
            if pd.isnull(t): return ""
            try:
                if hasattr(t, 'total_seconds'): 
                    seconds = int(t.total_seconds())
                    hours = (seconds // 3600) % 24
                    minutes = (seconds % 3600) // 60
                    return f"{hours:02d}:{minutes:02d}"
                s = str(t)
                if ":" in s:
                    parts = s.split(":")
                    return f"{int(parts[0]):02d}:{int(parts[1]):02d}"
                return s[:5]
            except:
                return str(t)
        
        filtered_df['Heure'] = filtered_df['Heure'].apply(format_time)

        # Export CSV Button
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Télécharger l'Aperçu (CSV)",
            data=csv,
            file_name=f"apercu_planning_{dept_name.replace(' ', '_')}.csv",
            mime='text/csv'
        )

        st.dataframe(
            filtered_df,
            column_config={
                "Date": st.column_config.DateColumn("Date", format="DD/MM/YYYY"),
            },
            use_container_width=True,
            hide_index=True
        )

        st.divider()
        st.info("💡 Si le planning vous convient, retournez sur votre Tableau de Bord pour le valider officiellement.")
