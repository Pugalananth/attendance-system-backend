"""Student Routes"""
from flask import Blueprint
from controllers.student_controller import (
    get_all_students,
    add_student,
    update_student,
    delete_student,
    get_student,
    get_dashboard_stats,
)
from utils.jwt_utils import require_admin, require_auth

student_bp = Blueprint("students", __name__)


@student_bp.route("", methods=["GET"])
@require_admin
def list_students():
    return get_all_students()


@student_bp.route("/add", methods=["POST"])
@require_admin
def create_student():
    return add_student()


@student_bp.route("/update/<student_id>", methods=["PUT"])
@require_admin
def edit_student(student_id):
    return update_student(student_id)


@student_bp.route("/delete/<student_id>", methods=["DELETE"])
@require_admin
def remove_student(student_id):
    return delete_student(student_id)


@student_bp.route("/<student_id>", methods=["GET"])
@require_auth
def single_student(student_id):
    return get_student(student_id)


@student_bp.route("/stats/dashboard", methods=["GET"])
@require_admin
def dashboard_stats():
    return get_dashboard_stats()
