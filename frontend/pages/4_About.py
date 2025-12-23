import streamlit as st

st.set_page_config(page_title="À Propos", page_icon="ℹ️")

st.title("ℹ️ À Propos du Planificateur")

st.markdown("""
### 🎓 Plateforme de Planification des Examens Universitaires
version 1.0.0 (Prototype)

Cette application est un **prototype frontend** conçu pour démontrer l'interface utilisateur et le flux de travail d'un système automatisé de planification d'examens.

#### Fonctionnalités Clés :
- **Tableau de Bord** : Vue d'ensemble des examens à venir et de l'utilisation des ressources.
- **Générer Emploi du Temps** : Simulation de l'exécution de l'algorithme de planification.
- **Voir Emploi du Temps** : Visionneuse d'emploi du temps interactive avec des capacités de filtrage avancées.
- **Statistiques** : Analyse visuelle de la distribution des examens et de l'utilisation des salles.

#### Stack Technologique :
- **Frontend** : Streamlit
- **Visualisation de Données** : Altair, Pandas
- **Logique** : Python

#### Note pour les Développeurs :
Cette application utilise des **données fictives** générées dans `frontend/utils/fake_data.py`. 
Pour connecter ceci à un vrai backend :
1. Remplacez `get_exams_data()` dans `fake_data.py` par des appels API vers votre backend.
2. Implémentez la logique du bouton `Générer` pour déclencher une requête POST.
3. Remplacez les statistiques statiques par des agrégats en temps réel provenant de la base de données.
""")

st.divider()
st.caption("Fait avec ❤️ avec Streamlit")
