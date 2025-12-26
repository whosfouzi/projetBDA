import streamlit as st
import pandas as pd
from backend.db import run_query

def show_my_exams():
    user = st.session_state.user
    role = user['type_utilisateur']
    
    st.title(f"🎓 Mon Planning ({role.replace('_', ' ').capitalize()})")

    def get_student_exams(student_id):
        # ... same query ...
        query = """
        SELECT 
            e.date_examen as Date,
            e.heure_debut as Heure,
            m.code_module as Code,
            m.nom as Module,
            s.nom as Salle,
            CONCAT(p.prenom, ' ', p.nom) as Surveillant
        FROM inscription i
        JOIN examen e ON i.id_module = e.id_module
        JOIN module m ON e.id_module = m.id_module
        JOIN salle s ON e.id_salle = s.id_salle
        JOIN professeur p ON e.id_professeur = p.id_professeur
        WHERE i.id_etudiant = %s
        ORDER BY e.date_examen, e.heure_debut
        """
        return run_query(query, (student_id,))

    def get_prof_exams(prof_id):
        query = """
        SELECT 
            e.date_examen as Date,
            e.heure_debut as Heure,
            m.code_module as Code,
            m.nom as Module,
            s.nom as Salle,
            f.nom as Formation
        FROM examen e
        JOIN module m ON e.id_module = m.id_module
        JOIN formation f ON m.id_formation = f.id_formation
        JOIN salle s ON e.id_salle = s.id_salle
        WHERE e.id_professeur = %s
        ORDER BY e.date_examen, e.heure_debut
        """
        return run_query(query, (prof_id,))

    df = pd.DataFrame()

    if role == 'etudiant':
        data = get_student_exams(user['id_etudiant'])
        df = pd.DataFrame(data)
    elif role == 'professeur':
        data = get_prof_exams(user['id_professeur'])
        df = pd.DataFrame(data)
    elif role == 'admin_examens' or role == 'vice_doyen': # If admin tests this view
        st.info("En tant qu'Admin, vous n'avez pas d'examens personnels. Voici une vue simulée vide.")
    
    if df.empty:
        st.info("Rien à afficher.")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)
