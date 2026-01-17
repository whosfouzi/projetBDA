import mysql.connector
import streamlit as st
import traceback
import threading
import queue
import time
import socket

# Global lock to prevent concurrent connection attempts
_connection_lock = threading.Lock()

def _test_port(host, port, timeout=1):
    """Test if MySQL port is accessible before attempting connection"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False

def _safe_connect_in_thread(config, result_queue, timeout_seconds=2):
    """
    Attempt MySQL connection in a separate thread with very aggressive timeout.
    This isolates the connection attempt from Streamlit completely.
    """
    conn = None
    start_time = time.time()
    
    try:
        # Very short timeout in config
        # Use use_pure=True to force Python connector which respects timeouts better on Windows
        config_with_timeout = config.copy()
        config_with_timeout['connection_timeout'] = timeout_seconds
        config_with_timeout['use_pure'] = True  # Force Python connector (better timeout handling)
        config_with_timeout['autocommit'] = False
        config_with_timeout['raise_on_warnings'] = False
        config_with_timeout['buffered'] = True
        
        # Attempt connection
        conn = mysql.connector.connect(**config_with_timeout)
        
        # Check if we exceeded timeout
        elapsed = time.time() - start_time
        if elapsed >= timeout_seconds + 0.5:  # Small buffer
            if conn:
                try:
                    conn.close()
                except:
                    pass
            result_queue.put(('error', f'Connection timeout after {elapsed:.2f} seconds'))
            return
        
        # Verify connection
        try:
            if conn and hasattr(conn, 'is_connected') and conn.is_connected():
                result_queue.put(('success', conn))
            else:
                if conn:
                    try:
                        conn.close()
                    except:
                        pass
                result_queue.put(('error', 'Connection established but not active'))
        except Exception as e:
            if conn:
                try:
                    conn.close()
                except:
                    pass
            result_queue.put(('error', f'Connection verification failed: {type(e).__name__}: {e}'))
            
    except mysql.connector.errors.OperationalError as e:
        result_queue.put(('error', f'OperationalError: {e}'))
    except mysql.connector.errors.InterfaceError as e:
        result_queue.put(('error', f'InterfaceError: {e}'))
    except mysql.connector.errors.DatabaseError as e:
        result_queue.put(('error', f'DatabaseError: {e}'))
    except mysql.connector.Error as e:
        result_queue.put(('error', f'MySQL Error: {e}'))
    except Exception as e:
        result_queue.put(('error', f'Unexpected error: {type(e).__name__}: {e}'))
    except BaseException as e:
        if isinstance(e, (KeyboardInterrupt, SystemExit)):
            raise
        result_queue.put(('error', f'BaseException: {type(e).__name__}: {e}'))
    finally:
        # Ensure we put something in queue if we haven't already
        if result_queue.empty():
            elapsed = time.time() - start_time
            result_queue.put(('error', f'Connection attempt failed after {elapsed:.2f} seconds'))

def get_connection():
    """
    Get a MySQL database connection using Streamlit secrets with aggressive timeout.
    Uses a separate thread with hard timeout to prevent hanging.
    NEVER raises uncaught exceptions - all errors are caught and converted.
    Returns None on any error.
    """
    # Try to acquire lock with a short timeout (0.5 seconds) to allow concurrent attempts to wait briefly
    if not _connection_lock.acquire(blocking=True, timeout=0.5):
        print("WARNING: Connection attempt already in progress, could not acquire lock after 0.5s")
        return None
    
    try:
        # Check if secrets are available
        try:
            if not hasattr(st, 'secrets') or st.secrets is None:
                print("ERROR: Streamlit secrets not available")
                return None
            
            mysql_config = st.secrets.get("mysql", {})
            if not mysql_config:
                print("ERROR: MySQL config section is empty")
                return None
        except Exception as e:
            print(f"ERROR: Secrets access failed: {type(e).__name__}: {e}")
            traceback.print_exc()
            return None
        
        # Build config safely
        try:
            host = str(mysql_config.get("host", "localhost"))
            port = int(mysql_config.get("port", 3306))
            
            # Quick port test first
            if not _test_port(host, port, timeout=1):
                print(f"ERROR: Port {port} on {host} is not accessible")
                print(f"       This usually means MySQL is not running or not listening on port {port}")
                print(f"       Please check:")
                print(f"       1. Is MySQL/XAMPP running?")
                print(f"       2. Is MySQL listening on port {port}?")
                print(f"       3. Check firewall settings")
                return None
            
            config = {
                "host": host,
                "port": port,
                "user": str(mysql_config.get("user", "root")),
                "password": str(mysql_config.get("password", "")),
                "database": str(mysql_config.get("database", "")),
                "autocommit": False,
                "raise_on_warnings": False,
                "use_pure": True,  # Use Python connector (better timeout handling on Windows)
            }
        except Exception as e:
            print(f"ERROR: Config build failed: {type(e).__name__}: {e}")
            traceback.print_exc()
            return None
        
        # Use thread with timeout (5 seconds for connection, 6 seconds max wait)
        result_queue = queue.Queue(maxsize=1)
        thread_timeout = 6  # Maximum wait time for thread
        
        thread = threading.Thread(
            target=_safe_connect_in_thread,
            args=(config, result_queue, 5),  # 5 second connection timeout
            daemon=True,
            name="MySQLConnectionThread"
        )
        
        thread.start()
        thread.join(timeout=thread_timeout)
        
        # Check if thread is still running (timeout exceeded)
        if thread.is_alive():
            print(f"ERROR: Connection attempt timed out after {thread_timeout} seconds - abandoning")
            print(f"       MySQL connection is taking too long. Possible causes:")
            print(f"       1. MySQL server is not running (check XAMPP Control Panel)")
            print(f"       2. MySQL is running but not accepting connections")
            print(f"       3. Network/firewall blocking the connection")
            print(f"       4. Wrong host/port in configuration")
            print(f"       5. Database '{config.get('database', 'N/A')}' does not exist")
            print(f"       Check your .streamlit/secrets.toml file and ensure MySQL is running")
            # Thread is daemon, will be killed when main thread exits
            # Return None immediately to not block Streamlit
            return None
        
        # Get result from queue
        try:
            if not result_queue.empty():
                status, result = result_queue.get_nowait()
                if status == 'success':
                    return result
                else:
                    print(f"ERROR: Connection failed: {result}")
                    return None
            else:
                print("ERROR: No result from connection thread (thread may have hung)")
                return None
        except queue.Empty:
            print("ERROR: Connection thread did not return result (queue empty)")
            return None
        except Exception as e:
            print(f"ERROR: Error getting connection result: {type(e).__name__}: {e}")
            traceback.print_exc()
            return None
            
    except Exception as e:
        print(f"ERROR: Critical error in get_connection: {type(e).__name__}: {e}")
        traceback.print_exc()
        return None
    finally:
        try:
            _connection_lock.release()
        except:
            pass

def run_query(query, params=None):
    """
    Execute a database query safely with comprehensive error handling.
    Returns: query results (list of dicts for SELECT) or empty list on error.
    NEVER raises exceptions - all errors are caught and logged.
    """
    conn = None
    cursor = None
    
    try:
        # Validate query
        if not query or not isinstance(query, str):
            print("ERROR: Invalid query parameter")
            return []
        
        # Get connection - this can return None on error
        conn = get_connection()
        if conn is None:
            print("ERROR: get_connection returned None - database may be unreachable")
            return []
        
        # Verify connection is active
        try:
            if not hasattr(conn, 'is_connected'):
                print("ERROR: Connection object missing is_connected method")
                return []
            
            if not conn.is_connected():
                print("ERROR: Connection is not active")
                return []
        except Exception as e:
            print(f"ERROR: Connection check failed: {type(e).__name__}: {e}")
            traceback.print_exc()
            return []
        
        # Create cursor
        try:
            cursor = conn.cursor(dictionary=True, buffered=True)
            if cursor is None:
                print("ERROR: cursor() returned None")
                return []
        except Exception as e:
            print(f"ERROR: Failed to create cursor: {type(e).__name__}: {e}")
            traceback.print_exc()
            return []
        
        # Execute query
        try:
            cursor.execute(query, params)
        except mysql.connector.errors.ProgrammingError as e:
            print(f"ERROR: Query syntax error: {e}")
            traceback.print_exc()
            return []
        except mysql.connector.errors.IntegrityError as e:
            print(f"ERROR: Query integrity error: {e}")
            traceback.print_exc()
            return []
        except mysql.connector.Error as e:
            print(f"ERROR: Query execution failed: {e}")
            traceback.print_exc()
            return []
        except Exception as e:
            print(f"ERROR: Unexpected error during query execution: {type(e).__name__}: {e}")
            traceback.print_exc()
            return []
        
        # Get results
        try:
            q = query.strip().upper()
            if q.startswith("SELECT") or q.startswith("SHOW") or q.startswith("DESC") or q.startswith("WITH"):
                results = cursor.fetchall()
                return results if results else []
            else:
                conn.commit()
                return cursor.lastrowid if cursor.lastrowid else []
        except Exception as e:
            print(f"ERROR: Error processing query results: {type(e).__name__}: {e}")
            traceback.print_exc()
            return []
            
    except Exception as e:
        print(f"ERROR: Critical error in run_query: {type(e).__name__}: {e}")
        traceback.print_exc()
        return []
        
    finally:
        # Always close resources safely - never raise exceptions
        try:
            if cursor is not None:
                try:
                    cursor.close()
                except:
                    pass
        except:
            pass
        
        try:
            if conn is not None:
                try:
                    if hasattr(conn, 'is_connected'):
                        try:
                            if conn.is_connected():
                                conn.close()
                            else:
                                conn.close()
                        except:
                            pass
                    else:
                        conn.close()
                except:
                    pass
        except:
            pass

def test_connection():
    """
    Test database connection and return (success: bool, message: str).
    Useful for debugging connection issues.
    NEVER raises exceptions.
    """
    try:
        conn = get_connection()
        if conn is None:
            return False, "Failed to create connection (get_connection returned None). Check terminal for details."
        
        try:
            if conn.is_connected():
                try:
                    conn.close()
                except:
                    pass
                return True, "Connection successful!"
            else:
                return False, "Connection established but not active."
        except Exception as e:
            return False, f"Connection check failed: {type(e).__name__}: {str(e)}"
    except Exception as e:
        return False, f"Connection test failed: {type(e).__name__}: {str(e)}"
