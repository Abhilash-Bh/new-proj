import os
from datetime import datetime, date, timedelta
from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'ems.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ─── Database Models ─────────────────────────────────────────────────────────
class Employee(db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True)
    emp_code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    department = db.Column(db.String(100), default='General')
    designation = db.Column(db.String(100), default='Staff')
    avatar = db.Column(db.String(500), nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    
    attendances = db.relationship('Attendance', backref='employee', lazy=True, cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f'<Employee {self.emp_code} - {self.name}>'

class Attendance(db.Model):
    __tablename__ = 'attendance'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    date = db.Column(db.String(20), nullable=False)          # YYYY-MM-DD
    date_formatted = db.Column(db.String(50), nullable=True) # e.g. "Mon, Oct 25"
    check_in = db.Column(db.DateTime, nullable=True)
    check_out = db.Column(db.DateTime, nullable=True)
    duty_seconds = db.Column(db.Integer, default=0)
    duty_hours = db.Column(db.String(30), default='--')      # e.g. "8h 15m"
    status = db.Column(db.String(50), default='Present')     # Present, Late, Checked In, Incomplete, Absent, Holiday
    remarks = db.Column(db.String(200), default='-')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f'<Attendance {self.employee_id} on {self.date} - {self.status}>'

def format_seconds(sec):
    if not sec or sec <= 0:
        return '0h 00m'
    hours = sec // 3600
    mins = (sec % 3600) // 60
    return f"{hours}h {mins:02d}m"

# ─── Office Timing Configuration (09:00 AM - 06:00 PM) ──────────────────────
OFFICE_START_HOUR = 9
OFFICE_START_MINUTE = 0
OFFICE_END_HOUR = 18
OFFICE_END_MINUTE = 0
OFFICE_GRACE_MINUTES = 15

# ─── Database Seeding ────────────────────────────────────────────────────────
def seed_database():
    db.create_all()
    main_emp = Employee.query.filter_by(emp_code='EMP-101').first()
    if main_emp:
        if main_emp.name != 'Abhilash Bhunia' or main_emp.avatar != '/static/images/abhilash_avatar.jpg':
            main_emp.name = 'Abhilash Bhunia'
            main_emp.email = 'abhilash.bhunia@hrsync.com'
            main_emp.avatar = '/static/images/abhilash_avatar.jpg'
            db.session.commit()
        alex_emp = Employee.query.filter_by(emp_code='EMP-108').first()
        if alex_emp and (alex_emp.name != 'Alex Mercer' or alex_emp.avatar != '/static/images/alex_mercer_avatar.jpg'):
            alex_emp.name = 'Alex Mercer'
            alex_emp.email = 'alex.mercer@hrsync.com'
            alex_emp.avatar = '/static/images/alex_mercer_avatar.jpg'
            alex_emp.designation = 'Senior HR Business Partner'
            db.session.commit()
        return
    
    # 1. Seed Main Employee: Abhilash Bhunia
    abhilash_avatar = "/static/images/abhilash_avatar.jpg"
    abhilash = Employee(
        emp_code='EMP-101',
        name='Abhilash Bhunia',
        email='abhilash.bhunia@hrsync.com',
        department='Engineering & Design',
        designation='Product Designer',
        avatar=abhilash_avatar,
        phone='+1 (555) 234-5678'
    )
    
    # 2. Seed Colleagues for HR dashboard
    sarah = Employee(
        emp_code='EMP-042',
        name='Sarah Jenkins',
        email='sarah.jenkins@hrsync.com',
        department='Engineering',
        designation='Lead Developer'
    )
    david = Employee(
        emp_code='EMP-215',
        name='David Chen',
        email='david.chen@hrsync.com',
        department='Sales',
        designation='Account Executive'
    )
    alex = Employee(
        emp_code='EMP-108',
        name='Alex Mercer',
        email='alex.mercer@hrsync.com',
        department='HR',
        designation='Senior HR Business Partner',
        avatar='/static/images/alex_mercer_avatar.jpg'
    )
    priya = Employee(
        emp_code='EMP-304',
        name='Priya Patel',
        email='priya.patel@hrsync.com',
        department='Marketing',
        designation='Content Strategist'
    )
    
    db.session.add_all([abhilash, sarah, david, alex, priya])
    db.session.commit()
    
    # 3. Seed historical attendance records for Abhilash
    base_now = datetime.now()
    yesterday = base_now - timedelta(days=1)
    day_2 = base_now - timedelta(days=2)
    day_3 = base_now - timedelta(days=3)
    day_4 = base_now - timedelta(days=4)
    day_5 = base_now - timedelta(days=5)

    records = [
        Attendance(
            employee_id=abhilash.id,
            date=yesterday.strftime('%Y-%m-%d'),
            date_formatted=yesterday.strftime('%a, %b %d'),
            check_in=yesterday.replace(hour=9, minute=0, second=0),
            check_out=yesterday.replace(hour=18, minute=15, second=0),
            duty_seconds=33300,
            duty_hours='9h 15m',
            status='Present',
            remarks='Shift completed'
        ),
        Attendance(
            employee_id=abhilash.id,
            date=day_2.strftime('%Y-%m-%d'),
            date_formatted=day_2.strftime('%a, %b %d'),
            check_in=day_2.replace(hour=9, minute=0, second=0),
            check_out=day_2.replace(hour=18, minute=0, second=0),
            duty_seconds=32400,
            duty_hours='9h 00m',
            status='Present',
            remarks='Shift completed'
        ),
        Attendance(
            employee_id=abhilash.id,
            date=day_3.strftime('%Y-%m-%d'),
            date_formatted=day_3.strftime('%a, %b %d'),
            check_in=day_3.replace(hour=9, minute=20, second=0),
            check_out=None,
            duty_seconds=0,
            duty_hours='--',
            status='Incomplete',
            remarks='Missed checkout'
        ),
        Attendance(
            employee_id=abhilash.id,
            date=day_4.strftime('%Y-%m-%d'),
            date_formatted=day_4.strftime('%a, %b %d'),
            check_in=day_4.replace(hour=8, minute=50, second=0),
            check_out=day_4.replace(hour=18, minute=10, second=0),
            duty_seconds=33600,
            duty_hours='9h 20m',
            status='Present',
            remarks='Shift completed'
        ),
        Attendance(
            employee_id=abhilash.id,
            date=day_5.strftime('%Y-%m-%d'),
            date_formatted=day_5.strftime('%a, %b %d'),
            check_in=None,
            check_out=None,
            duty_seconds=0,
            duty_hours='--',
            status='Holiday',
            remarks='Company Anniversary'
        )
    ]
    
    # 4. Seed today's records for colleagues on HR Dashboard
    today_str = base_now.strftime('%Y-%m-%d')
    today_formatted = base_now.strftime('%a, %b %d')
    colleague_today = [
        Attendance(
            employee_id=sarah.id,
            date=today_str,
            date_formatted=today_formatted,
            check_in=base_now.replace(hour=8, minute=42, second=0),
            check_out=None,
            duty_seconds=16200,
            duty_hours='4h 30m',
            status='Checked In',
            remarks='Checked In'
        ),
        Attendance(
            employee_id=david.id,
            date=today_str,
            date_formatted=today_formatted,
            check_in=base_now.replace(hour=9, minute=5, second=0),
            check_out=None,
            duty_seconds=14760,
            duty_hours='4h 06m',
            status='Checked In',
            remarks='Checked In'
        ),
        Attendance(
            employee_id=alex.id,
            date=today_str,
            date_formatted=today_formatted,
            check_in=base_now.replace(hour=8, minute=30, second=0),
            check_out=None,
            duty_seconds=16920,
            duty_hours='4h 42m',
            status='Checked In',
            remarks='Checked In'
        )
    ]
    
    db.session.add_all(records + colleague_today)
    db.session.commit()

with app.app_context():
    seed_database()

# ─── API: Attendance Check In / Check Out ─────────────────────────────────────
def get_request_employee():
    emp_code = request.args.get('emp_code')
    if not emp_code and request.is_json:
        data = request.get_json(silent=True) or {}
        emp_code = data.get('emp_code')
    if not emp_code:
        if request.referrer and ('/hr' in request.referrer or 'hr_' in request.referrer):
            emp_code = 'EMP-108'
        else:
            emp_code = 'EMP-101'
    emp = Employee.query.filter_by(emp_code=emp_code).first()
    if not emp and emp_code == 'EMP-108':
        emp = Employee.query.filter_by(department='HR').first()
    if not emp:
        emp = Employee.query.filter_by(emp_code='EMP-101').first()
    return emp

@app.route('/api/attendance/status')
def api_attendance_status():
    emp = get_request_employee()
    if not emp:
        return jsonify({'checked_in': False, 'has_record': False})
    
    today_str = datetime.now().strftime('%Y-%m-%d')
    record = Attendance.query.filter_by(employee_id=emp.id, date=today_str).first()
    
    if not record:
        return jsonify({
            'checked_in': False,
            'has_record': False,
            'check_in_time': '--:--',
            'check_out_time': '--:--',
            'duty_seconds': 0,
            'duty_hours': '--',
            'status': 'Not checked in',
            'check_in_iso': None,
            'emp_name': emp.name,
            'emp_code': emp.emp_code
        })
    
    is_checked_in = (record.check_out is None and record.check_in is not None)
    duty_sec = record.duty_seconds
    if is_checked_in and record.check_in:
        duty_sec = int((datetime.now() - record.check_in).total_seconds())
    
    return jsonify({
        'checked_in': is_checked_in,
        'has_record': True,
        'check_in_time': record.check_in.strftime('%I:%M %p') if record.check_in else '--:--',
        'check_out_time': record.check_out.strftime('%I:%M %p') if record.check_out else '--:--',
        'duty_seconds': duty_sec,
        'duty_hours': format_seconds(duty_sec) if (is_checked_in or record.duty_seconds > 0) else '--',
        'status': 'Checked in' if is_checked_in else record.status,
        'check_in_iso': record.check_in.isoformat() if record.check_in else None,
        'emp_name': emp.name,
        'emp_code': emp.emp_code
    })

@app.route('/api/attendance/toggle', methods=['POST'])
def api_attendance_toggle():
    emp = get_request_employee()
    if not emp:
        return jsonify({'error': 'Employee record not found'}), 404
    
    now = datetime.now()
    today_str = now.strftime('%Y-%m-%d')
    today_formatted = now.strftime('%a, %b %d')
    
    record = Attendance.query.filter_by(employee_id=emp.id, date=today_str).first()
    
    if not record:
        # Check In! Office hours: 09:00 AM - 06:00 PM (15m grace period)
        is_late = (now.hour > OFFICE_START_HOUR or (now.hour == OFFICE_START_HOUR and now.minute > OFFICE_GRACE_MINUTES))
        status = 'Late' if is_late else 'Checked In'
        record = Attendance(
            employee_id=emp.id,
            date=today_str,
            date_formatted=today_formatted,
            check_in=now,
            check_out=None,
            duty_seconds=0,
            duty_hours='0h 00m',
            status=status,
            remarks='Checked in on time' if status == 'Checked In' else 'Late check-in'
        )
        db.session.add(record)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'action': 'check_in',
            'checked_in': True,
            'check_in_time': record.check_in.strftime('%I:%M %p'),
            'check_out_time': '--:--',
            'duty_seconds': 0,
            'duty_hours': '0h 00m',
            'status': record.status,
            'check_in_iso': record.check_in.isoformat(),
            'emp_name': emp.name,
            'emp_code': emp.emp_code
        })
    elif record.check_out is None:
        # Check Out!
        record.check_out = now
        elapsed_sec = int((record.check_out - record.check_in).total_seconds()) if record.check_in else 0
        record.duty_seconds = max(record.duty_seconds, elapsed_sec)
        record.duty_hours = format_seconds(record.duty_seconds)
        record.status = 'Present'
        if now.hour < OFFICE_END_HOUR:
            record.remarks = 'Early checkout' if record.remarks in ['-', 'Checked in on time', ''] else record.remarks
        else:
            record.remarks = 'Shift completed' if record.remarks in ['-', 'Checked in on time', ''] else record.remarks
        db.session.commit()
        
        return jsonify({
            'success': True,
            'action': 'check_out',
            'checked_in': False,
            'check_in_time': record.check_in.strftime('%I:%M %p') if record.check_in else '--:--',
            'check_out_time': record.check_out.strftime('%I:%M %p'),
            'duty_seconds': record.duty_seconds,
            'duty_hours': record.duty_hours,
            'status': record.status,
            'emp_name': emp.name,
            'emp_code': emp.emp_code
        })
    else:
        # Resume Check-in session
        record.check_in = now
        record.check_out = None
        record.status = 'Checked In'
        db.session.commit()
        
        return jsonify({
            'success': True,
            'action': 'check_in',
            'checked_in': True,
            'check_in_time': record.check_in.strftime('%I:%M %p'),
            'check_out_time': '--:--',
            'duty_seconds': record.duty_seconds,
            'duty_hours': format_seconds(record.duty_seconds),
            'status': 'Checked In',
            'check_in_iso': record.check_in.isoformat(),
            'emp_name': emp.name,
            'emp_code': emp.emp_code
        })

# ─── Root ────────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login')
def login():
    return render_template('login.html')

# ─── HR Portal Routes ─────────────────────────────────────────────────────────
@app.route('/hr/dashboard')
def hr_dashboard():
    today_str = datetime.now().strftime('%Y-%m-%d')
    today_attendances = Attendance.query.filter_by(date=today_str).order_by(Attendance.id.desc()).all()
    all_employees = Employee.query.all()
    
    total_employees = len(all_employees)
    present_today = sum(1 for a in today_attendances if a.status in ['Present', 'Checked In', 'Late'])
    late_today = sum(1 for a in today_attendances if a.status == 'Late')
    absent_today = max(0, total_employees - present_today)
    
    # HR employee personal check-in state (Alex Mercer - EMP-108)
    alex = Employee.query.filter_by(emp_code='EMP-108').first()
    today_record = Attendance.query.filter_by(employee_id=alex.id, date=today_str).first() if alex else None
    
    is_checked_in = False
    today_duty_seconds = 0
    today_duty_hours = "--"
    
    if today_record:
        if today_record.check_out is None and today_record.check_in:
            is_checked_in = True
            today_duty_seconds = int((datetime.now() - today_record.check_in).total_seconds())
        else:
            today_duty_seconds = today_record.duty_seconds
        
        today_duty_hours = format_seconds(today_duty_seconds)
    
    return render_template(
        'Hr_dashboard.html',
        today_attendances=today_attendances,
        total_employees=total_employees,
        present_today=present_today,
        late_today=late_today,
        absent_today=absent_today,
        employee=alex,
        today_record=today_record,
        is_checked_in=is_checked_in,
        today_duty_seconds=today_duty_seconds,
        today_duty_hours=today_duty_hours
    )

@app.route('/hr/attendance')
def hr_attendance():
    records = Attendance.query.order_by(Attendance.id.desc()).all()
    all_employees = Employee.query.order_by(Employee.name.asc()).all()
    today_str = datetime.now().strftime('%Y-%m-%d')
    alex = Employee.query.filter_by(emp_code='EMP-108').first()
    today_record = Attendance.query.filter_by(employee_id=alex.id, date=today_str).first() if alex else None
    is_checked_in = False
    today_duty_seconds = 0
    today_duty_hours = "--"
    if today_record:
        if today_record.check_out is None and today_record.check_in:
            is_checked_in = True
            today_duty_seconds = int((datetime.now() - today_record.check_in).total_seconds())
        else:
            today_duty_seconds = today_record.duty_seconds
        today_duty_hours = format_seconds(today_duty_seconds)

    # Calculate dynamic attendance statistics
    total_records = len(records)
    total_seconds = sum(r.duty_seconds for r in records if r.duty_seconds)
    total_hours_formatted = format_seconds(total_seconds)
    
    present_count = sum(1 for r in records if r.status in ['Present', 'Checked In'])
    late_count = sum(1 for r in records if r.status == 'Late')
    incomplete_count = sum(1 for r in records if r.status == 'Incomplete')
    absent_count = sum(1 for r in records if r.status == 'Absent')
    holiday_count = sum(1 for r in records if r.status in ['Holiday', 'Leave'])

    return render_template(
        'hr_attendance.html',
        records=records,
        all_employees=all_employees,
        employee=alex,
        today_record=today_record,
        is_checked_in=is_checked_in,
        today_duty_seconds=today_duty_seconds,
        today_duty_hours=today_duty_hours,
        total_records=total_records,
        total_hours_formatted=total_hours_formatted,
        present_count=present_count,
        late_count=late_count,
        incomplete_count=incomplete_count,
        absent_count=absent_count,
        holiday_count=holiday_count
    )

@app.route('/api/attendance/update', methods=['POST'])
def api_attendance_update():
    data = request.get_json(silent=True) or {}
    record_id = data.get('record_id')
    if not record_id:
        return jsonify({'success': False, 'error': 'Record ID is required'}), 400
    
    record = Attendance.query.get(record_id)
    if not record:
        return jsonify({'success': False, 'error': 'Attendance record not found'}), 404
    
    new_status = data.get('status')
    if new_status:
        record.status = new_status
    
    new_remarks = data.get('remarks')
    if new_remarks is not None:
        record.remarks = new_remarks
    
    check_in_str = data.get('check_in')
    check_out_str = data.get('check_out')
    
    def parse_time_for_record(time_val, base_date_str):
        if not time_val:
            return None
        try:
            return datetime.fromisoformat(time_val)
        except Exception:
            pass
        for fmt in ('%H:%M', '%H:%M:%S', '%I:%M %p'):
            try:
                t = datetime.strptime(time_val.strip(), fmt).time()
                d = datetime.strptime(base_date_str, '%Y-%m-%d').date()
                return datetime.combine(d, t)
            except Exception:
                pass
        return None

    if check_in_str:
        parsed_in = parse_time_for_record(check_in_str, record.date)
        if parsed_in:
            record.check_in = parsed_in
            
    if check_out_str:
        parsed_out = parse_time_for_record(check_out_str, record.date)
        if parsed_out:
            record.check_out = parsed_out
            
    if record.check_in and record.check_out:
        diff_sec = int((record.check_out - record.check_in).total_seconds())
        record.duty_seconds = max(0, diff_sec)
        record.duty_hours = format_seconds(record.duty_seconds)
    elif record.status == 'Present' and (not record.duty_seconds or record.duty_seconds == 0):
        record.duty_seconds = 32400
        record.duty_hours = '9h 00m'
        
    db.session.commit()
    
    return jsonify({
        'success': True,
        'record': {
            'id': record.id,
            'employee_name': record.employee.name if record.employee else '',
            'date': record.date_formatted or record.date,
            'check_in': record.check_in.strftime('%I:%M %p') if record.check_in else '--:--',
            'check_out': record.check_out.strftime('%I:%M %p') if record.check_out else '--:--',
            'duty_hours': record.duty_hours,
            'status': record.status,
            'remarks': record.remarks
        }
    })

@app.route('/hr/leave')
def hr_leave():
    all_employees = Employee.query.all()
    return render_template('hr_leave.html', all_employees=all_employees)

@app.route('/hr/directory')
def hr_directory():
    return render_template('Hr_employee_directory.html')

@app.route('/hr/employee-profile')
def hr_employee_profile():
    emp_id = request.args.get('id')
    emp_code = request.args.get('emp_code')
    if emp_id:
        emp = Employee.query.get(emp_id)
    elif emp_code:
        emp = Employee.query.filter_by(emp_code=emp_code).first()
    else:
        emp = Employee.query.filter_by(emp_code='EMP-101').first()
    return render_template('hr_employee_profile.html', employee=emp)

@app.route('/hr/reports')
def hr_reports():
    return render_template('hr_report.html')

@app.route('/hr/add-employee', methods=['GET', 'POST'])
def hr_add_employee():
    if request.method == 'POST':
        return redirect(url_for('hr_directory'))
    return render_template('Hr_add_employee.html')

@app.route('/hr/profile', methods=['GET', 'POST'])
def hr_profile():
    if request.method == 'POST':
        return redirect(url_for('hr_profile'))
    return render_template('hr_profile.html', portal='hr')

@app.route('/hr/settings', methods=['GET', 'POST'])
def hr_settings():
    if request.method == 'POST':
        return redirect(url_for('hr_profile'))
    return render_template('hr_profile.html', portal='hr')

# ─── Employee Portal Routes ───────────────────────────────────────────────────
@app.route('/employee/dashboard')
def employee_dashboard():
    emp = Employee.query.filter_by(emp_code='EMP-101').first()
    today_str = datetime.now().strftime('%Y-%m-%d')
    today_record = Attendance.query.filter_by(employee_id=emp.id, date=today_str).first() if emp else None
    
    is_checked_in = False
    today_duty_seconds = 0
    today_duty_hours = "--"
    
    if today_record:
        if today_record.check_out is None and today_record.check_in:
            is_checked_in = True
            today_duty_seconds = int((datetime.now() - today_record.check_in).total_seconds())
        else:
            today_duty_seconds = today_record.duty_seconds
        
        today_duty_hours = format_seconds(today_duty_seconds)
    
    recent_records = Attendance.query.filter_by(employee_id=emp.id).order_by(Attendance.id.desc()).limit(5).all() if emp else []
    
    return render_template(
        'employee_dashboard.html',
        employee=emp,
        today_record=today_record,
        is_checked_in=is_checked_in,
        today_duty_seconds=today_duty_seconds,
        today_duty_hours=today_duty_hours,
        recent_records=recent_records
    )

@app.route('/employee/attendance')
def employee_attendance():
    emp = Employee.query.filter_by(emp_code='EMP-101').first()
    records = Attendance.query.filter_by(employee_id=emp.id).order_by(Attendance.id.desc()).all() if emp else []
    
    total_seconds = sum(r.duty_seconds for r in records)
    total_hours_formatted = format_seconds(total_seconds)
    
    days_present = sum(1 for r in records if r.status in ['Present', 'Checked In'])
    days_absent = sum(1 for r in records if r.status == 'Absent')
    days_leave = sum(1 for r in records if r.status in ['Leave', 'Holiday'])
    late_count = sum(1 for r in records if r.status == 'Late')
    total_working_days = len(records)
    
    return render_template(
        'employee_attendence.html',
        employee=emp,
        records=records,
        total_hours_formatted=total_hours_formatted,
        days_present=days_present,
        days_absent=days_absent,
        days_leave=days_leave,
        late_count=late_count,
        total_working_days=total_working_days
    )

@app.route('/employee/leave')
def employee_leave():
    emp = Employee.query.filter_by(emp_code='EMP-101').first()
    return render_template('employee_leave.html', employee=emp)

@app.route('/employee/profile', methods=['GET', 'POST'])
def employee_profile():
    emp = Employee.query.filter_by(emp_code='EMP-101').first()
    if request.method == 'POST':
        first_name = request.form.get('firstName', '').strip()
        last_name = request.form.get('lastName', '').strip()
        phone = request.form.get('phone', '').strip()
        if emp:
            full_name = f"{first_name} {last_name}".strip()
            if full_name:
                emp.name = full_name
            if phone:
                emp.phone = phone
            db.session.commit()
        return redirect(url_for('employee_profile'))
    return render_template('profile.html', portal='employee', employee=emp)

# ─── Run ──────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True, port=5000)
