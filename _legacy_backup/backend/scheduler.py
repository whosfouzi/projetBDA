import pandas as pd
from datetime import datetime, timedelta, time
from backend.db import run_query, get_connection
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
        
    def fetch_data(self):
        # 1. Fetch Modules with Student Counts
        q_mods = """
        SELECT m.id_module, m.nom, COUNT(i.id_etudiant) as nb_students, m.id_formation
        FROM module m
        LEFT JOIN inscription i ON m.id_module = i.id_module
        GROUP BY m.id_module
        ORDER BY nb_students DESC
        """
        self.modules = run_query(q_mods)
        
        # 2. Fetch Module -> Student Mapping (for Rule 3)
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
            self.prof_total_load[p['id_professeur']] = 0
            self.prof_daily_load[p['id_professeur']] = {}

    def get_slots(self):
        """Generate time slots (Day, Hour)"""
        slots = []
        current = self.start_date
        # Exam hours: 08:30, 11:00, 13:30, 16:00 (Example)
        daily_starts = [
            time(8, 30), time(11, 0), time(13, 30), time(16, 0)
        ]
        
        for d in range(self.days):
            date_obj = current + timedelta(days=d)
            # Skip Sundays/Weekends if needed (Skipping Sunday = 6)
            if date_obj.weekday() == 6: 
                continue
                
            date_str = date_obj.strftime("%Y-%m-%d")
            for h in daily_starts:
                slots.append((date_str, h))
        return slots

    def check_student_conflict(self, module_id, date_str):
        # Rule 3: Student max 1 exam per day
        students_in_module = self.module_students.get(module_id, set())
        for sid in students_in_module:
            if self.student_daily_exams.get(sid, {}).get(date_str, 0) >= 1:
                return True # Conflict found
        return False

    def check_room_availability(self, room_id, date_str, start_time, duration_mins=120):
        # Rule 5: Room Exclusivity
        # Simple overlap check. Assumes fixed slot duration for simplicity or checks intervals.
        # Here we just check if the room has ANY exam at this (date, start_time) slot.
        # Ideally we check full time range.
        
        # Convert to Minutes for comparison
        def to_mins(t): return t.hour * 60 + t.minute
        
        start_m = to_mins(start_time)
        end_m = start_m + duration_mins
        
        existing = self.room_schedule.get(room_id, {}).get(date_str, [])
        for (estart, eend) in existing:
            e_start_m = to_mins(estart)
            e_end_m = to_mins(eend)
            
            # Intersection logic
            if max(start_m, e_start_m) < min(end_m, e_end_m):
                return False # Overlap
        return True

    def find_room(self, nb_students, date_str, start_time):
        # Rule 4: Room Capacity > Students
        candidates = [r for r in self.rooms if r['capacite'] >= nb_students]
        
        for r in candidates:
            if self.check_room_availability(r['id_salle'], date_str, start_time):
                return r
        return None

    def find_prof(self, date_str):
        # Rule 1: Max 3 exams per day
        # Rule 2: Fairness (heuristic: pick least loaded)
        
        candidates = []
        for p in self.profs:
            pid = p['id_professeur']
            daily = self.prof_daily_load[pid].get(date_str, 0)
            if daily < 3:
                candidates.append(p)
                
        if not candidates:
            return None
            
        # Sort by TOTAL load for Fairness
        candidates.sort(key=lambda x: self.prof_total_load[x['id_professeur']])
        return candidates[0]

    def solve(self):
        self.fetch_data()
        slots = self.get_slots()
        
        for mod in self.modules:
            assigned = False
            mid = mod['id_module']
            nb_studs = mod['nb_students']
            
            # Try every slot
            for (date_str, t_start) in slots:
                # 1. Check Student Rule
                if self.check_student_conflict(mid, date_str):
                    continue
                
                # 2. Check Room Rule
                room = self.find_room(nb_studs, date_str, t_start)
                if not room:
                    continue
                
                # 3. Check Prof Rule
                prof = self.find_prof(date_str)
                if not prof:
                    continue
                    
                # ALL VALID -> ASSIGN
                self.commit_assignment(mod, room, prof, date_str, t_start)
                assigned = True
                break
            
            if not assigned:
                self.unscheduled.append(mod['nom'])

    def commit_assignment(self, mod, room, prof, date_str, t_start):
        # Update State
        mid = mod['id_module']
        pid = prof['id_professeur']
        rid = room['id_salle']
        
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
        # Calc End time (Assume 120 mins)
        duration = 120
        end_dt = (datetime.combine(datetime.today(), t_start) + timedelta(minutes=duration)).time()
        self.room_schedule[rid][date_str].append((t_start, end_dt))
        
        # Add to List for DB
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
        
        # Clear Future Exams
        # 'surveillance' table has ON DELETE CASCADE, so we only need to delete from 'examen'
        cursor.execute("DELETE FROM examen WHERE date_examen >= %s", (self.start_date,))
        
        # Bulk Insert
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
            
            # Insert Surveillance
            q_surv = """
            INSERT INTO surveillance (id_professeur, id_examen, date_surveillance)
            VALUES (%s, %s, %s)
            """
            cursor.execute(q_surv, (item['id_professeur'], exam_id, item['date_examen']))
            
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "assigned": len(self.schedule),
            "unscheduled": self.unscheduled,
            "prof_metrics": self.prof_total_load
        }
