
# 🕋 **Talangraga Umroh Backend**

[![Python](https://img.shields.io/badge/Python-3.14-blue.svg?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Framework-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?logo=postgresql)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Progress-Stage_4-success.svg)]()

Backend service for **Talangraga Umroh**, built with **FastAPI + PostgreSQL + Alembic**.  
This backend manages users, periodes, payments, and Umroh savings transactions —  
designed to power the **Talangraga Umroh Mobile App** (Compose Multiplatform).

---

## 🚀 **Progress Checklist**

| Step | Description | Status |
|------|--------------|--------|
| ✅ 1 | Python & Virtual Env Setup | Completed |
| ✅ 2 | FastAPI Base Project Scaffold (routes, config, CORS) | Completed |
| ✅ 3A | Database & Auth Setup (SQLAlchemy + JWT Auth) | Completed |
| ✅ 3B | Alembic Migration Setup + First Migration | Completed |
| ✅ 4 | Core Tables: `User`, `Periode`, `Payment`, `Transaction` | Completed |
| ⏭️ 5 | Protected `/users/me` Route (JWT Token Auth) | Next |
| 🚧 6 | CRUD APIs for Periode, Payment, Transaction | Upcoming |
| 🚧 7 | Dockerize FastAPI + Environment Config | Upcoming |
| 🚧 8 | Deploy to Railway/VPS or Docker Compose Stack | Upcoming |

---

## 🧩 **1️⃣ Project Setup**

```bash
# Clone the repo
git clone https://github.com/yourusername/talangraga-umroh-fastapi.git
cd talangraga-umroh-fastapi

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install fastapi "uvicorn[standard]" pydantic-settings python-dotenv sqlalchemy alembic psycopg2-binary python-jose[cryptography] passlib[bcrypt]
```

🗂 Folder Structure
app/
├── main.py
├── __init__.py
│
├── api/
│   ├── __init__.py
│   └── routes/
│       ├── __init__.py
│       ├── auth.py
│       └── health.py
│
├── core/
│   ├── __init__.py
│   ├── config.py
│   └── security.py
│
├── db/
│   ├── __init__.py
│   ├── base.py
│   ├── session.py
│   └── models/
│       ├── __init__.py
│       ├── user.py
│       ├── periode.py
│       ├── payment.py
│       └── transaction.py
│
└── schemas/
    ├── __init__.py
    ├── user.py
    ├── periode.py
    ├── payment.py
    └── transaction.py

---

## 🧱 2️⃣ Database Schema Overview
| Table          | Description                                                         |
| -------------- | ------------------------------------------------------------------- |
| `users`        | Stores user info (admin/member, profile, contact)                   |
| `periodes`     | Tracks monthly savings periods                                      |
| `payments`     | Lists payment methods (Bank, E-Wallet, etc.)                        |
| `transactions` | Links users, periodes, and payments — stores all Umroh savings logs |
Each model is version-controlled with Alembic migrations and validated using Pydantic schemas.

### Tech Stack
| Layer         | Tool                       |
| ------------- | -------------------------- |
| Framework     | FastAPI                    |
| Language      | Python 3.14                |
| Database      | PostgreSQL 16              |
| ORM           | SQLAlchemy 2.x             |
| Migration     | Alembic                    |
| Auth          | JWT (JSON Web Token)       |
| Password Hash | passlib[bcrypt]            |
| Config        | pydantic-settings + dotenv |
| Dev Server    | Uvicorn                    |
| Testing       | Pytest (planned)           |


## ⏭️ Next Steps
| Step            | Description                                                     |
| --------------- | --------------------------------------------------------------- |
| 🔐 **Step 5:**  | Add protected `/api/users/me` endpoint (JWT verification)       |
| 📅 **Step 6:**  | Implement CRUD APIs for `Periode`, `Payment`, and `Transaction` |
| 🐳 **Step 7:**  | Dockerize backend (FastAPI + Alembic + PostgreSQL stack)        |
| ☁️ **Step 8:**  | Deploy to Railway / Render / VPS                                |
| 🧪 **Step 9:**  | Add unit tests using Pytest + SQLite test DB                    |
| 📘 **Step 10:** | Generate API Docs (Swagger/OpenAPI auto)                        |


✨ Author

Iqbal Fauzi
Android Engineer @ Bobobox
Building Talangraga Umroh — Kotlin Multiplatform app + FastAPI backend.

📦 GitHub: @iqbalwork
💼 LinkedIn: linkedin.com/in/ifauzii
