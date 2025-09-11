from locust import HttpUser, task, between

ADMIN_USER = {"username": "ben", "password": "ben60367"}

class BudgetAppUser(HttpUser):
    wait_time = between(1, 3)
    token = None
    user_id = None

    def on_start(self):
        res = self.client.post("/api/login/", json=ADMIN_USER)
        if res.status_code == 200:
            data = res.json()
            self.token = data["access"]
            self.user_id = data["user_id"]
            print("Login successful, token:", self.token)
        else:
            print("Login failed:", res.status_code, res.text)

    def auth_headers(self):
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    @task
    def create_event(self):
        if not self.token:
            return
        event_data = {
            "name": "Load Test Event",
            "description": "Created by Locust",
            "venue": "Virtual Hall",
            "total_budget": 100000,
            "event_date": "2030-01-01"
        }
        res = self.client.post("/api/events/", headers=self.auth_headers(), json=event_data)
        print("Create event:", res.status_code, res.text)

    @task
    def get_events(self):
        if not self.token:
            return
        res = self.client.get("/api/events/", headers=self.auth_headers())
        print("Get events:", res.status_code)
        