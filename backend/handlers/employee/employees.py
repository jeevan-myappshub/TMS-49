from flask import request,jsonify 
from models.employee import Employee 
from utils.session_manager import get_session 
from utils.helpers import is_valid_email 

#  creating the curd operations as a bassic endpoints 
def create_employee():
    session=get_session()
    try:
        data=request.get_json()
        name=data.get('employee_name')
        email=data.get('email')
        manager_id=data.get('manager_id')

        if not name and not email:
            return jsonify({'error':'employee_name ans email is required.'}),400 #bad request        
        if not is_valid_email(email):
            return jsonify({'error':'invalid email format'}), 422  # unprocessaable entity 
        new_employee=Employee(employee_name=name,email=email,manager_id=manager_id)
        session.add(new_employee)
        session.commit() 
        return jsonify({
            'id':new_employee.id,
            'employee_name':new_employee.employee_name,
            'email':new_employee.email ,
            'manager_id': new_employee.manager_id
        }),201 
    finally:
        session.close()

def get_employees():
    session=get_session()
    try:
        employees=session.query(Employee).all()
        return jsonify([
            {
                'id':emp.id,
                'employee_name':emp.employee_name,
                 'email':emp.email,
                 'manager_id':emp.manager_id
            } for emp in employees
        ]),200 
    finally:
        session.close()

def get_employee(employee_id):
    session=get_session()
    try:
        emp=session.query(Employee).get(employee_id)
        if not emp:
            return jsonify({'error':'Employee not found.'}),404 
        return jsonify({
            'id': emp.id,
            'employee_name': emp.employee_name,
            'email': emp.email,
            'manager_id': emp.manager_id
        }),200
    finally:
        session.close()

def update_employee(employee_id):
    session = get_session()
    try:
        emp = session.query(Employee).get(employee_id)
        if not emp:
            return jsonify({'error': 'employee not found.'}), 404
        data = request.get_json()
        new_email = data.get('email', emp.email)
        if new_email and not is_valid_email(new_email):
            return jsonify({'error': 'invalid email format'}), 422

        emp.employee_name = data.get('employee_name', emp.employee_name)
        emp.email = new_email

        manager_name = data.get('manager_name')
        if manager_name:
            manager = session.query(Employee).filter_by(employee_name=manager_name).first()
            if not manager:
                return jsonify({'error': 'Manager not found.'}), 404
            emp.manager_id = manager.id
        else:
            emp.manager_id = data.get('manager_id', emp.manager_id)

        session.commit()
        return jsonify({
            'id': emp.id,
            'employee_name': emp.employee_name,
            'email': emp.email,
            'manager_id': emp.manager_id
        }), 200
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
                    'manager_id': sub.manager_id
                } for sub in subordinates
            ]
        }), 200
    finally:
        session.close()


#get employees without manager 
def get_employees_without_manager():
    session=get_session()
    try:
        employees=session.query(Employee).filter(Employee.manager_id==None).all()
        return jsonify([
        {
            'id': emp.id,
            'employee_name': emp.employee_name,
            'email': emp.email,
            'manager_id': emp.manager_id
        } for emp in employees
        ]),200 # ✅ OK
    finally:
        session.close()
        
