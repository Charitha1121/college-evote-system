import sqlite3

def create_initial_admin():
    conn = sqlite3.connect('voters.db')
    cursor = conn.cursor()

    # Admin Details
    club_name = "Tech Wizards"
    admin_user = "admin1"
    admin_pass = "pass123"
    department = "CSE"

    try:
        cursor.execute('''
            INSERT INTO clubs (name, admin_user, admin_pass, dept) 
            VALUES (?, ?, ?, ?)
        ''', (club_name, admin_user, admin_pass, department))
        
        conn.commit()
        print(f"Success! Admin created for {club_name}.")
        print(f"Username: {admin_user}")
        print(f"Password: {admin_pass}")
    except sqlite3.IntegrityError:
        print("Error: This admin username or club name already exists.")
    finally:
        conn.close()

if __name__ == "__main__":
    create_initial_admin()