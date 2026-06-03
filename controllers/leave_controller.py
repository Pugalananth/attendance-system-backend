"""
Enterprise Leave Controller
AI Employee Attendance System
"""

import logging

from datetime import datetime
from flask import request, jsonify
from bson import ObjectId

from utils.db import get_db

logger = logging.getLogger(__name__)

# =========================================================
# BSON SERIALIZER
# =========================================================

def serialize_doc(doc):
    if not doc:
        return doc
    doc["_id"] = str(doc["_id"])
    return doc

def serialize_list(docs):
    return [serialize_doc(doc) for doc in docs]

# =========================================================
# REQUEST LEAVE
# =========================================================

def request_leave():
    """Submit a leave request"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "message": "Request body required"
            }), 400

        # =================================================
        # REQUEST DATA
        # =================================================
        
        current_user = request.current_user
        employee_id = current_user["employee_id"]
        
        leave_type = str(
            data.get("leave_type", "")
        ).strip()
        
        start_date = str(
            data.get("start_date", "")
        ).strip()
        
        end_date = str(
            data.get("end_date", "")
        ).strip()
        
        total_days = int(
            data.get("total_days", 0)
        )
        
        reason = str(
            data.get("reason", "")
        ).strip()

        # =================================================
        # VALIDATION
        # =================================================
        
        if not all([leave_type, start_date, end_date, total_days, reason]):
            return jsonify({
                "success": False,
                "message": "All fields required"
            }), 400

        # =================================================
        # DATABASE
        # =================================================
        
        db = get_db()
        
        employee = db["users"].find_one({
            "employee_id": employee_id,
            "is_active": True,
        })

        if not employee:
            return jsonify({
                "success": False,
                "message": "Employee not found"
            }), 404

        # =================================================
        # DUPLICATE CHECK
        # =================================================
        
        existing = db["leave_requests"].find_one({
            "employee_id": employee_id,
            "start_date": start_date,
            "end_date": end_date,
            "status": {"$in": ["pending", "approved"]}
        })

        if existing:
            return jsonify({
                "success": False,
                "message": "Leave request already exists for these dates"
            }), 409

        # =================================================
        # CREATE LEAVE REQUEST DOC
        # =================================================
        
        leave_doc = {
            "employee_id": employee_id,
            "employee_name": employee.get("name", ""),
            "department": employee.get("department", ""),
            "leave_type": leave_type,
            "start_date": start_date,
            "end_date": end_date,
            "total_days": total_days,
            "reason": reason,
            "status": "pending",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        # =================================================
        # INSERT
        # =================================================
        
        result = db["leave_requests"].insert_one(leave_doc)
        leave_doc["_id"] = str(result.inserted_id)

        logger.info(f"Leave request created: {employee_id} - {leave_type}")

        return jsonify({
            "success": True,
            "message": "Leave request submitted successfully",
            "data": leave_doc,
        }), 201

    except Exception as e:
        logger.error(f"Leave request error: {e}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

# =========================================================
# GET MY LEAVE REQUESTS
# =========================================================

def get_my_leave_requests():
    """Get current user's leave requests"""
    try:
        current_user = request.current_user
        employee_id = current_user["employee_id"]

        db = get_db()

        records = list(
            db["leave_requests"]
            .find({"employee_id": employee_id})
            .sort("created_at", -1)
        )

        records = serialize_list(records)

        return jsonify({
            "success": True,
            "data": records,
        }), 200

    except Exception as e:
        logger.error(f"Fetch leave requests error: {e}")
        return jsonify({
            "success": False,
            "message": "Failed to fetch leave requests"
        }), 500

# =========================================================
# GET ALL LEAVE REQUESTS (ADMIN/HR)
# =========================================================

def get_all_leave_requests():
    """Get all leave requests (admin/hr only)"""
    try:
        db = get_db()

        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 50))
        status = request.args.get("status", None)

        skip = (page - 1) * limit
        query = {}
        
        if status:
            query["status"] = status

        records = list(
            db["leave_requests"]
            .find(query)
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
        )

        total = db["leave_requests"].count_documents(query)
        records = serialize_list(records)

        return jsonify({
            "success": True,
            "data": {
                "records": records,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total,
                }
            }
        }), 200

    except Exception as e:
        logger.error(f"Fetch all leave requests error: {e}")
        return jsonify({
            "success": False,
            "message": "Failed to fetch leave requests"
        }), 500

# =========================================================
# APPROVE LEAVE REQUEST
# =========================================================

def approve_leave(leave_id):
    """Approve a leave request"""
    try:
        db = get_db()
        
        leave_request = db["leave_requests"].find_one({
            "_id": ObjectId(leave_id)
        })

        if not leave_request:
            return jsonify({
                "success": False,
                "message": "Leave request not found"
            }), 404

        if leave_request["status"] != "pending":
            return jsonify({
                "success": False,
                "message": f"Cannot approve - status is {leave_request['status']}"
            }), 400

        # =================================================
        # UPDATE STATUS
        # =================================================
        
        db["leave_requests"].update_one(
            {"_id": ObjectId(leave_id)},
            {
                "$set": {
                    "status": "approved",
                    "approved_by": request.current_user["user_id"],
                    "updated_at": datetime.utcnow()
                }
            }
        )

        logger.info(f"Leave request approved: {leave_id}")

        return jsonify({
            "success": True,
            "message": "Leave request approved successfully"
        }), 200

    except Exception as e:
        logger.error(f"Approve leave error: {e}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

# =========================================================
# REJECT LEAVE REQUEST
# =========================================================

def reject_leave(leave_id):
    """Reject a leave request"""
    try:
        data = request.get_json()
        
        db = get_db()
        
        leave_request = db["leave_requests"].find_one({
            "_id": ObjectId(leave_id)
        })

        if not leave_request:
            return jsonify({
                "success": False,
                "message": "Leave request not found"
            }), 404

        if leave_request["status"] != "pending":
            return jsonify({
                "success": False,
                "message": f"Cannot reject - status is {leave_request['status']}"
            }), 400

        # =================================================
        # UPDATE STATUS
        # =================================================
        
        rejection_reason = data.get("rejection_reason", "")
        
        db["leave_requests"].update_one(
            {"_id": ObjectId(leave_id)},
            {
                "$set": {
                    "status": "rejected",
                    "rejection_reason": rejection_reason,
                    "rejected_by": request.current_user["user_id"],
                    "updated_at": datetime.utcnow()
                }
            }
        )

        logger.info(f"Leave request rejected: {leave_id}")

        return jsonify({
            "success": True,
            "message": "Leave request rejected successfully"
        }), 200

    except Exception as e:
        logger.error(f"Reject leave error: {e}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

# =========================================================
# CANCEL LEAVE REQUEST
# =========================================================

def cancel_leave(leave_id):
    """Cancel a leave request"""
    try:
        db = get_db()
        
        leave_request = db["leave_requests"].find_one({
            "_id": ObjectId(leave_id)
        })

        if not leave_request:
            return jsonify({
                "success": False,
                "message": "Leave request not found"
            }), 404

        if leave_request["status"] not in ["pending", "approved"]:
            return jsonify({
                "success": False,
                "message": f"Cannot cancel - status is {leave_request['status']}"
            }), 400

        # =================================================
        # UPDATE STATUS
        # =================================================
        
        db["leave_requests"].update_one(
            {"_id": ObjectId(leave_id)},
            {
                "$set": {
                    "status": "cancelled",
                    "updated_at": datetime.utcnow()
                }
            }
        )

        logger.info(f"Leave request cancelled: {leave_id}")

        return jsonify({
            "success": True,
            "message": "Leave request cancelled successfully"
        }), 200

    except Exception as e:
        logger.error(f"Cancel leave error: {e}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

# =========================================================
# GET LEAVE SUMMARY
# =========================================================

def get_leave_summary():
    """Get leave request summary"""
    try:
        current_user = request.current_user
        employee_id = current_user["employee_id"]

        db = get_db()

        total = db["leave_requests"].count_documents({
            "employee_id": employee_id
        })

        approved = db["leave_requests"].count_documents({
            "employee_id": employee_id,
            "status": "approved"
        })

        pending = db["leave_requests"].count_documents({
            "employee_id": employee_id,
            "status": "pending"
        })

        rejected = db["leave_requests"].count_documents({
            "employee_id": employee_id,
            "status": "rejected"
        })

        return jsonify({
            "success": True,
            "data": {
                "total": total,
                "approved": approved,
                "pending": pending,
                "rejected": rejected,
            }
        }), 200

    except Exception as e:
        logger.error(f"Leave summary error: {e}")
        return jsonify({
            "success": False,
            "message": "Failed to fetch leave summary"
        }), 500
