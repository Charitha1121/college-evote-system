# 🗳️ ElectraN8 — Smart College Election Platform

> **A secure, phase-controlled digital voting platform designed for transparent and organized college club elections.**

**Live Demo:** https://electran8.vercel.app/

---

## 📌 Overview

**ElectraN8** is a web-based election management platform developed specifically for **college club elections**.

Unlike conventional e-voting projects that simply provide a login page and voting form, ElectraN8 models an election as a controlled lifecycle:

**Candidate Registration → Admin Verification → Candidate Approval → Election Countdown → Time-Bound Voting → Results**

The platform gives administrators complete control over the election process while ensuring that only eligible and approved candidates participate in the election.

---

## 🎯 Problem Statement

Traditional college club elections often rely on:

* Manual candidate registration
* Paper-based voting
* Unstructured candidate verification
* Manual vote counting
* Limited transparency
* Difficulty controlling election timings
* Risk of duplicate voting

ElectraN8 addresses these issues by providing a centralized digital election workflow.

---

## 💡 Our Solution

ElectraN8 introduces a **phase-based election architecture**.

### 🟡 Phase 1 — Candidate Registration

The administrator opens candidate registration for a predefined period.

Interested students can:

* Register their candidacy
* Submit their student details
* Provide their registered phone number
* Submit their candidature for verification

Each phone number can be used for **only one candidate registration**.

---

### 🔵 Phase 2 — Candidate Verification

After registration, administrators review submitted candidates.

Each candidate can be:

* ✅ Approved
* ❌ Rejected

Only approved candidates are eligible to appear on the official ballot.

Rejected candidates are automatically excluded from the voting list.

---

### 🟣 Phase 3 — Election Countdown

Once candidate registration closes, the system transitions into the election preparation phase.

The platform displays:

* Election date
* Voting start time
* Countdown timer
* Election status
* Number of approved candidates

Candidates are not displayed to voters prematurely.

---

### 🟢 Phase 4 — Voting

Voting becomes available only during the configured election window.

The system ensures:

* Eligible voters can vote
* Only approved candidates appear
* A voter cannot vote multiple times
* Voting automatically closes when the election ends

---

### 🔴 Phase 5 — Election Results

After voting closes, election results can be displayed.

Administrators can monitor:

* Total eligible voters
* Total votes
* Participation percentage
* Candidate vote counts
* Election outcome

---

## ✨ Key Features

| Feature                   | Description                                                    |
| ------------------------- | -------------------------------------------------------------- |
| 🧑‍🎓 Student Eligibility | Restricts election participation to eligible college students  |
| 📱 Phone Verification     | Uses phone number as a unique registration identifier          |
| 📝 Candidate Registration | Students can submit candidature during the registration window |
| 🔐 Admin Verification     | Admin can approve or reject candidates                         |
| ⏰ Election Scheduling     | Registration and voting operate within predefined time windows |
| ⏳ Countdown               | Countdown to the upcoming election                             |
| 🗳️ Controlled Ballot     | Only approved candidates appear during voting                  |
| 🚫 Duplicate Prevention   | Prevents a voter from casting multiple votes                   |
| 📊 Results Dashboard      | Displays election statistics and results                       |
| 📈 Participation Tracking | Calculates voter participation                                 |
| 🎨 Responsive UI          | Designed for desktop and mobile users                          |
| 🔄 Election Lifecycle     | Registration → Verification → Voting → Results                 |

---

## 🏗️ System Architecture

```text
                    ┌─────────────────────┐
                    │      STUDENT        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Eligibility Check   │
                    └──────────┬──────────┘
                               │
              ┌────────────────┴────────────────┐
              │                                 │
              ▼                                 ▼
     Candidate Registration              Voter Authentication
              │                                 │
              ▼                                 │
     ┌──────────────────┐                      │
     │ Pending Candidate│                      │
     └────────┬─────────┘                      │
              │                                 │
              ▼                                 │
     ┌──────────────────┐                      │
     │ Admin Verification│                     │
     └───────┬─────┬────┘                      │
             │     │                           │
        APPROVE   REJECT                       │
             │                                 │
             ▼                                 │
     Approved Candidate                        │
             │                                 │
             └──────────────┐                  │
                            ▼                  ▼
                    ┌────────────────────────────┐
                    │       ELECTION BALLOT      │
                    └──────────────┬─────────────┘
                                   │
                                   ▼
                           Vote Submission
                                   │
                                   ▼
                           Duplicate Check
                                   │
                                   ▼
                              Vote Stored
                                   │
                                   ▼
                           Election Results
```

---

## 🛠️ Technology Stack

### Backend

* Python
* Flask
* SQLite

### Frontend

* HTML5
* CSS3
* JavaScript
* Jinja2 Templates

### Development Tools

* Git
* GitHub
* VS Code
* Python Virtual Environment

---

## 📂 Project Structure

```text
ElectraN8/
│
├── app.py
├── evote.db
├── requirements.txt
├── README.md
├── .gitignore
│
├── templates/
│   ├── home.html
│   ├── candidate_register.html
│   ├── admin_dashboard.html
│   ├── vote.html
│   ├── confirmation.html
│   └── results.html
│
└── static/
    ├── style.css
    └── results.png
```

---

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/ElectraN8.git
```

```bash
cd ElectraN8
```

### 2. Create a Virtual Environment

Windows:

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

If `requirements.txt` does not exist:

```bash
pip install flask
```

---

## ▶️ Run Locally

Start the Flask application:

```bash
python app.py
```

The application will normally be available at:

```text
http://127.0.0.1:5000
```

Open the URL in your browser.

---

## 🗄️ Database

ElectraN8 uses **SQLite**.

No separate MySQL or PostgreSQL installation is required for the college demonstration.

The database stores information such as:

* Student/voter records
* Candidate registrations
* Candidate approval status
* Vote counts
* Voting status

If you modify the database schema during development, recreate the development database or run the appropriate migration/update logic.

---

## 🗳️ Election Workflow

```text
                 ELECTION CREATED
                        │
                        ▼
             Candidate Registration
                        │
                        ▼
               Registration Closes
                        │
                        ▼
                Admin Verification
                   /          \
                  /            \
             APPROVED        REJECTED
                │                │
                ▼                ▼
        Official Candidate     Excluded
              List
                │
                ▼
           Election Countdown
                │
                ▼
          Voting Opens
                │
                ▼
        Students Cast Votes
                │
                ▼
          Voting Closes
                │
                ▼
          Results Released
```

---

## 🔐 Security & Integrity

ElectraN8 incorporates several mechanisms to improve election integrity:

### Candidate Uniqueness

A phone number can only be associated with one candidature during the registration process.

### Candidate Approval

Candidates are not automatically added to the ballot.

An administrator must explicitly approve them.

### Controlled Voting Window

Votes cannot be submitted before the election starts or after the election ends.

### Duplicate Vote Prevention

Once a voter has successfully voted, their voting status is updated to prevent another vote.

### Server-Side Validation

Election timing and eligibility are validated by the backend rather than relying solely on frontend JavaScript.

---

## 📊 Election Analytics

The dashboard can provide:

```text
Total Eligible Voters
        ↓
Total Votes Cast
        ↓
Participation Rate
        ↓
Candidate Vote Distribution
        ↓
Election Result
```

### Participation Rate

```text
Participation Rate =
(Total Votes Cast / Total Eligible Voters) × 100
```

---

## 🚀 Deployment

ElectraN8 can be deployed using a Python-compatible hosting platform.

Typical production setup:

```text
GitHub
   │
   ▼
Deployment Platform
   │
   ▼
Flask Application
   │
   ▼
ElectraN8
```

For production deployment, configure:

* `SECRET_KEY`
* Production database
* Environment variables
* Proper WSGI server
* HTTPS
* Admin authentication
* Persistent database storage

---

## 🌐 Live Application

### ElectraN8

🔗 **Live Demo:** https://electran8.vercel.app/

> If your final deployment URL is different, replace the URL above with the actual deployed application URL.

---

## 🧪 Demonstration Flow

For a college project demonstration:

### Step 1

Admin opens candidate registration.

### Step 2

Students submit their candidature.

### Step 3

Admin reviews applications.

### Step 4

Admin approves/rejects candidates.

### Step 5

Candidate registration closes automatically.

### Step 6

The system displays the election countdown.

### Step 7

Voting opens at the configured time.

### Step 8

Eligible students cast their votes.

### Step 9

Voting closes automatically at the configured end time.

### Step 10

Election results are displayed.

---

## 🧠 What Makes ElectraN8 Different?

Most student e-voting projects focus primarily on:

```text
Login → Vote → Result
```

ElectraN8 focuses on the **complete election lifecycle**:

```text
Registration
      ↓
Candidate Verification
      ↓
Admin Approval
      ↓
Election Scheduling
      ↓
Countdown
      ↓
Controlled Voting
      ↓
Duplicate Prevention
      ↓
Election Closure
      ↓
Results
```

This makes ElectraN8 closer to an **Election Management System** rather than simply a voting form.

---

## 🎓 Intended Use

ElectraN8 is designed as a **college demonstration and academic project** for:

* College club elections
* Student representative elections
* Department-level elections
* Student organization elections
* Academic demonstrations of election workflows

It should not be considered a production-grade public-election system without additional security auditing, authentication, cryptographic protections, infrastructure hardening, and independent verification.

---

## 🔮 Future Enhancements

Planned improvements include:

* 🔐 OTP-based authentication
* 📱 SMS-based voter verification
* 🔑 Secure admin authentication
* 🔏 Cryptographic vote integrity
* 📜 Tamper-evident audit logs
* 📊 Real-time election analytics
* 📄 Automated election report generation
* 🏆 Winner certificate generation
* 📧 Candidate approval notifications
* 🌐 Multi-election support
* 👥 Role-based access control
* ☁️ Production database support
* 📱 Progressive Web App support

---

## 👩‍💻 Project

**ElectraN8 — Smart College Election Platform**

Developed as a college-focused software engineering project with emphasis on:

> **Transparency • Controlled Elections • Candidate Verification • Time-Bound Voting • Digital Governance**

---

## 📜 License

This project is developed for educational and academic demonstration purposes.

You are free to study and modify the project for educational use.

---

## ⭐ Support

If you find ElectraN8 useful, consider giving the repository a ⭐ on GitHub.

**ElectraN8 — Vote Smart. Vote Fair.**
