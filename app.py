from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime, timedelta
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "evotex_secure_key_2026"

# -------------------------------
# CONFIGURATION (Timeline)
# -------------------------------
REGISTRATION_START = datetime(2026, 1, 1, 9, 0, 0)
REGISTRATION_END = datetime(2026, 1, 1, 18, 0, 0) 
VOTING_START = datetime(2026, 1, 20, 9, 0, 0)     
VOTING_END = datetime(2026, 1, 25, 18, 0, 0)       

# -------------------------------
# DATABASE SETUP
# -------------------------------
def get_db_connection():
    conn = sqlite3.connect('voters.db')
    conn.row_factory = sqlite3.Row  
    return conn

def init_db():
    conn = get_db_connection()
    # Table for Candidates
    conn.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll TEXT NOT NULL,
            phone TEXT NOT NULL,
            position TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            vote_count INTEGER DEFAULT 0
        )
    ''')
    # Table for Voter Tracking (To prevent double voting)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS voters (
            roll_number TEXT PRIMARY KEY
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# -------------------------------
# HELPER FUNCTIONS
# -------------------------------
def get_current_phase():
    # FOR TESTING: Change this to return whatever phase you want to see
    # return "REGISTRATION_OPEN"
    # return "VOTING_OPEN"
   # return "RESULTS_PHASE" 

    # LIVE LOGIC (Comment out the return above and uncomment this for production):
    
    now = datetime.now()
    if now < REGISTRATION_START: return "PRE_REGISTRATION"
    elif REGISTRATION_START <= now <= REGISTRATION_END: return "REGISTRATION_OPEN"
    elif REGISTRATION_END < now < VOTING_START: return "COUNTDOWN_TO_VOTING"
    elif VOTING_START <= now <= VOTING_END: return "VOTING_OPEN"
    else: return "RESULTS_PHASE"
    

# -------------------------------
# ROUTES
# -------------------------------

@app.route('/')
def home():
    phase = get_current_phase()
    now = datetime.now()
    countdown = None
    if phase == "REGISTRATION_OPEN":
        countdown = REGISTRATION_END - now
    elif phase == "COUNTDOWN_TO_VOTING":
        countdown = VOTING_START - now

    return render_template("home.html", phase=phase, countdown=countdown, 
                           reg_end=REGISTRATION_END, vote_start=VOTING_START)

@app.route('/candidate/register', methods=['GET', 'POST'])
def candidate_register():
    if get_current_phase() != "REGISTRATION_OPEN":
        flash("Registration is currently closed.")
        return redirect(url_for('home'))

    if request.method == 'POST':
        name, roll = request.form.get('name'), request.form.get('roll')
        phone, pos = request.form.get('phone'), request.form.get('position')
        
        conn = get_db_connection()
        conn.execute('INSERT INTO candidates (name, roll, phone, position) VALUES (?, ?, ?, ?)',
                     (name, roll, phone, pos))
        conn.commit()
        conn.close()
        return render_template("success.html", message="Application submitted successfully!")
    return render_template("candidate_register.html")

@app.route('/admin_dashboard')
def admin_dashboard():
    conn = get_db_connection()
    pending = conn.execute("SELECT * FROM candidates WHERE status = 'pending'").fetchall()
    approved = conn.execute("SELECT * FROM candidates WHERE status = 'approved'").fetchall()
    rejected = conn.execute("SELECT * FROM candidates WHERE status = 'rejected'").fetchall()
    conn.close()
    return render_template("admin_dashboard.html", pending=pending, approved=approved, rejected=rejected)

@app.route('/admin/approve/<int:candidate_id>')
def approve_candidate(candidate_id):
    conn = get_db_connection()
    conn.execute("UPDATE candidates SET status = 'approved' WHERE id = ?", (candidate_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/reject/<int:candidate_id>')
def reject_candidate(candidate_id):
    conn = get_db_connection()
    conn.execute("UPDATE candidates SET status = 'rejected' WHERE id = ?", (candidate_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/vote', methods=['GET', 'POST'])
def vote():
    if get_current_phase() != "VOTING_OPEN":
        return redirect(url_for('home'))

    conn = get_db_connection()
    if request.method == 'POST':
        candidate_id = request.form.get('candidate')
        voter_roll = request.form.get('voter_roll') # From the new input field

        # Check for double voting
        voted_already = conn.execute('SELECT 1 FROM voters WHERE roll_number = ?', (voter_roll,)).fetchone()
        if voted_already:
            conn.close()
            return "<h1>Access Denied</h1><p>This Roll Number has already cast a vote.</p>"

        if candidate_id and voter_roll:
            conn.execute("UPDATE candidates SET vote_count = vote_count + 1 WHERE id = ?", (candidate_id,))
            conn.execute("INSERT INTO voters (roll_number) VALUES (?)", (voter_roll,))
            conn.commit()
            conn.close()
            return render_template("success.html", message="Your vote has been recorded!")

    approved = conn.execute("SELECT * FROM candidates WHERE status = 'approved'").fetchall()
    conn.close()
    return render_template("vote.html", candidates=approved)

@app.route('/live_results')
def results():
    # Only block results if NOT in results phase
    if get_current_phase() != "RESULTS_PHASE":
        return "Results are not yet available.", 403

    conn = get_db_connection()
    results_data = conn.execute("SELECT name, vote_count, position FROM candidates WHERE status = 'approved' ORDER BY vote_count DESC").fetchall()
    conn.close()
    return render_template("results.html", results=results_data)
"""def get_current_phase():
    # FOR TESTING: Change this to return whatever phase you want to see
    # return "REGISTRATION_OPEN"
    # return "VOTING_OPEN"
    return "RESULTS_PHASE" """
if __name__ == '__main__':
    app.run(debug=True)