"""
Enterprise Employee Profile Controller
AI Employee Attendance System
"""

import logging
from datetime import datetime, timedelta

from flask import request, jsonify
from bson import ObjectId

from utils.db import get_db

logger = logging.getLogger(__name__)

# =========================================================
# BSON SERIALIZER
# =========================================================

def serialize_user(user):
    if not user:
        return None
    
    user["_id"] = str(user["_id"])
    
    if "created_at" in user:
        user["created_at"] = user["created_at"].isoformat() if isinstance(user["created_at"], datetime) else user["created_at"]
    
    if "password_hash" in user:
        del user["password_hash"]
    
    return user

def is_hr_or_admin():
    role = str(
        request.current_user.get(
            "role",
            ""
        )
    ).lower()

    return role in [
        "hr",
        "admin",
    ]


def get_hr_employee_query():

    return {
        "role": {
            "$in": [
                "employee",
                "Employee",
                "teamleader",
                "team_leader",
                "hr",
                "HR",
            ]
        },
        "$or": [
            {"is_active": True},
            {"status": {"$in": ["active", "Active"]}},
            {"status": {"$exists": False}},
        ],
    }


def get_legacy_attendance_sources(db):

    sources = [
        db["attendance"]
    ]

    for db_name in [
        "employee_attendance",
        "facetrack_office",
    ]:
        legacy_db = db.client[db_name]

        if "attendance" in legacy_db.list_collection_names():
            sources.append(
                legacy_db["attendance"]
            )

    return sources


def get_latest_attendance_date(db):

    latest_date = None

    for source in get_legacy_attendance_sources(db):
        record = source.find_one(
            {
                "date": {
                    "$exists": True
                }
            },
            sort=[
                ("date", -1)
            ]
        )

        if not record:
            continue

        record_date = str(
            record.get("date", "")
        )

        if (
            latest_date is None or
            record_date > latest_date
        ):
            latest_date = record_date

    return latest_date


def get_attendance_for_hr_date(
    db,
    report_date,
    employee_ids,
    employee_emails
):

    match_fields = []

    if employee_ids:
        match_fields.append({
            "employee_id": {
                "$in": employee_ids
            }
        })

    if employee_emails:
        match_fields.append({
            "email": {
                "$in": employee_emails
            }
        })

    query = {
        "date": report_date
    }

    if match_fields:
        query["$or"] = match_fields

    records = []

    for source in get_legacy_attendance_sources(db):
        records.extend(
            list(
                source.find(query)
            )
        )

    return records

# =========================================================
# GET EMPLOYEES FOR HR
# =========================================================

def get_employees_for_hr():
    """Get employee directory for HR."""
    try:
        if not is_hr_or_admin():
            return jsonify({
                "success": False,
                "message": "HR access required"
            }), 403

        db = get_db()

        page = int(
            request.args.get(
                "page",
                1
            )
        )

        limit = int(
            request.args.get(
                "limit",
                100
            )
        )

        search = str(
            request.args.get(
                "search",
                ""
            )
        ).strip()

        query = {
            "role": {
                "$in": [
                    "employee",
                    "Employee",
                    "teamleader",
                    "team_leader",
                    "hr",
                    "HR",
                ]
            }
        }

        if search:
            query["$or"] = [
                {
                    "name": {
                        "$regex": search,
                        "$options": "i",
                    }
                },
                {
                    "email": {
                        "$regex": search,
                        "$options": "i",
                    }
                },
                {
                    "employee_id": {
                        "$regex": search,
                        "$options": "i",
                    }
                },
            ]

        skip = (page - 1) * limit

        employees = list(
            db["users"]
            .find(query)
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
        )

        total = db["users"].count_documents(
            query
        )

        employees = [
            serialize_user(employee)
            for employee in employees
        ]

        return jsonify({
            "success": True,
            "employees": employees,
            "data": employees,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
            },
        }), 200

    except Exception as e:
        logger.error(f"Get employees error: {e}")
        return jsonify({
            "success": False,
            "message": "Failed to fetch employees"
        }), 500

# =========================================================
# DELETE EMPLOYEE FOR HR
# =========================================================

def delete_employee_for_hr(employee_id):
    """Delete an employee from HR employee management."""
    try:
        if not is_hr_or_admin():
            return jsonify({
                "success": False,
                "message": "HR access required"
            }), 403

        db = get_db()

        query = {
            "employee_id": employee_id
        }

        if ObjectId.is_valid(employee_id):
            query = {
                "$or": [
                    {
                        "_id": ObjectId(employee_id)
                    },
                    {
                        "employee_id": employee_id
                    },
                ]
            }

        employee = db["users"].find_one(
            query
        )

        if not employee:
            return jsonify({
                "success": False,
                "message": "Employee not found"
            }), 404

        db["users"].delete_one(
            {
                "_id": employee["_id"]
            }
        )

        return jsonify({
            "success": True,
            "message": "Employee deleted successfully"
        }), 200

    except Exception as e:
        logger.error(f"Delete employee error: {e}")
        return jsonify({
            "success": False,
            "message": "Failed to delete employee"
        }), 500


# =========================================================
# UPDATE EMPLOYEE VERIFICATION FOR HR
# =========================================================

def update_employee_verification(
    employee_id,
    is_verified
):
    """Approve or reject an employee from HR approval."""
    try:
        if not is_hr_or_admin():
            return jsonify({
                "success": False,
                "message": "HR access required"
            }), 403

        db = get_db()

        query = {
            "employee_id": employee_id
        }

        if ObjectId.is_valid(employee_id):
            query = {
                "$or": [
                    {
                        "_id": ObjectId(employee_id)
                    },
                    {
                        "employee_id": employee_id
                    },
                ]
            }

        status = (
            "active"
            if is_verified
            else "rejected"
        )

        result = db["users"].update_one(
            query,
            {
                "$set": {
                    "is_verified": is_verified,
                    "status": status,
                    "updated_at": datetime.utcnow(),
                }
            }
        )

        if result.matched_count == 0:
            return jsonify({
                "success": False,
                "message": "Employee not found"
            }), 404

        employee = db["users"].find_one(
            query
        )

        return jsonify({
            "success": True,
            "message": (
                "Employee approved"
                if is_verified
                else "Employee rejected"
            ),
            "data": serialize_user(employee),
        }), 200

    except Exception as e:
        logger.error(
            f"Employee verification error: {e}"
        )
        return jsonify({
            "success": False,
            "message": "Employee verification failed"
        }), 500

# =========================================================
# GET EMPLOYEE PROFILE
# =========================================================

def get_employee_profile():
    """Get detailed employee profile information"""
    try:
        current_user = request.current_user
        user_id = current_user["user_id"]

        db = get_db()

        user = db["users"].find_one({
            "_id": ObjectId(user_id)
        })

        if not user:
            return jsonify({
                "success": False,
                "message": "Employee not found"
            }), 404

        user_data = serialize_user(user)

        return jsonify({
            "success": True,
            "data": user_data,
        }), 200

    except Exception as e:
        logger.error(f"Profile error: {e}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

# =========================================================
# GET EMPLOYEE STATS
# =========================================================

def get_employee_stats():
    """Get employee attendance and leave statistics"""
    try:
        current_user = request.current_user
        employee_id = current_user["employee_id"]

        db = get_db()

        # =================================================
        # ATTENDANCE STATS
        # =================================================
        
        total_attendance = db["attendance"].count_documents({
            "employee_id": employee_id
        })

        present = db["attendance"].count_documents({
            "employee_id": employee_id,
            "status": "Present"
        })

        late = db["attendance"].count_documents({
            "employee_id": employee_id,
            "status": "Late"
        })

        # Calculate attendance percentage
        attendance_percent = 0
        if total_attendance > 0:
            attendance_percent = round((present / total_attendance) * 100)

        # =================================================
        # LEAVE STATS
        # =================================================
        
        total_leaves = db["leave_requests"].count_documents({
            "employee_id": employee_id
        })

        approved_leaves = db["leave_requests"].count_documents({
            "employee_id": employee_id,
            "status": "approved"
        })

        pending_leaves = db["leave_requests"].count_documents({
            "employee_id": employee_id,
            "status": "pending"
        })

        rejected_leaves = db["leave_requests"].count_documents({
            "employee_id": employee_id,
            "status": "rejected"
        })

        return jsonify({
            "success": True,
            "data": {
                "attendance": {
                    "total": total_attendance,
                    "present": present,
                    "late": late,
                    "percentage": attendance_percent,
                },
                "leaves": {
                    "total": total_leaves,
                    "approved": approved_leaves,
                    "pending": pending_leaves,
                    "rejected": rejected_leaves,
                }
            }
        }), 200

    except Exception as e:
        logger.error(f"Stats error: {e}")
        return jsonify({
            "success": False,
            "message": "Failed to fetch statistics"
        }), 500

# =========================================================
# UPDATE EMPLOYEE PROFILE
# =========================================================

def update_employee_profile():
    """Update employee profile information"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "message": "Request body required"
            }), 400

        current_user = request.current_user
        user_id = current_user["user_id"]

        db = get_db()

        # =================================================
        # ALLOWED FIELDS
        # =================================================
        
        allowed_fields = [
            "phone",
            "address",
            "city",
            "state",
            "pincode",
            "emergency_contact",
            "emergency_phone",
            "bio",
        ]

        update_data = {}
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]

        if not update_data:
            return jsonify({
                "success": False,
                "message": "No valid fields to update"
            }), 400

        update_data["updated_at"] = datetime.utcnow()

        # =================================================
        # UPDATE
        # =================================================
        
        result = db["users"].update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )

        if result.modified_count == 0:
            return jsonify({
                "success": False,
                "message": "No changes made"
            }), 400

        logger.info(f"Profile updated: {user_id}")

        return jsonify({
            "success": True,
            "message": "Profile updated successfully"
        }), 200

    except Exception as e:
        logger.error(f"Update profile error: {e}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

# =========================================================
# GET EMPLOYEE DASHBOARD
# =========================================================

def get_employee_dashboard():
    """Get comprehensive employee dashboard data"""
    try:
        current_user = request.current_user
        user_id = current_user["user_id"]
        employee_id = current_user["employee_id"]

        db = get_db()

        # =================================================
        # USER PROFILE
        # =================================================
        
        user = db["users"].find_one({
            "_id": ObjectId(user_id)
        })

        if not user:
            return jsonify({
                "success": False,
                "message": "Employee not found"
            }), 404

        user_data = serialize_user(user)

        # =================================================
        # TODAY'S ATTENDANCE
        # =================================================
        
        from datetime import date
        today = date.today().strftime("%Y-%m-%d")
        
        today_attendance = db["attendance"].find_one({
            "employee_id": employee_id,
            "date": today
        })

        # =================================================
        # ATTENDANCE STATS
        # =================================================
        
        total_attendance = db["attendance"].count_documents({
            "employee_id": employee_id
        })

        present = db["attendance"].count_documents({
            "employee_id": employee_id,
            "status": "Present"
        })

        late = db["attendance"].count_documents({
            "employee_id": employee_id,
            "status": "Late"
        })

        attendance_percent = 0
        if total_attendance > 0:
            attendance_percent = round((present / total_attendance) * 100)

        # =================================================
        # LEAVE STATS
        # =================================================
        
        approved_leaves = db["leave_requests"].count_documents({
            "employee_id": employee_id,
            "status": "approved"
        })

        pending_leaves = db["leave_requests"].count_documents({
            "employee_id": employee_id,
            "status": "pending"
        })

        return jsonify({
            "success": True,
            "data": {
                "profile": user_data,
                "today_attendance": {
                    "marked": today_attendance is not None,
                    "check_in": today_attendance.get("check_in") if today_attendance else None,
                    "status": today_attendance.get("status") if today_attendance else "Not Marked",
                },
                "stats": {
                    "attendance_percent": attendance_percent,
                    "total_days": total_attendance,
                    "present_days": present,
                    "late_days": late,
                    "approved_leaves": approved_leaves,
                    "pending_leaves": pending_leaves,
                }
            }
        }), 200

    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

# =========================================================
# GET HR DASHBOARD SUMMARY
# =========================================================

def get_hr_dashboard_summary():
    """Get workforce summary for HR dashboard."""
    try:
        db = get_db()
        today = datetime.utcnow().strftime("%Y-%m-%d")

        employees = list(
            db["users"].find(
                get_hr_employee_query(),
                {
                    "employee_id": 1,
                    "email": 1,
                }
            )
        )

        total_employees = len(employees)

        employee_ids = [
            employee.get("employee_id")
            for employee in employees
            if employee.get("employee_id")
        ]

        employee_emails = [
            employee.get("email")
            for employee in employees
            if employee.get("email")
        ]

        today_records = get_attendance_for_hr_date(
            db,
            today,
            employee_ids,
            employee_emails
        )

        if not today_records:
            latest_date = get_latest_attendance_date(db)

            if latest_date:
                today = latest_date
                today_records = get_attendance_for_hr_date(
                    db,
                    today,
                    employee_ids,
                    employee_emails
                )

        present_employees = len([
            record for record in today_records
            if str(record.get("status", "")).lower()
            == "present"
        ])

        late_entries = len([
            record for record in today_records
            if str(record.get("status", "")).lower()
            == "late"
        ])

        attended_employees = len(set([
            record.get("employee_id") or
            record.get("email")
            for record in today_records
            if record.get("employee_id") or
            record.get("email")
        ]))
        absent_employees = max(
            total_employees - attended_employees,
            0
        )

        attendance_rate = 0
        if total_employees > 0:
            attendance_rate = round(
                (attended_employees / total_employees) * 100
            )

        pending_leaves = db["leave_requests"].count_documents({
            "status": "pending"
        })

        pending_wfh = db["wfh_requests"].count_documents({
            "status": "pending"
        })

        return jsonify({
            "success": True,
            "data": {
                "totalEmployees": total_employees,
                "total_employees": total_employees,
                "attendanceRate": attendance_rate,
                "attendance_rate": attendance_rate,
                "presentEmployees": present_employees,
                "present_employees": present_employees,
                "todayAttendance": attended_employees,
                "today_attendance": attended_employees,
                "lateEntries": late_entries,
                "late_entries": late_entries,
                "absentEmployees": absent_employees,
                "absent_employees": absent_employees,
                "pendingLeaves": pending_leaves,
                "pending_leaves": pending_leaves,
                "pendingWFH": pending_wfh,
                "pending_wfh": pending_wfh,
                "pendingRequests": pending_leaves + pending_wfh,
                "pending_requests": pending_leaves + pending_wfh,
            }
        }), 200

    except Exception as e:
        logger.error(f"HR dashboard error: {e}")
        return jsonify({
            "success": False,
            "message": "Failed to fetch HR dashboard"
        }), 500

# =========================================================
# GET HR ANALYTICS
# =========================================================

def get_hr_analytics():
    """Get attendance analytics for the HR analytics screen."""
    try:
        if not is_hr_or_admin():
            return jsonify({
                "success": False,
                "message": "HR access required"
            }), 403

        db = get_db()
        today = datetime.utcnow().strftime("%Y-%m-%d")

        employees = list(
            db["users"].find(
                get_hr_employee_query(),
                {
                    "employee_id": 1,
                    "email": 1,
                    "department": 1,
                }
            )
        )

        total_employees = len(employees)
        employee_ids = [
            employee.get("employee_id")
            for employee in employees
            if employee.get("employee_id")
        ]

        employee_emails = [
            employee.get("email")
            for employee in employees
            if employee.get("email")
        ]

        today_records = get_attendance_for_hr_date(
            db,
            today,
            employee_ids,
            employee_emails
        )

        if not today_records:
            latest_date = get_latest_attendance_date(db)

            if latest_date:
                today = latest_date
                today_records = get_attendance_for_hr_date(
                    db,
                    today,
                    employee_ids,
                    employee_emails
                )

        present_employees = len([
            record for record in today_records
            if str(record.get("status", "")).lower()
            == "present"
        ])

        late_entries = len([
            record for record in today_records
            if str(record.get("status", "")).lower()
            == "late"
        ])

        attended_employees = len(set([
            record.get("employee_id") or
            record.get("email")
            for record in today_records
            if record.get("employee_id") or
            record.get("email")
        ]))

        absent_employees = max(
            total_employees - attended_employees,
            0
        )

        attendance_rate = 0
        if total_employees > 0:
            attendance_rate = round(
                (attended_employees / total_employees) * 100
            )

        pending_leaves = db["leave_requests"].count_documents({
            "status": "pending"
        })

        pending_wfh = db["wfh_requests"].count_documents({
            "status": "pending"
        })

        departments = {}
        for employee in employees:
            department = (
                employee.get("department") or
                "General"
            )
            departments.setdefault(
                department,
                {
                    "department": department,
                    "total": 0,
                    "attended": 0,
                    "percentage": 0,
                }
            )
            departments[department]["total"] += 1

        attended_ids = set([
            str(
                record.get("employee_id") or
                record.get("email")
            ).strip().lower()
            for record in today_records
            if record.get("employee_id") or
            record.get("email")
        ])

        for employee in employees:
            employee_keys = [
                employee.get("employee_id"),
                employee.get("email"),
            ]
            department = (
                employee.get("department") or
                "General"
            )

            if any(
                str(key).strip().lower()
                in attended_ids
                for key in employee_keys
                if key
            ):
                departments[department]["attended"] += 1

        for department in departments.values():
            if department["total"] > 0:
                department["percentage"] = round(
                    (
                        department["attended"] /
                        department["total"]
                    ) * 100
                )

        confidence_values = [
            float(record.get("confidence", 0))
            for record in today_records
            if record.get("confidence") is not None
        ]

        ai_accuracy = 98
        if confidence_values:
            ai_accuracy = round(
                sum(confidence_values) /
                len(confidence_values)
            )

        spoof_attempts = len([
            record for record in today_records
            if record.get("spoof_detected") is True
        ])

        return jsonify({
            "success": True,
            "data": {
                "date": today,
                "totalEmployees": total_employees,
                "total_employees": total_employees,
                "attendanceRate": attendance_rate,
                "attendance_rate": attendance_rate,
                "presentEmployees": present_employees,
                "present_employees": present_employees,
                "absentEmployees": absent_employees,
                "absent_employees": absent_employees,
                "lateEntries": late_entries,
                "late_entries": late_entries,
                "pendingLeaves": pending_leaves,
                "pending_leaves": pending_leaves,
                "pendingWFH": pending_wfh,
                "pending_wfh": pending_wfh,
                "pendingRequests": pending_leaves + pending_wfh,
                "pending_requests": pending_leaves + pending_wfh,
                "aiAccuracy": ai_accuracy,
                "ai_accuracy": ai_accuracy,
                "spoofAttempts": spoof_attempts,
                "spoof_attempts": spoof_attempts,
                "blinkVerification": True,
                "blink_verification": True,
                "departments": list(departments.values()),
            }
        }), 200

    except Exception as e:
        logger.error(f"HR analytics error: {e}")
        return jsonify({
            "success": False,
            "message": "Failed to fetch HR analytics"
        }), 500

# =========================================================
# GET RECENT ACTIVITY
# =========================================================

def get_recent_activity():
    """Get recent attendance and leave activity"""
    try:
        current_user = request.current_user
        employee_id = current_user["employee_id"]

        db = get_db()

        # =================================================
        # RECENT ATTENDANCE
        # =================================================
        
        recent_attendance = list(
            db["attendance"]
            .find({"employee_id": employee_id})
            .sort("created_at", -1)
            .limit(5)
        )

        for record in recent_attendance:
            record["_id"] = str(record["_id"])

        # =================================================
        # RECENT LEAVES
        # =================================================
        
        recent_leaves = list(
            db["leave_requests"]
            .find({"employee_id": employee_id})
            .sort("created_at", -1)
            .limit(5)
        )

        for record in recent_leaves:
            record["_id"] = str(record["_id"])

        return jsonify({
            "success": True,
            "data": {
                "recent_attendance": recent_attendance,
                "recent_leaves": recent_leaves,
            }
        }), 200

    except Exception as e:
        logger.error(f"Recent activity error: {e}")
        return jsonify({
            "success": False,
            "message": "Failed to fetch activity"
        }), 500
