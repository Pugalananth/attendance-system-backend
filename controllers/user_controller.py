"""
User Profile Controller - Get, Update User Profile
"""

from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
from bson import ObjectId
from datetime import datetime
from models.user_model_new import serialize_user

def get_profile(db):
    """Get user's profile"""
    try:
        current_user_id = get_jwt_identity()
        
        user = db.users.find_one({"_id": ObjectId(current_user_id)})
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify({
            "user": serialize_user(user),
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def update_profile(db):
    """Update user profile"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Fields that can be updated
        updatable = ['name', 'phone', 'designation', 'department']
        update_data = {k: v for k, v in data.items() if k in updatable}
        
        if not update_data:
            return jsonify({"error": "No valid fields to update"}), 400
        
        update_data['updated_at'] = datetime.utcnow()
        
        result = db.users.update_one(
            {"_id": ObjectId(current_user_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            return jsonify({"error": "User not found"}), 404
        
        # Get updated user
        user = db.users.find_one({"_id": ObjectId(current_user_id)})
        
        return jsonify({
            "message": "Profile updated successfully",
            "user": serialize_user(user),
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_user_by_id(db, user_id):
    """Get specific user by ID"""
    try:
        user = db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify({"user": serialize_user(user)}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_all_employees(db):
    """Get all employees (for HR and Admin)"""
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        role = request.args.get('role', 'employee')
        
        query = {"role": role, "status": "active"}
        
        total = db.users.count_documents(query)
        
        users = list(db.users.find(query)
            .skip((page - 1) * limit)
            .limit(limit))
        
        return jsonify({
            "total": total,
            "page": page,
            "limit": limit,
            "users": [serialize_user(u) for u in users],
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
