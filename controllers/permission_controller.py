"""
Permission Controller - Permission Requests
Professional Corporate Edition
"""

from flask import request, jsonify
from bson import ObjectId
from datetime import datetime
import logging
import traceback
from models.permission_model import (
    create_permission_doc,
    serialize_permission,
)

logger = logging.getLogger(__name__)

def create_permission_request(db):
    """Create permission request"""
    try:
        current_user = request.current_user
        current_user_id = current_user["user_id"]
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "message": "Request body required"}), 400

        required = ['permission_type', 'start_time', 'end_time']
        if not all(field in data for field in required):
            return jsonify({"success": False, "message": "Missing required fields"}), 400
        
        user = db["users"].find_one({"_id": ObjectId(current_user_id)})
        if not user:
            return jsonify({"success": False, "message": "User profile not found"}), 404
        
        permission_doc = create_permission_doc(
            user_id=ObjectId(current_user_id),
            employee_id=user.get('employee_id'),
            name=user.get('name'),
            permission_type=data['permission_type'],
            start_time=data['start_time'],
            end_time=data['end_time'],
            reason=data.get('reason', ''),
            status='pending',
        )
        
        db["permission_requests"].insert_one(permission_doc)
        
        return jsonify({
            "success": True,
            "message": "Permission request submitted successfully",
            "permission": serialize_permission(permission_doc),
        }), 201
        
    except Exception as e:
        logger.error(f"Create permission error: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"success": False, "message": f"Server Error: {str(e)}"}), 500

def get_my_permissions(db):
    """Get user's permission requests"""
    try:
        current_user = request.current_user
        current_user_id = current_user["user_id"]
        
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        status = request.args.get('status')
        
        query = {"user_id": ObjectId(current_user_id)}
        if status:
            query["status"] = status
        
        total = db["permission_requests"].count_documents(query)
        
        permissions = list(db["permission_requests"].find(query)
            .sort("created_at", -1)
            .skip((page - 1) * limit)
            .limit(limit))
        
        return jsonify({
            "success": True,
            "total": total,
            "page": page,
            "limit": limit,
            "permissions": [serialize_permission(p) for p in permissions],
        }), 200
        
    except Exception as e:
        logger.error(f"Get my permissions error: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"success": False, "message": f"Server Error: {str(e)}"}), 500

def get_pending_permissions(db):
    """Get all pending permission requests (HR/Admin)"""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        
        query = {"status": "pending"}
        
        total = db["permission_requests"].count_documents(query)
        
        permissions = list(db["permission_requests"].find(query)
            .sort("created_at", -1)
            .skip((page - 1) * limit)
            .limit(limit))
        
        return jsonify({
            "success": True,
            "total": total,
            "page": page,
            "limit": limit,
            "permissions": [serialize_permission(p) for p in permissions],
        }), 200
        
    except Exception as e:
        logger.error(f"Get pending permissions error: {str(e)}")
        return jsonify({"success": False, "message": f"Server Error: {str(e)}"}), 500

def get_all_permissions_hr(db):
    """Get all permission requests with filtering for HR (History)"""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 100))
        status = request.args.get('status')
        search = request.args.get('search')

        query = {}
        if status and status != 'all':
            query["status"] = status

        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"employee_id": {"$regex": search, "$options": "i"}}
            ]

        total = db["permission_requests"].count_documents(query)

        permissions = list(db["permission_requests"].find(query)
            .sort("created_at", -1)
            .skip((page - 1) * limit)
            .limit(limit))

        return jsonify({
            "success": True,
            "total": total,
            "permissions": [serialize_permission(p) for p in permissions],
        }), 200
    except Exception as e:
        logger.error(f"Get all permissions HR error: {str(e)}")
        return jsonify({"success": False, "message": f"Server Error: {str(e)}"}), 500

def approve_permission(db, permission_id):
    """Approve permission request"""
    try:
        current_user = request.current_user
        current_user_id = current_user["user_id"]
        data = request.get_json() or {}
        
        result = db["permission_requests"].update_one(
            {"_id": ObjectId(permission_id)},
            {"$set": {
                "status": "approved",
                "approved_by": ObjectId(current_user_id),
                "approval_date": datetime.utcnow(),
                "remarks": data.get('remarks', ''),
                "updated_at": datetime.utcnow(),
            }}
        )
        
        if result.matched_count == 0:
            return jsonify({"success": False, "message": "Permission request not found"}), 404
        
        permission = db["permission_requests"].find_one({"_id": ObjectId(permission_id)})
        
        return jsonify({
            "success": True,
            "message": "Permission request approved",
            "permission": serialize_permission(permission),
        }), 200
        
    except Exception as e:
        logger.error(f"Approve permission error: {str(e)}")
        return jsonify({"success": False, "message": f"Server Error: {str(e)}"}), 500

def reject_permission(db, permission_id):
    """Reject permission request"""
    try:
        current_user = request.current_user
        current_user_id = current_user["user_id"]
        data = request.get_json() or {}
        
        result = db["permission_requests"].update_one(
            {"_id": ObjectId(permission_id)},
            {"$set": {
                "status": "rejected",
                "approved_by": ObjectId(current_user_id),
                "approval_date": datetime.utcnow(),
                "remarks": data.get('remarks', ''),
                "updated_at": datetime.utcnow(),
            }}
        )
        
        if result.matched_count == 0:
            return jsonify({"success": False, "message": "Permission request not found"}), 404
        
        permission = db["permission_requests"].find_one({"_id": ObjectId(permission_id)})
        
        return jsonify({
            "success": True,
            "message": "Permission request rejected",
            "permission": serialize_permission(permission),
        }), 200
        
    except Exception as e:
        logger.error(f"Reject permission error: {str(e)}")
        return jsonify({"success": False, "message": f"Server Error: {str(e)}"}), 500
