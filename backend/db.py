import mysql.connector
import streamlit as st

def get_connection():
    return mysql.connector.connect(
        host=st.secrets["mysql"]["host"],
        port=st.secrets["mysql"]["port"],
        user=st.secrets["mysql"]["user"],
        password=st.secrets["mysql"]["password"],
        database=st.secrets["mysql"]["database"]
    )

def run_query(query, params=None):
    conn = get_connection()
    # Use buffered=True to fetch all results immediately and avoid 'Unread result found' errors
    cursor = conn.cursor(dictionary=True, buffered=True)
    try:
        cursor.execute(query, params)
        q = query.strip().upper()
        if q.startswith("SELECT") or q.startswith("SHOW") or q.startswith("DESC"):
            # Ensure we fetch ALL rows (critical for 13k students)
            return cursor.fetchall()
        else:
            conn.commit()
            return cursor.lastrowid
    except Exception as e:
        st.error(f"Database Error: {e}")
        return []
    finally:
        cursor.close()
        conn.close()
