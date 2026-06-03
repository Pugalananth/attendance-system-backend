"""
Task Controller - Work Assignment
"""

from flask import request, jsonify
from utils.db import get_db
from bson import ObjectId
from datetime import datetime

def create_task():
    try:
        data = request.get_json()
        current_user = request.current_user

        db = get_db()

        task_doc = {
            "title": data.get("title"),
            "description": data.get("description"),
            "assigned_to": data.get("assigned_to"), # user_id
            "assigned_by": current_user["user_id"],
            "status": "pending", # pending, in-progress, completed
            "priority": data.get("priority", "medium"),
            "due_date": data.get("due_date"),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        result = db["tasks"].insert_one(task_doc)
        task_doc["_id"] = str(result.inserted_id)

        return jsonify({
            "success": True,
            "message": "Task created successfully",
            "data": task_doc
        }), 201

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

def get_team_tasks():
    try:
        current_user = request.current_user
        db = get_db()

        tasks = list(db["tasks"].find({
            "assigned_by": current_user["user_id"]
        }).sort("created_at", -1))

        # Get member names for display
        members = list(db.users.find({"teamLeaderId": current_user["user_id"]}, {"name": 1}))
        member_map = {str(m["_id"]): m["name"] for m in members}

        for task in tasks:
            task["_id"] = str(task["_id"])
            task["assigned_to_name"] = member_map.get(str(task.get("assigned_to")), "Unknown")

        return jsonify({
            "success": True,
            "data": tasks
        }), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

def get_my_tasks():
    try:
        current_user = request.current_user
        db = get_db()

        tasks = list(db["tasks"].find({
            "assigned_to": current_user["user_id"]
        }))

        for task in tasks:
            task["_id"] = str(task["_id"])

        return jsonify({
            "success": True,
            "data": tasks
        }), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

def update_task_status(task_id):
    try:
        data = request.get_json()
        status = data.get("status")

        if status not in ["pending", "in-progress", "completed"]:
            return jsonify({"success": False, "message": "Invalid status"}), 400

        db = get_db()
        result = db["tasks"].update_one(
            {"_id": ObjectId(task_id)},
            {"$set": {"status": status, "updated_at": datetime.utcnow()}}
        )

        if result.matched_count == 0:
            return jsonify({"success": False, "message": "Task not found"}), 404

        return jsonify({
            "success": True,
            "message": "Task status updated"
        }), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

def delete_task(task_id):
    """Permanently remove a task assignment"""
    try:
        db = get_db()
        result = db["tasks"].delete_one({"_id": ObjectId(task_id)})

        if result.deleted_count == 0:
            return jsonify({"success": False, "message": "Task not found"}), 404

        return jsonify({
            "success": True,
            "message": "Task deleted successfully"
        }), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
