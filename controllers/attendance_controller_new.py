"""
Attendance Controller - Check-in, Check-out, History
"""

from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
from bson import ObjectId
from datetime import datetime, timedelta
from models.attendance_model_new import (
    create_attendance_doc,
    serialize_attendance,
)

def check_in(db):
    """Employee check-in with face recognition"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Get user
        user = db.users.find_one({"_id": ObjectId(current_user_id)})
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Check if already checked in today
        today = datetime.utcnow().strftime("%Y-%m-%d")
        existing = db.attendance.find_one({
            "user_id": ObjectId(current_user_id),
            "date": today,
            "check_type": "check_in"
        })
        
        if existing:
            return jsonify({"error": "Already checked in today"}), 400
        
        # Create check-in record
        attendance_doc = create_attendance_doc(
            user_id=ObjectId(current_user_id),
            employee_id=user['employee_id'],
            name=user['name'],
            check_type="check_in",
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            confidence=data.get('confidence', 0.0),
            device_info=data.get('device_info', ''),
        )
        
        result = db.attendance.insert_one(attendance_doc)
        
        return jsonify({
            "message": "Check-in successful",
            "attendance": serialize_attendance(attendance_doc),
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def check_out(db):
    """Employee check-out"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Get user
        user = db.users.find_one({"_id": ObjectId(current_user_id)})
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Check if already checked out today
        today = datetime.utcnow().strftime("%Y-%m-%d")
        existing_checkout = db.attendance.find_one({
            "user_id": ObjectId(current_user_id),
            "date": today,
            "check_type": "check_out"
        })
        
        if existing_checkout:
            return jsonify({"error": "Already checked out today"}), 400
        
        # Check if checked in today
        existing_checkin = db.attendance.find_one({
            "user_id": ObjectId(current_user_id),
            "date": today,
            "check_type": "check_in"
        })
        
        if not existing_checkin:
            return jsonify({"error": "No check-in found for today"}), 400
        
        # Create check-out record
        attendance_doc = create_attendance_doc(
            user_id=ObjectId(current_user_id),
            employee_id=user['employee_id'],
            name=user['name'],
            check_type="check_out",
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            confidence=data.get('confidence', 0.0),
            device_info=data.get('device_info', ''),
        )
        
        db.attendance.insert_one(attendance_doc)
        
        return jsonify({
            "message": "Check-out successful",
            "attendance": serialize_attendance(attendance_doc),
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_attendance_history(db):
    """Get user's attendance history"""
    try:
        current_user_id = get_jwt_identity()
        
        # Query parameters
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 30, type=int)
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        # Build query
        query = {"user_id": ObjectId(current_user_id)}
        
        if date_from or date_to:
            date_query = {}
            if date_from:
                date_query["$gte"] = date_from
            if date_to:
                date_query["$lte"] = date_to
            query["date"] = date_query
        
        # Count total
        total = db.attendance.count_documents(query)
        
        # Get records
        records = list(db.attendance.find(query)
            .sort("timestamp", -1)
            .skip((page - 1) * limit)
            .limit(limit))
        
        return jsonify({
            "total": total,
            "page": page,
            "limit": limit,
            "records": [serialize_attendance(r) for r in records],
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_daily_summary(db):
    """Get daily attendance summary"""
    try:
        current_user_id = get_jwt_identity()
        
        date = request.args.get('date', datetime.utcnow().strftime("%Y-%m-%d"))
        
        records = list(db.attendance.find({
            "user_id": ObjectId(current_user_id),
            "date": date
        }).sort("timestamp", 1))
        
        check_in = None
        check_out = None
        
        for record in records:
            if record['check_type'] == 'check_in' and not check_in:
                check_in = record
            elif record['check_type'] == 'check_out' and not check_out:
                check_out = record
        
        return jsonify({
            "date": date,
            "check_in": serialize_attendance(check_in) if check_in else None,
            "check_out": serialize_attendance(check_out) if check_out else None,
            "status": "present" if check_in else "absent",
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
