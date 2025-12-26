from backend.db import get_connection, run_query
from datetime import datetime, timedelta, time
import random

class GreedyScheduler:
    def __init__(self, start_date, days=14):
        self.start_date = start_date
        self.days = days
        self.log = []
        
        # State Tracking
        self.schedule = [] # List of assigned exams
        self.unscheduled = []
        
        # Constraint Trackers
        self.prof_daily_load = {} # {prof_id: {date_str: count}}
        self.prof_total_load = {} # {prof_id: total_count}
        self.student_daily_exams = {} # {student_id: {date_str: count}}
        self.room_schedule = {} # {room_id: {date_str: [(start_time, end_time)]}}
        
        # Dynamic Constraints (loaded from DB)
        self.constraints = self.load_constraints()
        
    def load_constraints(self):
        """Load constraint values from configuration_contraintes table."""
        query = "SELECT nom, valeur FROM configuration_contraintes"
        results = run_query(query)
        constraints = {}
        for row in results:
            constraints[row['nom']] = row['valeur']
        
        # Set defaults if not found
        return {
            'max_examens_etudiant_par_jour': constraints.get('max_examens_etudiant_par_jour', 1),
            'max_surveillances_prof_par_jour': constraints.get('max_surveillances_prof_par_jour', 3),
            'duree_examen_minutes': constraints.get('duree_examen_minutes', 90)  # 1:30h default
        }
        
    def fetch_data(self):
        # 1. Fetch Modules with Student Counts
        # Note: We need to count inscriptions per module
        q_mods = """
        SELECT m.id_module, m.nom, COUNT(i.id_etudiant) as nb_students, m.id_formation
        FROM module m
        LEFT JOIN inscription i ON m.id_module = i.id_module
        GROUP BY m.id_module
        ORDER BY nb_students DESC
        """
        self.modules = run_query(q_mods)
        
        # 2. Fetch Module -> Student Mapping (for Rule 3: Student Conflict)
        q_mod_students = "SELECT id_module, id_etudiant FROM inscription"
        raw_inscriptions = run_query(q_mod_students)
        self.module_students = {}
        for row in raw_inscriptions:
            mid = row['id_module']
            sid = row['id_etudiant']
            if mid not in self.module_students:
                self.module_students[mid] = set()
            self.module_students[mid].add(sid)
            
        # 3. Fetch Rooms
        self.rooms = run_query("SELECT id_salle, nom, capacite FROM salle ORDER BY capacite ASC")
        
        # 4. Fetch Profs
        self.profs = run_query("SELECT id_professeur, nom, prenom FROM professeur")
        # Init Prof Load
        for p in self.profs:
            pid = p['id_professeur']
            self.prof_total_load[pid] = 0
            self.prof_daily_load[pid] = {}

    def get_slots(self):
        """Generate time slots (Day, Hour)"""
        slots = []
        current = self.start_date
        # Exam hours: 08:30, 11:00, 13:30, 16:00
        daily_starts = [
            time(8, 30), time(11, 0), time(13, 30), time(16, 0)
        ]
        
        for d in range(self.days):
            date_obj = current + timedelta(days=d)
            # Skip Sundays (6)
            if date_obj.weekday() == 6: 
                continue
                
            date_str = date_obj.strftime("%Y-%m-%d")
            for h in daily_starts:
                slots.append((date_str, h))
        return slots

    def check_student_conflict(self, module_id, date_str):
        # Rule: Student max N exams per day (from config)
        max_allowed = self.constraints['max_examens_etudiant_par_jour']
        students_in_module = self.module_students.get(module_id, set())
        for sid in students_in_module:
            if self.student_daily_exams.get(sid, {}).get(date_str, 0) >= max_allowed:
                return True # Conflict found
        return False

    def check_room_availability(self, room_id, date_str, start_time, duration_mins=120):
        # Rule 5: Room Exclusivity
        def to_mins(t): return t.hour * 60 + t.minute
        
        start_m = to_mins(start_time)
        end_m = start_m + duration_mins
        
        existing = self.room_schedule.get(room_id, {}).get(date_str, [])
        for (estart, eend) in existing:
            # Check overlap
            # (StartA < EndB) and (EndA > StartB)
            # Here estart is a datetime.time object
            e_start_m = to_mins(estart)
            # eend might be time object
            e_end_m = to_mins(eend)
            
            if max(start_m, e_start_m) < min(end_m, e_end_m):
                return False # Overlap, not available
        return True

    def find_room(self, nb_students, date_str, start_time):
        # Rule 4: Room Capacity >= Students
        candidates = [r for r in self.rooms if r['capacite'] >= nb_students]
        
        for r in candidates:
            if self.check_room_availability(r['id_salle'], date_str, start_time):
                return r
        return None

    def find_prof(self, date_str):
        # Rule: Max N surveillances per day (from config)
        max_daily = self.constraints['max_surveillances_prof_par_jour']
        candidates = []
        for p in self.profs:
            pid = p['id_professeur']
            daily = self.prof_daily_load[pid].get(date_str, 0)
            if daily < max_daily:
                candidates.append(p)
                
        if not candidates:
            return None
            
        # Rule 2: Fairness (heuristic: pick prof with lowest TOTAL load)
        candidates.sort(key=lambda x: self.prof_total_load[x['id_professeur']])
        return candidates[0] # Pick the least loaded

    def solve(self):
        self.fetch_data()
        slots = self.get_slots()
        
        for mod in self.modules:
            assigned = False
            mid = mod['id_module']
            nb_studs = mod['nb_students']
            
            # If no students, skip or handle (here we skip mostly)
            if nb_studs == 0:
                # self.unscheduled.append(f"{mod['nom']} (0 students)")
                continue

            # Try every slot sequentially
            for (date_str, t_start) in slots:
                # 1. Student Check
                if self.check_student_conflict(mid, date_str):
                    continue
                
                # 2. Room Check
                room = self.find_room(nb_studs, date_str, t_start)
                if not room:
                    continue
                
                # 3. Prof Check
                prof = self.find_prof(date_str)
                if not prof:
                    continue
                    
                # All Valid -> Assign!
                self.commit_assignment(mod, room, prof, date_str, t_start)
                assigned = True
                break
            
            if not assigned:
                self.unscheduled.append(mod['nom'])

    def commit_assignment(self, mod, room, prof, date_str, t_start):
        mid = mod['id_module']
        pid = prof['id_professeur']
        rid = room['id_salle']
        duration = self.constraints['duree_examen_minutes']  # From config (default 90 min)
        
        # Update Prof Load
        self.prof_total_load[pid] += 1
        self.prof_daily_load[pid][date_str] = self.prof_daily_load[pid].get(date_str, 0) + 1
        
        # Update Student Load
        students = self.module_students.get(mid, set())
        for sid in students:
            if sid not in self.student_daily_exams: self.student_daily_exams[sid] = {}
            self.student_daily_exams[sid][date_str] = self.student_daily_exams[sid].get(date_str, 0) + 1
            
        # Update Room Schedule
        if rid not in self.room_schedule: self.room_schedule[rid] = {}
        if date_str not in self.room_schedule[rid]: self.room_schedule[rid][date_str] = []
        
        # Calculate End Time object
        # Quick hack for time addition
        full_dt = datetime.combine(datetime.today(), t_start) + timedelta(minutes=duration)
        end_time = full_dt.time()
        
        self.room_schedule[rid][date_str].append((t_start, end_time))
        
        # Add to Schedule List
        self.schedule.append({
            'id_module': mid,
            'id_professeur': pid,
            'id_salle': rid,
            'date_examen': date_str,
            'heure_debut': t_start,
            'duree': duration
        })

    def save(self):
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            # 1. Clear Future Exams AND Cache Tables
            # Start date usually implies "current session", so we wipe from start_date onwards
            cursor.execute("DELETE FROM examen WHERE date_examen >= %s", (self.start_date,))
            
            # Clear cache tables for the same date range to prevent accumulation
            cursor.execute("DELETE FROM cache_capacite_examens WHERE id_examen IN (SELECT id_examen FROM examen WHERE date_examen >= %s)", (self.start_date,))
            cursor.execute("DELETE FROM etudiant_examens_jour WHERE date_examen >= %s", (self.start_date,))
            cursor.execute("DELETE FROM suivi_surveillances_jour WHERE date_surveillance >= %s", (self.start_date,))
            
            # Reset professor totals (they'll be recalculated)
            cursor.execute("UPDATE professeur SET total_surveillances = 0")
            
            # 2. Insert New Schedule
            for item in self.schedule:
                # Insert Examen
                q_exam = """
                INSERT INTO examen (id_module, id_professeur, id_salle, date_examen, heure_debut, duree_minutes, annee_univ)
                VALUES (%s, %s, %s, %s, %s, %s, '2024-2025')
                """
                cursor.execute(q_exam, (
                    item['id_module'],
                    item['id_professeur'],
                    item['id_salle'],
                    item['date_examen'],
                    item['heure_debut'],
                    item['duree']
                ))
                exam_id = cursor.lastrowid
                
                # Insert Surveillance (Principal)
                q_surv = """
                INSERT INTO surveillance (id_professeur, id_examen, role)
                VALUES (%s, %s, 'principal')
                """
                cursor.execute(q_surv, (item['id_professeur'], exam_id))

                # --- CACHE TABLES POPULATION ---
                
                # 1. cache_capacite_examens
                nb_students = len(self.module_students.get(item['id_module'], set()))
                room_cap = next((r['capacite'] for r in self.rooms if r['id_salle'] == item['id_salle']), 0)
                
                cursor.execute("""
                    INSERT INTO cache_capacite_examens (id_examen, nb_etudiants_inscrits, capacite_salle)
                    VALUES (%s, %s, %s)
                """, (exam_id, nb_students, room_cap))
                
                # 2. etudiant_examens_jour
                students = self.module_students.get(item['id_module'], set())
                for sid in students:
                    cursor.execute("""
                        INSERT INTO etudiant_examens_jour (id_etudiant, date_examen, nb_examens, liste_examens)
                        VALUES (%s, %s, 1, %s)
                        ON DUPLICATE KEY UPDATE 
                        nb_examens = nb_examens + 1,
                        liste_examens = CONCAT(liste_examens, ',', %s)
                    """, (sid, item['date_examen'], str(exam_id), str(exam_id)))

                # 3. suivi_surveillances_jour
                cursor.execute("""
                    INSERT INTO suivi_surveillances_jour (id_professeur, date_surveillance, nombre_surveillances)
                    VALUES (%s, %s, 1)
                    ON DUPLICATE KEY UPDATE
                    nombre_surveillances = nombre_surveillances + 1
                """, (item['id_professeur'], item['date_examen']))
            
            # Update professeur.total_surveillances for all assigned professors
            for pid, count in self.prof_total_load.items():
                cursor.execute("""
                    UPDATE professeur 
                    SET total_surveillances = total_surveillances + %s
                    WHERE id_professeur = %s
                """, (count, pid))
            
            conn.commit()
            return {
                "assigned": len(self.schedule),
                "unscheduled": self.unscheduled
            }
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
