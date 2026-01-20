from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import random
import string
from datetime import datetime
import matplotlib
matplotlib.use('Agg')  # For non-GUI backend
import matplotlib.pyplot as plt
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

DB_NAME = "database.db"

# ----------------- Initialize Database -----------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Students table
    c.execute('''CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phone TEXT UNIQUE,
                    voted INTEGER DEFAULT 0,
                    token TEXT
                )''')

    # Candidates table
    c.execute('''CREATE TABLE IF NOT EXISTS candidates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    roll TEXT,
                    phone TEXT,
                    manifesto TEXT,
                    status TEXT DEFAULT 'pending',
                    votes INTEGER DEFAULT 0
                )''')

    # Votes ledger
    c.execute('''CREATE TABLE IF NOT EXISTS votes_ledger (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    voter_phone TEXT,
                    candidate_id INTEGER,
                    vote_hash TEXT,
                    timestamp TEXT
                )''')

    conn.commit()
    conn.close()

# Call init_db on startup
init_db()

# ----------------- Routes -----------------

# Home / Login
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        phone = request.form["phone"].strip()

        # Simple check: 10-digit number
        if not phone.isdigit() or len(phone) != 10:
            flash("Enter a valid 10-digit phone number!")
            return redirect(url_for("login"))

        # Token generation
        token = ''.join(random.choices(string.digits, k=6))
        session['token'] = token
        session['phone'] = phone

        # Save student in DB if not exist
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO students (phone, token) VALUES (?, ?)", (phone, token))
        c.execute("UPDATE students SET token=? WHERE phone=?", (token, phone))
        conn.commit()
        conn.close()

        # For demo: show token in flash (simulate SMS)
        flash(f"Your token is {token} (for demo, normally sent via SMS)")

        return redirect(url_for("token_verify"))

    return render_template("login.html")


# Token verification
@app.route("/token_verify", methods=["GET", "POST"])
def token_verify():
    if request.method == "POST":
        token_input = request.form["token"].strip()
        if token_input == session.get("token"):
            flash("Token verified! You can now vote.")
            return redirect(url_for("vote"))
        else:
            flash("Invalid token! Try again.")
            return redirect(url_for("token_verify"))

    return render_template("token_verify.html")


# Candidate Registration
@app.route("/register_candidate", methods=["GET", "POST"])
def register_candidate():
    if request.method == "POST":
        name = request.form["name"].strip()
        roll = request.form["roll"].strip()
        phone = request.form["phone"].strip()
        manifesto = request.form["manifesto"].strip()

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO candidates (name, roll, phone, manifesto) VALUES (?, ?, ?, ?)",
                  (name, roll, phone, manifesto))
        conn.commit()
        conn.close()

        flash("Candidate registration submitted! Waiting for admin approval.")
        return redirect(url_for("register_candidate"))

    return render_template("register_candidate.html")


# Voting Page
@app.route("/vote", methods=["GET", "POST"])
def vote():
    phone = session.get("phone")
    if not phone:
        flash("Login first!")
        return redirect(url_for("login"))

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Check if student already voted
    c.execute("SELECT voted FROM students WHERE phone=?", (phone,))
    voted_status = c.fetchone()
    if voted_status and voted_status[0] == 1:
        flash("You have already voted!")
        conn.close()
        return redirect(url_for("dashboard"))

    # Get approved candidates
    c.execute("SELECT id, name, manifesto FROM candidates WHERE status='approved'")
    candidates = c.fetchall()

    if request.method == "POST":
        candidate_id = request.form.get("candidate")
        if not candidate_id:
            flash("Select a candidate!")
            return redirect(url_for("vote"))

        # Update candidate vote
        c.execute("UPDATE candidates SET votes = votes + 1 WHERE id=?", (candidate_id,))
        # Update student voted status
        c.execute("UPDATE students SET voted=1 WHERE phone=?", (phone,))
        # Insert into ledger
        vote_hash = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        c.execute("INSERT INTO votes_ledger (voter_phone, candidate_id, vote_hash, timestamp) VALUES (?, ?, ?, ?)",
                  (phone, candidate_id, vote_hash, str(datetime.now())))

        conn.commit()
        conn.close()
        flash("Vote submitted successfully!")
        return redirect(url_for("confirmation"))

    conn.close()
    return render_template("vote.html", candidates=candidates)


# Confirmation Page
@app.route("/confirmation")
def confirmation():
    return render_template("confirmation.html")


# Admin Panel
@app.route("/admin", methods=["GET", "POST"])
def admin():
    password = "admin123"  # Simple admin password for demo
    if request.method == "POST":
        admin_pass = request.form["password"]
        if admin_pass != password:
            flash("Incorrect password!")
            return redirect(url_for("admin"))
        else:
            # Redirect to admin dashboard
            return redirect(url_for("admin_dashboard"))

    return render_template("admin.html")


# Admin Dashboard
@app.route("/admin_dashboard", methods=["GET", "POST"])
def admin_dashboard():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    if request.method == "POST":
        candidate_id = request.form.get("candidate_id")
        action = request.form.get("action")  # approve or reject

        if candidate_id and action:
            if action == "approve":
                c.execute("UPDATE candidates SET status='approved' WHERE id=?", (candidate_id,))
            elif action == "reject":
                c.execute("UPDATE candidates SET status='rejected' WHERE id=?", (candidate_id,))
            conn.commit()

    # Show pending candidates
    c.execute("SELECT id, name, roll, manifesto, status FROM candidates WHERE status='pending'")
    pending_candidates = c.fetchall()
    conn.close()

    return render_template("admin_dashboard.html", pending_candidates=pending_candidates)


# Dashboard (Voting stats)
@app.route("/dashboard")
def dashboard():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Total students
    c.execute("SELECT COUNT(*) FROM students")
    total_students = c.fetchone()[0]

    # Total voted
    c.execute("SELECT COUNT(*) FROM students WHERE voted=1")
    total_voted = c.fetchone()[0]

    # Participation rate
    participation = round((total_voted / total_students) * 100, 2) if total_students > 0 else 0

    # Candidate votes
    c.execute("SELECT name, votes FROM candidates WHERE status='approved'")
    candidates = c.fetchall()
    conn.close()

    # Generate chart
    if candidates:
        names = [x[0] for x in candidates]
        votes = [x[1] for x in candidates]
        plt.figure(figsize=(6,4))
        plt.bar(names, votes, color='skyblue')
        plt.xlabel("Candidates")
        plt.ylabel("Votes")
        plt.title("Election Results")
        plt.tight_layout()
        if not os.path.exists("static"):
            os.makedirs("static")
        chart_path = "static/results.png"
        plt.savefig(chart_path)
        plt.close()
    else:
        chart_path = None

    return render_template("dashboard.html",
                           total_students=total_students,
                           total_voted=total_voted,
                           participation=participation,
                           candidates=candidates,
                           chart_path=chart_path)


# Run Flask App
if __name__ == "__main__":
    app.run(debug=True)
