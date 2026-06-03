"""
Team Controller - Team Leader Operations
Professional Corporate Edition
"""

from flask import request, jsonify
from bson import ObjectId
from datetime import datetime
import logging
from utils.db import get_db
from models.permission_model import serialize_permission

logger = logging.getLogger(__name__)

def get_tl_members(db):
    """Get all employees assigned to the current TL"""
    try:
        current_tl = request.current_user
        tl_id = current_tl["user_id"]
        
        members = list(db.users.find({
            "teamLeaderId": tl_id,
            "role": "employee"
        }))
        
        for member in members:
            member["_id"] = str(member["_id"])
            if "password" in member: del member["password"]

        return jsonify({
            "success": True,
            "data": members
        }), 200
    except Exception as e:
        logger.error(f"TL members error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

def get_available_employees_tl(db):
    """Get employees not assigned to any team"""
    try:
        employees = list(db.users.find({
            "role": "employee",
            "$or": [
                {"teamLeaderId": {"$exists": False}},
                {"teamLeaderId": ""},
                {"teamLeaderId": None}
            ]
        }, {
            "name": 1,
            "employee_id": 1,
            "department": 1,
            "role": 1
        }))

        for e in employees:
            e["_id"] = str(e["_id"])

        return jsonify({
            "success": True,
            "data": employees
        }), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

def add_team_member_tl(db):
    """Assign an employee to current TL's team"""
    try:
        data = request.get_json()
        employee_id = data.get("employee_id")
        current_tl = request.current_user
        tl_id = current_tl["user_id"]
        
        if not employee_id:
            return jsonify({"success": False, "message": "Employee ID required"}), 400

        result = db.users.update_one(
            {"employee_id": employee_id, "role": "employee"},
            {"$set": {"teamLeaderId": tl_id}}
        )

        if result.matched_count == 0:
            return jsonify({"success": False, "message": "Employee not found or invalid role"}), 404

        return jsonify({"success": True, "message": "Member added to team"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

def remove_team_member_tl(db, employee_id):
    """Remove an employee from current TL's team"""
    try:
        current_tl = request.current_user
        tl_id = current_tl["user_id"]
        
        result = db.users.update_one(
            {"employee_id": employee_id, "teamLeaderId": tl_id},
            {"$unset": {"teamLeaderId": ""}}
        )
        
        if result.matched_count == 0:
            return jsonify({"success": False, "message": "Employee not in your team"}), 404

        return jsonify({"success": True, "message": "Member removed from team"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

def get_team_attendance_tl(db):
    """Get attendance logs for team members"""
    try:
        current_tl = request.current_user
        tl_id = current_tl["user_id"]
        date = request.args.get("date", datetime.utcnow().strftime("%Y-%m-%d"))
        
        members = list(db.users.find({"teamLeaderId": tl_id}, {"employee_id": 1, "name": 1}))
        member_ids = [m["employee_id"] for m in members]
        member_map = {m["employee_id"]: m["name"] for m in members}

        attendance = list(db.attendance.find({
            "employee_id": {"$in": member_ids},
            "date": date
        }))
        
        for entry in attendance:
            entry["_id"] = str(entry["_id"])
            entry["employee_name"] = member_map.get(entry["employee_id"], "Unknown")
            # Ensure other ObjectIds/dates are handled if they exist in attendance doc
            if "user_id" in entry: entry["user_id"] = str(entry["user_id"])
            if "created_at" in entry and isinstance(entry["created_at"], datetime):
                entry["created_at"] = entry["created_at"].isoformat()

        return jsonify({
            "success": True,
            "data": attendance
        }), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

def get_team_leave_requests(db):
    """Get leave requests of team members"""
    try:
        current_tl = request.current_user
        tl_id = current_tl["user_id"]
        
        members = list(db.users.find({"teamLeaderId": tl_id}, {"employee_id": 1}))
        member_ids = [m["employee_id"] for m in members]

        leaves = list(db.leave_requests.find({
            "employee_id": {"$in": member_ids}
        }).sort("created_at", -1))
        
        for leave in leaves:
            leave["_id"] = str(leave["_id"])
            if "user_id" in leave: leave["user_id"] = str(leave["user_id"])
            if "created_at" in leave and isinstance(leave["created_at"], datetime):
                leave["created_at"] = leave["created_at"].isoformat()
            if "updated_at" in leave and isinstance(leave["updated_at"], datetime):
                leave["updated_at"] = leave["updated_at"].isoformat()

        return jsonify({
            "success": True,
            "data": leaves
        }), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

def update_leave_tl(db, leave_id):
    """Approve or reject a leave request as TL"""
    try:
        data = request.get_json()
        status = data.get("status")
        remarks = data.get("remarks", "")

        if status not in ["approved", "rejected"]:
            return jsonify({"success": False, "message": "Invalid status"}), 400

        result = db.leave_requests.update_one(
            {"_id": ObjectId(leave_id)},
            {"$set": {
                "status": status,
                "remarks": remarks,
                "updated_at": datetime.utcnow()
            }}
        )

        if result.matched_count == 0:
            return jsonify({"success": False, "message": "Leave request not found"}), 404

        return jsonify({"success": True, "message": f"Leave {status}"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

def get_team_permission_requests(db):
    """Get permission requests of team members"""
    try:
        current_tl = request.current_user
        tl_id = current_tl["user_id"]
        
        # Get employees in this TL's team
        members = list(db.users.find({"teamLeaderId": tl_id}, {"employee_id": 1}))
        member_ids = [m["employee_id"] for m in members]
        
        # Fetch their permissions
        permissions = list(db.permission_requests.find({
            "employee_id": {"$in": member_ids}
        }).sort("created_at", -1))
        
        # Serialize with robust logic (handles ObjectIds and Datetimes)
        serialized = [serialize_permission(p) for p in permissions]

        return jsonify({
            "success": True,
            "data": serialized
        }), 200
    except Exception as e:
        logger.error(f"TL get permissions error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

def update_permission_tl(db, permission_id):
    """Approve or reject a permission request"""
    try:
        data = request.get_json()
        status = data.get("status")
        remarks = data.get("remarks", "")

        if status not in ["approved", "rejected"]:
            return jsonify({"success": False, "message": "Invalid status"}), 400

        result = db.permission_requests.update_one(
            {"_id": ObjectId(permission_id)},
            {"$set": {
                "status": status,
                "remarks": remarks,
                "updated_at": datetime.utcnow()
            }}
        )

        if result.matched_count == 0:
            return jsonify({"success": False, "message": "Permission request not found"}), 404

        return jsonify({"success": True, "message": f"Permission {status}"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

def get_team_dashboard_summary(db):
    """Get summary statistics for TL dashboard"""
    try:
        current_tl = request.current_user
        tl_id = current_tl["user_id"]
        today = datetime.utcnow().strftime("%Y-%m-%d")
        
        members = list(db.users.find({"teamLeaderId": tl_id}, {"employee_id": 1}))
        member_ids = [m["employee_id"] for m in members]
        total_members = len(member_ids)
        
        present_today = db.attendance.count_documents({
            "employee_id": {"$in": member_ids},
            "date": today,
            "status": "Present"
        })
        
        absent_today = total_members - present_today
        
        pending_leaves = db.leave_requests.count_documents({
            "employee_id": {"$in": member_ids},
            "status": "pending"
        })
        
        pending_permissions = db.permission_requests.count_documents({
            "employee_id": {"$in": member_ids},
            "status": "pending"
        })
        
        return jsonify({
            "success": True,
            "data": {
                "totalMembers": total_members,
                "presentToday": present_today,
                "absentToday": max(0, absent_today),
                "pendingLeaves": pending_leaves,
                "pendingPermissions": pending_permissions
            }
        }), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
