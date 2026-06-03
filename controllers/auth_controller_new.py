"""
Authentication Controller - Login, Registration
"""

from flask import request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token
from bson import ObjectId
from datetime import datetime
from models.user_model_new import (
    create_user_doc,
    verify_password,
    validate_email,
    validate_password,
    serialize_user,
)

def register_user(db):
    """Register new user - Admin only"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required = ['name', 'email', 'password', 'role']
        if not all(field in data for field in required):
            return jsonify({"error": "Missing required fields"}), 400
        
        # Validate email
        if not validate_email(data['email']):
            return jsonify({"error": "Invalid email format"}), 400
        
        # Validate password
        pwd_validation = validate_password(data['password'])
        if not pwd_validation['valid']:
            return jsonify({"error": pwd_validation['error']}), 400
        
        # Check if user already exists
        existing = db.users.find_one({"email": data['email'].lower()})
        if existing:
            return jsonify({"error": "Email already registered"}), 409
        
        # Create user document
        user_doc = create_user_doc(
            name=data['name'],
            email=data['email'],
            password=data['password'],
            role=data.get('role', 'employee'),
            employee_id=data.get('employee_id'),
            department=data.get('department', ''),
            phone=data.get('phone', ''),
            team_id=data.get('team_id'),
        )
        
        # Insert to database
        result = db.users.insert_one(user_doc)
        user_id = str(result.inserted_id)
        
        # Create tokens
        access_token = create_access_token(
            identity=user_id,
            additional_claims={"role": user_doc['role']}
        )
        refresh_token = create_refresh_token(identity=user_id)
        
        user_doc['_id'] = ObjectId(user_id)
        
        return jsonify({
            "message": "User registered successfully",
            "user": serialize_user(user_doc),
            "access_token": access_token,
            "refresh_token": refresh_token,
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def login_user(db):
    """Login user with email and password"""
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({"error": "Email and password required"}), 400
        
        # Find user
        user = db.users.find_one({"email": data['email'].lower()})
        if not user:
            return jsonify({"error": "Invalid credentials"}), 401
        
        # Verify password
        if not verify_password(data['password'], user['password']):
            return jsonify({"error": "Invalid credentials"}), 401
        
        # Check if active
        if user.get('status') != 'active':
            return jsonify({"error": "User account is inactive"}), 401
        
        # Update last login
        db.users.update_one(
            {"_id": user['_id']},
            {"$set": {"last_login": datetime.utcnow()}}
        )
        
        # Create tokens
        user_id = str(user['_id'])
        access_token = create_access_token(
            identity=user_id,
            additional_claims={"role": user['role']}
        )
        refresh_token = create_refresh_token(identity=user_id)
        
        return jsonify({
            "message": "Login successful",
            "user": serialize_user(user),
            "access_token": access_token,
            "refresh_token": refresh_token,
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
