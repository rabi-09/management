from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# MongoDB connection
mongo_uri = os.getenv("MONGO_URI")
db_name = os.getenv("DB_NAME")

client = MongoClient(mongo_uri)
db = client[db_name]
employees = db.employees

# Helper to convert ObjectId
def employee_serializer(emp):
    return {
        "_id": str(emp["_id"]),
        "name": emp["name"],
        "position": emp["position"],
        "salary": emp["salary"],
        "department": emp["department"]
    }

# 🟢 Create Employee
@app.route("/employees", methods=["POST"])
def add_employee():
    data = request.get_json()
    name = data.get("name")
    position = data.get("position")
    salary = data.get("salary")
    department = data.get("department")

    if not all([name, position, salary, department]):
        return jsonify({"error": "Missing required fields"}), 400

    new_emp = {
        "name": name,
        "position": position,
        "salary": salary,
        "department": department
    }
    result = employees.insert_one(new_emp)

    return jsonify({"message": "Employee added", "id": str(result.inserted_id)}), 201

# 🔵 Get All Employees
@app.route("/employees", methods=["GET"])
def get_employees():
    all_emps = [employee_serializer(e) for e in employees.find()]
    return jsonify(all_emps), 200

# 🟣 Get Single Employee
@app.route("/employees/<id>", methods=["GET"])
def get_employee(id):
    emp = employees.find_one({"_id": ObjectId(id)})
    if emp:
        return jsonify(employee_serializer(emp)), 200
    else:
        return jsonify({"error": "Employee not found"}), 404

# 🟠 Update Employee
@app.route("/employees/<id>", methods=["PUT"])
def update_employee(id):
    data = request.get_json()
    update_data = {k: v for k, v in data.items() if v is not None}

    result = employees.update_one({"_id": ObjectId(id)}, {"$set": update_data})
    if result.matched_count:
        return jsonify({"message": "Employee updated"}), 200
    else:
        return jsonify({"error": "Employee not found"}), 404

# 🔴 Delete Employee
@app.route("/employees/<id>", methods=["DELETE"])
def delete_employee(id):
    result = employees.delete_one({"_id": ObjectId(id)})
    if result.deleted_count:
        return jsonify({"message": "Employee deleted"}), 200
    else:
        return jsonify({"error": "Employee not found"}), 404

# ✅ Health Check
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Employee Management API running successfully"}), 200

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5001))
    app.run(debug=True, port=port)
