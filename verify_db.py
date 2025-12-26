import streamlit as st
from backend.db import get_connection

try:
    conn = get_connection()
    db_name = conn.database
    st.success(f"Successfully connected to database: **{db_name}**")
    print(f"VERIFICATION_SUCCESS: {db_name}")
    conn.close()
except Exception as e:
    st.error(f"Connection Failed: {e}")
    print(f"VERIFICATION_FAILED: {e}")
