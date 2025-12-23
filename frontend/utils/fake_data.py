import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def get_exams_data():
    """Generates mock data for exams."""
    departments = ['Informatique', 'Mathématiques', 'Physique', 'Biologie']
    subjects = {
        'Informatique': ['Structures de Données', 'Algorithmes', 'Systèmes de Bases de Données', 'Développement Web'],
        'Mathématiques': ['Calcul I', 'Calcul II', 'Algèbre Linéaire', 'Statistiques'],
        'Physique': ['Mécanique', 'Électromagnétisme', 'Physique Quantique', 'Thermodynamique'],
        'Biologie': ['Génétique', 'Biologie Cellulaire', 'Écologie', 'Microbiologie']
    }
    
    data = []
    base_date = datetime.now() + timedelta(days=7)
    
    for i in range(20):
        dept = np.random.choice(departments)
        subject = np.random.choice(subjects[dept])
        # Random date in the next 2 weeks, 9AM or 2PM
        date = base_date + timedelta(days=np.random.randint(0, 14))
        time = np.random.choice(['09:00', '14:00'])
        
        data.append({
            'ID Examen': f'EX-{100+i}',
            'Cours': subject,
            'Département': dept,
            'Date': date.strftime('%Y-%m-%d'),
            'Heure': time,
            'Salle': f'Salle {np.random.randint(101, 110)}',
            'Étudiants': np.random.randint(20, 150),
            'Formation': f'{dept} - Année {np.random.randint(1, 4)}'
        })
        
    return pd.DataFrame(data)

def get_rooms_data():
    """Generates mock data for rooms."""
    data = []
    for i in range(1, 11):
        data.append({
            'ID Salle': f'R-{100+i}',
            'Nom': f'Salle {100+i}',
            'Capacité': np.random.choice([30, 50, 100, 200]),
            'Bâtiment': np.random.choice(['Bâtiment A', 'Bâtiment B'])
        })
    return pd.DataFrame(data)

def get_stats_data():
    """Generates summary statistics."""
    return {
        'total_exams': 20,
        'total_students': 1250,
        'conflicts': 2,
        'rooms_utilized': 85
    }
