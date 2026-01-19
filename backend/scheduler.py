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
        self.spec_daily_exams = {} # {spec_id: {date_str: count}}
        
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
        # 1. Fetch Modules
        q_mods = """
        SELECT 
            m.id_module, m.nom, m.id_spec, 
            a.niveau as year_lvl, a.id_dep as dept_id
        FROM module m
        JOIN specialite s ON m.id_spec = s.id_spec
        JOIN annee_etude a ON s.id_annee = a.id_annee
        """
        self.modules = run_query(q_mods)
        
        # 2. Fetch Students & Groups
        q_all_students = "SELECT id_etudiant, id_spec, groupe_numero FROM etudiant"
        all_students = run_query(q_all_students)
        
        self.module_students = {}
        self.spec_groups = {} # {id_spec: {gid: count}}
        self.spec_students = {} # {id_spec: [sids]}

        # Pre-process students
        for s in all_students:
            sid = s['id_etudiant']
            spec = s['id_spec']
            gid = s['groupe_numero']
            
            self.spec_students.setdefault(spec, set()).add(sid)
            
            if spec not in self.spec_groups: self.spec_groups[spec] = {}
            if gid: 
                self.spec_groups[spec][gid] = self.spec_groups[spec].get(gid, 0) + 1

        for m in self.modules:
            mid = m['id_module']
            spec = m['id_spec']
            
            # Link students
            self.module_students[mid] = self.spec_students.get(spec, set())
            m['nb_students'] = len(self.module_students[mid])
            
            # Link groups (List of dicts: {'gid': gid, 'size': count})
            groups_dict = self.spec_groups.get(spec, {})
            # Sort groups by size desc
            m['groups'] = sorted([{'gid': k, 'size': v} for k, v in groups_dict.items()], key=lambda x: x['size'], reverse=True)

            
        # 3. Fetch Rooms
        self.rooms = run_query("SELECT id_salle, nom, capacite, type FROM salle ORDER BY capacite ASC")
        
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
        # Optimized: Modules belong to specs. If the spec already has an exam this day, 
        # all students in that spec are effectively busy.
        spec_id = next((m['id_spec'] for m in self.modules if m['id_module'] == module_id), None)
        if not spec_id: return False
        
        max_allowed = self.constraints['max_examens_etudiant_par_jour']
        load = self.spec_daily_exams.get(spec_id, {}).get(date_str, 0)
        return load >= max_allowed

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

    def find_rooms(self, groups_list, date_str, start_time):
        """
        Input: groups_list = [{'gid': 1, 'size': 35}, ...]
        Returns: assignments = [{'room': r, 'count': c, 'groups': [{'gid': 1, 'count': 35}]}]
        """
        MAX_AMPHI = 70 
        MAX_SALLE = 20
        
        # Use explicit groups
        groups = groups_list

            
        assignments = [] # [{'room': r, 'count': c}]
        used_room_ids = set()
        
        # Get all potential rooms once
        available_rooms = [r for r in self.rooms if self.check_room_availability(r['id_salle'], date_str, start_time)]
        # Separate Amphis and Salles
        amphis = sorted([r for r in available_rooms if r['type'] == 'amphi'], key=lambda x: x['capacite'])
        salles = sorted([r for r in available_rooms if r['type'] != 'amphi'], key=lambda x: x['capacite'], reverse=True) # Big salles first (usually 20 anyway)
        
        def is_room_used(rid):
            return rid in used_room_ids
        
        def mark_used(rid):
            used_room_ids.add(rid)

        # 2. Process Groups
        # We try to fill Amphis first (efficient for multiple groups)
        # Then Salles for remaining
        
        # Optimization: Try to couple groups into Amphis
        # E.g. Group 35 + Group 25 = 60 -> Perfect Amphi
        
        current_amphi_idx = 0
        current_amphi_fill = 0
        
        for g in groups:
            g_size = g['size']
            gid = g['gid']
            allocated = False
            
            # A. Try Amphi Allocation (Merge strategy)
            # Find an amphi that has space or is empty
            
            # 1. Check currently open amphi
            if current_amphi_idx < len(amphis):
                amp = amphis[current_amphi_idx]
                # Can we fit this group?
                if current_amphi_fill + g_size <= min(amp['capacite'], 70): # Hard cap 70
                    # Assign to this amphi
                    
                    # Check if we already have an assignment entry for this room
                    existing_assign = next((a for a in assignments if a['room']['id_salle'] == amp['id_salle']), None)
                    if existing_assign:
                        existing_assign['count'] += g_size
                        existing_assign['groups'].append({'gid': gid, 'count': g_size})
                    else:
                        assignments.append({'room': amp, 'count': g_size, 'groups': [{'gid': gid, 'count': g_size}]})
                    
                    current_amphi_fill += g_size
                    mark_used(amp['id_salle'])
                    allocated = True
                else:
                    # This amphi is full/too small for this group addition. Close it.
                    current_amphi_idx += 1
                    current_amphi_fill = 0
                    
                    # Try next amphi
                    if current_amphi_idx < len(amphis):
                        amp = amphis[current_amphi_idx]
                        if g_size <= min(amp['capacite'], 70):
                            assignments.append({'room': amp, 'count': g_size, 'groups': [{'gid': gid, 'count': g_size}]})
                            current_amphi_fill += g_size
                            mark_used(amp['id_salle'])
                            allocated = True
            
            if allocated: continue
            
            # B. If no Amphi, force Split into Salles
            # Group of 35 -> Salle (20) + Salle (15)
            
            remaining_in_group = g_size
            
            # Find free salles
            for s in salles:
                if is_room_used(s['id_salle']): continue
                
                # Take 20 or remaining
                chunk = min(remaining_in_group, MAX_SALLE)
                # Also limited by room cap (though data says salles are 20+)
                chunk = min(chunk, s['capacite'])
                
                assignments.append({'room': s, 'count': chunk, 'groups': [{'gid': gid, 'count': chunk}]})
                mark_used(s['id_salle'])
                remaining_in_group -= chunk
                
                if remaining_in_group <= 0:
                    allocated = True
                    break
            
            if not allocated:
                return None # Could not fit this group -> Fail this slot
                
        return assignments

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
                rooms = self.find_rooms(mod['groups'], date_str, t_start)
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
        
        # Optimized Specialization-Level Tracking
        spec_id = mod['id_spec']
        if spec_id not in self.spec_daily_exams: self.spec_daily_exams[spec_id] = {}
        self.spec_daily_exams[spec_id][date_str] = self.spec_daily_exams[spec_id].get(date_str, 0) + 1

        # Now handle the split across rooms based on our specific Allocation Plan
        # rooms is now [{'room': r, 'count': c}, ...]
        
        assigned_total = 0
        for assignment in rooms:
            r = assignment['room']
            count = assignment['count']
            rid = r['id_salle']
            
            # Double check against strict constraints (just in case)
            limit = self.constraints['max_etudiants_par_salle']
            if r['type'] != 'amphi' and count > limit:
                # This should not happen if find_rooms is correct
                print(f"WARNING: Room {rid} assigned {count} > {limit}. Cap: {r['capacite']}")
            
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
                'nb_students_assigned': count, # Explicit count from our plan
                'groups': assignment.get('groups', []) # Mapping of groups in this room
            })
            assigned_total += count

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
            'nb_students_assigned': exam.get('nb_students_assigned', 0),
            'groups': exam.get('groups', [])
        })

    def save(self):
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            # 0. Increase lock wait timeout for this session to avoid cloud latency issues
            cursor.execute("SET SESSION innodb_lock_wait_timeout = 180")
            # Temporarily disable foreign key checks for bulk delete/insert operations
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

            # 1. Clear Future Exams AND Cache Tables
            # Start date usually implies "current session", so we wipe from start_date onwards
            cursor.execute("DELETE FROM examen WHERE date_examen >= %s", (self.start_date,))
            
            # Clear cache tables (since they depend on examen IDs)
            cursor.execute("DELETE FROM exam_groupe_track WHERE id_examen NOT IN (SELECT id_examen FROM examen)")
            cursor.execute("DELETE FROM cache_capacite_examens WHERE id_examen NOT IN (SELECT id_examen FROM examen)")
            cursor.execute("DELETE FROM etudiant_examens_jour WHERE date_examen >= %s", (self.start_date,))
            cursor.execute("DELETE FROM suivi_surveillances_jour WHERE date_surveillance >= %s", (self.start_date,))
            
            # Reset professor totals (they'll be recalculated)
            cursor.execute("UPDATE professeur SET total_surveillances = 0")
            
            # 2. Prepare batch data for insertion
            exam_data = []
            surveillance_data = []
            group_track_data = []
            cache_capacite_data = []
            student_exam_updates = {}  # {(sid, date): set(exam_ids)}
            prof_surveillance_updates = {}  # {(pid, date): count}
            recorded_student_exams = set()
            
            # Collect all data first
            for item in self.final_schedule:
                exam_data.append((
                    item['id_module'],
                    item['id_professeur'],
                    item['id_salle'],
                    item['date_examen'],
                    item['heure_debut'],
                    item['duree'],
                    '2024-2025'
                ))
            
            # 3. Batch insert exams
            if exam_data:
                q_exam = """
                INSERT INTO examen (id_module, id_professeur, id_salle, date_examen, heure_debut, duree_minutes, annee_univ)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.executemany(q_exam, exam_data)
                first_exam_id = cursor.lastrowid
                
                # 4. Prepare dependent data
                for idx, item in enumerate(self.final_schedule):
                    exam_id = first_exam_id + idx
                    item_date = item['date_examen']
                    
                    # Surveillance
                    surveillance_data.append((item['id_professeur'], exam_id, 'principal'))
                    
                    # Group tracking
                    spec_id_val = next((m['id_spec'] for m in self.modules if m['id_module'] == item['id_module']), None)
                    if spec_id_val and 'groups' in item:
                        for g in item['groups']:
                            group_track_data.append((exam_id, spec_id_val, g['gid'], g['count']))
                    
                    # Cache capacite
                    nb_students = item.get('nb_students_assigned', 0)
                    room_cap = next((r['capacite'] for r in self.rooms if r['id_salle'] == item['id_salle']), 0)
                    cache_capacite_data.append((exam_id, nb_students, room_cap))
                    
                    # Professor daily load update
                    prof_key = (item['id_professeur'], item_date)
                    prof_surveillance_updates[prof_key] = prof_surveillance_updates.get(prof_key, 0) + 1

                # 5. Batch insert dependent tables (OUTSIDE LOOP)
                if surveillance_data:
                    cursor.executemany("INSERT INTO surveillance (id_professeur, id_examen, role) VALUES (%s, %s, %s)", surveillance_data)
                
                if group_track_data:
                    cursor.executemany("INSERT INTO exam_groupe_track (id_examen, id_spec, groupe_numero, assigned_count) VALUES (%s, %s, %s, %s)", group_track_data)
                
                if cache_capacite_data:
                    cursor.executemany("INSERT INTO cache_capacite_examens (id_examen, nb_etudiants_inscrits, capacite_salle) VALUES (%s, %s, %s)", cache_capacite_data)
                
                # 6. EXTREME OPTIMIZATION: Move student tracking updates to SQL JOINs
                # We use DISTINCT and GROUP BY to ensure each MODULE is only counted once per student per day,
                # even if it is split across multiple rooms (multiple id_examen).
                q_track_students = """
                INSERT INTO etudiant_examens_jour (id_etudiant, date_examen, nb_examens, liste_examens)
                SELECT 
                    s.id_etudiant, 
                    e.date_examen, 
                    COUNT(DISTINCT e.id_module), 
                    GROUP_CONCAT(DISTINCT e.id_examen)
                FROM examen e
                JOIN exam_groupe_track gt ON e.id_examen = gt.id_examen
                JOIN etudiant s ON gt.id_spec = s.id_spec AND gt.groupe_numero = s.groupe_numero
                WHERE e.date_examen >= %s
                GROUP BY s.id_etudiant, e.date_examen
                """
                cursor.execute(q_track_students, (self.start_date,))

                # B. Update Professor Tracking
                if prof_surveillance_updates:
                    prof_day_batch = []
                    for (pid, pdate), count in prof_surveillance_updates.items():
                        # Only 3 parameters needed because we use VALUES() in the update clause
                        prof_day_batch.append((pid, pdate, count))
                    
                    cursor.executemany("""
                        INSERT INTO suivi_surveillances_jour (id_professeur, date_surveillance, nombre_surveillances)
                        VALUES (%s, %s, %s)
                        ON DUPLICATE KEY UPDATE nombre_surveillances = nombre_surveillances + VALUES(nombre_surveillances)
                    """, prof_day_batch)
            
            # 7. Final Batch Update for Professor Totals
            if self.prof_total_load:
                prof_total_batch = []
                for pid, count in self.prof_total_load.items():
                    prof_total_batch.append((count, pid))
                
                cursor.executemany("""
                    UPDATE professeur 
                    SET total_surveillances = total_surveillances + %s
                    WHERE id_professeur = %s
                """, prof_total_batch)
            
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
            try:
                cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            except:
                pass
            cursor.close()
            conn.close()
