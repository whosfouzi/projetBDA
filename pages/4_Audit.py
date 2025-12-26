import streamlit as st
import pandas as pd
from backend.db import run_query

st.set_page_config(page_title="Audit & Qualité", page_icon="🛡️", layout="wide")

if 'user' not in st.session_state or not st.session_state.user:
    st.error("Veuillez vous connecter.")
    st.stop()

if st.session_state.user['type_utilisateur'] not in ['admin_examens', 'vice_doyen']:
    st.warning("Accès réservé aux administrateurs.")
    st.stop()

st.title("🛡️ Audit & Qualité")
st.markdown("Vérification automatique des contraintes et règles métier.")

col1, col2 = st.columns(2)

# Rule 1: Room Capacity
with col1:
    st.subheader("1. Capacité des Salles")
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
        st.success("✅ Aucune surcharge de salle détectée.")
    else:
        st.error(f"❌ {len(res1)} Salles en surcharge !")
        st.dataframe(res1)

# Rule 2: Teacher Load
with col2:
    st.subheader("2. Charge Professeurs")
    # Max 3 exams per day?
    q2 = """
    SELECT p.nom, e.date_examen, COUNT(*) as nb_exams
    FROM examen e
    JOIN professeur p ON e.id_professeur = p.id_professeur
    GROUP BY p.id_professeur, e.date_examen
    HAVING nb_exams > 3
    """
    res2 = run_query(q2)
    if not res2:
        st.success("✅ Aucun professeur en surcharge (>3/jour).")
    else:
        st.error(f"❌ {len(res2)} Professeurs surchargés !")
        st.dataframe(res2)

st.divider()

# Rule 3: Student Conflicts
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
    st.success("✅ Aucun conflit étudiant (2 examens à la même heure).")
else:
    st.error(f"❌ {len(res3)} Étudiants avec conflits !")
    st.dataframe(res3)
