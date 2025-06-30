from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config.config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS

from handlers.employee.employees import (
    create_employee,
    get_employees,
    get_employee,
    update_employee,
    delete_employee,
    get_subordinates,
    get_employees_without_manager
)
from handlers.timesheet.timesheet import (
    create_timesheet,
    get_timesheets,
    get_timesheet,
    update_timesheet,
    delete_timesheet,
    get_timesheets_by_employee,
    get_timesheets_by_week
)
from handlers.dailylogs.dailylogs import (
    create_daily_log,
    get_daily_logs,
    get_daily_log,
    update_daily_log,
    delete_daily_log,
    get_daily_logs_by_timesheet
)
from handlers.dailylogschanges.dailylogschanges import (
    add_log_change,
    get_all_log_changes,
    get_log_change,
    update_log_change,
    delete_log_change,
    get_log_changes
)

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS

db = SQLAlchemy(app)

# Employee Endpoints
@app.route("/api/employees", methods=["POST"])
def add_employee(): return create_employee()

@app.route("/api/employees", methods=["GET"])
def list_employees(): return get_employees()

@app.route("/api/employees/<int:employee_id>", methods=["GET"])
def retrieve_employee(employee_id): return get_employee(employee_id)

@app.route("/api/employees/<int:employee_id>", methods=["PUT"])
def modify_employee(employee_id): return update_employee(employee_id)

@app.route("/api/employees/<int:employee_id>", methods=["DELETE"])
def remove_employee(employee_id): return delete_employee(employee_id)

@app.route("/api/employees/<int:manager_id>/subordinates", methods=["GET"])
def list_subordinates(manager_id): return get_subordinates(manager_id)

@app.route("/api/employees/without-manager", methods=["GET"])
def list_employees_without_manager(): return get_employees_without_manager()

# Timesheet Endpoints
@app.route("/api/timesheets", methods=["POST"])
def add_timesheet(): return create_timesheet()

@app.route("/api/timesheets", methods=["GET"])
def list_timesheets(): return get_timesheets()

@app.route("/api/timesheets/<int:ts_id>", methods=["GET"])
def get_timesheet_by_id(ts_id): return get_timesheet(ts_id)

@app.route("/api/timesheets/<int:ts_id>", methods=["PUT"])
def update_timesheet_by_id(ts_id): return update_timesheet(ts_id)

@app.route("/api/timesheets/<int:ts_id>", methods=["DELETE"])
def delete_timesheet_by_id(ts_id): return delete_timesheet(ts_id)

@app.route("/api/employees/<int:employee_id>/timesheets", methods=["GET"])
def timesheets_by_employee(employee_id): return get_timesheets_by_employee(employee_id)

@app.route("/api/timesheets-by-week", methods=["GET"])
def timesheets_by_week(): return get_timesheets_by_week()

# Daily Log Endpoints
@app.route("/api/daily-logs", methods=["POST"])
def add_daily_log(): return create_daily_log()

@app.route("/api/daily-logs", methods=["GET"])
def list_daily_logs(): return get_daily_logs()

@app.route("/api/daily-logs/<int:log_id>", methods=["GET"])
def get_daily_log_by_id(log_id): return get_daily_log(log_id)

@app.route("/api/daily-logs/<int:log_id>", methods=["PUT"])
def update_daily_log_by_id(log_id): return update_daily_log(log_id)

@app.route("/api/daily-logs/<int:log_id>", methods=["DELETE"])
def delete_daily_log_by_id(log_id): return delete_daily_log(log_id)

@app.route("/api/timesheets/<int:timesheet_id>/daily-logs", methods=["GET"])
def logs_by_timesheet(timesheet_id): return get_daily_logs_by_timesheet(timesheet_id)

# Daily Log Change Endpoints
@app.route("/api/daily-log-changes", methods=["POST"])
def add_description_change(): return add_log_change()

@app.route("/api/daily-log-changes", methods=["GET"])
def list_log_changes(): return get_all_log_changes()

@app.route("/api/daily-log-changes/<int:change_id>", methods=["GET"])
def get_log_change_by_id(change_id): return get_log_change(change_id)

@app.route("/api/daily-log-changes/<int:change_id>", methods=["PUT"])
def update_log_change_by_id(change_id): return update_log_change(change_id)

@app.route("/api/daily-log-changes/<int:change_id>", methods=["DELETE"])
def delete_log_change_by_id(change_id): return delete_log_change(change_id)

@app.route("/api/daily-logs/<int:daily_log_id>/changes", methods=["GET"])
def view_log_changes(daily_log_id): return get_log_changes(daily_log_id)

if __name__ == '__main__':
    app.run(debug=True)