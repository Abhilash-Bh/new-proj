import sys
import os

sys.path.insert(0, r'd:\projects flask\EMS')
from app import app, db, Employee, Attendance

client = app.test_client()

print("--- Testing /api/attendance/status ---")
res = client.get('/api/attendance/status')
print("Status response:", res.status_code, res.get_json())

print("\n--- Testing /api/attendance/toggle (Check In) ---")
res = client.post('/api/attendance/toggle')
print("Check In response:", res.status_code, res.get_json())

print("\n--- Testing /api/attendance/status after Check In ---")
res = client.get('/api/attendance/status')
print("Status after Check In:", res.status_code, res.get_json())

print("\n--- Testing /api/attendance/toggle (Check Out) ---")
res = client.post('/api/attendance/toggle')
print("Check Out response:", res.status_code, res.get_json())

print("\n--- Testing /api/attendance/status after Check Out ---")
res = client.get('/api/attendance/status')
print("Status after Check Out:", res.status_code, res.get_json())
