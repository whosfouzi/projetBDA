"""
Script de test pour vérifier la connexion MySQL.
Exécutez ce script pour diagnostiquer les problèmes de connexion.
"""
import mysql.connector
import sys
import threading
import queue
import time
import socket

def _test_port(host, port, timeout=2):
    """Test if MySQL port is accessible"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        print(f"   Port test error: {e}")
        return False

def _connect_in_thread(config, result_queue, timeout=2):
    """Connect in a separate thread with very aggressive timeout"""
    conn = None
    start_time = time.time()
    
    try:
        # Very short timeout in config
        config_with_timeout = config.copy()
        config_with_timeout['connection_timeout'] = timeout
        
        # Attempt connection
        print(f"   [Thread] Début connexion à {time.time():.2f}")
        conn = mysql.connector.connect(**config_with_timeout)
        elapsed = time.time() - start_time
        print(f"   [Thread] Connexion réussie en {elapsed:.2f}s")
        
        if conn and conn.is_connected():
            result_queue.put(('success', conn))
        else:
            if conn:
                conn.close()
            result_queue.put(('error', 'Connection not active'))
            
    except mysql.connector.errors.OperationalError as e:
        elapsed = time.time() - start_time
        print(f"   [Thread] OperationalError après {elapsed:.2f}s: {e}")
        result_queue.put(('error', f'OperationalError: {e}'))
    except mysql.connector.errors.InterfaceError as e:
        elapsed = time.time() - start_time
        print(f"   [Thread] InterfaceError après {elapsed:.2f}s: {e}")
        result_queue.put(('error', f'InterfaceError: {e}'))
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"   [Thread] Exception après {elapsed:.2f}s: {type(e).__name__}: {e}")
        result_queue.put(('error', f'{type(e).__name__}: {e}'))
    finally:
        # Ensure we always put something in queue
        if result_queue.empty():
            elapsed = time.time() - start_time
            if elapsed >= timeout:
                result_queue.put(('error', f'Timeout after {elapsed:.2f} seconds'))
            else:
                result_queue.put(('error', 'Connection attempt completed with no result'))

def test_connection():
    """Test la connexion MySQL avec les paramètres de secrets.toml"""
    config = {
        "host": "localhost",
        "port": 3307,
        "user": "root",
        "password": "",
        "database": "optimisation_edt_2",
    }
    
    print("=" * 60)
    print("TEST DE CONNEXION MYSQL")
    print("=" * 60)
    print(f"Host: {config['host']}")
    print(f"Port: {config['port']}")
    print(f"User: {config['user']}")
    print(f"Database: {config['database']}")
    print(f"Password: {'(vide)' if not config['password'] else '(défini)'}")
    print("=" * 60)
    print()
    
    try:
        # First, test if port is accessible
        print("1. Test d'accessibilite du port...")
        if _test_port(config['host'], config['port'], timeout=2):
            print(f"   [OK] Port {config['port']} est accessible")
        else:
            print(f"   [ERREUR] Port {config['port']} n'est PAS accessible")
            print("   Solutions:")
            print("   - Vérifiez que MySQL est démarré")
            print("   - Vérifiez que MySQL écoute sur le port 3307")
            print("   - Vérifiez le pare-feu Windows")
            return False
        
        print()
        print("2. Tentative de connexion MySQL (timeout: 2 secondes)...")
        print("   (Le script s'arrêtera après 3 secondes maximum)")
        
        # Use thread with very aggressive timeout
        result_queue = queue.Queue(maxsize=1)
        thread_timeout = 3  # Maximum wait time
        
        thread = threading.Thread(
            target=_connect_in_thread,
            args=(config, result_queue, 2),  # 2 second connection timeout
            daemon=True
        )
        
        start_time = time.time()
        thread.start()
        thread.join(timeout=thread_timeout)
        elapsed = time.time() - start_time
        
        if thread.is_alive():
            print(f"   [ERREUR] TIMEOUT: La connexion a pris plus de {elapsed:.2f} secondes")
            print("   Le thread sera abandonné (daemon=True)")
            print()
            print("   PROBLÈME IDENTIFIÉ:")
            print("   mysql.connector.connect() se bloque même avec timeout")
            print()
            print("   SOLUTIONS:")
            print("   1. Vérifiez que MySQL accepte les connexions:")
            print("      - Ouvrez phpMyAdmin")
            print("      - Vérifiez que vous pouvez vous connecter")
            print("   2. Essayez de vous connecter avec un client MySQL:")
            print("      mysql -h localhost -P 3307 -u root")
            print("   3. Vérifiez les logs MySQL dans XAMPP")
            print("   4. Redémarrez MySQL dans XAMPP")
            return False
        
        if result_queue.empty():
            print(f"   [ERREUR] ERREUR: Aucun resultat apres {elapsed:.2f} secondes")
            return False
        
        status, result = result_queue.get_nowait()
        
        if status == 'error':
            print(f"   [ERREUR] ERREUR: {result}")
            print()
            print("Solutions possibles:")
            print("1. Vérifiez que MySQL est démarré dans XAMPP")
            print("2. Vérifiez que l'utilisateur 'root' existe")
            print("3. Vérifiez les permissions de l'utilisateur")
            print("4. Vérifiez que la base de données existe")
            return False
        
        conn = result
        
        if conn.is_connected():
            print("   [OK] CONNEXION REUSSIE!")
            print()
            
            # Test une requête simple
            print("3. Test d'une requete SQL...")
            cursor = conn.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"   Version MySQL: {version[0]}")
            
            # Vérifier si la base de données existe
            cursor.execute("SHOW DATABASES LIKE %s", (config['database'],))
            db_exists = cursor.fetchone()
            if db_exists:
                print(f"   [OK] Base de donnees '{config['database']}' existe")
            else:
                print(f"   [ERREUR] Base de donnees '{config['database']}' n'existe pas")
            
            cursor.close()
            conn.close()
            print()
            print("=" * 60)
            print("[OK] TEST TERMINE AVEC SUCCES!")
            print("=" * 60)
            return True
        else:
            print("   [ERREUR] Connexion etablie mais inactive")
            return False
            
    except Exception as e:
        print(f"[ERREUR] ERREUR INATTENDUE:")
        print(f"   Type: {type(e).__name__}")
        print(f"   Message: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
