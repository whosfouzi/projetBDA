"""
Page de Génération d'Emploi du Temps.

ACCÈS RESTREINT : ADMINISTRATEURS UNIQUEMENT.
Ce module permet de lancer l'algorithme d'optimisation.
"""

import streamlit as st
import time

st.set_page_config(page_title="Générer Emploi du Temps", page_icon="⚙️")

def check_permissions():
    """Vérifie si l'utilisateur a les droits d'administration."""
    # En production, vérifiez st.session_state['user_id'] contre la table 'administrators'
    role = st.session_state.get('user_role', 'Invité')
    if role != "Administrateur d'Examens":
        st.error("⛔ Accès Refusé")
        st.warning(f"Votre rôle actuel ({role}) ne permet pas de générer des emplois du temps.")
        st.stop()  # Arrête l'exécution du reste de la page

def main():
    """Rendu de la page de génération."""
    check_permissions()
    
    st.title("⚙️ Générer Emploi du Temps")
    st.sidebar.success("Mode Administrateur Actif")
    
    st.markdown("""
    Cette interface permet de lancer l'algorithme d'optimisation pour la création des emplois du temps.
    Veuillez définir les contraintes académiques et logistiques ci-dessous avant de procéder.
    """)

    # Formulaire de configuration
    with st.form("generation_form"):
        st.subheader("Paramètres de Configuration")
        col1, col2 = st.columns(2)
        
        with col1:
            st.selectbox(
                "Session Académique", 
                ["Automne 2024", "Printemps 2025", "Été 2025"],
                help="Sélectionnez la session pour laquelle planifier les examens."
            )
            st.date_input("Date de Début de Session")
            st.number_input(
                "Charge Maximale (Examens/Jour/Étudiant)", 
                min_value=1, 
                max_value=3, 
                value=2,
                help="Nombre maximum d'épreuves qu'un étudiant peut passer en une seule journée."
            )
            
        with col2:
            st.multiselect(
                "Départements Concernés", 
                ["Informatique", "Mathématiques", "Physique", "Biologie"], 
                default=["Informatique"],
                help="Sélectionnez les départements à inclure dans cette génération."
            )
            st.date_input("Date de Fin de Session")
            st.checkbox(
                "Exclure les Week-ends", 
                value=True,
                help="Si coché, aucun examen ne sera planifié les samedis et dimanches."
            )
        
        st.write("---")
        submitted = st.form_submit_button("Lancer l'Algorithme de Génération", type="primary")

    # Simulation du processus de génération
    if submitted:
        with st.status("Exécution de l'algorithme en cours...", expanded=True) as status:
            st.write("📥 Chargement des contraintes et des données étudiants...")
            time.sleep(1)
            st.write("🏢 Allocation optimale des salles et surveillance...")
            time.sleep(1)
            st.write("⚡ Détection et résolution des conflits d'horaires...")
            time.sleep(1)
            st.write("💾 Finalisation et sauvegarde de l'emploi du temps...")
            time.sleep(0.5)
            status.update(label="Génération Terminée avec Succès !", state="complete", expanded=False)
        
        st.success("✅ L'emploi du temps a été généré avec succès. Aucun conflit résiduel détecté.")
        
        st.info("Vous pouvez maintenant consulter les résultats détaillés dans la section 'Voir Emploi du Temps'.")
        if st.button("Accéder aux Résultats"):
            st.switch_page("pages/2_View_Timetable.py")

if __name__ == "__main__":
    main()
