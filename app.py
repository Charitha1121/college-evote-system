from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mail import Mail, Message 
from datetime import datetime, timedelta
import sqlite3
import secrets
import csv
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
# Define IST
IST = timezone(timedelta(hours=5, minutes=30))
now = datetime.now(IST)
app = Flask(__name__)
app.secret_key = secrets.token_hex(24)
app.permanent_session_lifetime = timedelta(minutes=30)

# --- MAIL CONFIGURATION ---
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'boddupallycharitha@gmail.com' 
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = 'boddupallycharitha@gmail.com'

mail = Mail(app)

# Path to your local CSV file
CSV_PATH = r'C:\Users\DELL\Desktop\evote\voters.csv'

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

# --- DATABASE INITIALIZATION & ROBUST CSV SYNC ---
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
        voter_roll TEXT, club TEXT, position TEXT
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS authorized_voters (
        roll TEXT PRIMARY KEY, name TEXT, phone TEXT, email TEXT, branch TEXT
    )''')

    if os.path.exists(CSV_PATH):
        try:
            with open(CSV_PATH, mode='r', encoding='utf-8-sig') as f:
                raw_reader = csv.DictReader(f)
                count = 0
                for row in raw_reader:
                    clean_row = {k.strip().lower(): v.strip() for k, v in row.items()}
                    conn.execute('''INSERT OR REPLACE INTO authorized_voters (roll, name, phone, email, branch) 
                                   VALUES (?, ?, ?, ?, ?)''', 
                                (clean_row.get('roll'), 
                                 clean_row.get('name'), 
                                 clean_row.get('phone'),
                                 clean_row.get('email'), 
                                 clean_row.get('branch')))
                    count += 1
            print(f">>> Successfully synced {count} records from {CSV_PATH}")
        except Exception as e:
            print(f">>> CSV Sync Error: {e}")
    else:
        print(f">>> Warning: CSV file not found at {CSV_PATH}")

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
    
    return render_template("home.html", user=user, reg_count=reg_count, vote_count=vote_count, phase=phase, ticker=ticker, year=calculate_year(roll), club=club)

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

@app.route('/registrations')
def registrations():
    if 'verified_voter' not in session: return redirect(url_for('login'))
    branch = session.get('branch', 'All')
    conn = get_db_connection()
    now = datetime.now().isoformat()
    my_clubs = conn.execute('''SELECT * FROM clubs WHERE dept IN (?, "All") 
                               AND reg_start <= ? AND reg_end >= ?''', (branch, now, now)).fetchall()
    conn.close()
    return render_template("reg_list.html", clubs=my_clubs)

@app.route('/apply/<club_name>', methods=['GET', 'POST'])
def apply(club_name):
    if 'verified_voter' not in session: return redirect(url_for('login'))
    roll = session['verified_voter']
    year = calculate_year(roll)
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM authorized_voters WHERE roll = ?', (roll,)).fetchone()
    allowed = conn.execute('SELECT position_name FROM positions_config WHERE club_name=? AND year=?', (club_name, year)).fetchall()
    positions = [row['position_name'] for row in allowed]

    if request.method == 'POST':
        pos = request.form.get('position')
        existing = conn.execute('SELECT id FROM candidates WHERE roll=? AND club=?', (roll, club_name)).fetchone()
        if not existing:
            conn.execute('INSERT INTO candidates (name, roll, phone, position, club) VALUES (?, ?, ?, ?, ?)',
                         (user['name'], roll, user['phone'], pos, club_name))
            conn.commit()
            flash(f"Applied successfully for {club_name}!", "success")
        else:
            flash(f"Already applied for {club_name}.", "warning")
        conn.close()
        return redirect(url_for('home'))
    
    conn.close()
    return render_template("apply_form.html", user=user, year=year, club=club_name, positions=positions)

@app.route('/voting_booth')
def voting_booth():
    if 'verified_voter' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    all_active_clubs = conn.execute('SELECT DISTINCT club FROM candidates WHERE status="approved"').fetchall()
    conn.close()
    return render_template("voting_list.html", clubs=all_active_clubs)

@app.route('/vote/<club_name>', methods=['GET', 'POST'])
def vote_club(club_name):
    if 'verified_voter' not in session: return redirect(url_for('login'))
    roll = session['verified_voter']
    conn = get_db_connection()

    if request.method == 'POST':
        # Get all selected candidate IDs (keys start with 'pos_')
        selected_cand_ids = [v for k, v in request.form.items() if k.startswith('pos_')]
        
        if not selected_cand_ids:
            flash("No votes were selected.", "warning")
            return redirect(url_for('vote_club', club_name=club_name))

        vote_summary = []
        # Process each selected candidate
        for c_id in selected_cand_ids:
            cand = conn.execute('SELECT name, position FROM candidates WHERE id = ?', (c_id,)).fetchone()
            
            # Record the vote in DB
            conn.execute('UPDATE candidates SET vote_count = vote_count + 1 WHERE id = ?', (c_id,))
            conn.execute('INSERT INTO votes_cast (voter_roll, club, position) VALUES (?, ?, ?)', 
                         (roll, club_name, cand['position']))
            
            vote_summary.append({
                'candidate': cand['name'],
                'position': cand['position']
            })

        conn.commit()
        
        # Store the whole batch in session for the multi-position report
        session['last_vote_batch'] = {
            'club': club_name,
            'votes': vote_summary,
            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        conn.close()
        return redirect(url_for('vote_report_prompt'))

    # Prepare data for display
    candidates = conn.execute('SELECT * FROM candidates WHERE club = ? AND status = "approved"', (club_name,)).fetchall()
    voted_rows = conn.execute('SELECT position FROM votes_cast WHERE voter_roll=? AND club=?', (roll, club_name)).fetchall()
    voted_positions = [v['position'] for v in voted_rows]
    
    conn.close()
    return render_template("vote_page.html", club_name=club_name, candidates=candidates, voted_positions=voted_positions)

# --- NEW REPORT ROUTES ---
@app.route('/vote_report_prompt')
def vote_report_prompt():
    # Updated to check for batch session data
    if 'last_vote_batch' not in session: return redirect(url_for('home'))
    return render_template("vote_report_prompt.html", batch=session['last_vote_batch'])

@app.route('/send_vote_report', methods=['POST'])
def send_vote_report():
    if 'verified_voter' not in session or 'last_vote_batch' not in session:
        return redirect(url_for('login'))
    
    roll = session['verified_voter']
    batch = session['last_vote_batch']
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM authorized_voters WHERE roll = ?', (roll,)).fetchone()
    conn.close()

    if user and user['email']:
        try:
            msg = Message(f"Voting Receipt: {batch['club']}", recipients=[user['email']])
            
            # Format multiple votes for the email body
            vote_list_text = ""
            for v in batch['votes']:
                vote_list_text += f"- {v['position']}: {v['candidate']}\n"

            msg.body = f"Hello {user['name']},\n\nThank you for voting in the {batch['club']} elections!\n\n" \
                       f"Your selections:\n{vote_list_text}\n" \
                       f"Date: {batch['time']}\n\n" \
                       f"Best regards,\nE-Voting System"
            mail.send(msg)
            flash("Complete report sent to your email successfully!", "success")
        except Exception as e:
            flash(f"Error sending email: {e}", "danger")
    else:
        flash("Email address not found.", "warning")
    
    session.pop('last_vote_batch', None) 
    return redirect(url_for('voting_booth'))

# -------------------------------
# ADMIN ROUTES & REMAINING
# -------------------------------

@app.route('/results')
def results():
    conn = get_db_connection()
    results_query = conn.execute('''SELECT * FROM candidates 
                                    WHERE status="approved" 
                                    ORDER BY club ASC, vote_count DESC''').fetchall()
    conn.close()
    return render_template("results.html", results=results_query)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        user = request.form.get('username')
        pw = request.form.get('password')
        conn = get_db_connection()
        admin = conn.execute('SELECT * FROM clubs WHERE admin_user = ? AND admin_pass = ?', (user, pw)).fetchone()
        conn.close()
        if admin:
            session.clear() 
            session['admin_club'] = admin['name']
            return redirect(url_for('admin_dashboard'))
        flash("Invalid Admin Credentials", "danger")
    return render_template("admin_login.html")

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
    app.run(debug=False)