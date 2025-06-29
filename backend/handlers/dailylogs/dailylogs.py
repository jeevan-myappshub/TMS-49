from flask import request, jsonify
from datetime import datetime
from models.dailylogs import DailyLog
from utils.session_manager import get_session
from utils.helpers import calculate_total_hours, format_timedelta_to_time, get_day_of_week

# Create daily log - POST /dailylogs
def create_daily_log():
    session = get_session()
    try:
        data = request.get_json()
        required_fields = ['timesheet_id', 'log_date']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400

        log_date = datetime.strptime(data['log_date'], "%Y-%m-%d").date()
        day_of_week = get_day_of_week(log_date)

        morning_in = data.get('morning_in')
        morning_out = data.get('morning_out')
        afternoon_in = data.get('afternoon_in')
        afternoon_out = data.get('afternoon_out')

        fmt = "%H:%M"
        morning_in = datetime.strptime(morning_in, fmt).time() if morning_in else None
        morning_out = datetime.strptime(morning_out, fmt).time() if morning_out else None
        afternoon_in = datetime.strptime(afternoon_in, fmt).time() if afternoon_in else None
        afternoon_out = datetime.strptime(afternoon_out, fmt).time() if afternoon_out else None

        total_td = calculate_total_hours(morning_in, morning_out, afternoon_in, afternoon_out)
        total_time_str = format_timedelta_to_time(total_td)

        log = DailyLog(
            timesheet_id=data['timesheet_id'],
            log_date=log_date,
            day_of_week=day_of_week,
            morning_in=morning_in,
            morning_out=morning_out,
            afternoon_in=afternoon_in,
            afternoon_out=afternoon_out,
            total_hours=total_time_str,
            descreption=data.get('descreption')
        )
        session.add(log)
        session.commit()
        return jsonify(log.as_dict()), 201
    finally:
        session.close()

# Get all daily logs - GET /dailylogs
def get_daily_logs():
    session = get_session()
    try:
        logs = session.query(DailyLog).all()
        return jsonify([log.as_dict() for log in logs]), 200
    finally:
        session.close()

# Get daily log by ID - GET /dailylogs/<id>
def get_daily_log(log_id):
    session = get_session()
    try:
        log = session.query(DailyLog).get(log_id)
        if not log:
            return jsonify({'error': 'Daily log not found'}), 404
        return jsonify(log.as_dict()), 200
    finally:
        session.close()

# Update daily log - PUT /dailylogs/<id>
def update_daily_log(log_id):
    session = get_session()
    try:
        log = session.query(DailyLog).get(log_id)
        if not log:
            return jsonify({'error': 'Daily log not found'}), 404

        data = request.get_json()
        if 'log_date' in data:
            log.log_date = datetime.strptime(data['log_date'], "%Y-%m-%d").date()
            log.day_of_week = get_day_of_week(log.log_date)

        fmt = "%H:%M"
        if 'morning_in' in data:
            log.morning_in = datetime.strptime(data['morning_in'], fmt).time() if data['morning_in'] else None
        if 'morning_out' in data:
            log.morning_out = datetime.strptime(data['morning_out'], fmt).time() if data['morning_out'] else None
        if 'afternoon_in' in data:
            log.afternoon_in = datetime.strptime(data['afternoon_in'], fmt).time() if data['afternoon_in'] else None
        if 'afternoon_out' in data:
            log.afternoon_out = datetime.strptime(data['afternoon_out'], fmt).time() if data['afternoon_out'] else None

        # Recalculate total hours
        total_td = calculate_total_hours(log.morning_in, log.morning_out, log.afternoon_in, log.afternoon_out)
        log.total_hours = format_timedelta_to_time(total_td)

        if 'descreption' in data:
            log.descreption = data['descreption']

        session.commit()
        return jsonify(log.as_dict()), 200
    finally:
        session.close()

# Delete daily log - DELETE /dailylogs/<id>
def delete_daily_log(log_id):
    session = get_session()
    try:
        log = session.query(DailyLog).get(log_id)
        if not log:
            return jsonify({'error': 'Daily log not found'}), 404
        session.delete(log)
        session.commit()
        return jsonify({'message': 'Daily log deleted successfully.'}), 200
    finally:
        session.close()

# Get daily logs by timesheet - GET /timesheets/<timesheet_id>/dailylogs
def get_daily_logs_by_timesheet(timesheet_id):
    session = get_session()
    try:
        logs = session.query(DailyLog).filter_by(timesheet_id=timesheet_id).all()
        return jsonify([log.as_dict() for log in logs]), 200
    finally:
        session.close()