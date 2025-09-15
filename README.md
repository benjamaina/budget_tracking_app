Budget Tracking App

A full-stack event budgeting and pledge tracking system built with Django REST Framework (backend) and React (Lovable) frontend, containerized with Docker + Nginx for easy deployment. Designed for event organizers to manage budgets, pledges, payments, tasks, and service providers, with support for M-Pesa integration and interactive dashboards.

✨ Features

Event Management – Create and manage multiple events.

Budgeting – Track budget items by category (venue, catering, etc.).

Pledges & Donations – Record pledges and monitor fulfillment.

Payments – Support for both manual entries and M-Pesa payments.

Service Providers – Manage vendors and payment records.

Tasks & Reminders – Assign and track event-related tasks.

Authentication – Secure API endpoints using JWT (SimpleJWT).

Caching & Performance – Redis integration for performance where needed.

Extensible Frontend – A React (Lovable) frontend integrated with backend APIs.

Containerized Deployment – Dockerized backend + frontend, served via Nginx.

🛠 Tech Stack

Backend

Python 3.x

Django 5.x

Django REST Framework

MySQL (default database, via django-decouple for config)

Redis (for caching)

Frontend

React (Lovable AI generated, customized)

Tailwind CSS + RippleUI

Deployment / Infra

Docker & Docker Compose

Nginx (reverse proxy for serving frontend + backend APIs)

SimpleJWT for authentication

FactoryBoy + Faker for testing

📂 Project Structure

budget_tracking_app/
├── backend/             # Django backend (DRF, models, views, serializers)
│   ├── events/
│   ├── pledges/
│   ├── payments/
│   ├── tasks/
│   ├── users/
│   ├── tests/
│   ├── manage.py
│   └── requirements.txt
├── frontend/            # React (Lovable) frontend
├── nginx/               # Nginx config for reverse proxy
├── docker-compose.yml   # Orchestration for backend, frontend, db, redis
└── Dockerfile(s)        # Service-specific Dockerfiles


🚀 Getting Started

Prerequisites

Docker & Docker Compose

Python 3.10+ (if running backend outside Docker)

Node.js (if running frontend outside Docker)

MySQL 8+

Redis (optional for caching)

🔹 Option 1: Run with Docker (recommended)
# Clone repository
git clone https://github.com/benjamaina/budget_tracking_app.git
cd budget_tracking_app

# Start services (backend, frontend, db, redis, nginx)
docker compose up --build


Backend runs on: http://localhost:8000/api/

Frontend runs on: http://localhost:3000/

Nginx reverse proxy: http://localhost/

🔹 Option 2: Manual Backend Setup
cd backend
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env  # configure DB + secrets
python manage.py migrate
python manage.py runserver

🔹 Option 3: Manual Frontend Setup
cd frontend
npm install
npm run dev


🌍 Environment Variables (.env for backend)

SECRET_KEY=your_django_secret_key
DEBUG=True
DB_NAME=budgetdb
DB_USER=ben
DB_PASSWORD=your_password
DB_HOST=db
DB_PORT=3306


📊 Roadmap

✅ Dockerize backend & frontend

✅ Add Nginx reverse proxy

🔜 Finalize React frontend integration

🔜 Full M-Pesa STK Push + callbacks

🔜 Export reports (PDF, Excel)

🔜 Notifications & reminders

🔜 Role-based access control (organizers vs donors)

🔜 CI/CD setup with GitHub Actions