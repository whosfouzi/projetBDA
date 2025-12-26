import streamlit as st
from backend.db import run_query

def show_audit():
    st.title("🛡️ Audit & Qualité")
    st.markdown("Vérification automatique de conformité.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("1. Capacité Salles")
        q1 = """
        SELECT s.nom as Salle, s.capacite, m.code_module, COUNT(i.id_etudiant) as Inscrits
        FROM examen e
        JOIN salle s ON e.id_salle = s.id_salle
        JOIN module m ON e.id_module = m.id_module
        JOIN inscription i ON m.id_module = i.id_module
        GROUP BY e.id_examen
        HAVING Inscrits > s.capacite
        """
        res1 = run_query(q1)
        if not res1:
            st.success("✅ Salles OK")
        else:
            st.error(f"❌ {len(res1)} Surcharges")
            st.dataframe(res1)

    with col2:
        st.subheader("2. Charge Profs")
        q2 = """
        SELECT p.nom, e.date_examen, COUNT(*) as nb_exams
        FROM examen e
        JOIN professeur p ON e.id_professeur = p.id_professeur
        GROUP BY p.id_professeur, e.date_examen
        HAVING nb_exams > 3
        """
        res2 = run_query(q2)
        if not res2:
            st.success("✅ Charge OK")
        else:
            st.error(f"❌ {len(res2)} Surcharges")
            st.dataframe(res2)

    st.subheader("3. Conflits Étudiants")
    q3 = """
    SELECT st.nom, st.prenom, e.date_examen, e.heure_debut, COUNT(*) as Examens_Simultanes
    FROM inscription i
    JOIN examen e ON i.id_module = e.id_module
    JOIN etudiant st ON i.id_etudiant = st.id_etudiant
    GROUP BY st.id_etudiant, e.date_examen, e.heure_debut
    HAVING Examens_Simultanes > 1
    """
    res3 = run_query(q3)
    if not res3:
        st.success("✅ Aucun conflit horaire.")
    else:
        st.error(f"❌ {len(res3)} Conflits")
        st.dataframe(res3)
