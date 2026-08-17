# 🗳️ ElectraN8 — Smart College Election Platform

> **A phase-controlled digital voting platform designed for transparent and organized college club elections.**

🌐 **Live Application:** https://charitha1121.pythonanywhere.com/login

---

## 📌 Overview

**ElectraN8** is a web-based election management platform designed specifically for **college club elections**.

Instead of treating an election as simply:

```text
Login → Vote → Result
```

ElectraN8 models the complete election lifecycle:

```text
Candidate Registration
        ↓
Admin Verification
        ↓
Candidate Approval / Rejection
        ↓
Election Countdown
        ↓
Time-Bound Voting
        ↓
Automatic Voting Closure
        ↓
Election Results
```

This makes the system more than a basic e-voting application — it functions as a **college election management platform**.

---

## 🎯 Problem Statement

Traditional college club elections can involve:

* Manual candidate registration
* Paper-based voting
* Manual vote counting
* Unstructured candidate verification
* Duplicate voting risks
* Difficulty controlling election timings
* Limited election transparency

ElectraN8 provides a centralized digital workflow for managing these stages.

---

## 💡 Core Concept

ElectraN8 divides an election into controlled phases.

### 🟡 Phase 1 — Candidate Registration

The administrator opens candidate registration for a predefined period.

Interested students can submit:

* Student name
* Student details
* Department
* Phone number
* Candidacy information

A phone number can only be used for one candidature.

---

### 🔵 Phase 2 — Candidate Verification

After registration closes, the administrator reviews all submitted applications.

Each candidate can be:

**✅ Approved**

or

**❌ Rejected**

Only approved candidates are eligible to participate in the election.

---

### 🟣 Phase 3 — Election Countdown

Once candidate registration ends, the platform switches to the election preparation phase.

The system displays a countdown until voting begins.

Students can see:

* Election date
* Voting start time
* Countdown
* Election status

---

### 🟢 Phase 4 — Time-Bound Voting

Voting becomes available only during the configured election window.

The system prevents voting:

* Before the election starts
* After the election ends
* More than once by the same voter

Only approved candidates appear on the ballot.

---

### 🔴 Phase 5 — Results

After voting closes, election results can be displayed.

The dashboard can provide:

* Total voters
* Votes cast
* Participation percentage
* Candidate vote counts
* Election outcome

---

# ✨ Key Features

| Feature                   | Description                                      |
| ------------------------- | ------------------------------------------------ |
| 🎓 College Election       | Designed specifically for student/club elections |
| 📝 Candidate Registration | Students can submit their candidature            |
| 📱 Unique Phone Number    | Prevents multiple candidature registrations      |
| 🔐 Admin Verification     | Admin reviews every candidate                    |
| ✅ Approval System         | Only approved candidates enter the ballot        |
| ❌ Rejection System        | Rejected candidates remain excluded              |
| ⏰ Election Scheduling     | Controls registration and voting windows         |
| ⏳ Countdown               | Displays time remaining before voting            |
| 🗳️ Controlled Ballot     | Displays only eligible candidates                |
| 🚫 Duplicate Prevention   | Prevents multiple votes                          |
| 🔒 Automatic Closure      | Voting closes after the configured deadline      |
| 📊 Results Dashboard      | Displays election statistics                     |
| 📈 Participation Tracking | Calculates voter participation                   |

---

# 🏗️ Election Architecture

```text
                    ┌──────────────────┐
                    │     STUDENT      │
                    └────────┬─────────┘
                             │
                             ▼
                  ┌────────────────────┐
                  │ Candidate or Voter │
                  └─────────┬──────────┘
                            │
             ┌──────────────┴──────────────┐
             │                             │
             ▼                             ▼
    Candidate Registration          Voter Authentication
             │                             │
             ▼                             │
      Pending Candidate                    │
             │                             │
             ▼                             │
      Admin Verification                  │
          /        \                       │
         /          \                      │
    APPROVED      REJECTED                 │
       │              │                    │
       ▼              ▼                    │
Official Ballot    Excluded                │
       │                                   │
       └──────────────┬────────────────────┘
                      ▼
                Voting Window
                      │
                      ▼
                Vote Submission
                      │
                      ▼
              Duplicate Vote Check
                      │
                      ▼
                 Vote Storage
                      │
                      ▼
                Voting Closure
                      │
                      ▼
                  Results
```

---

# 🛠️ Technology Stack

### Backend

* Python
* Flask
* SQLite

### Frontend

* HTML5
* CSS3
* JavaScript
* Jinja2

### Deployment

* PythonAnywhere

### Development

* Git
* GitHub
* VS Code
* Python Virtual Environment

---

# 📂 Project Structure

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

# ⚙️ Local Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/ElectraN8.git
cd ElectraN8
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# ▶️ Run Locally

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

---

# 🗄️ Database

ElectraN8 uses **SQLite**, so no separate MySQL installation is required for the academic demonstration.

The database manages:

* Voters
* Candidates
* Candidate status
* Vote counts
* Voting status

---

# 🌐 Live Deployment

ElectraN8 is deployed using **PythonAnywhere**.

### 🔗 Live Application

**https://charitha1121.pythonanywhere.com/login**

The deployed application provides access to the ElectraN8 election platform.

---

# 🚀 Deployment Architecture

```text
                    GitHub
                       │
                       ▼
                Python Application
                       │
                       ▼
                  Flask Backend
                       │
                       ▼
                 SQLite Database
                       │
                       ▼
              PythonAnywhere Server
                       │
                       ▼
                ElectraN8 Portal
```

---

# 🧪 Demonstration Workflow

For a college demonstration, the election can be conducted as follows:

### Step 1 — Open Registration

Admin enables candidate registration.

### Step 2 — Candidate Submission

Interested students submit their candidature.

### Step 3 — Registration Closes

The registration deadline automatically closes the registration portal.

### Step 4 — Admin Verification

Admin reviews candidate applications.

### Step 5 — Candidate Approval

Approved candidates are added to the official election list.

Rejected candidates are excluded.

### Step 6 — Election Countdown

The system displays the countdown until voting begins.

### Step 7 — Voting Opens

Eligible students can cast their votes.

### Step 8 — Voting Closes

The system automatically prevents votes after the configured deadline.

### Step 9 — Results

The election results are displayed.

---

# 🔐 Security & Integrity

ElectraN8 implements several controls:

### Candidate Uniqueness

A phone number cannot be reused for multiple candidate registrations.

### Admin Approval

Candidates do not automatically become election participants.

### Time-Based Restrictions

Registration and voting are controlled by server-side timestamps.

### Approved Candidate Filtering

Only candidates with an approved status are displayed on the ballot.

### Duplicate Vote Prevention

A voter who has already voted cannot submit another vote.

### Server-Side Validation

Election restrictions are enforced by the Flask backend instead of relying only on browser-side JavaScript.

---

# 📊 Election Analytics

The platform can calculate:

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

Participation rate:

```text
Participation Rate =
(Total Votes Cast / Total Eligible Voters) × 100
```

---

# 🧠 What Makes ElectraN8 Different?

Many basic student e-voting projects implement only:

```text
Login → Vote → Result
```

ElectraN8 focuses on **election lifecycle management**:

```text
Registration
      ↓
Verification
      ↓
Approval
      ↓
Election Preparation
      ↓
Countdown
      ↓
Voting
      ↓
Automatic Closure
      ↓
Results
```

The key differentiator is the **phase-based election model**.

The system does not expose all election functionality at once. Features become available according to the current election phase.

---

# 🔮 Future Enhancements

Potential production-level improvements include:

* 🔐 OTP authentication
* 📱 SMS verification
* 🔑 Secure admin authentication
* 🔏 Cryptographically signed ballots
* 📜 Tamper-evident audit logs
* 📊 Real-time analytics
* 📄 Automated election reports
* 🏆 Winner certificate generation
* 📧 Candidate notifications
* 👥 Role-based access control
* 🌐 Multiple simultaneous elections
* ☁️ PostgreSQL production database
* 📱 Progressive Web App

---

# 🎓 Academic Purpose

ElectraN8 is developed primarily as a **college academic and demonstration project**.

It demonstrates concepts including:

* Web application development
* Database management
* Authentication
* Authorization
* CRUD operations
* Election workflow design
* Time-based access control
* Data validation
* Dashboard analytics
* Deployment

It is **not intended to replace certified election infrastructure or public-election systems** without substantial additional security engineering and independent auditing.

---

# 👩‍💻 Project

## ElectraN8

### Smart College Election Platform

> **Register. Verify. Vote. Decide.**

**Live:**
https://charitha1121.pythonanywhere.com/login

---

## ⭐ Project Highlights

```text
✔ Phase-Based Election Management
✔ Candidate Registration
✔ Admin Approval / Rejection
✔ Time-Bound Voting
✔ Countdown-Based Election Preparation
✔ Duplicate Vote Prevention
✔ Automated Voting Closure
✔ Election Analytics
✔ SQLite Database
✔ Flask Backend
✔ PythonAnywhere Deployment
```

---

## 📜 License

This project is developed for educational and academic purposes.
