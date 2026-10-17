from datetime import date, timedelta
from app.scheduling import next_due, status_for


def add_vehicle(client, mileage=100000):
    response = client.post("/api/vehicles", json={
        "year": 2012, "make": "Jeep", "model": "Wrangler", "engine": "3.6L V6", "odometer": mileage
    })
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_empty_garage_and_vehicle(client):
    assert client.get("/api/vehicles").json() == []
    id = add_vehicle(client)
    vehicle = client.get("/api/vehicles").json()[0]
    assert vehicle["id"] == id
    assert vehicle["odometer"] == 100000
    assert client.post(f"/api/vehicles/{id}/odometer", json={"mileage": 99999}).status_code == 422


def test_whichever_comes_first():
    today = date.today()
    assert status_for(today, 501, today + timedelta(days=365), 500) == "overdue"
    assert status_for(today, 100, today - timedelta(days=1), 10000) == "overdue"
    assert status_for(today, 500, None, 500) == "due"
    assert status_for(today, 0, today + timedelta(days=5), None) == "due_soon"
    assert status_for(today, 0, None, 10000) == "upcoming"
    assert next_due(date(2026, 1, 31), 45000, 90, 3000) == (date(2026, 5, 1), 48000)


def test_task_complete_creates_history_and_reschedules(client):
    id = add_vehicle(client)
    task_response = client.post(f"/api/vehicles/{id}/tasks", json={
        "name": "Engine oil", "interval_days": 180, "interval_miles": 5000,
        "next_due_date": date.today().isoformat(), "next_due_mileage": 100000,
    })
    assert task_response.status_code == 201, task_response.text
    task = task_response.json()
    assert task["status"] == "due"
    service = client.post(f"/api/vehicles/{id}/tasks/{task['id']}/complete", json={
        "performed_at": date.today().isoformat(), "mileage": 100012,
        "cost": "67.50", "notes": "Synthetic 5W-20 oil", "parts": "Oil filter",
    })
    assert service.status_code == 201, service.text
    assert service.json()["task_id"] == task["id"]
    tasks = client.get(f"/api/vehicles/{id}/tasks").json()
    assert tasks[0]["next_due_mileage"] == 105012
    assert tasks[0]["next_due_date"] == (date.today() + timedelta(days=180)).isoformat()
    assert tasks[0]["status"] == "upcoming"
    records = client.get(f"/api/vehicles/{id}/service-records").json()
    assert len(records) == 1
    assert records[0]["service_type"] == "Engine oil"
    assert client.get("/api/vehicles").json()[0]["odometer"] == 100012


def test_edits_deletes_and_isolation(client):
    id = add_vehicle(client)
    other = add_vehicle(client, 3000)
    task = client.post(f"/api/vehicles/{id}/tasks", json={"name": "Tires", "next_due_mileage": 102000}).json()
    assert client.patch(f"/api/vehicles/{other}/tasks/{task['id']}", json={"name": "X"}).status_code == 404
    edited = client.patch(f"/api/vehicles/{id}/tasks/{task['id']}", json={"name": "Tire rotation"})
    assert edited.status_code == 200
    assert edited.json()["name"] == "Tire rotation"
    assert client.delete(f"/api/vehicles/{id}/tasks/{task['id']}").status_code == 204
    assert client.get(f"/api/vehicles/{id}/tasks").json() == []
    assert client.get("/api/vehicles/not-real/tasks").status_code == 404


def test_required_schedule_and_missing_vehicle(client):
    id = add_vehicle(client)
    assert client.post(f"/api/vehicles/{id}/tasks", json={"name": "Unscheduled"}).status_code == 422
    assert client.patch("/api/vehicles/not-real", json={"make": "Ford"}).status_code == 404
