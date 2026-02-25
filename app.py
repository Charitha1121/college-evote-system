from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime, timedelta
import sqlite3
import secrets
import os

app = Flask(__name__)
app.secret_key = secrets.token_hex(24)
app.permanent_session_lifetime = timedelta(minutes=30)

def get_db_connection():
    conn = sqlite3.connect('voters.db', timeout=10)
    conn.row_factory = sqlite3.Row  
    return conn

def calculate_year(roll):
    try:
        prefix = str(roll)[:2]
        if prefix == '23': return 3
        if prefix == '24': return 2
        return 1
    except: return 1

# --- DATABASE INITIALIZATION ---
def init_db():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS clubs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE, admin_user TEXT UNIQUE, admin_pass TEXT, dept TEXT,
        reg_start TEXT, reg_end TEXT, vote_start TEXT, vote_end TEXT
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS positions_config (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        club_name TEXT, year INTEGER, position_name TEXT
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS candidates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, roll TEXT, phone TEXT, position TEXT, club TEXT,
        status TEXT DEFAULT 'pending', vote_count INTEGER DEFAULT 0
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS votes_cast (
        voter_roll TEXT, club TEXT
    )''')
    conn.commit()
    conn.close()

init_db()

# -------------------------------
# STUDENT ROUTES
# -------------------------------

@app.route('/')
def home():
    if 'verified_voter' not in session:
        return redirect(url_for('login'))
    
    now = datetime.now()
    roll = session['verified_voter']
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM authorized_voters WHERE roll = ?', (roll,)).fetchone()
    
    if not user:
        session.clear()
        return redirect(url_for('login'))

    session['branch'] = user['branch']
    club = conn.execute('SELECT * FROM clubs WHERE dept IN (?, "All") LIMIT 1', (user['branch'],)).fetchone()
    
    phase = "SYSTEM_LIVE"
    ticker = False
    
    if club and club['reg_start'] and club['reg_end']:
        try:
            reg_s = datetime.fromisoformat(club['reg_start'])
            reg_e = datetime.fromisoformat(club['reg_end'])
            vote_s = datetime.fromisoformat(club['vote_start'])
            vote_e = datetime.fromisoformat(club['vote_end'])

            if now < reg_s: phase = "UPCOMING"
            elif reg_s <= now <= reg_e: phase = "REGISTRATION"
            elif now < vote_s: phase = "PRE_VOTING"
            elif vote_s <= now <= vote_e: phase = "VOTING"
            else:
                phase = "RESULTS"
                ticker = True
        except: phase = "SETUP"

    reg_count = conn.execute('SELECT COUNT(*) FROM clubs WHERE dept IN (?, "All")', (user['branch'],)).fetchone()[0]
    vote_count = conn.execute('SELECT COUNT(DISTINCT club) FROM candidates WHERE status="approved"').fetchone()[0]
    conn.close()
    
    return render_template("home.html", user=user, reg_count=reg_count, vote_count=vote_count, phase=phase, ticker=ticker, year=calculate_year(roll))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        roll = request.form.get('roll', '').strip()
        phone = request.form.get('phone', '').strip()
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM authorized_voters WHERE roll = ? AND phone = ?', (roll, phone)).fetchone()
        conn.close()
        if user:
            session['pending_roll'] = roll 
            token = str(secrets.randbelow(899999) + 100000)
            session['active_token'] = token 
            print(f">>> DEBUG TOKEN FOR {roll}: {token}")
            return redirect(url_for('token_verify'))
        flash("Unauthorized Roll Number or Phone.", "danger")
    return render_template("login.html")

@app.route('/token_verify', methods=['GET', 'POST'])
def token_verify():
    if 'pending_roll' not in session: return redirect(url_for('login'))
    if request.method == 'POST':
        if request.form.get('token') == session.get('active_token'):
            session['verified_voter'] = session['pending_roll']
            session.pop('active_token', None)
            session.pop('pending_roll', None)
            return redirect(url_for('home'))
        flash("Invalid Token", "danger")
    return render_template("token_verify.html")

@app.route('/voting_booth')
def voting_booth():
    if 'verified_voter' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    roll = session['verified_voter']
    
    voted_rows = conn.execute('SELECT club FROM votes_cast WHERE voter_roll = ?', (roll,)).fetchall()
    voted_list = [v['club'] for v in voted_rows]
    
    all_active_clubs = conn.execute('SELECT DISTINCT club FROM candidates WHERE status="approved"').fetchall()
    conn.close()
    return render_template("voting_list.html", clubs=all_active_clubs, voted_list=voted_list)

@app.route('/vote/<club_name>', methods=['GET', 'POST'])
def vote_club(club_name):
    if 'verified_voter' not in session: return redirect(url_for('login'))
    roll = session['verified_voter']
    conn = get_db_connection()
    
    already = conn.execute('SELECT * FROM votes_cast WHERE voter_roll=? AND club=?', (roll, club_name)).fetchone()
    if already:
        conn.close()
        flash(f"You have already cast your vote for {club_name}!", "danger")
        return redirect(url_for('voting_booth'))

    if request.method == 'POST':
        candidate_id = request.form.get('candidate_id')
        if candidate_id:
            conn.execute('UPDATE candidates SET vote_count = vote_count + 1 WHERE id = ?', (candidate_id,))
            conn.execute('INSERT INTO votes_cast (voter_roll, club) VALUES (?, ?)', (roll, club_name))
            conn.commit()
            conn.close()
            flash(f"Vote cast successfully for {club_name}!", "success")
            return redirect(url_for('voting_booth'))

    candidates = conn.execute('SELECT * FROM candidates WHERE club = ? AND status = "approved"', (club_name,)).fetchall()
    conn.close()
    return render_template("vote_page.html", club_name=club_name, candidates=candidates)

@app.route('/results')
def results():
    conn = get_db_connection()
    # Explicitly fetching as 'results' to match your HTML template
    results_query = conn.execute('''SELECT * FROM candidates 
                                   WHERE status="approved" 
                                   ORDER BY club ASC, vote_count DESC''').fetchall()
    conn.close()
    return render_template("results.html", results=results_query)

# -------------------------------
# ADMIN ROUTES
# -------------------------------

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        user = request.form.get('username')
        pw = request.form.get('password')
        conn = get_db_connection()
        admin = conn.execute('SELECT * FROM clubs WHERE admin_user = ? AND admin_pass = ?', (user, pw)).fetchone()
        conn.close()
        if admin:
            session.clear() # Clears any student flash messages
            session['admin_club'] = admin['name']
            return redirect(url_for('admin_dashboard'))
        flash("Invalid Admin Credentials", "danger")
    return render_template("admin_login.html")

# ADDED SECOND ROUTE DECORATOR TO PREVENT 404
@app.route('/admin/dashboard')
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin_club' not in session: return redirect(url_for('admin_login'))
    club_name = session['admin_club']
    conn = get_db_connection()
    club_info = conn.execute('SELECT * FROM clubs WHERE name = ?', (club_name,)).fetchone()
    pending = conn.execute('SELECT * FROM candidates WHERE club = ? AND status = "pending"', (club_name,)).fetchall()
    nominees = conn.execute('SELECT * FROM candidates WHERE club = ? AND status = "approved"', (club_name,)).fetchall()
    conn.close()
    return render_template("admin_dashboard.html", club=club_info, pending=pending, nominees=nominees)

@app.route('/admin/update_settings', methods=['POST'])
def update_settings():
    if 'admin_club' not in session: return redirect(url_for('admin_login'))
    club_name = session['admin_club']
    conn = get_db_connection()
    if 'reg_s' in request.form and request.form['reg_s']:
        conn.execute('''UPDATE clubs SET reg_start=?, reg_end=?, vote_start=?, vote_end=? WHERE name=?''', 
                     (request.form['reg_s'], request.form['reg_e'], request.form['vote_s'], request.form['vote_e'], club_name))
    if request.form.get('pos_name'):
        conn.execute('INSERT INTO positions_config (club_name, year, position_name) VALUES (?, ?, ?)',
                     (club_name, request.form['year_lvl'], request.form['pos_name']))
    conn.commit()
    conn.close()
    flash("Updated successfully!", "success")
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/decide/<int:cand_id>/<action>')
def decide_candidate(cand_id, action):
    if 'admin_club' not in session: return redirect(url_for('admin_login'))
    conn = get_db_connection()
    if action == 'approve':
        conn.execute('UPDATE candidates SET status = "approved" WHERE id = ?', (cand_id,))
        flash("Candidate Approved!", "success")
    else:
        conn.execute('DELETE FROM candidates WHERE id = ?', (cand_id,))
        flash("Candidate Rejected.", "info")
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)