from flask import request, jsonify
from models.employee import Employee
from utils.session_manager import get_session
from utils.helpers import is_valid_email

# ✅ Create Employee - POST /employees
def create_employee():
    session = get_session()
    try:
        data = request.get_json()
        name = data.get('employee_name')
        email = data.get('email')
        manager_id = data.get('manager_id')

        if not name or not email:
            return jsonify({'error': 'employee_name and email are required.'}), 400  # 🔴 Bad Request

        if not is_valid_email(email):
            return jsonify({'error': 'Invalid email format.'}), 422  # 🔴 Unprocessable Entity

        new_employee = Employee(employee_name=name, email=email, manager_id=manager_id)
        session.add(new_employee)
        session.commit()

        return jsonify({
            'id': new_employee.id,
            'employee_name': new_employee.employee_name,
            'email': new_employee.email,
            'manager_id': new_employee.manager_id
        }), 201  # ✅ Created
    finally:
        session.close()

# ✅ Get All Employees - GET /employees
def get_employees():
    session = get_session()
    try:
        employees = session.query(Employee).all()
        return jsonify([
            {
                'id': emp.id,
                'employee_name': emp.employee_name,
                'email': emp.email,
                'manager_id': emp.manager_id
            } for emp in employees
        ]), 200  # ✅ OK
    finally:
        session.close()

# ✅ Get Employee by ID - GET /employees/<id>
def get_employee(employee_id):
    session = get_session()
    try:
        emp = session.query(Employee).get(employee_id)
        if not emp:
            return jsonify({'error': 'Employee not found.'}), 404  # 🔴 Not Found
        return jsonify({
            'id': emp.id,
            'employee_name': emp.employee_name,
            'email': emp.email,
            'manager_id': emp.manager_id
        }), 200  # ✅ OK
    finally:
        session.close()

# ✅ Update Employee - PUT /employees/<id>
def update_employee(employee_id):
    session = get_session()
    try:
        emp = session.query(Employee).get(employee_id)
        if not emp:
            return jsonify({'error': 'Employee not found.'}), 404  # 🔴 Not Found

        data = request.get_json()
        new_email = data.get('email', emp.email)
        if new_email and not is_valid_email(new_email):
            return jsonify({'error': 'Invalid email format.'}), 422  # 🔴 Unprocessable Entity

        emp.employee_name = data.get('employee_name', emp.employee_name)
        emp.email = new_email
        emp.manager_id = data.get('manager_id', emp.manager_id)
        session.commit()
        return jsonify({
            'id': emp.id,
            'employee_name': emp.employee_name,
            'email': emp.email,
            'manager_id': emp.manager_id
        }), 200  # ✅ OK
    finally:
        session.close()

# ✅ Delete Employee - DELETE /employees/<id>
def delete_employee(employee_id):
    session = get_session()
    try:
        emp = session.query(Employee).get(employee_id)
        if not emp:
            return jsonify({'error': 'Employee not found.'}), 404  # 🔴 Not Found
        session.delete(emp)
        session.commit()
        return jsonify({'message': 'Employee deleted successfully.'}), 200  # ✅ OK
    finally:
        session.close()

# ✅ Get Subordinates - GET /employees/<manager_id>/subordinates
def get_subordinates(manager_id):
    session = get_session()
    try:
        manager = session.query(Employee).get(manager_id)
        if not manager:
            return jsonify({'error': 'Manager not found.'}), 404  # 🔴 Not Found

        subordinates = manager.subordinates
        return jsonify([
            {
                'id': sub.id,
                'employee_name': sub.employee_name,
                'email': sub.email,
                'manager_id': sub.manager_id
            } for sub in subordinates
        ]), 200  # ✅ OK
    finally:
        session.close()
# Note: The above functions assume that the Flask app and SQLAlchemy session management are properly set up.