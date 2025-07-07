from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config.config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
from datetime import datetime, timedelta
from utils.helpers import calculate_total_hours, safe_close
from utils.session_manager import get_session
from models.employee import Employee
from models.timesheet import Timesheet
from models.dailylogs import DailyLog
from models.dailylogschanges import DailyLogChange

# Import employee handlers
from handlers.employee.employees import (
    create_employee,
    get_employees,
    # get_employee_by_email,
    update_employee_by_email,
    delete_employee_by_email,
    #  get_manager_hierarchy_by_email,
    get_subordinates,
    get_employees_without_manager,
    get_employee_tree,
    get_employee_dashboard,
)

# Import timesheet handlers
from handlers.timesheet.timesheet import (
    create_timesheet,
    get_timesheets,
    get_timesheet,
    get_timesheets_by_employee_name,
    get_timesheet_by_employee_name_and_week,
    update_timesheet_by_employee_name_and_week,
    delete_timesheet_by_employee_name_and_week,
    get_timesheets_by_week
)

# Import daily logs handlers
from handlers.dailylogs.dailylogs import (
    create_daily_log,
    get_daily_logs,
    get_daily_log,
    update_daily_log,
    delete_daily_log,
    get_daily_logs_by_timesheet
)

# Import daily log changes handlers
from handlers.dailylogschanges.dailylogschanges import (
    add_log_change,
    get_all_log_changes,
    get_log_change,
    update_log_change,
    delete_log_change,
    get_log_changes
)

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
db = SQLAlchemy(app)

# ---------------- Employee Routes ----------------
@app.route("/api/employees", methods=["POST"])
def add_employee():
    return create_employee()

@app.route("/api/employees", methods=["GET"])
def list_employees():
    return get_employees()

# @app.route("/api/employees/by-email", methods=["GET"])
# def get_employee_by_email_route():
#     return get_employee_by_email()

@app.route("/api/employees/update-by-email", methods=["PUT"])
def update_employee_by_email_route():
    return update_employee_by_email()

@app.route("/api/employees/delete-by-email", methods=["DELETE"])
def delete_employee_by_email_route():
    return delete_employee_by_email()

# @app.route("/api/employees/manager-hierarchy-by-email", methods=["GET"])
# def get_manager_hierarchy_by_email_route():
#     return get_manager_hierarchy_by_email()

@app.route("/api/employees/<int:manager_id>/subordinates", methods=["GET"])
def list_subordinates(manager_id):
    return get_subordinates(manager_id)

@app.route("/api/employees/without-manager", methods=["GET"])
def list_employees_without_manager():
    return get_employees_without_manager()

@app.route("/api/employees/<int:employee_id>/tree", methods=["GET"])
def employee_tree(employee_id):
    return get_employee_tree(employee_id)

@app.route("/api/employees/dashboard", methods=["GET"])
def employee_dashboard():
    return get_employee_dashboard()

# @app.route("/api/employees/manager-hierarchy-by-email", methods=["GET"])
# def get_manager_hierarchy_by_email():
#     email = request.args.get('email')
#     session = get_session()
#     try:
#         emp = session.query(Employee).filter(Employee.email.ilike(email)).first()
#         if not emp:
#             return jsonify({'error': 'Employee not found.'}), 404
#         hierarchy = []
#         current = emp
#         while current.reports_to:
#             manager = session.query(Employee).get(current.reports_to)
#             if not manager:
#                 break
#             hierarchy.append({
#                 'id': manager.id,
#                 'employee_name': manager.employee_name,
#                 'email': manager.email,
#                 'reports_to': manager.reports_to
#             })
#             current = manager
#         return jsonify(hierarchy), 200
#     finally:
#         safe_close(session)

# @app.route("/api/employees/by-email", methods=["GET"])
# def get_employee_by_email():
#     email = request.args.get('email')
#     session = get_session()
#     try:
#         emp = session.query(Employee).filter(Employee.email.ilike(email)).first()
#         if not emp:
#             return jsonify({'error': 'Employee not found.'}), 404
#         return jsonify(emp.as_dict()), 200
#     finally:
#         safe_close(session)


@app.route("/api/employees/profile-with-hierarchy", methods=["GET"])
def get_employee_profile_with_hierarchy():
    email = request.args.get('email')
    session = get_session()
    try:
        emp = session.query(Employee).filter(Employee.email.ilike(email)).first()
        if not emp:
            return jsonify({'error': 'Employee not found.'}), 404

        # Build manager hierarchy
        hierarchy = []
        current = emp
        while current.reports_to:
            manager = session.query(Employee).get(current.reports_to)
            if not manager:
                break
            hierarchy.append({
                'id': manager.id,
                'employee_name': manager.employee_name,
                'email': manager.email,
                'reports_to': manager.reports_to
            })
            current = manager

        return jsonify({
            'employee': emp.as_dict(),
            'manager_hierarchy': hierarchy
        }), 200
    finally:
        safe_close(session)

        
# ---------------- Timesheet Routes ----------------
@app.route("/api/timesheets", methods=["POST"])
def add_timesheet():
    return create_timesheet()

@app.route("/api/timesheets", methods=["GET"])
def list_timesheets():
    return get_timesheets()

@app.route("/api/timesheets/<int:ts_id>", methods=["GET"])
def get_timesheet_by_id(ts_id):
    return get_timesheet(ts_id)

@app.route("/api/timesheets/by-employee-name", methods=["GET"])
def timesheets_by_employee_name():
    return get_timesheets_by_employee_name()

@app.route("/api/timesheets/by-employee-name-week", methods=["GET"])
def timesheet_by_employee_name_and_week():
    return get_timesheet_by_employee_name_and_week()

@app.route("/api/timesheets/by-employee-name-week", methods=["PUT"])
def update_timesheet_by_employee_name_and_week_route():
    return update_timesheet_by_employee_name_and_week()

@app.route("/api/timesheets/by-employee-name-week", methods=["DELETE"])
def delete_timesheet_by_employee_name_and_week_route():
    return delete_timesheet_by_employee_name_and_week()

@app.route("/api/timesheets-by-week", methods=["GET"])
def timesheets_by_week():
    return get_timesheets_by_week()

# ---------------- Daily Log Routes ----------------
@app.route("/api/daily-logs", methods=["POST"])
def add_daily_log():
    return create_daily_log()

@app.route("/api/daily-logs", methods=["GET"])
def list_daily_logs():
    return get_daily_logs()

@app.route("/api/daily-logs/<int:log_id>", methods=["GET"])
def get_daily_log_by_id(log_id):
    return get_daily_log(log_id)

@app.route("/api/daily-logs/<int:log_id>", methods=["PUT"])
def update_daily_log_by_id(log_id):
    return update_daily_log(log_id)

@app.route("/api/daily-logs/<int:log_id>", methods=["DELETE"])
def delete_daily_log_by_id(log_id):
    return delete_daily_log(log_id)

@app.route("/api/timesheets/<int:timesheet_id>/daily-logs", methods=["GET"])
def logs_by_timesheet(timesheet_id):
    return get_daily_logs_by_timesheet(timesheet_id)

# ---------------- Daily Log Change Routes ----------------
@app.route("/api/daily-log-changes", methods=["POST"])
def add_description_change():
    return add_log_change()

@app.route("/api/daily-log-changes", methods=["GET"])
def list_log_changes():
    return get_all_log_changes()

@app.route("/api/daily-log-changes/<int:change_id>", methods=["GET"])
def get_log_change_by_id(change_id):
    return get_log_change(change_id)

@app.route("/api/daily-log-changes/<int:change_id>", methods=["PUT"])
def update_log_change_by_id(change_id):
    return update_log_change(change_id)

@app.route("/api/daily-log-changes/<int:change_id>", methods=["DELETE"])
def delete_log_change_by_id(change_id):
    return delete_log_change(change_id)

@app.route("/api/daily-logs/<int:daily_log_id>/changes", methods=["GET"])
def view_log_changes(daily_log_id):
    return get_log_changes(daily_log_id)

@app.route("/api/daily-logs/save", methods=["POST"])
def save_daily_logs():
    session = get_session()
    try:
        logs = request.get_json()
        if not logs:
            return jsonify({'error': 'No logs provided.'}), 400

        for log_data in logs:
            log_id = log_data.get('id')
            if isinstance(log_id, str) and log_id.startswith('temp-'):
                # Create new log
                timesheet = session.query(Timesheet).filter_by(
                    employee_id=log_data.get('employee_id'),
                    week_starting=datetime.strptime(log_data.get('week_starting'), '%Y-%m-%d').date()
                ).first()
                if not timesheet:
                    return jsonify({'error': f'Timesheet not found for employee_id {log_data.get("employee_id")} and week {log_data.get("week_starting")}'}), 404

                new_log = DailyLog(
                    timesheet_id=timesheet.id,
                    date=datetime.strptime(log_data.get('date'), '%Y-%m-%d').date(),
                    time_in_am=log_data.get('time_in_am'),
                    time_out_am=log_data.get('time_out_am'),
                    time_in_pm=log_data.get('time_in_pm'),
                    time_out_pm=log_data.get('time_out_pm'),
                    description=log_data.get('description'),
                    total_hours=calculate_total_hours(
                        log_data.get('time_in_am'),
                        log_data.get('time_out_am'),
                        log_data.get('time_in_pm'),
                        log_data.get('time_out_pm')
                    )
                )
                session.add(new_log)
            else:
                # Update existing log
                log = session.query(DailyLog).get(log_id)
                if not log:
                    return jsonify({'error': f'Daily log with id {log_id} not found.'}), 404

                log.time_in_am = log_data.get('time_in_am') or log.time_in_am
                log.time_out_am = log_data.get('time_out_am') or log.time_out_am
                log.time_in_pm = log_data.get('time_in_pm') or log.time_in_pm
                log.time_out_pm = log_data.get('time_out_pm') or log.time_out_pm
                log.description = log_data.get('description') or log.description
                log.total_hours = calculate_total_hours(
                    log_data.get('time_in_am'),
                    log_data.get('time_out_am'),
                    log_data.get('time_in_pm'),
                    log_data.get('time_out_pm')
                )

        session.commit()
        return jsonify({'message': 'Logs saved successfully.'}), 200
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        safe_close(session)

# ---------------- Run App ----------------
if __name__ == '__main__':
    app.run(debug=True)