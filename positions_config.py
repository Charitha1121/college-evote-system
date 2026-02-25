def init_db():
    conn = get_db_connection()
    # Stores Club Settings & Timelines
    conn.execute('''CREATE TABLE IF NOT EXISTS clubs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        admin_user TEXT UNIQUE,
        admin_pass TEXT,
        dept TEXT,
        reg_start DATETIME,
        reg_end DATETIME,
        vote_start DATETIME,
        vote_end DATETIME
    )''')
    
    # Stores which positions are available for which years (e.g., Year 3: President)
    conn.execute('''CREATE TABLE IF NOT EXISTS positions_config (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        club_name TEXT,
        year INTEGER,
        position_name TEXT
    )''')

    # Existing tables remain...
    conn.execute('''CREATE TABLE IF NOT EXISTS candidates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, roll TEXT, phone TEXT, position TEXT, club TEXT,
        status TEXT DEFAULT 'pending', vote_count INTEGER DEFAULT 0
    )''')
    conn.commit()
    conn.close()