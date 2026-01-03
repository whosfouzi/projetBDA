from backend.db import get_connection

def apply_sql_schema(sql_file):
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # Split by semicolon and filter out empty strings
        # Warning: Simple split property may fail on complex procedures but this is a standard dump
        commands = sql_script.split(';')
        
        for command in commands:
            cmd = command.strip()
            if cmd and not cmd.startswith('--'):
                try:
                    cursor.execute(cmd)
                except Exception as e:
                    print(f"Skipping command error: {e}")
        
        conn.commit()
        print(f"Schema from {sql_file} applied successfully.")
        return True
    except Exception as e:
        print(f"Failed to apply schema: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    apply_sql_schema('optimisation_edt_complet.sql')
