Budget Tracking App

A full-stack event budgeting and pledge tracking system built with Django REST Framework (backend) and React (Lovable) frontend. Designed for event organizers to manage budgets, pledges, payments, tasks, and service providers, with support for M-Pesa integration and interactive dashboards.

✨ Features

Event Management – Create and manage multiple events.

Budgeting – Track budget items by category (venue, catering, etc.).

Pledges & Donations – Record pledges and monitor fulfillment.

Payments – Support for both manual entries and M-Pesa payments.

Service Providers – Manage vendors and payment records.

Tasks & Reminders – Assign and track event-related tasks.

Authentication – Secure API endpoints using JWT (SimpleJWT).

Caching & Performance – Redis integration for performance where needed.

Extensible Frontend – A React frontend (Lovable) is under development.

🛠 Tech Stack

Backend

Python 3.x

Django 5.x

Django REST Framework

MySQL (default database, via django-decouple for config)

Redis (for caching)

Frontend

React (Lovable AI generated, customized)

Tailwind CSS + RippleUI (planned styling stack)

Other

SimpleJWT for authentication

FactoryBoy + Faker for testing

Docker (optional for deployment)

📂 Project Structure
budget_tracking_app/
├── events/              # Event and budget item models, serializers, views
├── pledges/             # Pledge and donor management
├── payments/            # Vendor, M-Pesa, and manual payments
├── tasks/               # Task and reminder management
├── users/               # Authentication, JWT handling
├── tests/               # Unit and integration tests
├── manage.py
└── requirements.txt

🚀 Getting Started
Prerequisites

Python 3.10+

MySQL 8+

Redis (optional, for caching)

Node.js (for frontend, once merged)

Backend Setup
# Clone repository
git clone https://github.com/benjamaina/budget_tracking_app.git
cd budget_tracking_app

# Create virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your DB credentials and secret key

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver

Environment Variables (.env)
SECRET_KEY=your_django_secret_key
DEBUG=True
DB_NAME=budgetdb
DB_USER=ben
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306

🔑 Authentication

This project uses JWT.

Obtain tokens by POSTing to:

POST /api/token/
{
  "username": "your_username",
  "password": "your_password"
}


Use the access token in headers:

Authorization: Bearer <your_access_token>


Refresh tokens:

POST /api/token/refresh/
{
  "refresh": "<your_refresh_token>"
}

📡 API Documentation
🔹 Events

List Events
GET /api/events/

Create Event
POST /api/events/

{
  "name": "Wedding Ceremony",
  "date": "2025-12-20",
  "location": "Nairobi",
  "description": "Main family event"
}


Retrieve Event
GET /api/events/{id}/

Update Event
PUT /api/events/{id}/

Delete Event
DELETE /api/events/{id}/

🔹 Budget Items

List Budget Items for Event
GET /api/events/{event_id}/budget-items/

Create Budget Item
POST /api/events/{event_id}/budget-items/

{
  "category": "Catering",
  "description": "Buffet for 200 guests",
  "amount": 150000
}

🔹 Pledges

List Pledges for Event
GET /api/events/{event_id}/pledges/

Create Pledge
POST /api/events/{event_id}/pledges/

{
  "donor": {
    "name": "John Doe",
    "phone": "+254712345678"
  },
  "amount": 50000
}

🔹 Payments

Record Manual Payment
POST /api/events/{event_id}/payments/manual/

{
  "pledge_id": 2,
  "amount": 20000,
  "method": "cash"
}


Record M-Pesa Payment (Callback)
POST /api/mpesa/callback/

(Future: full STK Push integration)

🔹 Tasks

Create Task
POST /api/events/{event_id}/tasks/

{
  "title": "Book the venue",
  "due_date": "2025-11-01",
  "assigned_to": "committee_member"
}

🧪 Running Tests
pytest


FactoryBoy and Faker are used for generating test data.

📊 Roadmap

 Finalize React frontend integration

 M-Pesa payments (STK push & callbacks)

 Export reports (PDF, Excel)

 Notifications & reminders

 Role-based access control (organizers vs donors)

 CI/CD setup with GitHub Actions

🤝 Contributing

Pull requests are welcome. Please fork the repo and submit a PR for review.

📜 License

MIT License – feel free to use and adapt.
