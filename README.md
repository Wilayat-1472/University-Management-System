<p align="center">
  <img src="https://img.icons8.com/3d-fluency/94/graduation-cap.png" width="80" alt="UMS Logo"/>
</p>

<h1 align="center">University Management System</h1>

<p align="center">
  <em>A comprehensive, production-grade REST API for managing university operations<br/>built with FastAPI, SQLAlchemy, and a layered clean architecture.</em>
</p>

<p align="center">
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/></a>
  <a href="https://fastapi.tiangolo.com"><img src="https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"/></a>
  <a href="https://sqlalchemy.org"><img src="https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white" alt="SQLAlchemy"/></a>
  <a href="#"><img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="License"/></a>
</p>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-api-reference">API Reference</a> •
  <a href="#-roadmap">Roadmap</a>
</p>

---

## 📋 Overview

The **University Management System (UMS)** is a modular backend platform designed to digitize and streamline core university processes including:

- **User & Role Management** — RBAC-protected endpoints for Students, Faculty, and Admins
- **Course & Enrollment** — Course creation with geofencing support and student enrollment tracking
- **Smart Attendance** — Multi-layered verification engine with GPS geofencing, device fingerprinting, mock-location detection, and live heartbeat monitoring
- **Finance & Billing** — 1Bill-style invoice generation, fee structures, payment recording, and webhook integration
- **Payroll** — Staff salary management with status lifecycle tracking
- **Analytics Dashboard** — Revenue summaries, attendance metrics, enrollment stats, and payroll reports

> **Status:** Backend API is fully functional. Frontend development is in progress.

---

## ✨ Features

### 🔐 Authentication & Authorization

| Capability | Details |
| :--- | :--- |
| JWT Authentication | Access + Refresh token flow via OAuth2 password grant |
| Role-Based Access Control | Granular permissions for `Admin`, `Faculty`, and `Student` roles |
| Password Security | bcrypt hashing with salt |
| Token Expiry | Configurable access (30 min) and refresh (7 day) token lifetimes |

### 📚 Course Management

| Capability | Details |
| :--- | :--- |
| CRUD Operations | Create, list, and manage courses with credit hours |
| Geofencing | Each course stores latitude, longitude, and allowed radius for location-verified attendance |
| Enrollment | Students self-enroll; Faculty/Admin create courses |

### 📍 Smart Attendance System

The attendance module is the **flagship feature** — a multi-layered verification engine that goes beyond basic check-ins:

```
┌─────────────────────────────────────────────────────────────┐
│                   VERIFICATION PIPELINE                     │
│                                                             │
│  Step 1 ─ Verification Code    Session-specific random code │
│  Step 2 ─ Mock Location        Flags spoofed GPS signals    │
│  Step 3 ─ Device ID            Cross-checks MAC address     │
│  Step 4 ─ Geofencing           Haversine distance calc      │
│  Step 5 ─ Live Heartbeat       Periodic location pings      │
└─────────────────────────────────────────────────────────────┘
```

- **Session Management** — Instructors start/end attendance windows with auto-generated verification codes
- **Multi-Layer Verification** — Mock location detection → Device fingerprint matching → GPS geofencing
- **Heartbeat Monitoring** — Students send periodic location pings; if they leave the radius mid-session, their status downgrades to `Remote`
- **Status Classification** — `Present` · `Late` · `Remote` · `Absent` with full audit trail

### 💰 Finance & Billing

| Capability | Details |
| :--- | :--- |
| Fee Structures | Per-course or university-wide fee definitions by semester |
| 1Bill-Style Invoices | Auto-generated consumer numbers, bill references, and shareable payment links |
| Payment Recording | Manual (Cash, Bank Transfer) and digital (JazzCash, EasyPaisa, Card) methods |
| Webhook Integration | 1Bill callback endpoint for automatic payment reconciliation |
| Invoice Lifecycle | `Unpaid` → `Partially Paid` → `Paid` / `Overdue` / `Cancelled` |

### 💼 Payroll Management

| Capability | Details |
| :--- | :--- |
| Salary Records | Monthly payroll entries with base salary, allowances, and deductions |
| Status Workflow | `Pending` → `Processed` → `Paid` |
| Staff Scoping | Payrolls linked to Faculty and Admin users |

### 📊 Analytics & Reporting

| Endpoint | Description |
| :--- | :--- |
| `GET /analytics/revenue` | Revenue summary — invoiced vs collected vs outstanding, grouped by semester |
| `GET /analytics/attendance` | Per-course attendance rates and verification metrics |
| `GET /analytics/enrollments` | Student enrollment counts per course |
| `GET /analytics/payroll` | Total payroll expenses grouped by month |

---

## 🏗 Architecture

The project follows a **clean, layered architecture** that separates concerns across distinct layers:

```
backend/
├── app/
│   ├── main.py                # FastAPI app entry point
│   ├── config.py              # Centralized settings (DB, JWT, CORS)
│   ├── database.py            # SQLAlchemy engine, session, Base
│   │
│   ├── models/                # ORM models (data layer)
│   │   ├── user.py            # User with role FK and device MAC
│   │   ├── role.py            # Role definitions
│   │   ├── profile.py         # Extended user profile
│   │   ├── course.py          # Course + Enrollment + geofencing
│   │   ├── attendance.py      # Session, Record, Heartbeat
│   │   └── finance.py         # FeeStructure, Invoice, Payment, Payroll
│   │
│   ├── schemas/               # Pydantic request/response schemas
│   │   ├── auth.py            # Token schemas
│   │   ├── user.py            # User CRUD schemas
│   │   ├── course.py          # Course and Enrollment schemas
│   │   ├── attendance.py      # Attendance schemas
│   │   └── finance.py         # Finance, Invoice, Payment schemas
│   │
│   ├── routers/               # API route handlers
│   │   ├── auth.py            # Login, Register, /me
│   │   ├── users.py           # User management (Admin)
│   │   ├── profile.py         # Profile CRUD
│   │   ├── courses.py         # Course and Enrollment endpoints
│   │   ├── attendance.py      # Session, Mark, Heartbeat
│   │   ├── finance.py         # Fee structures and Payroll
│   │   ├── payments.py        # Invoices, Payments, Webhooks
│   │   └── analytics.py       # Dashboard analytics
│   │
│   ├── services/              # Business logic layer
│   │   ├── auth_service.py    # Token validation, current user
│   │   ├── user_service.py    # User CRUD operations
│   │   ├── course_service.py  # Course logic
│   │   ├── attendance_service.py  # Verification engine
│   │   ├── finance_service.py # Fee and payroll logic
│   │   ├── billing_service.py # Invoice generation and payments
│   │   └── analytics_service.py   # Aggregation queries
│   │
│   ├── middleware/            # Custom middleware
│   │   └── rbac.py            # RoleChecker dependency
│   │
│   └── utils/                 # Shared utilities
│       └── security.py        # Password hashing, JWT helpers
│
├── tests/                     # Test suite
├── seed_data.py               # Database seeder
└── requirements.txt           # Python dependencies
```

**Design Principles:**

- **Separation of Concerns** — Routers handle HTTP, Services handle business logic, Models handle persistence
- **Dependency Injection** — FastAPI's `Depends()` for DB sessions, authentication, and RBAC
- **Schema Validation** — Pydantic v2 models enforce strict input/output contracts
- **Database Agnostic** — SQLite for development, PostgreSQL-ready for production (single config switch)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- pip
- Git

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Wilayat-1472/University-Management-System.git
cd University-Management-System/backend

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Linux / macOS
# venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the `backend/` directory:

```env
# Database (default: SQLite — switch to PostgreSQL for production)
DATABASE_URL=sqlite:///./ums.db
# DATABASE_URL=postgresql://user:password@localhost:5432/ums_db

# JWT Secret — CHANGE THIS IN PRODUCTION
SECRET_KEY=your-super-secret-key-here

# Token expiry
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### Seed & Run

```bash
# 4. Seed the database with default roles and admin user
python seed_data.py

# 5. Start the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Default admin credentials:**

| Field | Value |
| :--- | :--- |
| Username | `admin` |
| Email | `admin@ums.edu` |
| Password | `adminpassword` |

> ⚠️ **Change the default admin credentials immediately in production.**

### Explore the API

Once the server is running, visit:

- **Swagger UI** — [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc** — [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 📡 API Reference

All endpoints are prefixed with `/api/v1`. Authentication uses **Bearer JWT tokens**.

### Auth — `/api/v1/auth`

| Method | Endpoint | Auth | Description |
| :--- | :--- | :---: | :--- |
| `POST` | `/login` | — | OAuth2 login, returns access + refresh tokens |
| `POST` | `/register` | — | Register a new user |
| `GET` | `/me` | ✅ | Get current authenticated user |

### Users — `/api/v1/users`

| Method | Endpoint | Auth | Roles | Description |
| :--- | :--- | :---: | :--- | :--- |
| `GET` | `/` | ✅ | Admin | List all users |
| `GET` | `/{id}` | ✅ | Admin | Get user by ID |

### Profile — `/api/v1/profile`

| Method | Endpoint | Auth | Description |
| :--- | :--- | :---: | :--- |
| `GET` | `/me` | ✅ | Get own profile |
| `PUT` | `/me` | ✅ | Update own profile |

### Courses — `/api/v1/courses`

| Method | Endpoint | Auth | Roles | Description |
| :--- | :--- | :---: | :--- | :--- |
| `GET` | `/` | ✅ | Any | List all courses |
| `POST` | `/` | ✅ | Faculty, Admin | Create a new course |
| `POST` | `/{id}/enroll` | ✅ | Student | Enroll in a course |

### Attendance — `/api/v1/attendance`

| Method | Endpoint | Auth | Roles | Description |
| :--- | :--- | :---: | :--- | :--- |
| `POST` | `/sessions` | ✅ | Faculty, Admin | Start attendance session |
| `PUT` | `/sessions/{id}/end` | ✅ | Faculty, Admin | End attendance session |
| `GET` | `/sessions/{id}/records` | ✅ | Faculty, Admin | Get session records |
| `POST` | `/mark` | ✅ | Student | Mark attendance with verification |
| `POST` | `/heartbeat` | ✅ | Student | Send location heartbeat |

### Finance — `/api/v1/finance`

| Method | Endpoint | Auth | Roles | Description |
| :--- | :--- | :---: | :--- | :--- |
| `POST` | `/fees` | ✅ | Admin | Create fee structure |
| `GET` | `/fees` | ✅ | Admin, Faculty | List fee structures |
| `POST` | `/payroll` | ✅ | Admin | Create payroll entry |
| `GET` | `/payroll` | ✅ | Admin | List payroll records |
| `PUT` | `/payroll/{id}/status` | ✅ | Admin | Update payroll status |

### Payments — `/api/v1/payments`

| Method | Endpoint | Auth | Roles | Description |
| :--- | :--- | :---: | :--- | :--- |
| `POST` | `/invoices` | ✅ | Admin | Generate 1Bill-style invoice |
| `GET` | `/invoices` | ✅ | Admin | List all invoices |
| `GET` | `/invoices/me` | ✅ | Student | View own invoices |
| `GET` | `/invoices/pay/{token}` | — | Public | View invoice via payment link |
| `POST` | `/record` | ✅ | Admin | Record manual payment |
| `POST` | `/webhook/1bill` | — | Webhook | 1Bill payment callback |

### Analytics — `/api/v1/analytics`

| Method | Endpoint | Auth | Roles | Description |
| :--- | :--- | :---: | :--- | :--- |
| `GET` | `/revenue` | ✅ | Admin | Revenue summary by semester |
| `GET` | `/attendance` | ✅ | Admin, Faculty | Attendance analytics by course |
| `GET` | `/enrollments` | ✅ | Admin, Faculty | Enrollment stats by course |
| `GET` | `/payroll` | ✅ | Admin | Payroll summary by month |

---

## 🛠 Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Language** | Python 3.10+ |
| **Framework** | FastAPI 0.111 |
| **ORM** | SQLAlchemy 2.0 |
| **Migrations** | Alembic 1.13 |
| **Validation** | Pydantic v2 (with email support) |
| **Auth** | python-jose (JWT) + bcrypt |
| **Database** | SQLite (dev) / PostgreSQL (prod) |
| **Server** | Uvicorn (ASGI) |
| **Env Config** | python-dotenv |

---

## 🧪 Testing

```bash
# Run the test suite from the backend directory
cd backend
python -m pytest tests/ -v
```

**Current test coverage:**

- `test_finance.py` — Fee structure, invoice, and payment flow tests
- `test_verification.py` — Attendance verification pipeline tests

---

## 🗺 Roadmap

- [x] Core architecture, user auth, roles, and profiles
- [x] Course management with geofencing and enrollment
- [x] Smart attendance verification engine (GPS + device + heartbeat)
- [x] Finance module (fee structures, 1Bill invoices, payments, payroll)
- [x] Analytics dashboard endpoints
- [ ] Frontend (React + Vite) — *In Progress*
- [ ] Alembic migration scripts for schema versioning
- [ ] Email notifications (invoice reminders, attendance alerts)
- [ ] Docker containerization and CI/CD pipeline
- [ ] Production deployment (PostgreSQL + Nginx + Gunicorn)

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch — `git checkout -b feature/amazing-feature`
3. **Commit** your changes — `git commit -m 'feat: add amazing feature'`
4. **Push** to the branch — `git push origin feature/amazing-feature`
5. **Open** a Pull Request

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <strong>Built with ❤️ using FastAPI</strong>
</p>
