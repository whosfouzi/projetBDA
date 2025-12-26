from backend.db import get_connection
import random

def seed_database():
    conn = get_connection()
    cursor = conn.cursor(buffered=True)
    
    try:
        # 1. Clean Data (including cache tables)
        tables = [
            'cache_capacite_examens', 'etudiant_examens_jour', 'suivi_surveillances_jour',
            'surveillance', 'inscription', 'examen', 'module', 
            'etudiant', 'professeur', 'utilisateur',  # Clean users too!
            'salle', 'formation', 'departement', 'batiment'
        ]
        for t in tables:
            cursor.execute(f"DELETE FROM {t}")
        
        print("Tables cleaned.")

        # 2. Batiment
        cursor.execute("INSERT INTO batiment (id_batiment, nom) VALUES (1, 'Batiment Sciences A')")

        # 3. Departements
        # Schema: id_dep, nom
        depts = [
            (1, "Informatique"), (2, "Mathématiques"), (3, "Physique")
        ]
        dept_ids = []
        for did, nom in depts:
            cursor.execute("INSERT INTO departement (id_dep, nom) VALUES (%s, %s)", (did, nom))
            dept_ids.append(did)
        
        # 4. Formations
        # Schema: id_formation, nom, niveau, id_departement, nb_modules
        formations = []
        levels = ['L1', 'L2', 'L3', 'M1']
        curr_fid = 1
        for did in dept_ids:
            for lvl in levels:
                cursor.execute("""
                    INSERT INTO formation (id_formation, nom, niveau, id_departement, nb_modules) 
                    VALUES (%s, %s, %s, %s, 6)
                """, (curr_fid, f"Licence {lvl} Dept {did}", lvl, did))
                formations.append((curr_fid, did)) # Store (fid, dept_id)
                curr_fid += 1

        # 5. Salles
        # Schema: id_salle, nom, capacite, type, id_batiment
        room_ids = []
        for i in range(1, 11):
            rid = i
            nom = f"Salle {100+i}"
            cap = random.choice([30, 50, 100])
            type_salle = 'amphi' if cap > 80 else 'salle'
            cursor.execute("""
                INSERT INTO salle (id_salle, nom, capacite, type, id_batiment) 
                VALUES (%s, %s, %s, %s, 1)
            """, (rid, nom, cap, type_salle))
            room_ids.append(rid)

        # Default Password Hash for 'password123'
        # Generated via hashlib.sha256(b"password123").hexdigest()
        default_pw = 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f'
        
        # Admin Password Hash for 'admin'
        admin_pw = '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918'
        
        # 6. Configuration Constraints (seed default values)
        constraints_data = [
            ('max_examens_etudiant_par_jour', 1, 'Maximum 1 examen par jour par étudiant'),
            ('max_surveillances_prof_par_jour', 3, 'Maximum 3 surveillances par jour par professeur'),
            ('duree_examen_minutes', 90, 'Durée standard d\'un examen (1h30)')
        ]
        for nom, valeur, desc in constraints_data:
            cursor.execute("""
                INSERT INTO configuration_contraintes (nom, valeur, description)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE valeur = VALUES(valeur)
            """, (nom, valeur, desc))
        print("Configuration constraints seeded.")
        
        # 7. Admin User
        cursor.execute("""
            INSERT INTO utilisateur (email, mot_de_passe_hash, type_utilisateur, actif)
            VALUES ('admin@univ.edu', %s, 'admin_examens', 1)
        """, (admin_pw,))
        print("Admin user created: admin@univ.edu / admin")

        # 7. Professeurs (Algerian Names)
        prof_ids = []
        prof_data = [
            ("Bouchenak", "Fatima"),
            ("Khelifi", "Ahmed"),
            ("Bensaid", "Karim"),
            ("Benali", "Nadia"),
            ("Mansouri", "Yacine"),
            ("Chaouch", "Leïla"),
            ("Zerrouki", "Mohamed"),
            ("Saadi", "Samira"),
            ("Taleb", "Omar"),
            ("Abbas", "Rym")
        ]
        for i, (nom, prenom) in enumerate(prof_data):
            pid = i + 1
            email = f"{nom.lower()}@univ.edu"
            dept_id = random.choice(dept_ids)
            
            # Insert into PROFESSEUR
            cursor.execute("""
                INSERT INTO professeur (id_professeur, nom, prenom, specialite, grade, id_departement) 
                VALUES (%s, %s, %s, 'Informatique', 'Professeur', %s)
            """, (pid, nom, prenom, dept_id))
            
            # Insert into UTILISATEUR
            cursor.execute("""
                INSERT INTO utilisateur (email, mot_de_passe_hash, type_utilisateur, id_professeur, actif)
                VALUES (%s, %s, 'professeur', %s, 1)
            """, (email, default_pw, pid))
            
            prof_ids.append(pid)

        # 7. Étudiants (Algerian Names)
        student_ids = []
        algerian_first_names = [
            "Amine", "Rania", "Youcef", "Sara", "Bilal", "Amina", "Karim", "Lina",
            "Mehdi", "Yasmine", "Sofiane", "Meriem", "Hamza", "Chaima", "Riad",
            "Nesrine", "Walid", "Sihem", "Farid", "Houda", "Ilyes", "Maissa",
            "Nabil", "Imane", "Samir", "Soundous", "Adel", "Selma", "Hichem", "Nawel"
        ]
        algerian_last_names = [
            "Benali", "Khelifi", "Bouazza", "Meziane", "Hamidi", "Saidi", "Larbi",
            "Medjahdi", "Belkacem", "Brahimi", "Achour", "Bouzid", "Cherif", "Djamel",
            "Ferhat", "Ghazi", "Haddad", "Slimani", "Kacem", "Lounis"
        ]
        
        for i in range(1, 51):
            sid = i
            nom = random.choice(algerian_last_names)
            prenom = random.choice(algerian_first_names)
            email = f"e{i}@student.univ.edu"
            matricule = f"2024{i:04d}"
            # Assign random formation
            fid, _ = random.choice(formations)
            
            # Insert into ETUDIANT
            cursor.execute("""
                INSERT INTO etudiant (id_etudiant, matricule, nom, prenom, promo, id_formation) 
                VALUES (%s, %s, %s, %s, '2024', %s)
            """, (sid, matricule, nom, prenom, fid))
            
            # Insert into UTILISATEUR
            cursor.execute("""
                INSERT INTO utilisateur (email, mot_de_passe_hash, type_utilisateur, id_etudiant, actif)
                VALUES (%s, %s, 'etudiant', %s, 1)
            """, (email, default_pw, sid))
            
            student_ids.append(sid)

        # 8. Modules
        # Schema: id_module, nom, code_module, credits, semestre, id_formation
        module_ids = []
        curr_mid = 1
        for (fid, dept_id) in formations:
            # 3 modules per formation
            for i in range(1, 4):
                code = f"M{fid}0{i}"
                nom = f"Module {code}"
                cursor.execute("""
                    INSERT INTO module (id_module, nom, code_module, credits, semestre, id_formation) 
                    VALUES (%s, %s, %s, 4, 1, %s)
                """, (curr_mid, nom, code, fid))
                module_ids.append(curr_mid)
                curr_mid += 1

        # 9. Inscriptions
        # Random enrollments
        for sid in student_ids:
            mods = random.sample(module_ids, k=random.randint(3, 5))
            for mid in mods:
                cursor.execute("INSERT INTO inscription (id_etudiant, id_module) VALUES (%s, %s)", (sid, mid))

        conn.commit()
        return True, "Database seeded successfully (Fixed: No Emails, Added Matricules/Depts)!"
        
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        cursor.close()
        conn.close()
