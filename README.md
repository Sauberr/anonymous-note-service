<h1 align="center">🔒 Anonymous Note Service</h1>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-blue?style=for-the-badge&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/FastAPI-0.115+-green?style=for-the-badge&logo=fastapi&logoColor=white">
  </br>
  <img src="https://img.shields.io/badge/PostgreSQL-16+-blue?style=for-the-badge&logo=postgresql&logoColor=white">
  <img src="https://img.shields.io/badge/SQLAlchemy-2.0+-red?style=for-the-badge&logo=sqlalchemy&logoColor=white">
  </br>
  <img src="https://img.shields.io/badge/Docker-Ready-blue?style=for-the-badge&logo=docker&logoColor=white">
  <img src="https://img.shields.io/badge/OAuth2-Google-orange?style=for-the-badge&logo=google&logoColor=white">
  </br>
  <img src="https://img.shields.io/badge/Admin-FastAdmin-purple?style=for-the-badge&logo=react&logoColor=white">
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge">
</p>

<h2 align="left">📋 About</h2>

**Anonymous Note Service** is a modern, privacy-first platform for creating and sharing notes without revealing your identity. Built with **FastAPI** and **Python 3.12+**, it provides a fast, secure, and scalable backend for anonymous communication.

Users can create notes with optional image attachments, set them as ephemeral (auto-deleted after one read) or permanent, and configure custom expiration times. Each note is protected by a secret key — only those who know it can access the content.

The service features full **OAuth2 social authentication** (Google), **JWT-based access tokens**, and a beautiful **React-powered admin dashboard** with real-time charts and statistics. Background tasks like note expiration are handled automatically by **APScheduler**.

---

## 🛠️ Stack

| Layer | Technology |
|-------|-----------|
| **Language** | [Python 3.12+](https://python.org/) |
| **Framework** | [FastAPI 0.115+](https://fastapi.tiangolo.com/) |
| **Database** | [PostgreSQL 16+](https://postgresql.org/) |
| **ORM** | [SQLAlchemy 2.0+](https://sqlalchemy.org/) with asyncpg |
| **Migrations** | [Alembic](https://alembic.sqlalchemy.org/) |
| **Auth** | [FastAPI Users](https://fastapi-users.github.io/fastapi-users/) + OAuth2 |
| **Admin Panel** | [FastAdmin](https://github.com/vsdudakov/fastadmin) (React UI) |
| **Scheduler** | [APScheduler](https://apscheduler.readthedocs.io/) |
| **Server** | [Uvicorn](https://www.uvicorn.org/) + [Gunicorn](https://gunicorn.org/) |
| **Deployment** | [Docker](https://docker.com/) + Docker Compose |
| **Testing** | [pytest](https://pytest.org/) + pytest-asyncio |
| **Code Quality** | Black, Ruff, isort |

---

## 🚀 Features

- **Anonymous Notes** — create notes without registration, protected by a secret key
- **Ephemeral Mode** — notes auto-delete after being read once
- **Custom Expiry** — set a lifetime for any note
- **Image Attachments** — optionally attach an image to a note
- **OAuth2 Authentication** — Google social login support
- **JWT Tokens** — secure session management
- **Admin Dashboard** — React-based admin panel at `/admin` with:
  - Full CRUD for users, notes, tokens, OAuth accounts
  - Live charts: user status, note types, provider distribution
  - Bulk actions: activate/deactivate users, delete expired notes
- **Localization** — i18n support via fastapi-babel
- **Background Tasks** — automatic note expiration via APScheduler
- **Docker Ready** — fully containerized with Docker Compose

---

## ⚡ Quick Start with Docker

```bash
# 1. Clone the repository
git clone https://github.com/Sauberr/anonymous-note-service.git
cd anonymous-note-service

# 2. Copy environment file
cp test.env .env

# 3. Start all services
docker compose up --build -d

# 4. Run migrations
docker compose exec backend alembic upgrade head

# 5. Create superuser for admin panel
docker compose exec backend python -m app.actions.create_superuser
```

Access the app:
- **Main app**: http://localhost:8000
- **Admin panel**: http://localhost:8000/admin
- **API docs**: http://localhost:8000/docs

---

## 🛠️ Local Development

### Prerequisites

- Python 3.12+
- Poetry
- PostgreSQL 16 (or Docker)

### Steps

**1. Clone and install dependencies:**
```bash
git clone https://github.com/Sauberr/anonymous-note-service.git
cd anonymous-note-service
poetry install
```

**2. Configure environment:**
```bash
cp test.env .env
```

Open `.env` and set your values:
```env
APP_CONFIG__DB__URL=postgresql+asyncpg://user:password@localhost:5433/dbname

APP_CONFIG__DEFAULT_EMAIL=admin@example.com
APP_CONFIG__DEFAULT_PASSWORD=YourStrongPassword!

APP_CONFIG__ACCESS_TOKEN__RESET_PASSWORD_TOKEN_SECRET=your-secret-key
APP_CONFIG__ACCESS_TOKEN__VERIFICATION_TOKEN_SECRET=your-secret-key

APP_CONFIG__OAUTH2__CLIENT_ID=your-google-client-id
APP_CONFIG__OAUTH2__CLIENT_SECRET=your-google-client-secret
```

**3. Start PostgreSQL:**
```bash
docker compose up pg -d
```

**4. Apply migrations:**
```bash
poetry run alembic upgrade head
```

**5. Create admin superuser:**
```bash
poetry run python -m app.actions.create_superuser
```

**6. Run the server:**
```bash
poetry run uvicorn app.main:main_app --reload --port 8000
```

---

## 🧪 Running Tests

```bash
# Via Docker
docker compose up tests

# Locally
poetry run pytest app/notes/tests -v
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Main page |
| `POST` | `/api/v1/notes/` | Create a note |
| `POST` | `/api/v1/notes/{hash}` | Get a note by hash + secret |
| `GET` | `/api/v1/notes/{hash}` | Get note result page |
| `GET` | `/api/v1/notes/list` | Paginated notes list |
| `POST` | `/api/v1/auth/login` | Login (JWT) |
| `POST` | `/api/v1/auth/register` | Register |
| `GET` | `/api/v1/auth/google/authorize` | OAuth2 Google login |
| `GET` | `/admin` | Admin dashboard |
| `GET` | `/docs` | Swagger UI |

---

## 🐳 Docker Services

| Service | Description | Port |
|---------|-------------|------|
| `backend` | FastAPI application | `8000` |
| `pg` | PostgreSQL 16 database | `5433` |
| `pgadmin` | pgAdmin UI | `8080` |

---

## 📜 License

This project is licensed under the [MIT License](https://github.com/Sauberr/anonymous-note-service/blob/master/LICENSE).

---

## 📞 Contact

For questions or feedback, reach out at **dmitriybirilko@gmail.com**
