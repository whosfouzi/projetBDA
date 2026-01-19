import mysql.connector
import streamlit as st
import os

def get_connection():
    # Use Railway internal variables if available, otherwise fallback to Streamlit secrets
    host = os.getenv("MYSQLHOST") or st.secrets["mysql"]["host"]
    port = int(os.getenv("MYSQLPORT") or st.secrets["mysql"]["port"])
    user = os.getenv("MYSQLUSER") or st.secrets["mysql"]["user"]
    password = os.getenv("MYSQLPASSWORD") or st.secrets["mysql"]["password"]
    database = os.getenv("MYSQLDATABASE") or st.secrets["mysql"]["database"]

    return mysql.connector.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database
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
def run_batch_insert(query, data_list):
    """Execute batch insert for better performance with multiple rows."""
    if not data_list:
        return
    
    conn = get_connection()
    cursor = conn.cursor(buffered=True)
    try:
        cursor.executemany(query, data_list)
        conn.commit()
        return cursor.rowcount
    except Exception as e:
        conn.rollback()
        st.error(f"Batch Insert Error: {e}")
        raise e
    finally:
        cursor.close()
        conn.close()
