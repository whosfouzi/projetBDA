import hashlib
from backend.db import run_query

def hash_password(password):
    """SHA-256 hash."""
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate(email, password):
    """Vérifie l'utilisateur en base de données."""
    pwd_hash = hash_password(password)
    
    query = """
    SELECT id_compte, email, type_utilisateur, id_professeur, id_etudiant 
    FROM utilisateur 
    WHERE email = %s AND mot_de_passe_hash = %s AND actif = 1
    """
    results = run_query(query, (email, pwd_hash))
    
    if results:
        return results[0]
    return None

def get_user_role_label(role_code):
    mapping = {
        "vice_doyen": "Vice-Doyen",
        "admin_examens": "Administrateur",
        "chef_departement": "Chef de Département",
        "professeur": "Professeur",
        "etudiant": "Étudiant"
    }
    return mapping.get(role_code, role_code)
