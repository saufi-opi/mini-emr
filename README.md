# ClinicCare Mini EMR

A minimal, secure, and intuitive EMR tool for clinics to search ICD-10 codes, record consultation notes, and manage users.

## Tech Stack
- **Backend**: FastAPI, SQLModel, PostgreSQL, Redis, uv
- **Frontend**: Vue 3, Vite, Shadcn
- **DevOps**: Docker Compose

## Getting Started

### Prerequisites
- Docker and Docker Compose installed.

### Setup
1. **Clone the repository** (if you haven't already).
2. **Setup environment variables**:
   Copy the example environment file and adjust values as needed:
   ```bash
   cp .env.example .env
   ```
3. **Run the application**:
   Use Docker Compose to build and start the services:
   ```bash
   docker-compose up -d --build
   ```
   *Note: On first startup, the backend automatically runs migrations and seeds initial data (Admin/Doctor users and ICD-10 codes).*

### Accessing the App
- **Frontend**: [http://localhost](http://localhost)
- **Backend API**: [http://localhost/api/v1](http://localhost/api/v1)
- **Interactive Documentation**: [http://localhost/docs](http://localhost/docs)

### Default Credentials
If you used the defaults in `.env.example`:
- **Admin**: `admin@example.com` / `aaAA1234`
- **Doctor**: `doctor@example.com` / `aaAA1234`
