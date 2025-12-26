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
        # Use vue_profs_surcharges view
        q2 = """
        SELECT p.nom, p.prenom, v.date_surveillance as Date, v.nombre_surveillances as Surveillances
        FROM vue_profs_surcharges v
        JOIN professeur p ON v.id_professeur = p.id_professeur
        """
        res2 = run_query(q2)
        if not res2:
            st.success("✅ Charge OK")
        else:
            st.error(f"❌ {len(res2)} Surcharges")
            st.dataframe(res2, hide_index=True)

    st.subheader("3. Conflits Étudiants")
    # Use vue_etudiants_conflits view
    q3 = """
    SELECT e.nom, e.prenom, v.date_examen as Date, v.nb_examens as Nb_Examens
    FROM vue_etudiants_conflits v
    JOIN etudiant e ON v.id_etudiant = e.id_etudiant
    """
    res3 = run_query(q3)
    if not res3:
        st.success("✅ Aucun conflit horaire.")
    else:
        st.error(f"❌ {len(res3)} Conflits")
        st.dataframe(res3, hide_index=True)
