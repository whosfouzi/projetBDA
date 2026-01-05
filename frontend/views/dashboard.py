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
                st.markdown(f"""
                <div class="timeline-grid">
                    <div style="font-weight:bold; color:var(--accent); font-size:1.2rem;">
                        {str(exam['heure_debut'])[:5]}
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
        SELECT e.date_examen, e.heure_debut, m.nom as module, s.nom as salle
        FROM etudiant stu
        JOIN module m ON stu.id_spec = m.id_spec
        JOIN examen e ON m.id_module = e.id_module
        JOIN salle s ON e.id_salle = s.id_salle
        WHERE stu.id_etudiant = {user['id_etudiant']}
        AND e.date_examen >= CURDATE()
        ORDER BY e.date_examen, e.heure_debut
        LIMIT 5
    """)
    
    if not upcoming:
        st.success("🎉 Aucun examen à venir. Bonne révision !")
    else:
        st.dataframe(pd.DataFrame(upcoming), use_container_width=True, hide_index=True)


# --- MAIN ROUTER ---
def show_dashboard():
    user = st.session_state.get('user', {})
    role = user.get('type_utilisateur', 'guest')
    
    if role in ['admin_examens', 'vice_doyen']:
        show_admin_dashboard()
    elif role == 'professeur':
        show_prof_dashboard(user)
    elif role == 'etudiant':
        show_student_dashboard(user)
    else:
        st.warning("Veuillez vous connecter.")
