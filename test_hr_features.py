import unittest
from datetime import datetime
from app import app, db, Employee, Attendance

class TestHrFeatures(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.ctx = app.app_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()

    def test_hr_dashboard_elements(self):
        res = self.client.get('/hr/dashboard')
        self.assertEqual(res.status_code, 200)
        html = res.get_data(as_text=True)
        self.assertIn('id="checkin-card"', html)
        self.assertIn('id="checkin-timer"', html)
        self.assertIn('id="checkin-btn"', html)
        self.assertIn('id="topbar-status-badge"', html)
        self.assertIn('id="snapshot-checkin"', html)
        self.assertIn('Office Timing:', html)
        self.assertIn('09:00 AM – 06:00 PM', html)
        print("PASS: /hr/dashboard contains check-in hero card, timer, snapshot, and topbar status badge.")

    def test_hr_leave_elements(self):
        res = self.client.get('/hr/leave')
        self.assertEqual(res.status_code, 200)
        html = res.get_data(as_text=True)
        self.assertIn('openApplyLeaveModal()', html)
        self.assertIn('id="hr-leave-modal"', html)
        self.assertIn('id="modal-employee"', html)
        self.assertIn('id="modal-leave-type"', html)
        self.assertIn('id="modal-start-date"', html)
        self.assertIn('id="modal-end-date"', html)
        self.assertIn('id="modal-duration-label"', html)
        self.assertIn('id="pending-approvals-tbody"', html)
        self.assertIn('id="leave-history-tbody"', html)
        self.assertIn('id="metric-pending"', html)
        self.assertIn('id="metric-approved"', html)
        self.assertIn('toast-notification', html)
        print("PASS: /hr/leave contains functional Apply Leave button, modal, form elements, and tables.")

    def test_hr_checkin_checkout_api(self):
        # 1. Check status for EMP-108
        res = self.client.get('/api/attendance/status?emp_code=EMP-108')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('checked_in', data)
        self.assertEqual(data.get('emp_name'), 'Alex Mercer')
        print(f"PASS: Status for EMP-108: checked_in={data['checked_in']}, name={data.get('emp_name')}")

        # 2. Toggle check-in/out for EMP-108
        res = self.client.post('/api/attendance/toggle', json={'emp_code': 'EMP-108'})
        self.assertEqual(res.status_code, 200)
        toggle_data = res.get_json()
        self.assertTrue(toggle_data.get('success'))
        self.assertEqual(toggle_data.get('emp_name'), 'Alex Mercer')
        print(f"PASS: Toggle action={toggle_data.get('action')}, checked_in={toggle_data.get('checked_in')}")

if __name__ == '__main__':
    unittest.main()
