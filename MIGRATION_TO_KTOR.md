# Migration Plan: FastAPI to Ktor (Talangraga Backend)

## Goal Description
Migrate the existing **Talangraga Umroh** backend service from **FastAPI (Python)** to **Ktor (Kotlin)**. The goal is to replicate all existing features including Authentication (JWT), Database interactions (PostgreSQL), and functional modules (User, Payment, Periode, Transaction) while leveraging Kotlin's type safety and Ktor's asynchronous capabilities.

## Strategic Decisions

### Database Migration Strategy
Currently, the project uses **Alembic** for migrations.
- **Decision**: Migrate to **Flyway** (native JVM ecosystem) for a fully contained JVM project.

### Authentication Token Invalidation
The current Blacklist is **in-memory** (`BLACKLISTED_REFRESH_TOKENS` set).
- **Decision**: In the Ktor migration, implement **Redis** or a Database table for token blacklisting to ensure persistence across restarts.

## Dependencies Mapping

| Category | FastAPI (Current) | Ktor (Target) |
| :--- | :--- | :--- |
| **Language** | Python 3.10+ | Kotlin 1.9+ |
| **Framework** | FastAPI | Ktor Server |
| **Build Tool** | pip / requirements.txt | Gradle (Kotlin DSL) |
| **Database ORM** | SQLAlchemy | **Exposed** (JetBrains) or Ktorm |
| **DB Driver** | psycopg2 | Postgres JDBC Driver |
| **Migrations** | Alembic | **Flyway** |
| **Serialization** | Pydantic | **Kotlinx Serialization** |
| **Authentication** | python-jose, passlib | Ktor Auth JWT, BCrypt |
| **Validation** | Pydantic | Ktor Request Validation / Konform |
| **Htttp Client** | httpx | Ktor Client |
| **DI** | FastAPI `Depends` | **Koin** (or manual DI) |

## Proposed Architecture (Clean Architecture)

FastAPI structure is relatively flat. For Ktor, we will use a more structured Layered Architecture:

```
src/main/kotlin/com/talangraga/
├── Application.kt          # Entry point, plugin configuration
├── plugins/                # One file per plugin (Routing, Serialization, Security, Databases)
├── features/               # Vertical Slice Architecture (Recommended)
│   ├── auth/
│   │   ├── AuthRoutes.kt
│   │   ├── AuthController.kt
│   │   ├── AuthService.kt
│   │   ├── AuthRepository.kt
│   │   └── models/         # DTOs and Tables
│   ├── user/
│   │   └── ...
│   ├── payment/
│   │   └── ...
│   ├── periode/
│   │   └── ...
│   └── transaction/
│       └── ...
├── core/
│   ├── database/           # DatabaseFactory, Migration logic
│   ├── security/           # Token generation, Hashing utils
│   └── util/               # Response wrappers, extensions
└── resources/
    ├── application.yaml    # Config (replaces .env usage directly)
    └── logback.xml         # Logging config
```

## Migration Steps

### Phase 1: Project Initialization
1. Initialize Ktor project with Gradle.
2. Configure `application.yaml` to match `.env` variables.
3. Set up `plugins` architecture (Routing, StatusPages for exception handling, ContentNegotiation for JSON).

### Phase 2: Database & Models
1. Configure **Exposed** with HikariCP for connection pooling.
2. Create **Flyway** migration scripts (mirroring current Alembic schema).
3. Port SQLAlchemy Models (`app/db/models`) to Exposed `Table` objects:
    - `User`, `Transaction`, `Payment`, `Periode`.

### Phase 3: Core Utilities & Auth
1. Implement `ResponseWrapper` to match `BaseResponse` format.
2. Implement `PasswordUtil` (BCrypt) to replace `passlib`.
3. Implement `TokenService` (JWT) to replace `core/security.py`.
4. Configure Ktor 'Bearer' Auth provider.
5. **Improvement**: Implement Redis/DB-based token blacklist.

### Phase 4: Feature Migration
#### Authentication
- Port logic from `app/api/routes/auth.py`.
- Endpoints: Register, Login, Refresh Token (critical path), Logout, Forgot Password.

#### User Management
- Endpoints: Profile, Update, Delete (Admin).

#### Business Features (Payment, Periode, Transaction)
- Port logic module by module.
- Ensure Transactional integrity (Exposed `transaction { }` block).

### Phase 5: Verification
1. Write Integration Tests using Ktor `testApplication`.
2. Verify End-to-End flows (Register -> Login -> Create Transaction).
