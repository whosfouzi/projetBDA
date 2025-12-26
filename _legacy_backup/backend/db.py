import streamlit as st

try:
    import mysql.connector
except ImportError:
    mysql = None

def get_connection():
    """
    Etablit une connexion à la base de données MySQL.
    """
    if mysql is None:
        st.error("Le module 'mysql-connector-python' est manquant. Installez-le avec `pip install mysql-connector-python`.")
        return None

    try:
        # Configuration via st.secrets ou défaut
        if "mysql" in st.secrets:
            config = st.secrets["mysql"]
            return mysql.connector.connect(
                host=config.get("host", "localhost"),
                user=config.get("user", "root"),
                password=config.get("password", ""),
                database=config.get("database", "optimisation_edt")
            )
        
        # Fallback local (Dev)
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="optimisation_edt"
        )
    except mysql.connector.Error as err:
        st.error(f"Erreur DB: {err}")
        return None

def run_query(query, params=None):
    """Exécute une requête SQL."""
    conn = get_connection()
    if conn is None:
        return []
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        if query.strip().upper().startswith("SELECT"):
            result = cursor.fetchall()
            return result
        else:
            conn.commit()
            return cursor.rowcount
    except Exception as err:
        st.error(f"Erreur SQL: {err}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
