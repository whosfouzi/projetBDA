import streamlit as st
import pandas as pd
from backend.validation import get_all_violations

st.set_page_config(page_title="Audit & Qualité", page_icon="🛡️", layout="wide")

def load_css():
    """Charge le fichier de style personnalisé."""
    with open("frontend/assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

st.title("🛡️ Audit de Conformité (Qualité)")
st.markdown("Vérification automatique des 5 règles métiers.")

if st.button("Lancer l'Audit"):
    with st.spinner("Exécution des vérifications..."):
        violations = get_all_violations()

    # Rule 1
    st.header("1. Surcharge Enseignants")
    v1 = violations['teacher_overload']
    if not v1:
        st.success("✅ Règle Respectée (Max 3 examens/jour)")
    else:
        st.error(f"❌ {len(v1)} Violations Détectées")
        st.dataframe(pd.DataFrame(v1), width="stretch")

    # Rule 2
    st.header("2. Équité (Distribution)")
    v2 = violations['teacher_fairness']
    if v2 and v2[0]['ecart_type'] is not None:
        std_dev = v2[0]['ecart_type']
        avg = v2[0]['moyenne']
        st.metric("Écart-Type (Standard Deviation)", f"{std_dev:.2f}", help="Plus c'est proche de 0, plus c'est équitable.")
        if std_dev < 1.0:
            st.success("✅ Distribution Équitable")
        else:
            st.warning("⚠️ Disparités détectées dans la charge de travail")
    else:
        st.info("Pas assez de données pour calculer l'équité.")

    # Rule 3
    st.header("3. Surcharge Étudiants")
    v3 = violations['student_overload']
    if not v3:
        st.success("✅ Règle Respectée (Max 1 examen/jour)")
    else:
        st.error(f"❌ {len(v3)} Violations Détectées")
        st.dataframe(pd.DataFrame(v3), width="stretch")

    # Rule 4
    st.header("4. Capacité Salles (>20 Étudiants)")
    v4 = violations['room_capacity']
    if not v4:
        st.success("✅ Règle Respectée (Max 20 étudiants/salle)")
    else:
        st.error(f"❌ {len(v4)} Salles en Surcapacité (>20)")
        st.dataframe(pd.DataFrame(v4), width="stretch")

    # Rule 5
    st.header("5. Conflits de Salles")
    v5 = violations['room_conflicts']
    if not v5:
        st.success("✅ Règle Respectée (Aucun chevauchement)")
    else:
        st.error(f"❌ {len(v5)} Double Réservations Détectées")
        st.dataframe(pd.DataFrame(v5), width="stretch")
else:
    st.info("Cliquez sur le bouton pour lancer l'audit.")
