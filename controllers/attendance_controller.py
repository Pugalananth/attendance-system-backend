"""
Enterprise Attendance Controller
AI Employee Attendance Management System
"""

import io
import csv
import logging
import calendar

from datetime import (
    datetime,
    date,
    time,
    timedelta
)

from flask import (
    request,
    jsonify,
    make_response,
)

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

    return [
        serialize_doc(doc)
        for doc in docs
    ]

# =========================================================
# MARK ATTENDANCE
# =========================================================

def mark_attendance():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Request body required"}), 400

        employee_id = str(data.get("employee_id", "")).strip()
        confidence = float(data.get("confidence", 0))
        location = data.get("location", "Office")
        check_type = data.get("type", "check_in") # 'check_in' or 'check_out'
        device_info = request.headers.get("User-Agent", "Mobile App")

        if not employee_id:
            return jsonify({"success": False, "message": "Employee ID required"}), 400

        db = get_db()
        employee = db["users"].find_one({"employee_id": employee_id, "is_active": True})

        if not employee:
            return jsonify({"success": False, "message": "Employee not found"}), 404

        now = datetime.now()
        today = now.strftime("%Y-%m-%d")
        current_time_str = now.strftime("%I:%M %p")

        if check_type == "check_in":
            # DUPLICATE CHECK
            existing = db["attendance"].find_one({"employee_id": employee_id, "date": today})
            if existing:
                return jsonify({"success": False, "message": "Already checked in today"}), 409

            # LATE LOGIC
            is_late = False
            late_minutes = 0

            company_settings = db.company_settings.find_one({})
            if company_settings and company_settings.get("workingStartTime"):
                try:
                    start_time_str = company_settings.get("workingStartTime")
                    # Start time format usually "09:00 AM"
                    start_time_obj = datetime.strptime(start_time_str, "%I:%M %p").time()
                    current_time_obj = now.time()

                    if current_time_obj > start_time_obj:
                        is_late = True
                        # Calculate late minutes
                        diff = datetime.combine(date.today(), current_time_obj) - datetime.combine(date.today(), start_time_obj)
                        late_minutes = int(diff.total_seconds() / 60)
                except Exception as ex:
                    logger.error(f"Late calculation error: {ex}")

            attendance_doc = {
                "employee_id": employee_id,
                "employee_name": employee.get("name", ""),
                "department": employee.get("department", ""),
                "role": employee.get("role", "employee"),
                "date": today,
                "check_in": current_time_str,
                "check_out": None,
                "status": "Present",
                "isLate": is_late,
                "lateMinutes": late_minutes,
                "confidence": confidence,
                "location": location,
                "device_info": device_info,
                "ai_verified": True,
                "created_at": datetime.utcnow(),
            }

            result = db["attendance"].insert_one(attendance_doc)
            attendance_doc["_id"] = str(result.inserted_id)

            return jsonify({"success": True, "message": "Checked in successfully", "data": attendance_doc}), 201

        elif check_type == "check_out":
            existing = db["attendance"].find_one({"employee_id": employee_id, "date": today})
            if not existing:
                return jsonify({"success": False, "message": "No check-in record found for today"}), 404

            if existing.get("check_out"):
                return jsonify({"success": False, "message": "Already checked out today"}), 409

            db["attendance"].update_one(
                {"_id": existing["_id"]},
                {"$set": {"check_out": current_time_str, "updated_at": datetime.utcnow()}}
            )

            return jsonify({"success": True, "message": "Checked out successfully"}), 200

        else:
            return jsonify({"success": False, "message": "Invalid check type"}), 400

    except Exception as e:
        logger.error(f"Mark attendance error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

def get_all_attendance():
    try:
        db = get_db()
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 50))
        skip = (page - 1) * limit
        records = list(db["attendance"].find().sort("created_at", -1).skip(skip).limit(limit))
        total = db["attendance"].count_documents({})
        records = serialize_list(records)
        return jsonify({"success": True, "data": {"records": records, "pagination": {"page": page, "limit": limit, "total": total}}}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

def get_student_attendance(employee_id):
    try:
        db = get_db()
        records = list(db["attendance"].find({"employee_id": employee_id}).sort("created_at", -1))
        records = serialize_list(records)
        return jsonify({"success": True, "data": records}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

def get_attendance_report():
    try:
        db = get_db()
        today = date.today().strftime("%Y-%m-%d")
        total_staff = db["users"].count_documents({"role": {"$ne": "admin"}})
        records = list(db["attendance"].find({"date": today}).sort("created_at", -1))

        present_count = len(records)
        late_count = len([r for r in records if r.get("isLate") == True])

        return jsonify({
            "success": True,
            "data": {
                "date": today,
                "total": total_staff,
                "present": present_count,
                "late": late_count,
                "records": serialize_list(records)
            }
        }), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

def get_monthly_attendance_report():
    try:
        db = get_db()
        now = datetime.now()
        year = int(request.args.get("year", now.year))
        month = int(request.args.get("month", now.month))
        filter_type = request.args.get("filter", "Monthly") # Today, Weekly, Monthly

        total_staff = db["users"].count_documents({"role": {"$ne": "admin"}})

        if filter_type == "Today":
            start_date = now.strftime("%Y-%m-%d")
            end_date = now.strftime("%Y-%m-%d")
        elif filter_type == "Weekly":
            start_of_week = now - timedelta(days=now.weekday())
            start_date = start_of_week.strftime("%Y-%m-%d")
            end_date = now.strftime("%Y-%m-%d")
        else: # Monthly
            start_date = f"{year}-{month:02d}-01"
            last_day = calendar.monthrange(year, month)[1]
            end_date = f"{year}-{month:02d}-{last_day:02d}"

        query = {"date": {"$gte": start_date, "$lte": end_date}}
        records = list(db["attendance"].find(query).sort("created_at", -1))

        # summary stats
        present_count = len(records)
        late_count = len([r for r in records if r.get("isLate") == True])

        # Today's specific counts for leaves/wfh
        on_leave = db.leave_requests.count_documents({"status": "approved", "start_date": {"$lte": now.strftime("%Y-%m-%d")}, "end_date": {"$gte": now.strftime("%Y-%m-%d")}})
        on_wfh = db.wfh_requests.count_documents({"status": "approved", "date": now.strftime("%Y-%m-%d")})

        return jsonify({
            "success": True,
            "data": {
                "records": serialize_list(records),
                "summary": {
                    "total": total_staff,
                    "present": present_count,
                    "late": late_count,
                    "onLeave": on_leave,
                    "onWFH": on_wfh
                }
            }
        }), 200
    except Exception as e:
        logger.error(f"Report fetch error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

def export_csv():
    try:
        db = get_db()
        records = list(db["attendance"].find())
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Employee ID", "Employee Name", "Department", "Date", "Check In", "Check Out", "Status", "Is Late"])
        for r in records:
            writer.writerow([r.get("employee_id"), r.get("employee_name"), r.get("department"), r.get("date"), r.get("check_in"), r.get("check_out"), r.get("status"), r.get("isLate")])
        response = make_response(output.getvalue())
        response.headers["Content-Type"] = "text/csv"
        response.headers["Content-Disposition"] = "attachment; filename=attendance.csv"
        return response
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

def get_employee_report():
    try:
        current_user = request.current_user
        db = get_db()
        records = list(db["attendance"].find({"employee_id": current_user["employee_id"]}))
        stats = {
            "total": len(records),
            "present": len([r for r in records if r.get("status") == "Present"]),
            "late": len([r for r in records if r.get("isLate") == True])
        }
        return jsonify({"success": True, "data": stats})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

def get_my_today_attendance():
    try:
        current_user = request.current_user
        db = get_db()
        today = datetime.now().strftime("%Y-%m-%d")
        record = db["attendance"].find_one({"employee_id": current_user["employee_id"], "date": today})
        return jsonify({"success": True, "data": serialize_doc(record) if record else None}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
