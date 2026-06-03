"""
Enterprise Attendance Routes
"""

from flask import (
Blueprint,
jsonify,
request,
)

from utils.jwt_utils import (
require_auth,
require_admin,
require_hr,
require_teamleader,
require_employee,
)

from controllers.attendance_controller import (
mark_attendance,
get_all_attendance,
get_student_attendance,
get_attendance_report,
get_monthly_attendance_report,
export_csv,
get_employee_report,
)

# =====================================================

# BLUEPRINT

# =====================================================

attendance_bp = Blueprint(
"attendance",
__name__,
url_prefix="/api/attendance"
)

# =====================================================

# HEALTH

# =====================================================

@attendance_bp.route(
"/health",
methods=["GET"]
)
def attendance_health():
    return jsonify({
        "success": True,
        "service": "Attendance",
        "status": "running",
    }), 200

# =====================================================

# TEST

# =====================================================

@attendance_bp.route(
"/test123",
methods=["GET"]
)
def attendance_test():
    return jsonify({
        "success": True,
        "message": "Attendance routes working"
    }), 200

# =====================================================

# MARK ATTENDANCE

# =====================================================

@attendance_bp.route(
"/mark",
methods=["POST"]
)
@require_auth
def mark():
    return mark_attendance()

# =====================================================

# FACE ATTENDANCE

# =====================================================

@attendance_bp.route(
"/face-mark",
methods=["POST"]
)
@require_auth
def face_mark():
    return mark_attendance()

# =====================================================

# TODAY ATTENDANCE

# =====================================================

@attendance_bp.route(
"/today",
methods=["GET"]
)
@require_auth
def today_attendance():
    return get_attendance_report()

# =====================================================

# LIVE ATTENDANCE

# =====================================================

@attendance_bp.route(
"/live",
methods=["GET"]
)
@require_admin
def live_attendance():
    return get_all_attendance()

# =====================================================

# ALL ATTENDANCE

# =====================================================

@attendance_bp.route(
"/all",
methods=["GET"]
)
@require_admin
def all_attendance():
    return get_all_attendance()

# =====================================================

# HR ATTENDANCE OVERVIEW

# =====================================================

@attendance_bp.route(
"/overview",
methods=["GET"]
)
@require_auth
def hr_attendance_overview():
    role = str(
        request.current_user.get(
            "role",
            ""
        )
    ).lower()

    if role not in [
        "hr",
        "admin",
    ]:
        return jsonify({
            "success": False,
            "message": "HR access required"
        }), 403

    return get_all_attendance()

# =====================================================

# EMPLOYEE ATTENDANCE

# =====================================================

@attendance_bp.route(
"/employee/<employee_id>",
methods=["GET"]
)
@require_auth
def employee_attendance(employee_id):
    return get_student_attendance(
        employee_id
    )

# =====================================================

# MY ATTENDANCE

# =====================================================

@attendance_bp.route(
"/my-attendance",
methods=["GET"]
)
@require_auth
def my_attendance():
    current_user = request.current_user

    employee_id = current_user[
        "employee_id"
    ]

    return get_student_attendance(
        employee_id
    )

# =====================================================

# MY RECORD

# =====================================================

@attendance_bp.route(
"/my-record",
methods=["GET"]
)
@require_auth
def my_record():
    current_user = request.current_user

    employee_id = current_user[
        "employee_id"
    ]

    return get_student_attendance(
        employee_id
    )

# =====================================================

# TEAM ATTENDANCE

# =====================================================

@attendance_bp.route(
"/team",
methods=["GET"]
)
@require_teamleader
def team_attendance():
    return get_all_attendance()

# =====================================================

# REPORT

# =====================================================

@attendance_bp.route(
"/report",
methods=["GET"]
)
@require_hr
def report():
    return get_attendance_report()

# =====================================================

# MONTHLY REPORT

# =====================================================

@attendance_bp.route(
"/monthly-report",
methods=["GET"]
)
@require_hr
def monthly_report():
    return get_monthly_attendance_report()

# =====================================================

# EMPLOYEE REPORT

# =====================================================

@attendance_bp.route(
"/my-report",
methods=["GET"]
)
@require_auth
def my_report():
    return get_employee_report()

# =====================================================

# ANALYTICS

# =====================================================

@attendance_bp.route(
"/analytics",
methods=["GET"]
)
@require_admin
def analytics():
    return get_all_attendance()

# =====================================================

# SUMMARY

# =====================================================

@attendance_bp.route(
"/summary",
methods=["GET"]
)
@require_auth
def summary():
    return get_attendance_report()

@attendance_bp.route(
"/my-today",
methods=["GET"]
)
@require_auth
def my_today():
    from controllers.attendance_controller import get_my_today_attendance
    return get_my_today_attendance()

# =====================================================

# EXPORT CSV

# =====================================================

@attendance_bp.route(
"/export/csv",
methods=["GET"]
)
@require_hr
def export_attendance_csv():
    return export_csv()

# =====================================================

# EXPORT PDF

# =====================================================

@attendance_bp.route(
"/export/pdf",
methods=["GET"]
)
@require_hr
def export_attendance_pdf():
    return export_csv()

# =====================================================

# ROUTES LIST

# =====================================================

@attendance_bp.route(
"/routes",
methods=["GET"]
)
def attendance_routes_list():
    return jsonify({

        "success": True,

        "routes": [

            "/api/attendance/health",
            "/api/attendance/test123",
            "/api/attendance/mark",
            "/api/attendance/face-mark",
            "/api/attendance/today",
            "/api/attendance/live",
            "/api/attendance/all",
            "/api/attendance/overview",
            "/api/attendance/employee/<employee_id>",
            "/api/attendance/my-attendance",
            "/api/attendance/my-record",
            "/api/attendance/team",
            "/api/attendance/report",
            "/api/attendance/monthly-report",
            "/api/attendance/my-report",
            "/api/attendance/analytics",
            "/api/attendance/summary",
            "/api/attendance/export/csv",
            "/api/attendance/export/pdf"

        ]

    }), 200
