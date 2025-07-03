# Budget Tracking App

A Django-based web application to help users plan events and track budgets, pledges, and donations effectively — ideal for occasions like weddings, church events, or community fundraisers.

## 🔍 Features

- Create and manage multiple events with individual budgets
- Track pledges and actual payments from donors
- Automatically calculate totals, balance remaining, and progress
- Reuse donor info (name + phone) across multiple events
- JSON API with token-based authentication (JWT)
- Modular architecture with test coverage using `factory_boy` and DRF test tools

## 🚀 Tech Stack

- Python 3.x
- Django + Django REST Framework
- SQLite (default), easily swappable to Postgres/MySQL
- Factory Boy & Faker for testing
- JWT (via SimpleJWT) for authentication

## 📦 Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/benjamaina/budget_tracking_app.git
cd budget_tracking_app

🔐 Authentication
This project uses JWT-based authentication.
To obtain a token:

POST to /api/token/ with username and password

Use the returned token in your headers like so:

Authorization: Bearer <your_token_here>


🧪 Running Tests
bash
Copy
Edit
python manage.py test
Tests are written with:

APITestCase from DRF

factory_boy for generating mock data

Coverage includes events, pledges, budgets, and donors

📂 Project Structure
graphql
Copy
Edit
budget_tracking_app/
├── budgetapp/       # Core models like Event, BudgetItem, Donor, Pledge
├── events/          # Event API views and tests
├── pledges/         # Pledge views, serializers, etc.
├── tests/           # Automated test cases and factories
├── manage.py
└── requirements.txt
📈 Future Improvements
Email or SMS reminders for upcoming events

Frontend dashboard with charts & progress indicators

M-Pesa integration for real payment tracking

Export budget reports to CSV or PDF

Mobile-friendly frontend (e.g. Flutter or Next.js)

👨‍💻 Author
Benjamin Maina
GitHub: benjamaina

Feel free to fork, raise issues, or contribute! This app was built to solve real-world budgeting challenges in a simple, practical way.

