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
            
            st.success(f"✅ Planning généré avec succès ! ({results['assigned']} créneaux)")
            st.markdown("---")
            
            # --- SMART MATRIX VISUALIZATION ---
            from backend.db import run_query
            import pandas as pd
            
            # 1. Fetch Basic Exam Data
            q_exams = f"""
            SELECT 
                e.id_examen, e.date_examen as Date, e.heure_debut as Heure,
                m.id_module, m.code_module as Code, m.nom as Module, s.nom as Salle
            FROM examen e
            JOIN module m ON e.id_module = m.id_module
            JOIN salle s ON e.id_salle = s.id_salle
            WHERE e.date_examen >= '{start_date}'
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

            if not df_exams.empty:
                # 3. Smart Allocation & Grouping
                spec_grid = {} 
                occupancy = {r['id_examen']: r['nb_etudiants_inscrits'] 
                            for r in run_query("SELECT id_examen, nb_etudiants_inscrits FROM cache_capacite_examens")}
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
                        session_key = (d, h, code, m_name)
                        spec_grid[s_name][session_key] = []
                        
                        while s_rem > 0 and exam_idx < len(sorted_exams):
                            spec_grid[s_name][session_key].append({
                                "group": f"G{g_count}",
                                "salle": sorted_exams[exam_idx]['Salle']
                            })
                            
                            take = min(s_rem, current_room_rem)
                            s_rem -= take
                            current_room_rem -= take
                            
                            if current_room_rem <= 0:
                                exam_idx += 1
                                if exam_idx < len(sorted_exams):
                                    current_room_rem = occupancy.get(sorted_exams[exam_idx]['id_examen'], 0)
                            g_count += 1

                # Selectbox by Speciality
                all_s_names = sorted(df_counts['Specialite'].unique())
                selected_spec = st.selectbox("Sélectionnez une Spécialité pour voir les résultats", all_s_names)
                
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

                s_sessions = spec_grid.get(selected_spec, {})
                if not s_sessions:
                    st.info(f"Aucun examen pour {selected_spec}.")
                else:
                    flat_rows = []
                    for (d, h, code, m_name), rooms in s_sessions.items():
                        salle_list = ", ".join(list(set(r['salle'] for r in rooms)))
                        flat_rows.append({
                            "Date": d,
                            "Heure": format_time(h),
                            "Code": code,
                            "Module": m_name,
                            "Salles": salle_list
                        })
                    
                    df_s = pd.DataFrame(flat_rows).sort_values(['Date', 'Heure'])
                    if df_s.empty:
                        st.info(f"Aucun examen pour {selected_spec}.")
                    else:
                        st.markdown(f"### 🗓️ Résultats : {selected_spec}")
                        st.dataframe(
                            df_s[["Date", "Heure", "Code", "Module", "Salles"]],
                            column_config={
                                "Date": st.column_config.DateColumn("Date", format="DD/MM/YYYY"),
                            },
                            use_container_width=True,
                            hide_index=True
                        )
            else:
                st.warning("Aucun examen généré.")
                
        except Exception as e:
            st.error(f"Erreur technique : {e}")
            import traceback
            st.code(traceback.format_exc())


