import sqlite3

def create_initial_admins():
    conn = sqlite3.connect('voters.db')
    cursor = conn.cursor()

    # Ensure the table exists before inserting
    cursor.execute('''CREATE TABLE IF NOT EXISTS clubs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE, admin_user TEXT UNIQUE, admin_pass TEXT, dept TEXT,
        reg_start TEXT, reg_end TEXT, vote_start TEXT, vote_end TEXT
    )''')

    # List of Admin Details (Club Name, Username, Password, Department)
    clubs_to_add = [
        ("Tech Wizards", "admin1", "pass123", "CSE"),
        ("Eco Club", "admin2", "green456", "ECE"),
        ("Literary Society", "admin3", "read789", "MECH")
    ]

    for club in clubs_to_add:
        try:
            cursor.execute('''
                INSERT INTO clubs (name, admin_user, admin_pass, dept) 
                VALUES (?, ?, ?, ?)
            ''', club)
            print(f"Success! Admin created for {club[0]}. (User: {club[1]})")
        except sqlite3.IntegrityError:
            print(f"Skip: The club '{club[0]}' or username '{club[1]}' already exists.")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_initial_admins()