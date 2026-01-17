import hashlib
import traceback
from backend.db import run_query

def hash_password(password):
    """Hashes a password using SHA-256."""
    try:
        return hashlib.sha256(password.encode()).hexdigest()
    except Exception as e:
        print(f"ERROR: Password hashing failed: {e}")
        traceback.print_exc()
        return None

def check_login(email, password):
    """
    Verifies email and password.
    Returns: (user_dict, error_message)
    NEVER raises exceptions - all errors are caught and returned as error messages.
    """
    try:
        # Validate inputs
        if not email or not password:
            return None, "Email et mot de passe requis."
        
        # Hash password
        hashed = hash_password(password)
        if hashed is None:
            return None, "Erreur lors du traitement du mot de passe."
        
        # Build and execute query
        query = """
        SELECT 
            u.id_utilisateur, u.email, u.type_utilisateur, u.id_professeur, u.id_etudiant,
            COALESCE(p.nom, e.nom) as nom,
            COALESCE(p.prenom, e.prenom) as prenom,
            s.nom as spec_nom,
            g.nom as groupe_nom
        FROM utilisateur u
        LEFT JOIN professeur p ON u.id_professeur = p.id_professeur
        LEFT JOIN etudiant e ON u.id_etudiant = e.id_etudiant
        LEFT JOIN specialite s ON e.id_spec = s.id_spec
        LEFT JOIN groupe g ON e.id_spec = g.id_spec AND e.groupe_numero = g.numero
        WHERE u.email = %s AND u.mot_de_passe_hash = %s AND u.actif = 1
        """
        
        # Execute query - run_query never raises, always returns list
        results = run_query(query, (email, hashed))
        
        # Check results
        if results and isinstance(results, list) and len(results) > 0:
            # Success - return user data
            return results[0], None
        else:
            # No results - could be wrong credentials or database error
            # Check console logs to distinguish
            return None, "Email ou mot de passe incorrect."
            
    except Exception as e:
        # Catch ANY exception - this should never happen, but safety first
        error_msg = f"Erreur inattendue lors de la connexion: {type(e).__name__}: {str(e)}"
        print(f"ERROR in check_login: {error_msg}")
        traceback.print_exc()
        return None, "Une erreur s'est produite lors de la connexion. Veuillez vérifier la configuration de la base de données."

def restore_session(email):
    """
    Restore user session from email.
    Returns user dict or None.
    NEVER raises exceptions.
    """
    try:
        if not email:
            return None
            
        query = """
        SELECT 
            u.id_utilisateur, u.email, u.type_utilisateur, u.id_professeur, u.id_etudiant,
            COALESCE(p.nom, e.nom) as nom,
            COALESCE(p.prenom, e.prenom) as prenom,
            s.nom as spec_nom,
            g.nom as groupe_nom
        FROM utilisateur u
        LEFT JOIN professeur p ON u.id_professeur = p.id_professeur
        LEFT JOIN etudiant e ON u.id_etudiant = e.id_etudiant
        LEFT JOIN specialite s ON e.id_spec = s.id_spec
        LEFT JOIN groupe g ON e.id_spec = g.id_spec AND e.groupe_numero = g.numero
        WHERE u.email = %s AND u.actif = 1
        """
        results = run_query(query, (email,))
        
        if results and isinstance(results, list) and len(results) > 0:
            return results[0]
        return None
    except Exception as e:
        print(f"ERROR in restore_session: {e}")
        traceback.print_exc()
        return None

def get_user_name(role, p_id, s_id):
    """
    Helper to fetch readable name based on role.
    NEVER raises exceptions - always returns a string.
    """
    try:
        if role == 'professeur' and p_id:
            try:
                res = run_query("SELECT nom, prenom FROM professeur WHERE id_professeur=%s", (p_id,))
                if res and isinstance(res, list) and len(res) > 0:
                    return f"{res[0]['prenom']} {res[0]['nom']}"
            except Exception as e:
                print(f"Warning: Could not fetch professor name: {e}")
        
        if role == 'etudiant' and s_id:
            try:
                res = run_query("SELECT nom, prenom FROM etudiant WHERE id_etudiant=%s", (s_id,))
                if res and isinstance(res, list) and len(res) > 0:
                    return f"{res[0]['prenom']} {res[0]['nom']}"
            except Exception as e:
                print(f"Warning: Could not fetch student name: {e}")
    except Exception as e:
        print(f"Warning: Error in get_user_name: {e}")
        traceback.print_exc()
    
    # Fallback to role name
    return role.capitalize() if role else "Utilisateur"
