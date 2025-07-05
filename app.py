from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config.config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
from datetime import datetime, timedelta
from models.employee import Employee
from models.timesheet import Timesheet
from models.dailylogs import DailyLog
from models.dailylogschanges import DailyLogChange

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
db = SQLAlchemy(app)

# --- Employee APIs ---
@app.route("/api/employees/by-email", methods=["GET"])
def get_employee_by_email():
    email = request.args.get('email')
    emp = Employee.query.filter_by(email=email).first()
    if not emp:
        return jsonify({'error': 'Employee not found.'}), 404
    return jsonify(emp.as_dict()), 200

# --- Timesheet APIs ---
@app.route("/api/timesheets", methods=["POST"])
def create_timesheet():
    data = request.get_json()
    employee_name = data.get("employee_name")
    week_starting = data.get("week_starting")
    if not employee_name or not week_starting:
        return jsonify({"error": "employee_name and week_starting are required"}), 400
    employee = Employee.query.filter(Employee.employee_name.ilike(employee_name)).first()
    if not employee:
        return jsonify({"error": "Employee not found"}), 404
    try:
        week_starting_date = datetime.strptime(week_starting, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"error": "Invalid week_starting format. Use YYYY-MM-DD."}), 400
    # Check if already exists
    ts = Timesheet.query.filter_by(employee_id=employee.id, week_starting=week_starting_date).first()
    if ts:
        return jsonify(ts.as_dict()), 200
    new_ts = Timesheet(employee_id=employee.id, week_starting=week_starting_date)
    db.session.add(new_ts)
    db.session.commit()
    return jsonify(new_ts.as_dict()), 201

@app.route("/api/timesheets/by-employee-name-week", methods=["GET"])
def get_timesheet_by_employee_name_and_week():
    employee_name = request.args.get("employee_name")
    week_starting = request.args.get("week_starting")
    if not employee_name or not week_starting:
        return jsonify({"error": "employee_name and week_starting query params required"}), 400
    employee = Employee.query.filter(Employee.employee_name.ilike(employee_name)).first()
    if not employee:
        return jsonify({"error": "Employee not found"}), 404
    try:
        week_starting_date = datetime.strptime(week_starting, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"error": "Invalid week_starting format. Use YYYY-MM-DD."}), 400
    ts = Timesheet.query.filter_by(employee_id=employee.id, week_starting=week_starting_date).first()
    if not ts:
        return jsonify({"error": "Timesheet not found"}), 404
    return jsonify(ts.as_dict()), 200

# --- Daily Log APIs ---
@app.route("/api/daily-logs", methods=["POST"])
def create_daily_log():
    data = request.get_json()
    timesheet_id = data.get('timesheet_id')
    log_date = data.get('log_date')
    if not timesheet_id or not log_date:
        return jsonify({'error': 'timesheet_id and log_date are required'}), 400
    try:
        log_date_obj = datetime.strptime(log_date, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({'error': 'Invalid log_date format. Use YYYY-MM-DD.'}), 400
    log = DailyLog(
        timesheet_id=timesheet_id,
        log_date=log_date_obj,
        day_of_week=data.get('day_of_week'),
        morning_in=data.get('morning_in'),
        morning_out=data.get('morning_out'),
        afternoon_in=data.get('afternoon_in'),
        afternoon_out=data.get('afternoon_out'),
        total_hours=data.get('total_hours'),
        description=data.get('description')
    )
    db.session.add(log)
    db.session.commit()
    return jsonify(log.as_dict()), 201

@app.route("/api/daily-logs/<int:log_id>", methods=["PUT"])
def update_daily_log(log_id):
    log = DailyLog.query.get(log_id)
    if not log:
        return jsonify({'error': 'Daily log not found'}), 404
    data = request.get_json()
    for field in ['morning_in', 'morning_out', 'afternoon_in', 'afternoon_out', 'description']:
        if field in data:
            setattr(log, field, data[field])
    db.session.commit()
    return jsonify(log.as_dict()), 200

@app.route("/api/daily-logs/<int:log_id>/changes", methods=["GET"])
def get_log_changes(log_id):
    changes = DailyLogChange.query.filter_by(daily_log_id=log_id).all()
    return jsonify([c.as_dict() for c in changes]), 200

@app.route("/api/daily-log-changes", methods=["POST"])
def add_log_change():
    data = request.get_json()
    daily_log_id = data.get("daily_log_id")
    new_description = data.get("new_description")
    if not daily_log_id or not new_description:
        return jsonify({"error": "daily_log_id and new_description are required"}), 400
    change = DailyLogChange(daily_log_id=daily_log_id, new_description=new_description)
    db.session.add(change)
    db.session.commit()
    return jsonify(change.as_dict()), 201

# --- Dashboard API ---
@app.route("/api/employees/dashboard", methods=["GET"])
def employee_dashboard():
    email = request.args.get('email')
    week_starting = request.args.get('week_starting')  # MM/DD/YYYY
    emp = Employee.query.filter_by(email=email).first()
    if not emp:
        return jsonify({'error': 'Employee not found.'}), 404
    # Manager hierarchy
    hierarchy = []
    current = emp
    while current.reports_to:
        manager = Employee.query.get(current.reports_to)
        if not manager:
            break
        hierarchy.append({
            'id': manager.id,
            'employee_name': manager.employee_name,
            'email': manager.email,
            'reports_to': manager.reports_to
        })
        current = manager
    # Parse week_starting
    timesheets_data = []
    daily_logs_data = []
    if week_starting:
        try:
            week_start = datetime.strptime(week_starting, '%m/%d/%Y')
            week_end = week_start + timedelta(days=6)
            timesheets = Timesheet.query.filter(
                Timesheet.employee_id == emp.id,
                Timesheet.week_starting >= week_start,
                Timesheet.week_starting <= week_end
            ).all()
            timesheet_ids = [ts.id for ts in timesheets]
            timesheets_data = [ts.as_dict() for ts in timesheets]
            if timesheet_ids:
                logs = DailyLog.query.filter(DailyLog.timesheet_id.in_(timesheet_ids)).all()
                daily_logs_data = [log.as_dict() for log in logs]
        except ValueError:
            return jsonify({'error': 'Invalid week_starting format. Use MM/DD/YYYY.'}), 400
    return jsonify({
        'employee': emp.as_dict(),
        'manager_hierarchy': hierarchy,
        'timesheets': timesheets_data,
        'daily_logs': daily_logs_data
    }), 200

@app.route("/api/employees/by-email", methods=["GET"])
def get_employee_by_email():
    email = request.args.get('email')
    emp = Employee.query.filter(Employee.email.ilike(email)).first()  # <-- use ilike here
    if not emp:
        return jsonify({'error': 'Employee not found.'}), 404
    return jsonify(emp.as_dict()), 200

if __name__ == '__main__':
    app.run(debug=True)