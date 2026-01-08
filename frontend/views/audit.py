import streamlit as st
import pandas as pd
from backend.db import run_query

def show_audit():
    st.title("🛡️ Audit & Qualité")
    st.markdown("Vérification automatique de conformité.")

    # --- 0. NO FRIDAY CHECK ---
    st.subheader("0. Respect du Chômage (Vendredi)")
    res_fri = run_query("SELECT id_examen, date_examen FROM examen WHERE WEEKDAY(date_examen) = 4")
    if not res_fri:
        st.success("✅ Aucun examen n'est programmé le Vendredi.")
    else:
        st.error(f"❌ ALERTE : {len(res_fri)} Examens trouvés le Vendredi !")
        st.dataframe(res_fri)
    st.divider()

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
            df1 = pd.DataFrame(res1)
            csv1 = df1.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Rapport Surcharges (CSV)", csv1, "surcharges.csv", "text/csv")
            st.dataframe(df1, hide_index=True)

    with col2:
        st.subheader("2. Charge Profs")
        # Existing query for prof surcharge
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
            df2 = pd.DataFrame(res2)
            csv2 = df2.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Rapport Profs (CSV)", csv2, "surcharge_profs.csv", "text/csv")
            st.dataframe(df2, hide_index=True)

    st.subheader("3. Conflits Étudiants")
    q3 = """
    SELECT 
        stu.nom, 
        stu.prenom, 
        ex.date_examen as Date, 
        COUNT(DISTINCT ex.id_module) as Nb_Modules,
        GROUP_CONCAT(DISTINCT m.code_module SEPARATOR ', ') as Modules
    FROM etudiant stu
    JOIN module m ON stu.id_spec = m.id_spec
    JOIN examen ex ON m.id_module = ex.id_module
    GROUP BY stu.id_etudiant, ex.date_examen
    HAVING Nb_Modules > (SELECT valeur FROM configuration_contraintes WHERE nom='max_examens_etudiant_par_jour' LIMIT 1)
    """
    res3 = run_query(q3)
    if not res3:
        st.success("✅ Aucun conflit horaire (1 examen par jour respecté).")
    else:
        st.error(f"❌ {len(res3)} Étudiants en conflit")
        df3 = pd.DataFrame(res3)
        csv3 = df3.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Rapport Conflits Étudiants (CSV)", csv3, "conflits_etudiants.csv", "text/csv")
        st.dataframe(df3, hide_index=True)

    # --- FINAL VALIDATION (DOYEN ONLY) ---
    if st.session_state.user.get('type_utilisateur') == 'vice_doyen':
        st.divider()
        st.subheader("🛡️ Validation Finale du Vice-Doyen")
        if not res_fri and not res1 and not res3:
            st.success("✨ Tous les contrôles sont au vert. Le planning est conforme aux règles académiques.")
            if st.button("🏛️ Apposer la Signature Officielle (Doyen)", use_container_width=True, type="primary"):
                st.balloons()
                st.success("📜 Planning officiellement validé pour la Faculté des Sciences !")
        else:
            st.warning("⚠️ Les conflits bloquants doivent être résolus avant la signature finale.")
