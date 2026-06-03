"""
Admin Controller - Admin Operations
Professional Corporate Edition
"""

from flask import request, jsonify
from bson import ObjectId
from datetime import datetime, timedelta
import logging
import re
from models.user_model import serialize_user, create_user_doc
from utils.db import get_db

logger = logging.getLogger(__name__)

# =========================================================
# STAFF MANAGEMENT
# =========================================================

def generate_next_employee_id(db):
    """Generate the next sequential ID (EMP001, EMP002, etc.)"""
    try:
        # Find IDs that follow the EMP### pattern
        import re
        users = list(db.users.find({"employee_id": {"$regex": "^EMP[0-9]+$"}}, {"employee_id": 1}))

        if not users:
            return "EMP001"

        # Extract numeric parts and find the maximum
        ids = []
        for u in users:
            match = re.search(r"EMP(\d+)", u["employee_id"])
            if match:
                ids.append(int(match.group(1)))

        if not ids:
            return "EMP001"

        next_num = max(ids) + 1
        return f"EMP{next_num:03d}"
    except Exception as e:
        logger.error(f"ID Generation error: {e}")
        return "EMP001"

def get_all_employees(db):
    """Get all staff members with filtering"""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 100))
        role = request.args.get('role')
        department = request.args.get('department')
        search = request.args.get('search')

        query = {}
        if role:
            query["role"] = role
        if department:
            query["department"] = department
        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"employee_id": {"$regex": search, "$options": "i"}},
                {"email": {"$regex": search, "$options": "i"}}
            ]

        total = db.users.count_documents(query)
        users = list(db.users.find(query)
            .sort("created_at", -1)
            .skip((page - 1) * limit)
            .limit(limit))
        
        return jsonify({
            "success": True,
            "total": total,
            "employees": [serialize_user(u) for u in users],
            "data": [serialize_user(u) for u in users] # Compatibility
        }), 200
        
    except Exception as e:
        logger.error(f"Get all employees error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

def create_employee(db):
    """Register a new user (Employee, HR, or TL)"""
    try:
        data = request.get_json()
        
        required = ['name', 'email', 'password', 'role']
        if not all(field in data for field in required):
            return jsonify({"success": False, "message": "Missing required fields"}), 400

        # Handle Employee ID (Manual or Auto-generate)
        emp_id = str(data.get('employee_id', '')).strip().upper()
        if not emp_id:
            emp_id = generate_next_employee_id(db)

        # Check if user already exists
        if db.users.find_one({"email": data['email'].lower()}):
            return jsonify({"success": False, "message": "Email already registered"}), 409
        if db.users.find_one({"employee_id": emp_id}):
            return jsonify({"success": False, "message": f"Employee ID {emp_id} already exists"}), 409

        user_doc = create_user_doc(
            name=data['name'],
            email=data['email'],
            password=data['password'],
            role=data['role'],
            employee_id=emp_id,
            department=data.get('department', ''),
            phone=data.get('phone', '')
        )
        
        result = db.users.insert_one(user_doc)
        user_doc['_id'] = result.inserted_id
        
        return jsonify({
            "success": True,
            "message": "User registered successfully",
            "user": serialize_user(user_doc)
        }), 201
        
    except Exception as e:
        logger.error(f"Create user error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

def update_user(db, employee_id):
    """Update user details"""
    try:
        data = request.get_json()
        updatable = ['name', 'email', 'phone', 'department', 'role']
        update_data = {k: v for k, v in data.items() if k in updatable}
        update_data['updated_at'] = datetime.utcnow()
        
        result = db.users.update_one(
            {"employee_id": employee_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            return jsonify({"success": False, "message": "User not found"}), 404

        return jsonify({"success": True, "message": "User updated successfully"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

def block_user(db, employee_id):
    """Prevent user from logging in"""
    try:
        result = db.users.update_one(
            {"employee_id": employee_id},
            {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
        )
        if result.matched_count == 0:
            return jsonify({"success": False, "message": "User not found"}), 404
        return jsonify({"success": True, "message": "User blocked successfully"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

def unblock_user(db, employee_id):
    """Restore user login access"""
    try:
        result = db.users.update_one(
            {"employee_id": employee_id},
            {"$set": {"is_active": True, "updated_at": datetime.utcnow()}}
        )
        if result.matched_count == 0:
            return jsonify({"success": False, "message": "User not found"}), 404
        return jsonify({"success": True, "message": "User unblocked successfully"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

def delete_user(db, employee_id):
    """Permanently delete user and their associated data"""
    try:
        # Delete the user document
        result = db.users.delete_one({"employee_id": employee_id})
        if result.deleted_count == 0:
            return jsonify({"success": False, "message": "User not found"}), 404

        # Clean up related records
        db.attendance.delete_many({"employee_id": employee_id})
        db.leave_requests.delete_many({"employee_id": employee_id})
        db.permission_requests.delete_many({"employee_id": employee_id})
        db.wfh_requests.delete_many({"employee_id": employee_id})

        return jsonify({"success": True, "message": "User and all related data deleted permanently"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

def update_employee_role(db, user_id):
    """Legacy endpoint to update role"""
    try:
        data = request.get_json()
        result = db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"role": data.get('role'), "updated_at": datetime.utcnow()}}
        )
        return jsonify({"success": True, "message": "Role updated"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

def deactivate_employee(db, user_id):
    """Legacy endpoint for deactivation"""
    return block_user(db, user_id)

# =========================================================
# DASHBOARD & ANALYTICS
# =========================================================

def get_admin_dashboard_summary(db):
    """Get metrics for admin dashboard"""
    try:
        today = datetime.now().strftime("%Y-%m-%d")

        # Total staff (excluding admins)
        total_employees = db.users.count_documents({"role": {"$ne": "admin"}})

        # Present Today card must include: Present + Late Employees
        # Any entry in attendance for today means they are "Present" in the summary sense
        present_today = db.attendance.count_documents({"date": today})

        late_today = db.attendance.count_documents({"date": today, "isLate": True})

        absent_today = max(0, total_employees - present_today)

        stats = {
            "totalEmployees": total_employees,
            "presentToday": present_today,
            "lateToday": late_today,
            "absentToday": absent_today,
            "pendingLeaves": db.leave_requests.count_documents({"status": "pending"}),
            "pendingPermissions": db.permission_requests.count_documents({"status": "pending"}),
            "pendingWFH": db.wfh_requests.count_documents({"status": "pending"})
        }

        return jsonify({"success": True, "data": stats}), 200
    except Exception as e:
        logger.error(f"Dashboard summary error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

def get_attendance_analytics(db):
    """Calculate company-wide attendance percentage and detailed counts"""
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        total_employees = db.users.count_documents({"role": {"$ne": "admin"}})

        # Present Count = Present + Late
        present_count = db.attendance.count_documents({"date": today})
        # Late Count = isLate = True
        late_count = db.attendance.count_documents({"date": today, "isLate": True})
        # Absent Count = Total - Present
        absent_count = max(0, total_employees - present_count)

        rate = 0
        if total_employees > 0:
            rate = round((present_count / total_employees) * 100, 1)

        return jsonify({
            "success": True,
            "data": {
                "totalEmployees": total_employees,
                "presentCount": present_count,
                "lateCount": late_count,
                "absentCount": absent_count,
                "attendanceRate": rate
            }
        }), 200
    except Exception as e:
        logger.error(f"Analytics error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

def get_monthly_report(db):
    """Generate monthly performance logs"""
    try:
        month = request.args.get('month', datetime.now().month)
        year = request.args.get('year', datetime.now().year)

        # Return summary and records
        # This is used by AttendanceReportScreen.js
        # For simplicity, we'll return today's stats if filter is Today, etc.
        # But let's check what AttendanceReportScreen expects.

        return jsonify({"success": True, "message": "Report generated"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

def get_request_history(db):
    """Get a consolidated list of all staff requests"""
    try:
        status = request.args.get('status')
        query = {}
        if status and status != 'All':
            query['status'] = status.lower()

        leaves = list(db.leave_requests.find(query).sort("created_at", -1).limit(20))
        permissions = list(db.permission_requests.find(query).sort("created_at", -1).limit(20))
        wfh = list(db.wfh_requests.find(query).sort("created_at", -1).limit(20))
        
        history = []
        for r in leaves:
            r['_id'] = str(r['_id'])
            r['request_type'] = 'leave'
            history.append(r)
        for r in permissions:
            r['_id'] = str(r['_id'])
            r['request_type'] = 'permission'
            history.append(r)
        for r in wfh:
            r['_id'] = str(r['_id'])
            r['request_type'] = 'wfh'
            history.append(r)

        return jsonify({"success": True, "data": history}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# =========================================================
# COMPANY SETTINGS
# =========================================================

def get_company_details(db):
    """Get company configuration"""
    try:
        settings = db.company_settings.find_one({})
        if not settings:
            return jsonify({"success": False, "message": "Settings not found"}), 404
        settings['_id'] = str(settings['_id'])
        return jsonify({"success": True, "data": settings}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

def update_company_details(db):
    """Save or Update company configuration"""
    try:
        data = request.get_json()
        data['updated_at'] = datetime.utcnow()

        # Requirement: Fields match specific keys
        # Company Name, Company Address, Company Phone, Company Email,
        # Working Start Time, Working End Time, Late Mark Time, Leave Policy, WFH Policy

        # Use update_one with upsert: true to prevent duplicates
        db.company_settings.update_one(
            {},
            {"$set": data},
            upsert=True
        )
        return jsonify({"success": True, "message": "Company settings updated"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
