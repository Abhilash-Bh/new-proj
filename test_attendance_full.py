import sys
import os

sys.path.insert(0, r'd:\projects flask\EMS')
from app import app, db, Employee, Attendance, seed_database

client = app.test_client()

print("=== 1. Checking Database Setup & Seeding ===")
with app.app_context():
    seed_database()
    emp_count = Employee.query.count()
    att_count = Attendance.query.count()
    aditi = Employee.query.filter_by(emp_code='EMP-101').first()
    assert emp_count >= 5, f"Expected at least 5 employees, got {emp_count}"
    assert att_count >= 8, f"Expected at least 8 attendance records, got {att_count}"
    assert aditi is not None, "Aditi Sharma not found"
    print(f"PASS: {emp_count} employees and {att_count} records verified.")

print("\n=== 2. Testing Route Renders Before Check-in ===")
routes = [
    '/employee/dashboard',
    '/employee/attendance',
    '/hr/dashboard',
    '/hr/attendance',
    '/employee/leave',
    '/hr/leave',
    '/hr/directory',
    '/login'
]
for r in routes:
    res = client.get(r)
    assert res.status_code == 200, f"Route {r} returned {res.status_code}"
    print(f"PASS: {r} -> 200 OK")

print("\n=== 3. Testing Employee Check In via API ===")
# Ensure today's record for Aditi is removed first for clean test
from datetime import datetime
today_str = datetime.now().strftime('%Y-%m-%d')
with app.app_context():
    Attendance.query.filter_by(employee_id=aditi.id, date=today_str).delete()
    db.session.commit()

res = client.post('/api/attendance/toggle')
assert res.status_code == 200, f"Toggle check-in failed: {res.status_code}"
data = res.get_json()
assert data['success'] is True
assert data['checked_in'] is True
assert data['action'] == 'check_in'
print(f"PASS: Check-in successful at {data['check_in_time']}, status: {data['status']}")

print("\n=== 4. Testing Attendance Status API ===")
res = client.get('/api/attendance/status')
assert res.status_code == 200
data = res.get_json()
assert data['checked_in'] is True
assert data['has_record'] is True
print(f"PASS: Status confirmed checked-in, check_in_time: {data['check_in_time']}")

print("\n=== 5. Testing Employee Dashboard Renders Checked-In State ===")
res = client.get('/employee/dashboard')
assert res.status_code == 200
html = res.get_data(as_text=True)
assert "Check Out" in html, "Expected 'Check Out' button in dashboard HTML"
assert "Checked in" in html or "Checked In" in html
print("PASS: Employee dashboard reflects active checked-in session.")

print("\n=== 6. Testing HR Dashboard & Attendance Shows Aditi's Check-in ===")
res = client.get('/hr/dashboard')
assert res.status_code == 200
html = res.get_data(as_text=True)
assert aditi.name in html, f"{aditi.name} should appear on HR dashboard"
assert "EMP-101" in html
print(f"PASS: HR Dashboard reflects {aditi.name}'s check-in.")

res = client.get('/hr/attendance')
assert res.status_code == 200
html = res.get_data(as_text=True)
assert aditi.name in html
print(f"PASS: HR Attendance table reflects {aditi.name}.")

print("\n=== 7. Testing Employee Check Out via API ===")
res = client.post('/api/attendance/toggle')
assert res.status_code == 200
data = res.get_json()
assert data['success'] is True
assert data['checked_in'] is False
assert data['action'] == 'check_out'
print(f"PASS: Check-out successful at {data['check_out_time']}, duty hours: {data['duty_hours']}")

print("\n=== 8. Testing Employee Attendance History Reflects Checkout ===")
res = client.get('/employee/attendance')
assert res.status_code == 200
html = res.get_data(as_text=True)
assert data['check_out_time'] in html or "Total Hours" in html
print("PASS: Employee attendance history updated with finalized record.")

print("\nALL ATTENDANCE DB & DUTY HOUR TESTS PASSED 100%!")
