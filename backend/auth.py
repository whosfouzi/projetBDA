import hashlib
from backend.db import run_query

def hash_password(password):
    """Hashes a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def check_login(email, password):
    """
    Verifies email and password.
    Returns: (user_dict, error_message)
    """
    hashed = hash_password(password)
    
    query = """
    SELECT id_compte, email, type_utilisateur, id_professeur, id_etudiant 
    FROM utilisateur 
    WHERE email = %s AND mot_de_passe_hash = %s AND actif = 1
    """
    results = run_query(query, (email, hashed))
    
    if results:
        # Return the first match (email should be unique)
        return results[0], None
    else:
        return None, "Email ou mot de passe incorrect."

def get_user_name(role, p_id, s_id):
    """Helper to fetch readable name based on role."""
    if role == 'professeur' and p_id:
        res = run_query("SELECT nom, prenom FROM professeur WHERE id_professeur=%s", (p_id,))
        if res: return f"{res[0]['prenom']} {res[0]['nom']}"
    
    if role == 'etudiant' and s_id:
        res = run_query("SELECT nom, prenom FROM etudiant WHERE id_etudiant=%s", (s_id,))
        if res: return f"{res[0]['prenom']} {res[0]['nom']}"
        
    return role.capitalize()
