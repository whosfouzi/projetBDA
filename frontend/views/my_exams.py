import streamlit as st
import pandas as pd
from backend.db import run_query

def show_my_exams():
    user = st.session_state.user
    role = user['type_utilisateur']
    
    st.title(f"🎓 Mon Planning ({role.replace('_', ' ').capitalize()})")

    def get_student_exams(student_id):
        query = """
        SELECT 
            e.date_examen as Date,
            e.heure_debut as Heure,
            m.code_module as Code,
            m.nom as Module,
            s.nom as Salle,
            CONCAT(p.prenom, ' ', p.nom) as Surveillant
        FROM etudiant stu
        JOIN module m ON stu.id_spec = m.id_spec
        JOIN examen e ON m.id_module = e.id_module
        JOIN salle s ON e.id_salle = s.id_salle
        JOIN professeur p ON e.id_professeur = p.id_professeur
        WHERE stu.id_etudiant = %s
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
            spec.nom as Spécialité
        FROM examen e
        JOIN module m ON e.id_module = m.id_module
        JOIN specialite spec ON m.id_spec = spec.id_spec
        JOIN salle s ON e.id_salle = s.id_salle
        WHERE e.id_professeur = %s
        ORDER BY e.date_examen, e.heure_debut
        """
        return run_query(query, (prof_id,))

    df = pd.DataFrame()
    is_validated = False
    id_dep = None

    if role == 'etudiant':
        # Get Dept
        res_dep = run_query("""
            SELECT a.id_dep 
            FROM etudiant e 
            JOIN specialite s ON e.id_spec = s.id_spec 
            JOIN annee_etude a ON s.id_annee = a.id_annee 
            WHERE e.id_etudiant = %s
        """, (user['id_etudiant'],))
        if res_dep: id_dep = res_dep[0]['id_dep']
        
        # Check Validation
        if id_dep:
            v = run_query("SELECT est_valide FROM validation_edt WHERE id_dep = %s AND session_nom = 'Janvier 2026'", (id_dep,))
            is_validated = v[0]['est_valide'] if v else False

        if is_validated:
            data = get_student_exams(user['id_etudiant'])
            df = pd.DataFrame(data)
        else:
            st.warning("⏳ Le planning de votre département est en attente de validation par le Chef de Département.")

    elif role == 'professeur':
        # Get Dept
        res_dep = run_query("SELECT id_departement FROM professeur WHERE id_professeur = %s", (user['id_professeur'],))
        if res_dep: id_dep = res_dep[0]['id_departement']
        
        # Check Validation
        if id_dep:
            v = run_query("SELECT est_valide FROM validation_edt WHERE id_dep = %s AND session_nom = 'Janvier 2026'", (id_dep,))
            is_validated = v[0]['est_valide'] if v else False

        if is_validated:
            data = get_prof_exams(user['id_professeur'])
            df = pd.DataFrame(data)
        else:
            st.warning("⏳ Le planning de votre département est en attente de validation par le Chef de Département.")

    elif role == 'admin_examens' or role == 'vice_doyen' or role == 'chef_departement':
        st.info("Cette vue est réservée aux Étudiants et Professeurs pour leur planning personnel.")
    
    if not df.empty:
        # Format Time
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
        df['Heure'] = df['Heure'].apply(format_time)
        st.dataframe(df, use_container_width=True, hide_index=True)
    elif is_validated:
        st.info("Rien à afficher.")
