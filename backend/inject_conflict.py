from backend.db import get_connection

def inject():
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        print("💉 Injecting Conflicts...")
        
        # 1. Get some IDs
        cursor.execute("SELECT id_module FROM module LIMIT 2")
        mods = cursor.fetchall()
        m1, m2 = mods[0][0], mods[1][0]
        
        cursor.execute("SELECT id_salle FROM salle LIMIT 1")
        rid = cursor.fetchone()[0]
        
        cursor.execute("SELECT id_professeur FROM professeur LIMIT 1")
        pid = cursor.fetchone()[0]
        
        # 2. Assign Student 1 to BOTH modules (to ensure student conflict)
        cursor.execute("SELECT id_etudiant FROM etudiant LIMIT 1")
        sid = cursor.fetchone()[0]
        
        # Ensure enrollment
        cursor.execute("INSERT IGNORE INTO inscription (id_etudiant, id_module) VALUES (%s, %s)", (sid, m1))
        cursor.execute("INSERT IGNORE INTO inscription (id_etudiant, id_module) VALUES (%s, %s)", (sid, m2))
        
        # 3. Create Conflict: Two exams, Same Time, Same Room
        # This triggers:
        #   - Room Conflict (2 exams in same room at same time)
        #   - Student Conflict (Student 'sid' has 2 exams at same time)
        
        date_conflict = '2025-06-15'
        time_conflict = '09:00:00'
        
        # Exam A
        cursor.execute("""
            INSERT INTO examen (id_module, id_professeur, id_salle, date_examen, heure_debut, duree_minutes, annee_univ)
            VALUES (%s, %s, %s, %s, %s, 60, '2024')
        """, (m1, pid, rid, date_conflict, time_conflict))
        
        # Exam B (Conflict!)
        cursor.execute("""
            INSERT INTO examen (id_module, id_professeur, id_salle, date_examen, heure_debut, duree_minutes, annee_univ)
            VALUES (%s, %s, %s, %s, %s, 60, '2024')
        """, (m2, pid, rid, date_conflict, time_conflict))

        conn.commit()
        print(f"✅ Sabotage Successful! Two exams scheduled on {date_conflict} at {time_conflict} in Salle ID {rid}.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    inject()
