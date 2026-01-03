from backend.db import get_connection, run_query
from datetime import datetime, timedelta, time
import random

class GreedyScheduler:
    def __init__(self, start_date, days=14):
        self.start_date = start_date
        self.days = days
        self.log = []
        
        # State Tracking
        self.schedule = [] # List of assigned exams (preliminary: module, room, slot)
        self.final_schedule = [] # Final list with professors
        self.unscheduled = []
        self.flags = [] # For reporting workload violations
        
        # Constraint Trackers
        self.prof_daily_load = {} # {prof_id: {date_str: count}}
        self.prof_total_load = {} # {prof_id: total_count}
        self.student_daily_exams = {} # {student_id: {date_str: count}}
        self.room_schedule = {} # {room_id: {date_str: [(start_time, end_time)]}}
        self.prof_schedule = {} # {prof_id: {date_str: [(start_time, end_time)]}}
        
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
            'max_etudiants_par_salle': constraints.get('max_etudiants_par_salle', 20),
            'duree_examen_minutes': constraints.get('duree_examen_minutes', 90)  # 1:30h default
        }
        
    def fetch_data(self):
        # 1. Fetch Modules with Student Counts (Implicit by Speciality)
        q_mods = """
        SELECT 
            m.id_module, m.nom, m.id_spec, 
            a.niveau as year_lvl, a.id_dep as dept_id,
            (SELECT COUNT(*) FROM etudiant e WHERE e.id_spec = m.id_spec) as nb_students
        FROM module m
        JOIN specialite s ON m.id_spec = s.id_spec
        JOIN annee_etude a ON s.id_annee = a.id_annee
        GROUP BY m.id_module, m.nom, m.id_spec, a.niveau, a.id_dep
        ORDER BY nb_students DESC
        """
        self.modules = run_query(q_mods)
        
        # 2. Fetch Module -> Student Mapping (Implicit by Speciality)
        # Instead of reading from 'inscription', we link students to modules via 'id_spec'
        q_all_students = "SELECT id_etudiant, id_spec FROM etudiant"
        all_students = run_query(q_all_students)
        
        self.module_students = {}
        # Map students once for efficiency
        spec_students = {} # {id_spec: [sid1, sid2...]}
        for s in all_students:
            spec_students.setdefault(s['id_spec'], set()).add(s['id_etudiant'])
        
        for m in self.modules:
            mid = m['id_module']
            sid_spec = m['id_spec']
            self.module_students[mid] = spec_students.get(sid_spec, set())
            
        # 3. Fetch Rooms
        self.rooms = run_query("SELECT id_salle, nom, capacite FROM salle ORDER BY capacite ASC")
        
        # 4. Fetch Profs
        self.profs = run_query("SELECT id_professeur, nom, prenom, id_departement FROM professeur")
        # Init Prof Load
        for p in self.profs:
            pid = p['id_professeur']
            self.prof_total_load[pid] = 0
            self.prof_daily_load[pid] = {}

    def get_slots(self):
        """Generate time slots (Day, Hour)"""
        slots = []
        current = self.start_date
        # Exam hours: 09:00, 11:00, 13:00, 15:00
        daily_starts = [
            time(9, 0), time(11, 0), time(13, 0), time(15, 0)
        ]
        
        for d in range(self.days):
            date_obj = current + timedelta(days=d)
            # Skip Fridays (4) and Sundays (6)
            if date_obj.weekday() in [4, 6]: 
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

    def find_rooms(self, total_students, date_str, start_time):
        """
        Find a set of rooms to accommodate total_students, with max per room from config.
        Returns a list of rooms or None.
        """
        MAX_PER_ROOM = self.constraints['max_etudiants_par_salle']
        # Calculate how many rooms we need
        import math
        needed_rooms = math.ceil(total_students / MAX_PER_ROOM)
        
        assigned_rooms = []
        
        # We need to find 'needed_rooms' available rooms
        # We prefer smaller rooms first to save big ones? Or just any that fit 20?
        # Since max is 20, any room with cap >= 20 is good. Even cap >= 1 works if we fill it?
        # The constraint says "no room may host more than 20".
        # It doesn't say we MUST put 20. But to minimize rooms, we target 20.
        # Let's naive approach: Find N rooms that have cap >= 1 (we just need space).
        # Actually, we need rooms that can hold the chunk we put in. 
        # Simpler: Find N rooms with capacity >= 20. If not enough big rooms, maybe smaller ones?
        # "This constraint applies to all rooms... no room may host more than 20"
        # So we cap usage at 20. The room physical capacity must also be respected.
        # Usage = min(20, room.capacity).
        
        students_to_seat = total_students
        potential_rooms = []
        
        # Get all available rooms at this slot
        for r in self.rooms:
            if self.check_room_availability(r['id_salle'], date_str, start_time):
                potential_rooms.append(r)
        
        # Sort by capacity? Or random?
        # Let's sort by capacity ascending to use smallest viable rooms first?
        # Or descending to ensure we fit 20?
        # We want to fit 20 students comfortably.
        potential_rooms.sort(key=lambda x: x['capacite'], reverse=True)
        
        picked = []
        for r in potential_rooms:
            cap = min(r['capacite'], MAX_PER_ROOM)
            if cap > 0:
                picked.append(r)
                students_to_seat -= cap
                if students_to_seat <= 0:
                    break
        
        if students_to_seat <= 0:
            return picked
        return None

    def check_prof_availability(self, prof_id, date_str, start_time, duration_mins=None):
        if duration_mins is None:
            duration_mins = self.constraints['duree_examen_minutes']
            
        def to_mins(t): return t.hour * 60 + t.minute
        start_m = to_mins(start_time)
        end_m = start_m + duration_mins
        
        existing = self.prof_schedule.get(prof_id, {}).get(date_str, [])
        for (estart, eend) in existing:
            e_start_m = to_mins(estart)
            e_end_m = to_mins(eend)
            if max(start_m, e_start_m) < min(end_m, e_end_m):
                return False # Overlap
        return True

    def solve(self):
        random.seed(42)
        self.fetch_data()
        slots = self.get_slots()
        
        for mod in self.modules:
            assigned = False
            mid = mod['id_module']
            ylvl = mod['year_lvl']
            nb_studs = mod['nb_students']
            if nb_studs == 0: continue

            # Search all available slots across all days
            for (date_str, t_start) in slots:
                # Rule 3: Student Conflict
                if self.check_student_conflict(mid, date_str):
                    continue
                
                # Rule 4: Room Availability
                rooms = self.find_rooms(nb_studs, date_str, t_start)
                if not rooms:
                    continue
                
                self.commit_preliminary_assignment(mod, rooms, date_str, t_start)
                assigned = True
                break
            
            if not assigned:
                self.unscheduled.append(f"{mod['nom']} ({ylvl})")
        
        # Pass 2: Professor Assignment
        self.assign_professors()

    def commit_preliminary_assignment(self, mod, rooms, date_str, t_start):
        mid = mod['id_module']
        duration = self.constraints['duree_examen_minutes']
        
        full_dt = datetime.combine(datetime.today(), t_start) + timedelta(minutes=duration)
        end_time = full_dt.time()
        
        # Update Student Load (Preliminary) - Once per module, not per room chunk
        students = self.module_students.get(mid, set())
        for sid in students:
            if sid not in self.student_daily_exams: self.student_daily_exams[sid] = {}
            # We add 1 to the load. 
            # CAUTION: If we already added this module to this day (unlikely in greedy pass 1), don't double count.
            # Dict .get() handles fresh addition.
            # But wait, we are splitting one module into multiple entries.
            # We should only increment student load ONCE.
            # The current logic loops rooms. We must do student load UPDATE outside the room loop.
            pass
            
        # Actually, let's update student load here for the WHOLE module assignment
        for sid in students:
             if sid not in self.student_daily_exams: self.student_daily_exams[sid] = {}
             # Only increment if not already counted for this module/time? 
             # Just incrementing is fine because we only call commit_preliminary once per module.
             self.student_daily_exams[sid][date_str] = self.student_daily_exams[sid].get(date_str, 0) + 1

        # Now handle the split across rooms
        students_remaining = len(students) if students else mod['nb_students'] # Fallback
        
        for r in rooms:
            rid = r['id_salle']
            
            # Calculate how many students in this room
            # We cap at config Max or room capacity
            limit = self.constraints['max_etudiants_par_salle']
            cap = min(r['capacite'], limit)
            students_in_room = min(students_remaining, cap)
            students_remaining -= students_in_room
            
            # Update Room Schedule
            if rid not in self.room_schedule: self.room_schedule[rid] = {}
            if date_str not in self.room_schedule[rid]: self.room_schedule[rid][date_str] = []
            self.room_schedule[rid][date_str].append((t_start, end_time))
            
            # Add Exam Entry
            self.schedule.append({
                'module': mod,
                'room': r,
                'date_examen': date_str,
                'heure_debut': t_start,
                'duree': duration,
                'nb_students_assigned': students_in_room 
            })

    def assign_professors(self):
        # Group preliminary exams by date
        exams_by_day = {} # {date_str: [exams]}
        for exam in self.schedule:
            d = exam['date_examen']
            if d not in exams_by_day: exams_by_day[d] = []
            exams_by_day[d].append(exam)
        
        for d, day_exams in exams_by_day.items():
            assigned_today = []
            available_profs = self.profs.copy()
            
            # Pass 1: Compact 3-exam blocks (Efficiency)
            for prof in available_profs:
                pid = prof['id_professeur']
                did = prof['id_departement']
                remaining_exams = [e for e in day_exams if e not in assigned_today]
                if not remaining_exams: break
                
                pool = sorted(remaining_exams, key=lambda x: (0 if x['module']['dept_id'] == did else 1, x['heure_debut']))
                
                current_prof_block = []
                for e in pool:
                    if self.check_prof_availability_local(pid, d, e['heure_debut'], e['duree'], current_prof_block):
                        current_prof_block.append(e)
                        if len(current_prof_block) == 3: break
                
                if len(current_prof_block) == 3:
                    for e in current_prof_block:
                        self.finalize_assignment(e, prof)
                        assigned_today.append(e)

            # Pass 2: Individual Assignments for Leftovers
            limit = self.constraints['max_surveillances_prof_par_jour']
            leftover = [e for e in day_exams if e not in assigned_today]
            
            for e in leftover:
                prof_found = False
                # Try same dept first
                candidates = sorted(available_profs, key=lambda x: 0 if x['id_departement'] == e['module']['dept_id'] else 1)
                
                for prof in candidates:
                    pid = prof['id_professeur']
                    if self.prof_daily_load[pid].get(d, 0) < limit:
                        if self.check_prof_availability(pid, d, e['heure_debut'], e['duree']):
                            self.finalize_assignment(e, prof)
                            assigned_today.append(e)
                            prof_found = True
                            break
                
                if not prof_found:
                    self.unscheduled.append(f"{e['module']['nom']} (Insufficient surveillance capacity)")

    def check_prof_availability_local(self, prof_id, date_str, start_time, duration, current_block):
        if not self.check_prof_availability(prof_id, date_str, start_time, duration):
            return False
        
        def to_mins(t): return t.hour * 60 + t.minute
        start_m = to_mins(start_time)
        end_m = start_m + duration
        
        for e in current_block:
            e_start_m = to_mins(e['heure_debut'])
            e_end_m = e_start_m + e['duree']
            if max(start_m, e_start_m) < min(end_m, e_end_m):
                return False
        return True

    def finalize_assignment(self, exam, prof):
        pid = prof['id_professeur']
        d = exam['date_examen']
        t_start = exam['heure_debut']
        duration = exam['duree']
        
        # Update Prof Load
        self.prof_total_load[pid] += 1
        self.prof_daily_load[pid][d] = self.prof_daily_load[pid].get(d, 0) + 1
        
        # Update Prof Schedule
        if pid not in self.prof_schedule: self.prof_schedule[pid] = {}
        if d not in self.prof_schedule[pid]: self.prof_schedule[pid][d] = []
        
        full_dt = datetime.combine(datetime.today(), t_start) + timedelta(minutes=duration)
        end_time = full_dt.time()
        self.prof_schedule[pid][d].append((t_start, end_time))
        
        self.final_schedule.append({
            'id_module': exam['module']['id_module'],
            'id_professeur': pid,
            'id_salle': exam['room']['id_salle'],
            'date_examen': d,
            'heure_debut': t_start,
            'duree': duration,
            'nb_students_assigned': exam.get('nb_students_assigned', 0)
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
            for item in self.final_schedule:
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
                # Use the specific split count if available, otherwise total (fallback)
                nb_students = item.get('nb_students_assigned', len(self.module_students.get(item['id_module'], set())))
                
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
                "assigned": len(self.final_schedule),
                "unscheduled": self.unscheduled,
                "flags": self.flags
            }
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
