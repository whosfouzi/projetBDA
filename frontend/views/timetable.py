import streamlit as st
import pandas as pd
from backend.db import run_query

def show_timetable():
    st.title("📅 Planning Global des Examens")

    # 1. Fetch Basic Exam Data
    q_exams = """
    SELECT 
        e.id_examen, e.date_examen as Date, e.heure_debut as Heure,
        m.id_module, m.code_module as Code, m.nom as Module,
        s.nom as Salle, s.capacite as TotalCap, CONCAT(p.prenom, ' ', p.nom) as Surveillant,
        c.nb_etudiants_inscrits as Occupied
    FROM examen e
    JOIN module m ON e.id_module = m.id_module
    JOIN salle s ON e.id_salle = s.id_salle
    LEFT JOIN professeur p ON e.id_professeur = p.id_professeur
    LEFT JOIN cache_capacite_examens c ON e.id_examen = c.id_examen
    ORDER BY e.date_examen, e.heure_debut, s.nom
    """
    df_exams = pd.DataFrame(run_query(q_exams))
    
    # 2. Fetch Student Counts per Speciality per Module (Implicit)
    q_counts = """
    SELECT m.id_module, s.nom as Specialite, COUNT(e.id_etudiant) as nb
    FROM module m
    JOIN specialite s ON m.id_spec = s.id_spec
    LEFT JOIN etudiant e ON s.id_spec = e.id_spec
    GROUP BY m.id_module, s.id_spec
    """
    df_counts = pd.DataFrame(run_query(q_counts))

    if df_exams.empty:
        st.info("Aucun examen programmé.")
        return

    # 3. Smart Allocation & Grouping
    # Mapping: (Specialite, Date, Heure, Code) -> List of {group_label, salle, surveillant}
    spec_grid = {} # {s_name: { (d, h, code): [rooms] }}
    
    occupancy = {r['id_examen']: r['nb_etudiants_inscrits'] for r in run_query("SELECT id_examen, nb_etudiants_inscrits FROM cache_capacite_examens")}
    sessions = df_exams.groupby(['id_module', 'Date', 'Heure', 'Code', 'Module'])
    
    for (mid, d, h, code, m_name), session_exams in sessions:
        sorted_exams = session_exams.sort_values('Salle').to_dict('records')
        mod_counts = df_counts[df_counts['id_module'] == mid].to_dict('records')
        
        exam_idx = 0
        current_room_rem = occupancy.get(sorted_exams[exam_idx]['id_examen'], 0) if sorted_exams else 0
        
        for s_count in mod_counts:
            s_name = s_count['Specialite']
            s_rem = s_count['nb']
            g_count = 1
            
            if s_name not in spec_grid: spec_grid[s_name] = {}
            # Session key now carries the full name
            session_key = (d, h, code, m_name)
            spec_grid[s_name][session_key] = []
            
            while s_rem > 0 and exam_idx < len(sorted_exams):
                room_data = sorted_exams[exam_idx]
                
                # Assign this room to the Specialite with a group label
                spec_grid[s_name][session_key].append({
                    "group": f"G{g_count}",
                    "salle": room_data['Salle'],
                    "prof": room_data['Surveillant']
                })
                
                take = min(s_rem, current_room_rem)
                s_rem -= take
                current_room_rem -= take
                
                if current_room_rem <= 0:
                    exam_idx += 1
                    if exam_idx < len(sorted_exams):
                        current_room_rem = occupancy.get(sorted_exams[exam_idx]['id_examen'], 0)
                
                g_count += 1

    # 4. Display Logic
    user = st.session_state.get('user', {})
    role = user.get('type_utilisateur') if user else None
    
    # Time Formatting helper for the dataframe
    def format_time(t):
        if pd.isnull(t): return ""
        if hasattr(t, 'total_seconds'): 
            seconds = int(t.total_seconds())
            hours = (seconds // 3600) % 24
            minutes = (seconds % 3600) // 60
            return f"{hours:02d}:{minutes:02d}"
        return str(t)[:5]
    df_exams['Heure'] = df_exams['Heure'].apply(format_time)

    # Effective Capacity logic for Admin
    res_limit = run_query("SELECT valeur FROM configuration_contraintes WHERE nom = 'max_etudiants_par_salle'")
    global_limit = res_limit[0]['valeur'] if res_limit else 20
    df_exams['Capacité'] = df_exams.apply(lambda x: f"{int(x['Occupied'])} / {min(int(x['TotalCap'] if 'TotalCap' in x else 0), global_limit)}", axis=1)

    # Selectbox by Speciality
    all_s_names = sorted(df_counts['Specialite'].unique())
    selected_spec = st.selectbox("Sélectionnez une Spécialité", all_s_names)
    
    cols_to_show = ['Date', 'Heure', 'Code', 'Module', 'Surveillant', 'Salle']
    if role in ['admin_examens', 'vice_doyen']:
        cols_to_show.append('Capacité')

    # Each Specialite sees the specific rooms assigned to it
    s_sessions = spec_grid.get(selected_spec, {})
    if not s_sessions:
        st.info(f"Aucun examen pour {selected_spec}.")
    else:
        # Flatten the grid into a list
        flat_rows = []
        for (d, h, code, m_name), rooms in s_sessions.items():
            for r in rooms:
                flat_rows.append({
                    "Date": d,
                    "Heure": format_time(h),
                    "Code": code,
                    "Module": m_name,
                    "Salle": r['salle'],
                    "Surveillant": r['prof'],
                    "Groupe": r['group']
                })
        
        df_s = pd.DataFrame(flat_rows)
        if df_s.empty:
            st.info(f"Aucun examen pour {selected_spec}.")
        else:
            st.markdown(f"### 📅 Emploi du Temps : {selected_spec}")
            st.dataframe(
                df_s[["Date", "Heure", "Code", "Module", "Groupe", "Salle", "Surveillant"]],
                column_config={
                    "Date": st.column_config.DateColumn("Date", format="DD/MM/YYYY"),
                },
                use_container_width=True,
                hide_index=True
            )
