from backend.db import run_query

# 1. Teacher Limit (Max 3/day)
def check_teacher_overload():
    query = """
    SELECT 
        p.nom, p.prenom, s.date_surveillance, s.nombre_surveillances
    FROM suivi_surveillances_jour s
    JOIN professeur p ON s.id_professeur = p.id_professeur
    WHERE s.nombre_surveillances > 3
    """
    return run_query(query)

# 2. Teacher Fairness (StdDev) - Requires MySQL 8.0+ for STDDEV
def check_teacher_fairness():
    # Calcul de l'écart-type du nombre total de surveillances par prof
    query = """
    SELECT STDDEV(total_surveillances) as ecart_type, AVG(total_surveillances) as moyenne
    FROM (
        SELECT COUNT(*) as total_surveillances 
        FROM surveillance 
        GROUP BY id_professeur
    ) as sub
    """
    return run_query(query)

# 3. Student Limit (1 exam/day)
def check_student_overload():
    query = """
    SELECT e.nom, e.prenom, ex.date_examen, COUNT(*) as nb_examens
    FROM inscription i
    JOIN examen ex ON i.id_module = ex.id_module
    JOIN etudiant e ON i.id_etudiant = e.id_etudiant
    GROUP BY e.id_etudiant, ex.date_examen
    HAVING nb_examens > 1
    """
    return run_query(query)

# 4. Room Capacity (Max 20 Students per Exam - User Rule)
def check_room_capacity_rule():
    # User specifies "room cant have more than 20 student per exam"
    query = """
    SELECT 
        ex.id_examen, m.nom as module, s.nom as salle, COUNT(i.id_etudiant) as nb_etudiants
    FROM examen ex
    JOIN inscription i ON ex.id_module = i.id_module
    JOIN salle s ON ex.id_salle = s.id_salle
    JOIN module m ON ex.id_module = m.id_module
    GROUP BY ex.id_examen
    HAVING nb_etudiants > 20
    """
    return run_query(query)

# 5. Room Exclusivity (No Double Booking)
def check_room_conflicts():
    query = """
    SELECT 
        e1.id_examen as exam1_id, e2.id_examen as exam2_id,
        s.nom as salle,
        e1.date_examen,
        e1.heure_debut as start1, e1.heure_fin as end1,
        e2.heure_debut as start2, e2.heure_fin as end2
    FROM examen e1
    JOIN examen e2 ON e1.id_salle = e2.id_salle
    JOIN salle s ON e1.id_salle = s.id_salle
    WHERE e1.id_examen < e2.id_examen
    AND e1.date_examen = e2.date_examen
    AND (
        (e1.heure_debut < e2.heure_fin AND e1.heure_fin > e2.heure_debut)
    )
    """
    return run_query(query)

def get_all_violations():
    return {
        "teacher_overload": check_teacher_overload(),
        "teacher_fairness": check_teacher_fairness(),
        "student_overload": check_student_overload(),
        "room_capacity": check_room_capacity_rule(),
        "room_conflicts": check_room_conflicts()
    }
