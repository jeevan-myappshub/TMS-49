from flask import request, jsonify
from models.timesheet import Timesheet
from models.employee import Employee
from utils.session_manager import get_session

# Create a timesheet - POST /timesheets
def create_timesheet():
    session = get_session()
    try:
        data = request.get_json()
        employee_id = data.get("employee_id")
        week_starting = data.get("week_starting")  # Expecting format: YYYY-MM-DD

        if not employee_id or not week_starting:
            return jsonify({"error": "employee_id and week_starting are required"}), 400

        # Optionally: check if employee exists
        employee = session.query(Employee).get(employee_id)
        if not employee:
            return jsonify({"error": "Employee not found"}), 404

        new_ts = Timesheet(employee_id=employee_id, week_starting=week_starting)
        session.add(new_ts)
        session.commit()

        return jsonify(new_ts.as_dict()), 201
    finally:
        session.close()

# Get all timesheets - GET /timesheets
def get_timesheets():
    session = get_session()
    try:
        timesheets = session.query(Timesheet).all()
        return jsonify([ts.as_dict() for ts in timesheets]), 200
    finally:
        session.close()

# Get timesheet by ID - GET /timesheets/<id>
def get_timesheet(ts_id):
    session = get_session()
    try:
        ts = session.query(Timesheet).get(ts_id)
        if not ts:
            return jsonify({"error": "Timesheet not found"}), 404
        return jsonify(ts.as_dict()), 200
    finally:
        session.close()

# Update timesheet - PUT /timesheets/<id>
def update_timesheet(ts_id):
    session = get_session()
    try:
        ts = session.query(Timesheet).get(ts_id)
        if not ts:
            return jsonify({"error": "Timesheet not found"}), 404

        data = request.get_json()
        employee_id = data.get("employee_id", ts.employee_id)
        week_starting = data.get("week_starting", ts.week_starting)

        # Optionally: check if employee exists
        if employee_id != ts.employee_id:
            employee = session.query(Employee).get(employee_id)
            if not employee:
                return jsonify({"error": "Employee not found"}), 404

        ts.employee_id = employee_id
        ts.week_starting = week_starting
        session.commit()
        return jsonify(ts.as_dict()), 200
    finally:
        session.close()

# Delete timesheet - DELETE /timesheets/<id>
def delete_timesheet(ts_id):
    session = get_session()
    try:
        ts = session.query(Timesheet).get(ts_id)
        if not ts:
            return jsonify({"error": "Timesheet not found"}), 404
        session.delete(ts)
        session.commit()
        return jsonify({"message": "Timesheet deleted successfully."}), 200
    finally:
        session.close()

# Custom: Get timesheets by employee - GET /employees/<employee_id>/timesheets
def get_timesheets_by_employee(employee_id):
    session = get_session()
    try:
        timesheets = session.query(Timesheet).filter_by(employee_id=employee_id).all()
        return jsonify([ts.as_dict() for ts in timesheets]), 200
    finally:
        session.close()

# Custom: Get timesheets by week - GET /timesheets?week_starting=YYYY-MM-DD
def get_timesheets_by_week():
    session = get_session()
    try:
        week_starting = request.args.get("week_starting")
        if not week_starting:
            return jsonify({"error": "week_starting query param required"}), 400
        timesheets = session.query(Timesheet).filter_by(week_starting=week_starting).all()
        return jsonify([ts.as_dict() for ts in timesheets]), 200
    finally:
        session.close()