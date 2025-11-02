# 🕋 **Talangraga Umroh Backend**

[![Python](https://img.shields.io/badge/Python-3.14-blue.svg?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Framework-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?logo=postgresql)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Progress-Stage_4B-success.svg)]()

Backend service for **Talangraga Umroh**, built with **FastAPI + PostgreSQL + Alembic**.  
This backend manages **user authentication**, **admin management**, and **Umroh savings transactions**,  
powering the **Talangraga Umroh Mobile App** (Kotlin Multiplatform + Compose Multiplatform).

---

## 🚀 **Progress Checklist**

| Step | Description | Status |
|------|--------------|--------|
| ✅ 1 | Python & Virtual Env Setup | Completed |
| ✅ 2 | FastAPI Base Project Scaffold (routes, config, CORS) | Completed |
| ✅ 3A | Database, SQLAlchemy ORM, JWT Auth (Access & Refresh) | Completed |
| ✅ 3B | Alembic Migration Setup + First Migration | Completed |
| ✅ 4A | Profile, Refresh Token Flow, Token Expiry Check | Completed |
| ✅ 4B | Logout Endpoint (invalidate refresh token) | Completed |
| 🚧 5 | Dockerize FastAPI + PostgreSQL + Alembic Stack | Upcoming |
| 🚧 6 | Deploy to Railway / Render / VPS | Upcoming |

---

## 🧩 **Project Setup**

```bash
# Clone the repo
git clone https://github.com/iqbalwork/talangraga-umroh-fastapi.git
cd talangraga-umroh-fastapi

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

---

### 🧱 **Project Structure**

```
app/
├── main.py                     # Entry point
│
├── api/
│   ├── __init__.py
│   └── routes/
│       ├── __init__.py
│       └── auth.py             # Auth endpoints (register, login, profile, refresh, logout, delete)
│
├── core/
│   ├── __init__.py
│   ├── config.py               # Environment config (dotenv / pydantic-settings)
│   └── security.py             # JWT, hashing, token utilities
│
├── db/
│   ├── __init__.py
│   ├── base.py
│   ├── session.py              # SQLAlchemy engine and get_db()
│   └── models/
│       ├── __init__.py
│       └── user.py             # User model definition
│
└── schemas/
    ├── __init__.py
    └── user.py                 # Request & response schemas
```

---

## 🧠 **Tech Stack**

| Layer | Tool |
|--------|------|
| **Framework** | FastAPI |
| **Language** | Python 3.14 |
| **Database** | PostgreSQL 16 |
| **ORM** | SQLAlchemy 2.x |
| **Migration** | Alembic |
| **Auth** | JWT (Access + Refresh) |
| **Password Hashing** | passlib[bcrypt] |
| **Config** | pydantic-settings + dotenv |
| **Dev Server** | Uvicorn |

---

## 🔐 **Authentication Features**

| Feature | Description |
|----------|--------------|
| 🔑 Register | Register new users with email, username, or phone |
| 🔒 Login | Login using email / username / phone number |
| 🔁 Refresh | Refresh access token using refresh token |
| 🚪 Logout | Invalidate refresh token (blacklist) |
| ⏰ Token Expiry | Access token auto-expires (30 min), refresh (7 days) |
| 👤 Profile | Authenticated `/auth/profile` endpoint |
| 🧩 Roles | `admin` and `member` user types |
| 🗑️ Delete | Admin-only delete user |
| 📱 KMP Integration | Ktor `Auth` + auto refresh + retry support |

---

## 📡 **API Endpoints Summary**

| Method | Endpoint | Description | Auth |
|--------|-----------|-------------|------|
| `POST` | `/auth/register` | Register new user | ❌ |
| `POST` | `/auth/login` | Login (email / username / phone) | ❌ |
| `GET` | `/auth/profile` | Get current user profile | ✅ Access Token |
| `POST` | `/auth/refresh` | Refresh access token | ✅ Refresh Token |
| `POST` | `/auth/logout` | Logout and invalidate refresh token | ✅ Refresh Token |
| `POST` | `/auth/forgot-password` | Simulated forgot password | ❌ |
| `DELETE` | `/auth/delete/{user_id}` | Delete user (admin only) | ✅ Access Token |

---

## 🔁 **Access, Refresh & Logout Flow**

### 1️⃣ Login → Receive Tokens
```json
{
  "access_token": "short-lived JWT",
  "refresh_token": "long-lived JWT",
  "user": {...}
}
```

### 2️⃣ Use Access Token
Every request sends:
```
Authorization: Bearer <access_token>
```

### 3️⃣ If Expired → Refresh
```
POST /auth/refresh
Authorization: Bearer <refresh_token>
```
→ Returns new `access_token`.

### 4️⃣ Logout → Invalidate Refresh Token
```
POST /auth/logout
Authorization: Bearer <refresh_token>
```
→ Refresh token is blacklisted and cannot be reused.

---

## 🤝 **KMP Integration (Ktor Auth)**

Example from the Kotlin Multiplatform mobile app:

```kotlin
install(Auth) {
    bearer {
        loadTokens {
            BearerTokens(tokenManager.getAccessToken(), tokenManager.getRefreshToken())
        }

        refreshTokens {
            val refresh = tokenManager.getRefreshToken() ?: return@refreshTokens null
            val response = client.post("https://api.talangraga.com/auth/refresh") {
                header("Authorization", "Bearer $refresh")
            }
            if (response.status.isSuccess()) {
                val newAccess = response.body<JsonObject>()["data"]?.jsonObject?.get("access_token")?.jsonPrimitive?.content
                if (newAccess != null) {
                    tokenManager.saveAccessToken(newAccess)
                    BearerTokens(newAccess, refresh)
                } else null
            } else null
        }
    }
}
```

✅ Auto refreshes and retries on `401 Access token expired`.

---

## ⚙️ **Run Server**

```bash
uvicorn app.main:app --reload
```

Docs available at 👉 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## ☁️ **Next Plans**

- [ ] `/auth/change-password` endpoint  
- [ ] `/payments`, `/transactions`, `/periodes` modules  
- [ ] Dockerize + Deploy to Railway / Render  
- [ ] Add tests with Pytest + SQLite  
- [ ] Add Redis for persistent token blacklist  

---

## 👨‍💻 **Author**

**Iqbal Fauzi**  
Android Engineer @ Bobobox  
Building **Talangraga Umroh** — Kotlin Multiplatform app + FastAPI backend  

📦 GitHub: [@iqbalwork](https://github.com/iqbalwork)  
💼 LinkedIn: [linkedin.com/in/ifauzii](https://linkedin.com/in/ifauzii)
