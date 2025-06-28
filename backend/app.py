from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config.config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS  
from handlers.employee.employee import (
    create_employee,
    get_employees,
    get_employee,
    update_employee,
    delete_employee,
    get_subordinates
)




app= Flask(__name__)
CORS(app)  

app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS  

db= SQLAlchemy(app)


@app.route("/api/employees", methods=["POST"])
def add_employee():
    return create_employee()

@app.route("/api/employees", methods=["GET"])
def list_employees():
    return get_employees()

@app.route("/api/employees/<int:employee_id>", methods=["GET"])
def retrieve_employee(employee_id):
    return get_employee(employee_id)

@app.route("/api/employees/<int:employee_id>", methods=["PUT"])
def modify_employee(employee_id):
    return update_employee(employee_id)

@app.route("/api/employees/<int:employee_id>", methods=["DELETE"])
def remove_employee(employee_id):
    return delete_employee(employee_id)

@app.route("/api/employees/<int:manager_id>/subordinates", methods=["GET"])
def list_subordinates(manager_id):
    return get_subordinates(manager_id)
if __name__ == '__main__':
    app.run(debug=True)