import mysql.connector
import streamlit as st

def get_connection():
    # Add connection pooling for better performance with cloud databases
    return mysql.connector.connect(
        host=st.secrets["mysql"]["host"],
        port=st.secrets["mysql"]["port"],
        user=st.secrets ["mysql"]["user"],
        password=st.secrets["mysql"]["password"],
        database=st.secrets["mysql"]["database"],
        pool_size=5,  # Connection pool for reuse
        pool_name="exam_scheduler_pool",
        pool_reset_session=True
    )

def run_query(query, params=None):
    conn = get_connection()
    # Use buffered=True to fetch all results immediately and avoid 'Unread result found' errors
    cursor = conn.cursor(dictionary=True, buffered=True)
    try:
        cursor.execute(query, params)
        q = query.strip().upper()
        if q.startswith("SELECT") or q.startswith("SHOW") or q.startswith("DESC"):
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
