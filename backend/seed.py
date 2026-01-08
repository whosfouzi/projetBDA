from backend.db import get_connection
import random
import sys

def seed_database():
    conn = get_connection()
    cursor = conn.cursor(buffered=True)
    
    try:
        # 1. Clean Data
        tables = [
            'cache_capacite_examens', 'etudiant_examens_jour', 'suivi_surveillances_jour',
            'surveillance', 'inscription', 'examen', 'module', 
            'etudiant', 'utilisateur', 'specialite', 'annee_etude',
            'professeur', 'departement', 'faculte', 'salle', 'batiment', 'configuration_contraintes'
        ]
        for t in tables:
            cursor.execute(f"DELETE FROM {t}")
        print("1. Tables cleaned.")

        # 1a. Set realistic constraints
        cursor.execute("INSERT INTO configuration_contraintes (nom, valeur) VALUES ('max_etudiants_par_salle', 250)")
        cursor.execute("INSERT INTO configuration_contraintes (nom, valeur) VALUES ('max_examens_etudiant_par_jour', 1)")
        cursor.execute("INSERT INTO configuration_contraintes (nom, valeur) VALUES ('max_surveillances_prof_par_jour', 3)")
        cursor.execute("INSERT INTO configuration_contraintes (nom, valeur) VALUES ('duree_examen_minutes', 90)")

        # 2. Institutional Hierarchy
        cursor.execute("INSERT INTO faculte (nom) VALUES ('Faculté des Sciences')")
        fac_id = cursor.lastrowid
        depts_data = ["Informatique", "Mathématiques", "Physique", "Chimie", "Biologie", "Agronomie", "STAPS"]
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

        # 3. Infrastructure (Massive UMBB Sciences)
        cursor.execute("INSERT INTO batiment (id_batiment, nom) VALUES (1, 'Campus Sciences')")
        # 12 Amphis (250-600 seats)
        for i in range(1, 13):
            cursor.execute("INSERT INTO salle (nom, capacite, type, id_batiment) VALUES (%s, %s, 'amphi', 1)", 
                           (f"Amphi {chr(64+i)}", random.choice([300, 400, 600])))
        # 150 Salles (40-100 seats)
        for i in range(1, 151):
            cursor.execute("INSERT INTO salle (nom, capacite, type, id_batiment) VALUES (%s, %s, 'salle', 1)", 
                           (f"Salle S{i:02d}", random.choice([40, 60, 80, 100])))
        # 50 Labs (20-40 seats)
        for i in range(1, 51):
            cursor.execute("INSERT INTO salle (nom, capacite, type, id_batiment) VALUES (%s, %s, 'labo', 1)", 
                           (f"Labo L{i:02d}", random.choice([20, 30, 40])))
        print("3. Infrastructure created (Massive Scale).")

        # 4. Professors
        prof_source = ["Bouchenak", "Khelifi", "Bensaid", "Benali", "Mansouri", "Chaouch", "Zerrouki", "Saadi", "Taleb", "Abbas"]
        default_pw = 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f' # password123
        p_data = [] 
        for i in range(1000):
            p_data.append((f"{random.choice(prof_source)}_{i}", "Prenom", random.choice(list(dept_ids.values()))))
        cursor.executemany("INSERT INTO professeur (nom, prenom, id_departement) VALUES (%s, %s, %s)", p_data)
        
        cursor.execute("SELECT id_professeur, nom FROM professeur")
        all_profs = cursor.fetchall()
        p_ids = [r[0] for r in all_profs]
        up_data = [] 
        for pid, nom in all_profs:
            up_data.append((f"{nom.lower()}@univ.edu", default_pw, 'professeur', pid, 1))
        cursor.executemany("INSERT INTO utilisateur (email, mot_de_passe_hash, type_utilisateur, id_professeur, actif) VALUES (%s, %s, %s, %s, %s)", up_data)

        # 5. Modules (6 per speciality)
        dept_modules = {
            "Informatique": ["ASD", "AN", "BDD", "POO", "SYST", "RES"],
            "Mathématiques": ["AN1", "ALG", "PROB", "STAT", "GEO", "TOP"],
            "Physique": ["MECA", "THER", "ELEC", "OPT", "QUAN", "NUC"],
            "Chimie": ["ORGA", "MIN", "GEN", "ANAL", "BIO", "POLY"],
            "Biologie": ["BIO1", "GENE", "MICRO", "ECOL", "IMMU", "BOT"],
            "Agronomie": ["SOL", "EAU", "PLANT", "IRR", "PATH", "MGT"],
            "STAPS": ["MOTR", "PERF", "PSY", "ENTR", "MGT", "SOC"]
        }
        for spec in spec_ids:
            pool = dept_modules.get(spec['dname'], ["MOD"]*6)
            for m_code in pool:
                cursor.execute("""
                    INSERT INTO module (nom, code_module, credits, semestre, id_spec, id_professeur_resp)
                    VALUES (%s, %s, 6, 1, %s, %s)
                """, (f"{m_code} {spec['name']}", f"{m_code}-{spec['id']}-{random.randint(100,999)}", spec['id'], random.choice(p_ids)))
        print("5. Modules created.")

        # 6. Students
        s_data = [] 
        for i in range(1, 13001):
            spec = random.choice(spec_ids)
            s_data.append((f"2024{i:05d}", f"Etud_{i}", "Prenom", spec['id']))
        cursor.executemany("INSERT INTO etudiant (matricule, nom, prenom, id_spec) VALUES (%s, %s, %s, %s)", s_data)
        
        cursor.execute("SELECT id_etudiant, matricule FROM etudiant")
        all_stus = cursor.fetchall()
        us_data = [] 
        for sid, mat in all_stus:
            us_data.append((f"e{mat}@student.edu", default_pw, 'etudiant', sid, 1))
        chunk_size = 1000
        for i in range(0, len(us_data), chunk_size):
            cursor.executemany("INSERT INTO utilisateur (email, mot_de_passe_hash, type_utilisateur, id_etudiant, actif) VALUES (%s, %s, %s, %s, %s)", us_data[i:i+chunk_size])
        
        # 7. Admin & Specific Demo Accounts
        admin_pw = '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918' # hash for 'admin'
        chef_pw = 'fa0990ab6f2ecfd562611cedad67152e8c1117f91c22d15094d1e242314243af' # hash for 'chef123'
        doyen_pw = '384fe335d04e0940d1c4daafafb8ec3f997ee5cd841a8dc67d18d397668a0c05' # hash for 'doyen123'
        
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
