from backend.db import get_connection
import random
import sys

# Algerian Names Data
ALG_FIRST_NAMES = [
    "Mohamed", "Ahmed", "Yacine", "Amine", "Mehdi", "Walid", "Karim", "Omar", "Youssef", "Brahim",
    "Fatima", "Meriem", "Sarah", "Amina", "Khadija", "Zineb", "Nour", "Imane", "Samia", "Leila",
    "Sofiane", "Hichem", "Sami", "Adel", "Fares", "Nabil", "Riad", "Tarek", "Lotfi", "Redha",
    "Houda", "Lamia", "Nadia", "Salma", "Rania", "Manel", "Asma", "Ibtissem", "Wafa", "Hanane",
    "Khaled", "Mourad", "Mustapha", "Kamel", "Abderrahmane", "Ali", "Hassan", "Bilal", "Hakim", "Faycal"
]

ALG_LAST_NAMES = [
    "Benali", "Belhadj", "Bouras", "Mebarki", "Saidi", "Rahmani", "Toumi", "Dahmani", "Amrani", "Moussaoui",
    "Belkacem", "Brahimi", "Hamdi", "Mansouri", "Bouziane", "Cherif", "Haddad", "Meziane", "Ouali", "Ziani",
    "Boukhalfa", "Chaib", "Djerbal", "Ferhat", "Gherbi", "Hachi", "Idir", "Khelil", "Larbi", "Mokhtari",
    "Nedjar", "Osmani", "Sifi", "Talbi", "Yahia", "Zerrouki", "Abid", "Boudiaf", "Chalah", "Derradji",
    "Fekir", "Gasmi", "Hamza", "Issaadi", "Kadi", "Labidi", "Mahdjoub", "Nouioua", "Ouahab", "Ramdani"
]

def seed_database():
    conn = get_connection()
    if conn is None:
        return False, "Impossible de se connecter à la base de données. Vérifiez que MySQL est démarré et que les paramètres de connexion sont corrects."
    
    cursor = conn.cursor(buffered=True)
    
    try:
        # 1. Clean Data & Rebuild Schema
        # We drop everything to ensure clean state, then recreate strict schema.
        tables = [
            'cache_capacite_examens', 'etudiant_examens_jour', 'suivi_surveillances_jour', 'exam_groupe_track',
            'surveillance', 'inscription', 'examen', 'module', 
            'utilisateur', 'etudiant', 'groupe', 'professeur', 'specialite', 'annee_etude',
            'departement', 'salle', 'batiment', 'faculte', 'configuration_contraintes'
        ]
        
        # Disable foreign keys to allow dropping parents
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        for t in tables:
            cursor.execute(f"DROP TABLE IF EXISTS {t}")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        print("1. Tables dropped.")

        # 2. Schema Definition
        schema_cmds = [
            """CREATE TABLE configuration_contraintes (
                id_contrainte INT AUTO_INCREMENT PRIMARY KEY,
                nom VARCHAR(255) NOT NULL UNIQUE,
                valeur INT NOT NULL
            )""",
            """CREATE TABLE faculte (
                id_fac INT AUTO_INCREMENT PRIMARY KEY,
                nom VARCHAR(255) NOT NULL
            )""",
             """CREATE TABLE batiment (
                id_batiment INT AUTO_INCREMENT PRIMARY KEY,
                nom VARCHAR(255) NOT NULL
            )""",
            """CREATE TABLE departement (
                id_dep INT AUTO_INCREMENT PRIMARY KEY,
                nom VARCHAR(255) NOT NULL,
                id_fac INT,
                FOREIGN KEY (id_fac) REFERENCES faculte(id_fac) ON DELETE CASCADE
            )""",
             """CREATE TABLE salle (
                id_salle INT AUTO_INCREMENT PRIMARY KEY,
                nom VARCHAR(255) NOT NULL,
                capacite INT NOT NULL,
                type ENUM('amphi', 'salle', 'labo') NOT NULL,
                id_batiment INT,
                FOREIGN KEY (id_batiment) REFERENCES batiment(id_batiment) ON DELETE CASCADE
            )""",
            """CREATE TABLE annee_etude (
                id_annee INT AUTO_INCREMENT PRIMARY KEY,
                niveau VARCHAR(50) NOT NULL,
                id_dep INT,
                FOREIGN KEY (id_dep) REFERENCES departement(id_dep) ON DELETE CASCADE
            )""",
            """CREATE TABLE specialite (
                id_spec INT AUTO_INCREMENT PRIMARY KEY,
                nom VARCHAR(255) NOT NULL,
                id_annee INT,
                FOREIGN KEY (id_annee) REFERENCES annee_etude(id_annee) ON DELETE CASCADE
            )""",
            """CREATE TABLE groupe (
                id_spec INT NOT NULL,
                numero INT NOT NULL,
                nom VARCHAR(50) NOT NULL,
                PRIMARY KEY (id_spec, numero),
                FOREIGN KEY (id_spec) REFERENCES specialite(id_spec) ON DELETE CASCADE
            )""",
             """CREATE TABLE professeur (
                id_professeur INT AUTO_INCREMENT PRIMARY KEY,
                nom VARCHAR(100) NOT NULL,
                prenom VARCHAR(100) NOT NULL,
                specialite VARCHAR(100),
                grade VARCHAR(50),
                id_departement INT,
                total_surveillances INT DEFAULT 0,
                FOREIGN KEY (id_departement) REFERENCES departement(id_dep) ON DELETE SET NULL
            )""",
             """CREATE TABLE etudiant (
                id_etudiant INT AUTO_INCREMENT PRIMARY KEY,
                matricule VARCHAR(30) NOT NULL UNIQUE,
                nom VARCHAR(100) NOT NULL,
                prenom VARCHAR(100) NOT NULL,
                id_spec INT NOT NULL,
                groupe_numero INT,
                FOREIGN KEY (id_spec) REFERENCES specialite(id_spec) ON DELETE CASCADE,
                FOREIGN KEY (id_spec, groupe_numero) REFERENCES groupe(id_spec, numero)
            )""",
             """CREATE TABLE module (
                id_module INT AUTO_INCREMENT PRIMARY KEY,
                nom VARCHAR(255) NOT NULL,
                code_module VARCHAR(50),
                credits INT,
                semestre INT,
                id_spec INT,
                id_professeur_resp INT,
                FOREIGN KEY (id_spec) REFERENCES specialite(id_spec) ON DELETE CASCADE,
                FOREIGN KEY (id_professeur_resp) REFERENCES professeur(id_professeur) ON DELETE SET NULL
            )""",
            """CREATE TABLE utilisateur (
                id_utilisateur INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(255) NOT NULL UNIQUE,
                mot_de_passe_hash VARCHAR(255) NOT NULL,
                type_utilisateur VARCHAR(50) NOT NULL,
                id_professeur INT,
                id_etudiant INT,
                actif TINYINT(1) DEFAULT 1,
                FOREIGN KEY (id_professeur) REFERENCES professeur(id_professeur) ON DELETE CASCADE,
                FOREIGN KEY (id_etudiant) REFERENCES etudiant(id_etudiant) ON DELETE CASCADE
            )""",
            """CREATE TABLE examen (
                id_examen INT AUTO_INCREMENT PRIMARY KEY,
                id_module INT,
                id_professeur INT,
                id_salle INT,
                date_examen DATE,
                heure_debut TIME,
                duree_minutes INT,
                annee_univ VARCHAR(20),
                FOREIGN KEY (id_module) REFERENCES module(id_module) ON DELETE CASCADE,
                FOREIGN KEY (id_professeur) REFERENCES professeur(id_professeur) ON DELETE SET NULL,
                FOREIGN KEY (id_salle) REFERENCES salle(id_salle) ON DELETE SET NULL
            )""",
            """CREATE TABLE surveillance (
                id_surveillance INT AUTO_INCREMENT PRIMARY KEY,
                id_professeur INT,
                id_examen INT,
                role VARCHAR(50),
                FOREIGN KEY (id_professeur) REFERENCES professeur(id_professeur) ON DELETE CASCADE,
                FOREIGN KEY (id_examen) REFERENCES examen(id_examen) ON DELETE CASCADE
            )""",
            """CREATE TABLE cache_capacite_examens (
                id_examen INT PRIMARY KEY,
                nb_etudiants_inscrits INT,
                capacite_salle INT,
                FOREIGN KEY (id_examen) REFERENCES examen(id_examen) ON DELETE CASCADE
            )""",
            """CREATE TABLE exam_groupe_track (
                id_examen INT,
                id_spec INT,
                groupe_numero INT,
                assigned_count INT,
                PRIMARY KEY (id_examen, id_spec, groupe_numero),
                FOREIGN KEY (id_examen) REFERENCES examen(id_examen) ON DELETE CASCADE,
                FOREIGN KEY (id_spec, groupe_numero) REFERENCES groupe(id_spec, numero)
            )""",
            """CREATE TABLE etudiant_examens_jour (
                id_etudiant INT,
                date_examen DATE,
                nb_examens INT DEFAULT 0,
                liste_examens VARCHAR(255),
                PRIMARY KEY (id_etudiant, date_examen),
                FOREIGN KEY (id_etudiant) REFERENCES etudiant(id_etudiant) ON DELETE CASCADE
            )""",
             """CREATE TABLE suivi_surveillances_jour (
                id_professeur INT,
                date_surveillance DATE,
                nombre_surveillances INT DEFAULT 0,
                PRIMARY KEY (id_professeur, date_surveillance),
                FOREIGN KEY (id_professeur) REFERENCES professeur(id_professeur) ON DELETE CASCADE
            )""",
            """CREATE TABLE IF NOT EXISTS validation_edt (
              id_validation int(11) NOT NULL AUTO_INCREMENT,
              id_dep int(11) NOT NULL,
              session_nom varchar(50) NOT NULL,
              est_valide tinyint(1) DEFAULT 0,
              date_validation datetime DEFAULT NULL,
              id_professeur_validateur int(11) DEFAULT NULL,
              PRIMARY KEY (id_validation),
              UNIQUE KEY id_dep (id_dep,session_nom),
              KEY id_professeur_validateur (id_professeur_validateur),
              CONSTRAINT validation_edt_ibfk_1 FOREIGN KEY (id_dep) REFERENCES departement (id_dep) ON DELETE CASCADE,
              CONSTRAINT validation_edt_ibfk_2 FOREIGN KEY (id_professeur_validateur) REFERENCES professeur (id_professeur) ON DELETE SET NULL
            )"""
        ]
        
        for cmd in schema_cmds:
            cursor.execute(cmd)

        print("2. Schema created.")

        # Define default passwords
        # 'password123' -> ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f
        default_pw = 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f'
        admin_pw = '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918' # hash for 'admin'
        chef_pw = 'fa0990ab6f2ecfd562611cedad67152e8c1117f91c22d15094d1e242314243af' # hash for 'chef123'
        doyen_pw = '384fe335d04e0940d1c4daafafb8ec3f997ee5cd841a8dc67d18d397668a0c05' # hash for 'doyen123'

        # 3. Institutional Hierarchy (Re-added to populate spec_ids)
        cursor.execute("INSERT INTO faculte (nom) VALUES ('Faculté des Sciences')")
        fac_id = cursor.lastrowid
        depts_data = ["Informatique", "Mathématiques", "Physique", "Chimie", "Biologie", "Agronomie", "STAPS", "Décanat"]
        dept_ids = {}
        for dname in depts_data:
            cursor.execute("INSERT INTO departement (nom, id_fac) VALUES (%s, %s)", (dname, fac_id))
            dept_ids[dname] = cursor.lastrowid
        
        specs_map = {
            "Informatique": {"L1": ["TC MI"], "L2": ["LMD Info", "LMD ISIL"], "L3": ["LMD GL", "LMD SI", "LP RT"], "M1": ["LMD IA", "LMD RSD"], "M2": ["LMD Cyber", "LMD BD"]},
            "Mathématiques": {"L1": ["TC Math"], "L2": ["Math F"], "L3": ["AN", "STAT"], "M1": ["PROB", "ALG"], "M2": ["OPT"]},
            "Physique": {"L1": ["TC SM"], "L2": ["Phys F"], "L3": ["Phys E", "ELN"], "M1": ["Phys Q", "NUC"], "M2": ["ASTRO"]},
            "Chimie": {"L1": ["TC Chim"], "L2": ["Chim O"], "L3": ["Chim A", "Gen C"], "M1": ["POLY", "ENV"], "M2": ["Chim V"]},
            "Biologie": {"L1": ["TC Bio"], "L2": ["GENE", "MICRO"], "L3": ["BIOCH", "ECOL"], "M1": ["BIOTECH", "IMMU"], "M2": ["Gen B"]},
            "Agronomie": {"L1": ["TC Agro"], "L2": ["PROD V"], "L3": ["SOL", "ENT"], "M1": ["IRR", "PATH"], "M2": ["MGT A"]},
            "STAPS": {"L1": ["TC STAPS"], "L2": ["ENTR S"], "L3": ["EDUC M", "MGT S"], "M1": ["PERF S"], "M2": ["PSY S"]}
        }

        spec_ids = []
        for dname, years_dict in specs_map.items():
            did = dept_ids[dname]
            for lvl, s_names in years_dict.items():
                cursor.execute("INSERT INTO annee_etude (niveau, id_dep) VALUES (%s, %s)", (lvl, did))
                aid = cursor.lastrowid
                for sname in s_names:
                    cursor.execute("INSERT INTO specialite (nom, id_annee) VALUES (%s, %s)", (sname, aid))
                    spec_ids.append({'id': cursor.lastrowid, 'name': sname, 'dname': dname})

        # 4. Set realistic constraints
        cursor.execute("DELETE FROM configuration_contraintes") # Clear first
        cursor.execute("INSERT INTO configuration_contraintes (nom, valeur) VALUES ('max_etudiants_par_salle', 20)")
        cursor.execute("INSERT INTO configuration_contraintes (nom, valeur) VALUES ('max_examens_etudiant_par_jour', 1)")
        cursor.execute("INSERT INTO configuration_contraintes (nom, valeur) VALUES ('max_surveillances_prof_par_jour', 3)")
        cursor.execute("INSERT INTO configuration_contraintes (nom, valeur) VALUES ('duree_examen_minutes', 90)")
        
        # 5. Populate Resources (Rooms, Profs, Modules)
        print("Creating Resources...")
        
        # Buildings
        cursor.execute("INSERT INTO batiment (nom) VALUES ('Bloc A'), ('Bloc B'), ('Bloc C'), ('Amphis Centraux')")
        bat_ids = {'A': 1, 'B': 2, 'C': 3, 'Amphi': 4} # Assuming auto-inc starts at 1
        
        # Rooms
        # Amphis (1-10)
        for i in range(1, 11):
            cap = random.choice([60, 65, 70])
            cursor.execute("INSERT INTO salle (nom, capacite, type, id_batiment) VALUES (%s, %s, 'amphi', %s)", (f"Amphi {i}", cap, bat_ids['Amphi']))
            
        # Salles & Labos
        # For each Bloc A, B, C
        for b_char, bid in bat_ids.items():
            if b_char == 'Amphi': continue
            # 15 Salles per block
            for i in range(1, 16):
                cursor.execute("INSERT INTO salle (nom, capacite, type, id_batiment) VALUES (%s, 20, 'salle', %s)", (f"Salle {b_char}{i}", bid))
            # 5 Labos per block
            for i in range(1, 6):
                cursor.execute("INSERT INTO salle (nom, capacite, type, id_batiment) VALUES (%s, 20, 'labo', %s)", (f"Labo {b_char}{i}", bid))

        # Professors
        prof_ids_by_dep = {}
        for dname, did in dept_ids.items():
            prof_ids_by_dep[did] = []
            # 20 Profs per dept
            # 20 Profs per dept
            for i in range(1, 21): 
                if dname == "Informatique" and i == 1:
                    first = "Amine"
                    last = "Ziani"
                else:
                    first = random.choice(ALG_FIRST_NAMES)
                    last = random.choice(ALG_LAST_NAMES)
                
                cursor.execute("INSERT INTO professeur (nom, prenom, id_departement) VALUES (%s, %s, %s)", (last, first, did))
                prof_ids_by_dep[did].append(cursor.lastrowid)

        # Modules
        # spec_ids has {'id': ..., 'name': ..., 'dname': ...}
        for sp in spec_ids:
            sid = sp['id']
            dname = sp['dname']
            did = dept_ids[dname]
            profs = prof_ids_by_dep.get(did, [])
            if not profs: continue
            
            # Create 6 modules for Semester 1
            for i in range(1, 7):
                m_code = f"M{sid}_{i}"
                m_resp = random.choice(profs)
                cursor.execute("INSERT INTO module (nom, code_module, credits, semestre, id_spec, id_professeur_resp) VALUES (%s, %s, 4, 1, %s, %s)",
                               (f"Module {m_code}", m_code, sid, m_resp))


        # 6. Students & Groups
        # We need to create groups for each spec
        s_data = [] 
        
        # Pre-generate groups for each spec
        spec_groups = {} # {spec_id: [gid1, gid2...]}
        
        for sp in spec_ids:
            sid = sp['id']
            # Create a few groups for this spec
            # Logic: We create students, then assign. 
            # Better: Create groups first. How many? Dynamic.
            spec_groups[sid] = []
        
        # Let's generate 13,000 students, assigning them to specs, and creating groups on the fly
        # 13000 / 30 = 433 groups total
        
        current_group_id = None
        current_spec_id = None
        students_in_current_group = 0
        
        # We process by spec to fill groups sequentially
        stud_per_spec = 13000 // len(spec_ids)
        
        for sp in spec_ids:
            sid = sp['id']
            sname = sp['name']
            
            # Create first group for this spec
            group_idx = 1
            cursor.execute("INSERT INTO groupe (id_spec, numero, nom) VALUES (%s, %s, %s)", (sid, group_idx, f"Groupe {group_idx}"))
            
            # Create students for this spec
            for i in range(stud_per_spec):
                mat = f"2024{sid}{i:04d}"
                # Note: We store group_idx (numero) directly
                
                # Hero Student Name Constraint
                # Assuming this is the first spec in the list loop
                if sp == spec_ids[0] and i == 0:
                    s_first = "Sarah"
                    s_last = "Toumi"
                else:
                    s_first = random.choice(ALG_FIRST_NAMES)
                    s_last = random.choice(ALG_LAST_NAMES)

                s_data.append((mat, s_last, s_first, sid, group_idx))
                
                students_in_current_group += 1
                if students_in_current_group >= 35: # Max Group Size
                    # New Group
                    group_idx += 1
                    cursor.execute("INSERT INTO groupe (id_spec, numero, nom) VALUES (%s, %s, %s)", (sid, group_idx, f"Groupe {group_idx}"))
                    students_in_current_group = 0

        cursor.executemany("INSERT INTO etudiant (matricule, nom, prenom, id_spec, groupe_numero) VALUES (%s, %s, %s, %s, %s)", s_data)
        
        cursor.execute("SELECT id_etudiant, matricule FROM etudiant")
        all_stus = cursor.fetchall()
        us_data = [] 
        
        # Hero Student: Link a specific email to the first student
        first_student_id = all_stus[0][0] if all_stus else None

        for sid, mat in all_stus:
            if sid == first_student_id:
                email = "sarah.toumi@student.edu"
            else:
                email = f"e{mat}@student.edu"
            us_data.append((email, default_pw, 'etudiant', sid, 1))
        chunk_size = 1000
        for i in range(0, len(us_data), chunk_size):
            cursor.executemany("INSERT INTO utilisateur (email, mot_de_passe_hash, type_utilisateur, id_etudiant, actif) VALUES (%s, %s, %s, %s, %s)", us_data[i:i+chunk_size])
        
        # 7.1 Create Users for Professors
        cursor.execute("SELECT id_professeur, nom, prenom FROM professeur")
        all_profs = cursor.fetchall()
        p_users = []
        for pid, nom, prenom in all_profs:
            # Sanitize email
            safe_nom = nom.lower().replace(" ", "")
            safe_prenom = prenom.lower().replace(" ", "")
            email = f"{safe_prenom}.{safe_nom}@univ.edu"
            p_users.append((email, default_pw, 'professeur', pid, 1))
        
        # Insert Prof Users using executemany for speed
        # Note: We might have duplicate emails if names are identical. 
        # For a seed script, we can ignore or handle. simpler: just try/except or ignore duplicates?
        # Better: make email unique. 
        # Given 1000 profs and 50 names, collisions are guaranteed.
        # Let's add ID to email to be safe: prenom.nom.id@univ.edu to avoid unique constraint crash.
        p_users_safe = []
        for pid, nom, prenom in all_profs:
             safe_nom = nom.lower().replace(" ", "")
             safe_prenom = prenom.lower().replace(" ", "")
             
             # Hero Account: Amine Ziani
             if nom == "Ziani" and prenom == "Amine":
                 email = "amine.ziani@univ.edu"
             else:
                 email = f"{safe_prenom}.{safe_nom}.{pid}@univ.edu"
                 
             p_users_safe.append((email, default_pw, 'professeur', pid, 1))
             
        for i in range(0, len(p_users_safe), chunk_size):
             cursor.executemany("INSERT INTO utilisateur (email, mot_de_passe_hash, type_utilisateur, id_professeur, actif) VALUES (%s, %s, %s, %s, %s)", p_users_safe[i:i+chunk_size])

        # 7. Admin & Specific Demo Accounts

        
        # Admin
        cursor.execute("INSERT INTO utilisateur (email, mot_de_passe_hash, type_utilisateur, actif) VALUES ('admin@univ.edu', %s, 'admin_examens', 1)", (admin_pw,))
        
        # Vice-Doyen (Logic: Link to a random professor)
        cursor.execute("SELECT id_professeur FROM professeur LIMIT 1")
        p_doyen = cursor.fetchone()[0]
        cursor.execute("INSERT INTO utilisateur (email, mot_de_passe_hash, type_utilisateur, id_professeur, actif) VALUES ('doyen@univ.edu', %s, 'vice_doyen', %s, 1)", (doyen_pw, p_doyen))

        # Chefs de Département
        dept_emails = {
            "Informatique": "chef.info@univ.edu",
            "Mathématiques": "chef.maths@univ.edu",
            "Physique": "chef.phys@univ.edu",
            "Chimie": "chef.chimie@univ.edu",
            "Biologie": "chef.bio@univ.edu",
            "Agronomie": "chef.agro@univ.edu",
            "STAPS": "chef.staps@univ.edu"
        }
        for dname, email in dept_emails.items():
            did = dept_ids[dname]
            cursor.execute("SELECT id_professeur FROM professeur WHERE id_departement = %s LIMIT 1", (did,))
            p_chef = cursor.fetchone()[0]
            cursor.execute("INSERT INTO utilisateur (email, mot_de_passe_hash, type_utilisateur, id_professeur, actif) VALUES (%s, %s, 'chef_departement', %s, 1)", (email, chef_pw, p_chef))

        conn.commit()
        print("6. 13,000 students created.")
        return True, "13k scale-up successful."
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    success, msg = seed_database()
    if success: print(f"✅ {msg}")
    else:
        print(f"❌ {msg}")
        sys.exit(1)
