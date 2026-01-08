import streamlit as st
import pandas as pd
from backend.db import run_query, get_connection
from datetime import date

# --- CUSTOM UI HELPERS ---
def card(title, value, sub="", role="neutral"):
    st.markdown(f"""
    <div class="academic-card">
        <span class="role-badge {role}">{role}</span>
        <h3>{title}</h3>
        <div class="value">{value}</div>
        <div class="sub">{sub}</div>
    </div>
    """, unsafe_allow_html=True)

# --- ROLE VIEWS ---

def show_admin_dashboard():
    st.markdown("<h1>🎓 Console d'Administration</h1>", unsafe_allow_html=True)
    
    # 1. Strategic KPIs
    c1, c2, c3, c4 = st.columns(4)
    
    # Fetch Data
    stats = run_query("""
        SELECT 
            (SELECT COUNT(*) FROM examen) as total_exams,
            (SELECT COUNT(*) FROM etudiant) as total_students,
            (SELECT COUNT(*) FROM professeur) as total_profs,
            (SELECT COUNT(*) FROM salle) as total_rooms
    """)[0]
    
    with c1: card("Examens Planifiés", stats['total_exams'], "Session Courante", "admin")
    with c2: card("Étudiants", stats['total_students'], "Inscrits", "student")
    with c3: card("Professeurs", stats['total_profs'], "Actifs", "prof")
    with c4: card("Salles", stats['total_rooms'], "Disponibles", "neutral")

    st.markdown("### 🛠️ Actions Rapides & Configuration")
    
    # Config Panel (Accordion Style)
    with st.expander("⚙️ Paramètres de Contraintes Globales", expanded=True):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT nom, valeur FROM configuration_contraintes")
        constraints = {row['nom']: row['valeur'] for row in cursor.fetchall()}
        conn.close()

        with st.form("admin_config"):
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                val1 = st.number_input("Max Examens/Étudiant/Jour", 1, 5, constraints.get('max_examens_etudiant_par_jour', 1))
            with c2:
                val2 = st.number_input("Max Surv./Prof/Jour", 1, 10, constraints.get('max_surveillances_prof_par_jour', 3))
            with c3:
                val3 = st.number_input("Capacité Strict Salle", 1, 500, constraints.get('max_etudiants_par_salle', 20))
            with c4:
                val4 = st.number_input("Durée (min)", 30, 240, constraints.get('duree_examen_minutes', 90), step=30)
                
            if st.form_submit_button("💾 Mettre à jour"):
                conn = get_connection()
                cur = conn.cursor()
                updates = [
                    ('max_examens_etudiant_par_jour', val1),
                    ('max_surveillances_prof_par_jour', val2),
                    ('max_etudiants_par_salle', val3),
                    ('duree_examen_minutes', val4)
                ]
                for n, v in updates:
                    cur.execute("UPDATE configuration_contraintes SET valeur=%s WHERE nom=%s", (v, n))
                conn.commit()
                conn.close()
                st.success("Configuration mise à jour!")
                st.rerun()

def show_prof_dashboard(user):
    st.markdown(f"<h1>👨‍🏫 Espace Enseignant <span style='font-weight:300; font-size:1.5rem'>| {user['nom']} {user['prenom']}</span></h1>", unsafe_allow_html=True)
    
    # Timeline for Today
    today = date.today()
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.markdown("### 📅 Vos Surveillances Aujourd'hui")
        today_exams = run_query(f"""
            SELECT e.heure_debut, s.nom as salle, m.nom as module, e.duree_minutes
            FROM surveillance surv
            JOIN examen e ON surv.id_examen = e.id_examen
            JOIN salle s ON e.id_salle = s.id_salle
            JOIN module m ON e.id_module = m.id_module
            WHERE surv.id_professeur = {user['id_professeur']} 
            AND e.date_examen = CURDATE()
            ORDER BY e.heure_debut
        """)
        
        if not today_exams:
            st.info("✅ Aucune surveillance prévue pour aujourd'hui.")
        else:
            for exam in today_exams:
                # Format Time
                h = exam['heure_debut']
                h_str = ""
                if hasattr(h, 'total_seconds'):
                    s = int(h.total_seconds())
                    h_str = f"{(s // 3600) % 24:02d}:{(s % 3600) // 60:02d}"
                else:
                    h_str = str(h)[:5]
                
                st.markdown(f"""
                <div class="timeline-grid">
                    <div style="font-weight:bold; color:var(--accent); font-size:1.2rem;">
                        {h_str}
                    </div>
                    <div>
                        <div style="font-weight:600; font-size:1.1rem;">{exam['module']}</div>
                        <div style="color:#64748b;">📍 {exam['salle']} • ⏱️ {exam['duree_minutes']} min</div>
                    </div>
                </div>
                <div style="height:10px;"></div>
                """, unsafe_allow_html=True)

    with c2:
        st.markdown("### 📊 Votre Charge")
        load = run_query(f"SELECT COUNT(*) as c FROM surveillance WHERE id_professeur={user['id_professeur']}")[0]['c']
        card("Total Surveillances", load, "Session 2024-2025", "prof")

def show_student_dashboard(user):
    st.markdown(f"<h1>🎓 Espace Étudiant <span style='font-weight:300; font-size:1.5rem'>| {user['nom']} {user['prenom']}</span></h1>", unsafe_allow_html=True)
    
    # Exam Permit Card
    st.markdown("### 🎫 Vos Prochains Examens")
    upcoming = run_query(f"""
        SELECT 
            e.date_examen, 
            e.heure_debut, 
            m.nom as module, 
            GROUP_CONCAT(s.nom SEPARATOR ', ') as salle
        FROM etudiant stu
        JOIN module m ON stu.id_spec = m.id_spec
        JOIN examen e ON m.id_module = e.id_module
        JOIN salle s ON e.id_salle = s.id_salle
        WHERE stu.id_etudiant = {user['id_etudiant']}
        AND e.date_examen >= CURDATE()
        GROUP BY e.id_module, e.date_examen, e.heure_debut
        ORDER BY e.date_examen, e.heure_debut
        LIMIT 10
    """)
    
    if not upcoming:
        st.success("🎉 Aucun examen à venir. Bonne révision !")
    else:
        df = pd.DataFrame(upcoming)
        # Format Time
        def format_time(t):
            if pd.isnull(t): return ""
            try:
                if hasattr(t, 'total_seconds'): 
                    seconds = int(t.total_seconds())
                    return f"{(seconds // 3600) % 24:02d}:{(seconds % 3600) // 60:02d}"
                s = str(t)
                if ":" in s:
                    parts = s.split(":")
                    return f"{int(parts[0]):02d}:{int(parts[1]):02d}"
                return s[:5]
            except:
                return str(t)
        df['heure_debut'] = df['heure_debut'].apply(format_time)
        st.dataframe(df, use_container_width=True, hide_index=True)


# --- MAIN ROUTER ---
def show_vice_doyen_dashboard(user):
    u_nom = user.get('nom') or 'Doyen'
    u_prenom = user.get('prenom') or ''
    st.markdown(f"<h1>🏛️ Cabinet du Vice-Doyen <span style='font-weight:300; font-size:1.5rem'>| {u_nom} {u_prenom}</span></h1>", unsafe_allow_html=True)
    
    # 1. Global KPIs
    c1, c2, c3, c4 = st.columns(4)
    
    # KPI Queries
    usage = run_query("SELECT (SUM(nb_etudiants_inscrits) / SUM(capacite_salle) * 100) as rate FROM cache_capacite_examens")[0]['rate'] or 0
    total_exams = run_query("SELECT COUNT(*) as c FROM examen")[0]['c']
    conflicts = run_query("""
        SELECT COUNT(*) as c FROM (
            SELECT id_etudiant, date_examen FROM etudiant_examens_jour WHERE nb_examens > 1
        ) as t
    """)[0]['c']
    prof_avg = run_query("SELECT AVG(total_surveillances) as avg_load FROM professeur")[0]['avg_load'] or 0

    with c1: card("Taux Occupation Salles", f"{usage:.1f}%", "Efficacité spatiale", "admin")
    with c2: card("Examens Totaux", total_exams, "Planifiés", "neutral")
    with c3: card("Conflits Étudiants", conflicts, "Non respect règle 1/jour", "student" if conflicts == 0 else "neutral")
    with c4: card("Charge Moy. Prof", f"{prof_avg:.1f}", "Surveillances / prof", "prof")

    # 2. Strategic Charts
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("### 📊 Examens par Département")
        dept_stats = run_query("""
            SELECT d.nom, COUNT(e.id_examen) as nb_exams
            FROM departement d
            JOIN annee_etude a ON d.id_dep = a.id_dep
            JOIN specialite s ON a.id_annee = s.id_annee
            JOIN module m ON s.id_spec = m.id_spec
            JOIN examen e ON m.id_module = e.id_module
            GROUP BY d.id_dep
        """)
        if dept_stats:
            df_dept = pd.DataFrame(dept_stats)
            st.bar_chart(df_dept.set_index('nom'), color="#3b82f6")

    with col_b:
        st.markdown("### 🛡️ Taux de Conflits par Département")
        # PDF Req: "Taux de conflits par département"
        conflict_stats = run_query("""
            SELECT d.nom, COUNT(DISTINCT c.id_etudiant) as nb_conflits
            FROM departement d
            JOIN annee_etude a ON d.id_dep = a.id_dep
            JOIN specialite s ON a.id_annee = s.id_annee
            JOIN etudiant stu ON s.id_spec = stu.id_spec
            JOIN etudiant_examens_jour c ON stu.id_etudiant = c.id_etudiant
            WHERE c.nb_examens > 1
            GROUP BY d.id_dep
        """)
        if conflict_stats:
            df_conf = pd.DataFrame(conflict_stats)
            st.bar_chart(df_conf.set_index('nom'), color="#ef4444")
        else:
            st.success("✅ Aucun conflit dans l'ensemble de la faculté.")

    st.markdown("### 👨‍🏫 Charge de Surveillance (Distribution)")
    # PDF Req: "KPIs académiques (heures profs)"
    prof_data = run_query("SELECT total_surveillances FROM professeur WHERE total_surveillances > 0")
    if prof_data:
        df_prof = pd.DataFrame(prof_data)
        st.area_chart(df_prof['total_surveillances'].value_counts().sort_index(), color="#10b981")
    
    st.markdown("### 🏛️ Occupation Globale des Salles & Amphis")
    # PDF Req: "Vue stratégique globale : occupation globale des amphis et salles"
    room_stats = run_query("""
        SELECT 
            CASE WHEN s.capacite > 50 THEN 'Amphithéâtres' ELSE 'Salles de TD' END as Categorie,
            COUNT(DISTINCT e.id_examen) as Nb_Exams,
            SUM(c.nb_etudiants_inscrits) as Total_Etudiants
        FROM salle s
        LEFT JOIN examen e ON s.id_salle = e.id_salle
        LEFT JOIN cache_capacite_examens c ON e.id_examen = c.id_examen
        GROUP BY Categorie
    """)
    if room_stats:
        col1, col2 = st.columns(2)
        df_rooms = pd.DataFrame(room_stats)
        with col1:
            st.markdown("**Répartition des Examens**")
            st.bar_chart(df_rooms.set_index('Categorie')['Nb_Exams'], color="#6366f1")
        with col2:
            st.markdown("**Volume Étudiant par Type**")
            st.bar_chart(df_rooms.set_index('Categorie')['Total_Etudiants'], color="#8b5cf6")

    st.markdown("### ✅ État des Validations Administrative")
    validations = run_query("""
        SELECT d.nom as Département, IF(v.est_valide, '✅ Validé', '⏳ En attente') as Statut, v.date_validation
        FROM departement d
        LEFT JOIN validation_edt v ON d.id_dep = v.id_dep AND v.session_nom = 'Janvier 2026'
    """)
    st.table(validations)

def show_chef_departement_dashboard(user):
    # Fetch Dept Info
    dept_info = run_query(f"""
        SELECT d.id_dep, d.nom 
        FROM professeur p 
        JOIN departement d ON p.id_departement = d.id_dep 
        WHERE p.id_professeur = {user['id_professeur']}
    """)[0]
    
    st.markdown(f"<h1>📋 Département {dept_info['nom']} <span style='font-weight:300; font-size:1.5rem'>| Chef: {user.get('nom', 'Responsable')}</span></h1>", unsafe_allow_html=True)
    
    # 1. Dept KPIs
    c1, c2, c3 = st.columns(3)
    
    dept_id = dept_info['id_dep']
    stats = run_query(f"""
        SELECT 
            (SELECT COUNT(*) FROM examen e JOIN module m ON e.id_module = m.id_module JOIN specialite s ON m.id_spec = s.id_spec JOIN annee_etude a ON s.id_annee = a.id_annee WHERE a.id_dep = {dept_id}) as exams,
            (SELECT COUNT(*) FROM etudiant e JOIN specialite s ON e.id_spec = s.id_spec JOIN annee_etude a ON s.id_annee = a.id_annee WHERE a.id_dep = {dept_id}) as students,
            (SELECT COUNT(*) FROM professeur WHERE id_departement = {dept_id}) as profs
    """)[0]
    
    with c1: card("Examens Dept", stats['exams'], "Planifiés", "admin")
    with c2: card("Étudiants", stats['students'], "Inscrits Dept", "student")
    with c3: card("Professeurs", stats['profs'], "Effectif Dept", "prof")

    # 2. Validation Action
    st.markdown("### 🖋️ Validation du Planning")
    val_status = run_query(f"SELECT est_valide FROM validation_edt WHERE id_dep = {dept_id} AND session_nom = 'Janvier 2026'")
    
    is_valide = val_status[0]['est_valide'] if val_status else False
    
    if is_valide:
        st.success("✅ Le planning de votre département a été validé.")
    else:
        st.warning("⚠️ Le planning est en attente de votre validation.")
        if st.button("🚀 Valider le Planning de Session", use_container_width=True):
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO validation_edt (id_dep, session_nom, est_valide, date_validation, id_professeur_validateur)
                VALUES (%s, %s, 1, NOW(), %s)
                ON DUPLICATE KEY UPDATE est_valide = 1, date_validation = NOW(), id_professeur_validateur = %s
            """, (dept_id, 'Janvier 2026', user['id_professeur'], user['id_professeur']))
            conn.commit()
            conn.close()
            st.success("Planning validé avec succès!")
            st.rerun()

    # 3. Dept Specific Conflicts & Trends
    st.markdown("### 📉 Statistiques de Performance Dept")
    col_x, col_y = st.columns(2)
    
    with col_x:
        st.markdown("**🛡️ Conflits par Spécialité**")
        dept_conflicts = run_query(f"""
            SELECT s.nom as Specialite, COUNT(DISTINCT e.id_etudiant) as nb_students
            FROM etudiant_examens_jour e
            JOIN etudiant stu ON e.id_etudiant = stu.id_etudiant
            JOIN specialite s ON stu.id_spec = s.id_spec
            JOIN annee_etude a ON s.id_annee = a.id_annee
            WHERE a.id_dep = {dept_id} AND e.nb_examens > 1
            GROUP BY s.id_spec
        """)
        if not dept_conflicts:
            st.info("✅ Aucun conflit.")
        else:
            st.dataframe(pd.DataFrame(dept_conflicts), hide_index=True)

    with col_y:
        st.markdown("**📅 Charge par Jour (Effectif)**")
        day_load = run_query(f"""
            SELECT e.date_examen as Date, COUNT(DISTINCT e.id_examen) as Exams
            FROM examen e
            JOIN module m ON e.id_module = m.id_module
            JOIN specialite s ON m.id_spec = s.id_spec
            JOIN annee_etude a ON s.id_annee = a.id_annee
            WHERE a.id_dep = {dept_id}
            GROUP BY e.date_examen
        """)
        if day_load:
            st.line_chart(pd.DataFrame(day_load).set_index('Date'))

def show_dashboard():
    user = st.session_state.get('user', {})
    role = user.get('type_utilisateur', 'guest')
    
    if role == 'admin_examens':
        show_admin_dashboard()
    elif role == 'vice_doyen':
        show_vice_doyen_dashboard(user)
    elif role == 'chef_departement':
        show_chef_departement_dashboard(user)
    elif role == 'professeur':
        show_prof_dashboard(user)
    elif role == 'etudiant':
        show_student_dashboard(user)
    else:
        st.warning("Veuillez vous connecter.")
