from flask import request, jsonify
from models.employee import Employee
from utils.session_manager import get_session
from utils.helpers import is_valid_email

# Create employee
def create_employee():
    session = get_session()
    try:
        data = request.get_json()
        name = data.get('employee_name')
        email = data.get('email')
        reports_to = data.get('reports_to')
        manager_name = data.get('manager_name')

        if not name or not email:
            return jsonify({'error': 'employee_name and email are required.'}), 400
        if not is_valid_email(email):
            return jsonify({'error': 'invalid email format'}), 422

        manager_id = None
        if manager_name:
            manager = session.query(Employee).filter_by(employee_name=manager_name).first()
            if not manager:
                return jsonify({'error': 'Manager not found.'}), 404
            manager_id = manager.id
        elif reports_to:
            if str(reports_to).lower() == 'self':
                return jsonify({'error': 'Employee cannot report to themselves.'}), 400
            manager = session.query(Employee).get(reports_to)
            if not manager:
                return jsonify({'error': 'Manager not found.'}), 404
            manager_id = manager.id

        new_employee = Employee(employee_name=name, email=email, reports_to=manager_id)
        session.add(new_employee)
        session.commit()
        return jsonify({
            'id': new_employee.id,
            'employee_name': new_employee.employee_name,
            'email': new_employee.email,
            'reports_to': new_employee.reports_to
        }), 201
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

# Get all employees
def get_employees():
    session = get_session()
    try:
        employees = session.query(Employee).all()
        return jsonify([
            {
                'id': emp.id,
                'employee_name': emp.employee_name,
                'email': emp.email,
                'reports_to': emp.reports_to
            } for emp in employees
        ]), 200
    finally:
        session.close()

# Get single employee
def get_employee(employee_id):
    session = get_session()
    try:
        emp = session.query(Employee).get(employee_id)
        if not emp:
            return jsonify({'error': 'Employee not found.'}), 404
        return jsonify({
            'id': emp.id,
            'employee_name': emp.employee_name,
            'email': emp.email,
            'reports_to': emp.reports_to
        }), 200
    finally:
        session.close()

# Update employee
def update_employee(employee_id):
    session = get_session()
    try:
        emp = session.query(Employee).get(employee_id)
        if not emp:
            return jsonify({'error': 'Employee not found.'}), 404

        data = request.get_json()
        new_email = data.get('email', emp.email)
        if new_email and not is_valid_email(new_email):
            return jsonify({'error': 'invalid email format'}), 422

        emp.employee_name = data.get('employee_name', emp.employee_name)
        emp.email = new_email

        manager_name = data.get('manager_name')
        reports_to = data.get('reports_to')

        if manager_name:
            manager = session.query(Employee).filter_by(employee_name=manager_name).first()
            if not manager:
                return jsonify({'error': 'Manager not found.'}), 404
            if manager.id == emp.id:
                return jsonify({'error': 'Employee cannot report to themselves.'}), 400
            emp.reports_to = manager.id
        elif reports_to is not None:
            if reports_to == emp.id:
                return jsonify({'error': 'Employee cannot report to themselves.'}), 400
            if reports_to:
                manager = session.query(Employee).get(reports_to)
                if not manager:
                    return jsonify({'error': 'Manager not found.'}), 404
                emp.reports_to = manager.id
            else:
                emp.reports_to = None

        session.commit()
        return jsonify({
            'id': emp.id,
            'employee_name': emp.employee_name,
            'email': emp.email,
            'reports_to': emp.reports_to
        }), 200
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

# Delete employee
def delete_employee(employee_id):
    session = get_session()
    try:
        emp = session.query(Employee).get(employee_id)
        if not emp:
            return jsonify({'error': 'Employee not found.'}), 404

        subordinates = session.query(Employee).filter(Employee.reports_to == employee_id).all()
        for sub in subordinates:
            sub.reports_to = None

        session.delete(emp)
        session.commit()
        return jsonify({'message': 'Employee deleted successfully. Subordinates updated.'}), 200
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

# Get subordinates
def get_subordinates(manager_id):
    session = get_session()
    try:
        manager = session.query(Employee).get(manager_id)
        if not manager:
            return jsonify({'error': 'Manager not found.'}), 404

        subordinates = manager.subordinates
        return jsonify({
            'manager_id': manager.id,
            'manager_name': manager.employee_name,
            'subordinates': [
                {
                    'id': sub.id,
                    'employee_name': sub.employee_name,
                    'email': sub.email,
                    'reports_to': sub.reports_to
                } for sub in subordinates
            ]
        }), 200
    finally:
        session.close()

# Get employees without manager
def get_employees_without_manager():
    session = get_session()
    try:
        employees = session.query(Employee).filter(Employee.reports_to == None).all()
        return jsonify([
            {
                'id': emp.id,
                'employee_name': emp.employee_name,
                'email': emp.email,
                'reports_to': emp.reports_to
            } for emp in employees
        ]), 200
    finally:
        session.close()

# Get manager hierarchy
def get_manager_hirerarchy(employee_id):
    session = get_session()
    try:
        emp = session.query(Employee).get(employee_id)
        if not emp:
            return jsonify({'error': 'Employee not found.'}), 404

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
            'employee_id': emp.id,
            'employee_name': emp.employee_name,
            'manager_hierarchy': hierarchy
        }), 200
    finally:
        session.close()

# Get full employee tree
def get_employee_tree(employee_id):
    session = get_session()
    try:
        root = session.query(Employee).get(employee_id)
        if not root:
            return jsonify({'error': 'Employee not found.'}), 404

        def build_tree(emp):
            return {
                'id': emp.id,
                'employee_name': emp.employee_name,
                'email': emp.email,
                'reports_to': emp.reports_to,
                'subordinates': [build_tree(sub) for sub in emp.subordinates]
            }

        tree = build_tree(root)
        return jsonify(tree), 200
    finally:
        session.close()
