import streamlit as st
from backend.db import run_query

def show_audit():
    st.title("🛡️ Audit & Qualité")
    st.markdown("Vérification automatique de conformité.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("1. Capacité Salles")
        q1 = """
        SELECT e.id_examen, m.code_module as Module, s.nom as Salle, 
               c.nb_etudiants_inscrits as Inscrits, c.capacite_salle as Capacité
        FROM cache_capacite_examens c
        JOIN examen e ON c.id_examen = e.id_examen
        JOIN module m ON e.id_module = m.id_module
        JOIN salle s ON e.id_salle = s.id_salle
        WHERE c.nb_etudiants_inscrits > c.capacite_salle
        """
        res1 = run_query(q1)
        if not res1:
            st.success("✅ Capacités OK")
        else:
            st.error(f"❌ {len(res1)} Surcharges")
            st.dataframe(res1, hide_index=True)

    with col2:
        st.subheader("2. Charge Profs")
        # Check if any prof has more than max allowed (usually 3)
        q2 = """
        SELECT p.nom, p.prenom, e.date_examen as Date, COUNT(*) as Surveillances
        FROM surveillance s
        JOIN professeur p ON s.id_professeur = p.id_professeur
        JOIN examen e ON s.id_examen = e.id_examen
        GROUP BY p.id_professeur, e.date_examen
        HAVING Surveillances > (SELECT valeur FROM configuration_contraintes WHERE nom='max_surveillances_prof_par_jour' LIMIT 1)
        """
        res2 = run_query(q2)
        if not res2:
            st.success("✅ Charge OK")
        else:
            st.error(f"❌ {len(res2)} Surcharges")
            st.dataframe(res2, hide_index=True)

    st.subheader("3. Conflits Étudiants")
    # Check if any student has > 1 exam per day (Implicit enrollment)
    q3 = """
    SELECT stu.nom, stu.prenom, ex.date_examen as Date, COUNT(*) as Nb_Examens
    FROM etudiant stu
    JOIN module m ON stu.id_spec = m.id_spec
    JOIN examen ex ON m.id_module = ex.id_module
    GROUP BY stu.id_etudiant, ex.date_examen
    HAVING Nb_Examens > (SELECT valeur FROM configuration_contraintes WHERE nom='max_examens_etudiant_par_jour' LIMIT 1)
    """
    res3 = run_query(q3)
    if not res3:
        st.success("✅ Aucun conflit horaire.")
    else:
        st.error(f"❌ {len(res3)} Conflits")
        st.dataframe(res3, hide_index=True)
