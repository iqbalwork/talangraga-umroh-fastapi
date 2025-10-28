# 🕋 **Talangraga Umroh Backend**

[![Python](https://img.shields.io/badge/Python-3.14-blue.svg?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Framework-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?logo=postgresql)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Progress-Stage_3B-success.svg)]()

Backend service for **Talangraga Umroh**, built with **FastAPI + PostgreSQL + Alembic**.  
This backend manages users, authentication, and Umroh savings transactions.  
Designed to power the **Talangraga Umroh Mobile App** (Compose Multiplatform).

---

## 🚀 **Progress Checklist**

| Step | Description | Status |
|------|--------------|--------|
| ✅ 1 | Python & Virtual Env Setup | Completed |
| ✅ 2 | FastAPI Base Project Scaffold (routes, config, CORS) | Completed |
| ✅ 3A | Database & Auth Setup (SQLAlchemy + JWT Auth) | Completed |
| ✅ 3B | Alembic Migration Setup + First Migration | Completed |
| ⏭️ 4 | Protected `/users/me` Route (JWT Token Auth) | Next |
| 🚧 5 | Dockerize FastAPI + Environment Config | Upcoming |
| 🚧 6 | Deploy to Railway/VPS or Docker Compose Stack | Upcoming |

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
│       └── user.py
│
└── schemas/
    ├── __init__.py
    └── user.py

Tech Stack
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

Next Step
| Step           | Description                                                      |
| -------------- | ---------------------------------------------------------------- |
| 🔐 **Step 4:** | Add protected `/api/users/me` endpoint (JWT token verification)  |
| 🐳 **Step 5:** | Dockerize backend (FastAPI + Alembic + PostgreSQL unified stack) |
| ☁️ **Step 6:** | Deploy to Railway, Render, or VPS                                |
| 🧰 **Step 7:** | Add unit tests using Pytest + SQLite test DB                     |

✨ Author

Iqbal Fauzi
Android Engineer @ Bobobox
Building Talangraga Umroh — Kotlin Multiplatform app + FastAPI backend.

📦 GitHub: @iqbalwork
💼 LinkedIn: linkedin.com/in/ifauzii