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

# Connect to MongoDB Atlas
mongo_uri = os.getenv("MONGO_URI")
db_name = os.getenv("DB_NAME")

client = MongoClient(mongo_uri)
db = client[db_name]
students = db.students

# Helper function to convert ObjectId
def student_serializer(student):
    return {
        "_id": str(student["_id"]),
        "name": student["name"],
        "age": student["age"],
        "course": student["course"]
    }

# 🟢 Create Student
@app.route("/students", methods=["POST"])
def add_student():
    data = request.get_json()
    name = data.get("name")
    age = data.get("age")
    course = data.get("course")

    if not all([name, age, course]):
        return jsonify({"error": "Missing fields"}), 400

    new_student = {"name": name, "age": age, "course": course}
    result = students.insert_one(new_student)
    print("Studnet created")
    return jsonify({"message": "Student added", "id": str(result.inserted_id)}), 201

# 🔵 Read All Students
@app.route("/students", methods=["GET"])
def get_students():
    all_students = [student_serializer(s) for s in students.find()]
    return jsonify(all_students), 200

# 🟣 Read One Student
@app.route("/students/<id>", methods=["GET"])
def get_student(id):
    student = students.find_one({"_id": ObjectId(id)})
    if student:
        return jsonify(student_serializer(student)), 200
    else:
        return jsonify({"error": "Student not found"}), 404

# 🟠 Update Student
@app.route("/students/<id>", methods=["PUT"])
def update_student(id):
    data = request.get_json()
    updated_data = {k: v for k, v in data.items() if v is not None}
    
    result = students.update_one({"_id": ObjectId(id)}, {"$set": updated_data})
    if result.matched_count:
        return jsonify({"message": "Student updated"}), 200
    else:
        return jsonify({"error": "Student not found"}), 404

# 🔴 Delete Student
@app.route("/students/<id>", methods=["DELETE"])
def delete_student(id):
    result = students.delete_one({"_id": ObjectId(id)})
    if result.deleted_count:
        return jsonify({"message": "Student deleted"}), 200
    else:
        return jsonify({"error": "Student not found"}), 404

# ✅ Health Check
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Flask Student Management API running successfully"}), 200

if __name__ == "__main__":
    app.run(debug=True, port=5002)
