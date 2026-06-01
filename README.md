<![CDATA[<div align="center">

# 🎓 University Management System

**A comprehensive, production-grade REST API for managing university operations — built with FastAPI, SQLAlchemy, and a layered clean architecture.**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)](https://sqlalchemy.org)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

---

[Features](#-features) · [Architecture](#-architecture) · [Quick Start](#-quick-start) · [API Reference](#-api-reference) · [Roadmap](#-roadmap)

</div>

---

## 📋 Overview

The **University Management System (UMS)** is a modular backend platform designed to digitize and streamline core university processes including:

- **User & Role Management** — RBAC-protected endpoints for Students, Faculty, and Admins
- **Course & Enrollment** — Course creation with geofencing support and student enrollment tracking
- **Smart Attendance** — Multi-layered verification engine with GPS geofencing, device fingerprinting, mock-location detection, and live heartbeat monitoring
- **Finance & Billing** — 1Bill-style invoice generation, fee structures, payment recording, and webhook integration
- **Payroll** — Staff salary management with status lifecycle tracking
- **Analytics Dashboard** — Revenue summaries, attendance metrics, enrollment stats, and payroll reports

> **Status:** Backend API is fully functional. Frontend development is planned.

---

## ✨ Features

### 🔐 Authentication & Authorization
| Capability | Details |
|---|---|
| JWT Authentication | Access + Refresh token flow via OAuth2 password grant |
| Role-Based Access Control | Granular permissions for `Admin`, `Faculty`, and `Student` roles |
| Password Security | bcrypt hashing with salt |
| Token Expiry | Configurable access (30 min) and refresh (7 day) token lifetimes |

### 📚 Course Management
| Capability | Details |
|---|---|
| CRUD Operations | Create, list, and manage courses with credit hours |
| Geofencing | Each course stores latitude, longitude, and allowed radius for location-verified attendance |
| Enrollment | Students self-enroll; Faculty/Admin create courses |

### 📍 Smart Attendance System
The attendance module is the flagship feature — a **multi-layered verification engine** that goes beyond basic check-ins:

```
┌─────────────────────────────────────────────────────────┐
│                  VERIFICATION PIPELINE                  │
├─────────────────────────────────────────────────────────┤
│  1. Verification Code  →  Session-specific random code  │
│  2. Mock Location      →  Flags spoofed GPS signals     │
│  3. Device ID          →  Cross-checks MAC address      │
│  4. Geofencing         →  Haversine distance calc       │
│  5. Live Heartbeat     →  Periodic location pings       │
└─────────────────────────────────────────────────────────┘
```

- **Session Management** — Instructors start/end attendance windows with auto-generated verification codes
- **Multi-Layer Verification** — Mock location detection → Device fingerprint matching → GPS geofencing
- **Heartbeat Monitoring** — Students send periodic location pings; if they leave the radius mid-session, their status downgrades to `Remote`
- **Status Classification** — `Present` · `Late` · `Remote` · `Absent` with full audit trail

### 💰 Finance & Billing
| Capability | Details |
|---|---|
| Fee Structures | Per-course or university-wide fee definitions by semester |
| 1Bill-Style Invoices | Auto-generated consumer numbers, bill references, and shareable payment links |
| Payment Recording | Manual (Cash, Bank Transfer) and digital (JazzCash, EasyPaisa, Card) methods |
| Webhook Integration | 1Bill callback endpoint for automatic payment reconciliation |
| Invoice Lifecycle | `Unpaid` → `Partially Paid` → `Paid` / `Overdue` / `Cancelled` |

### 💼 Payroll Management
| Capability | Details |
|---|---|
| Salary Records | Monthly payroll entries with base salary, allowances, and deductions |
| Status Workflow | `Pending` → `Processed` → `Paid` |
| Staff Scoping | Payrolls linked to Faculty and Admin users |

### 📊 Analytics & Reporting
| Endpoint | Description |
|---|---|
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
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Centralized settings (DB, JWT, CORS)
│   ├── database.py          # SQLAlchemy engine, session, and Base
│   │
│   ├── models/              # SQLAlchemy ORM models (data layer)
│   │   ├── user.py          # User with role FK & device MAC
│   │   ├── role.py          # Role (Admin, Faculty, Student)
│   │   ├── profile.py       # Extended user profile
│   │   ├── course.py        # Course + Enrollment + geofencing
│   │   ├── attendance.py    # Session, Record, Heartbeat
│   │   └── finance.py       # FeeStructure, Invoice, Payment, Payroll
│   │
│   ├── schemas/             # Pydantic request/response schemas
│   │   ├── auth.py          # Token schemas
│   │   ├── user.py          # User CRUD schemas
│   │   ├── profile.py       # Profile schemas
│   │   ├── course.py        # Course & Enrollment schemas
│   │   ├── attendance.py    # Attendance schemas
│   │   └── finance.py       # Finance, Invoice, Payment schemas
│   │
│   ├── routers/             # API route definitions
│   │   ├── auth.py          # Login, Register, /me
│   │   ├── users.py         # User management (Admin)
│   │   ├── profile.py       # Profile CRUD
│   │   ├── courses.py       # Course & Enrollment endpoints
│   │   ├── attendance.py    # Session, Mark, Heartbeat
│   │   ├── finance.py       # Fee structures & Payroll
│   │   ├── payments.py      # Invoices, Payments, Webhooks
│   │   └── analytics.py     # Dashboard analytics
│   │
│   ├── services/            # Business logic layer
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── course_service.py
│   │   ├── attendance_service.py
│   │   ├── finance_service.py
│   │   ├── billing_service.py
│   │   └── analytics_service.py
│   │
│   ├── middleware/           # RBAC middleware
│   │   └── rbac.py          # RoleChecker dependency
│   │
│   └── utils/               # Shared utilities
│       └── security.py      # Password hashing, JWT creation
│
├── tests/                   # Test suite
│   ├── test_finance.py
│   └── test_verification.py
│
├── seed_data.py             # Database seeder (roles + admin user)
└── requirements.txt         # Python dependencies
```

### Design Principles

- **Separation of Concerns** — Routers handle HTTP, Services handle business logic, Models handle persistence
- **Dependency Injection** — FastAPI's `Depends()` for DB sessions, authentication, and RBAC
- **Schema Validation** — Pydantic v2 models enforce strict input/output contracts
- **Database Agnostic** — SQLite for development, PostgreSQL-ready for production (single config switch)

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **pip** (or any Python package manager)
- **Git**

### 1. Clone the Repository

```bash
git clone https://github.com/Wilayat-1472/University-Management-System.git
cd University-Management-System/backend
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
# venv\Scripts\activate         # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Database (default: SQLite — switch to PostgreSQL for production)
DATABASE_URL=sqlite:///./ums.db
# DATABASE_URL=postgresql://ums_user:ums_password@localhost:5432/ums_db

# JWT Secret — CHANGE THIS IN PRODUCTION
SECRET_KEY=your-super-secret-key-here

# Token expiry
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### 5. Seed the Database

```bash
python seed_data.py
```

This creates the default roles (`Student`, `Faculty`, `Admin`) and an admin user:

| Field | Value |
|---|---|
| Username | `admin` |
| Email | `admin@ums.edu` |
| Password | `adminpassword` |

> ⚠️ **Change the default admin credentials immediately in production.**

### 6. Run the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 7. Explore the API

| Resource | URL |
|---|---|
| 🌐 Root | [http://localhost:8000](http://localhost:8000) |
| 📖 Swagger UI | [http://localhost:8000/api/v1/openapi.json](http://localhost:8000/docs) |
| 📘 ReDoc | [http://localhost:8000/redoc](http://localhost:8000/redoc) |

---

## 📡 API Reference

All endpoints are prefixed with `/api/v1`. Authentication uses **Bearer JWT tokens**.

### Authentication
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/auth/login` | ❌ | OAuth2 login → returns access + refresh tokens |
| `POST` | `/auth/register` | ❌ | Register a new user |
| `GET` | `/auth/me` | ✅ | Get current authenticated user |

### Users
| Method | Endpoint | Auth | Roles | Description |
|---|---|---|---|---|
| `GET` | `/users/` | ✅ | Admin | List all users |
| `GET` | `/users/{id}` | ✅ | Admin | Get user by ID |

### Profile
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/profile/me` | ✅ | Get own profile |
| `PUT` | `/profile/me` | ✅ | Update own profile |

### Courses
| Method | Endpoint | Auth | Roles | Description |
|---|---|---|---|---|
| `GET` | `/courses/` | ✅ | Any | List all courses |
| `POST` | `/courses/` | ✅ | Faculty, Admin | Create a new course |
| `POST` | `/courses/{id}/enroll` | ✅ | Student | Enroll in a course |

### Attendance
| Method | Endpoint | Auth | Roles | Description |
|---|---|---|---|---|
| `POST` | `/attendance/sessions` | ✅ | Faculty, Admin | Start attendance session |
| `PUT` | `/attendance/sessions/{id}/end` | ✅ | Faculty, Admin | End attendance session |
| `GET` | `/attendance/sessions/{id}/records` | ✅ | Faculty, Admin | Get session records |
| `POST` | `/attendance/mark` | ✅ | Student | Mark attendance (with verification) |
| `POST` | `/attendance/heartbeat` | ✅ | Student | Send location heartbeat |

### Finance
| Method | Endpoint | Auth | Roles | Description |
|---|---|---|---|---|
| `POST` | `/finance/fees` | ✅ | Admin | Create fee structure |
| `GET` | `/finance/fees` | ✅ | Admin, Faculty | List fee structures |
| `POST` | `/finance/payroll` | ✅ | Admin | Create payroll entry |
| `GET` | `/finance/payroll` | ✅ | Admin | List payroll records |
| `PUT` | `/finance/payroll/{id}/status` | ✅ | Admin | Update payroll status |

### Payments
| Method | Endpoint | Auth | Roles | Description |
|---|---|---|---|---|
| `POST` | `/payments/invoices` | ✅ | Admin | Generate 1Bill-style invoice |
| `GET` | `/payments/invoices` | ✅ | Admin | List all invoices |
| `GET` | `/payments/invoices/me` | ✅ | Student | View own invoices |
| `GET` | `/payments/invoices/pay/{token}` | ❌ | Public | View invoice via payment link |
| `POST` | `/payments/record` | ✅ | Admin | Record manual payment |
| `POST` | `/payments/webhook/1bill` | ❌ | Webhook | 1Bill payment callback |

### Analytics
| Method | Endpoint | Auth | Roles | Description |
|---|---|---|---|---|
| `GET` | `/analytics/revenue` | ✅ | Admin | Revenue summary by semester |
| `GET` | `/analytics/attendance` | ✅ | Admin, Faculty | Attendance analytics by course |
| `GET` | `/analytics/enrollments` | ✅ | Admin, Faculty | Enrollment stats by course |
| `GET` | `/analytics/payroll` | ✅ | Admin | Payroll summary by month |

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| **Language** | Python 3.10+ |
| **Framework** | FastAPI 0.111 |
| **ORM** | SQLAlchemy 2.0 |
| **Migrations** | Alembic 1.13 |
| **Validation** | Pydantic v2 (with email support) |
| **Auth** | python-jose (JWT) + bcrypt |
| **Database** | SQLite (dev) / PostgreSQL (prod-ready) |
| **Server** | Uvicorn (ASGI) |
| **Env Config** | python-dotenv |

---

## 🧪 Testing

Run the test suite from the `backend/` directory:

```bash
python -m pytest tests/ -v
```

Current test coverage:
- `test_finance.py` — Fee structure, invoice, and payment flow tests
- `test_verification.py` — Attendance verification pipeline tests

---

## 🗺 Roadmap

- [x] **Phase 1** — Core architecture, user auth, roles, and profiles
- [x] **Phase 2** — Course management with geofencing and enrollment
- [x] **Phase 3** — Smart attendance verification engine (GPS + device + heartbeat)
- [x] **Phase 4** — Finance module (fee structures, 1Bill invoices, payments, payroll)
- [x] **Phase 5** — Analytics dashboard endpoints
- [ ] **Phase 6** — Frontend (React + Vite) — *In Progress*
- [ ] **Phase 7** — Alembic migration scripts for schema versioning
- [ ] **Phase 8** — Email notifications (invoice reminders, attendance alerts)
- [ ] **Phase 9** — Docker containerization and CI/CD pipeline
- [ ] **Phase 10** — Production deployment (PostgreSQL + Nginx + Gunicorn)

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'feat: add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with ❤️ using FastAPI**

[⬆ Back to Top](#-university-management-system)

</div>
]]>
