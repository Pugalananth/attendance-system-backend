"""
Attendance Routes - Check-in, Check-out, History
"""

from flask import Blueprint
from flask_jwt_extended import jwt_required
from controllers.attendance_controller_new import (
    check_in,
    check_out,
    get_attendance_history,
    get_daily_summary,
)
from utils.db import get_db

attendance_bp = Blueprint(
    'attendance',
    __name__,
    url_prefix='/api/attendance'
)

@attendance_bp.route('/check-in', methods=['POST'])
@jwt_required()
def employee_check_in():
    db = get_db()
    return check_in(db)

@attendance_bp.route('/check-out', methods=['POST'])
@jwt_required()
def employee_check_out():
    db = get_db()
    return check_out(db)

@attendance_bp.route('/history', methods=['GET'])
@jwt_required()
def attendance_history():
    db = get_db()
    return get_attendance_history(db)

@attendance_bp.route('/daily-summary', methods=['GET'])
@jwt_required()
def daily_summary():
    db = get_db()
    return get_daily_summary(db)
