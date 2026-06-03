"""
Work From Home Routes - WFH Requests
"""

from flask import Blueprint
from flask_jwt_extended import jwt_required
from controllers.wfh_controller import (
    create_wfh_request,
    get_my_wfh_requests,
    get_pending_wfh_requests,
    approve_wfh_request,
    reject_wfh_request,
)
from utils.db import get_db

wfh_bp = Blueprint(
    'wfh',
    __name__,
    url_prefix='/api/wfh'
)

@wfh_bp.route('/request', methods=['POST'])
@jwt_required()
def create_wfh():
    db = get_db()
    return create_wfh_request(db)

@wfh_bp.route('/my-requests', methods=['GET'])
@jwt_required()
def my_wfh_requests():
    db = get_db()
    return get_my_wfh_requests(db)

@wfh_bp.route('/pending', methods=['GET'])
@jwt_required()
def pending_wfh_requests():
    db = get_db()
    return get_pending_wfh_requests(db)

@wfh_bp.route('/<wfh_id>/approve', methods=['POST'])
@jwt_required()
def approve_wfh(wfh_id):
    db = get_db()
    return approve_wfh_request(db, wfh_id)

@wfh_bp.route('/<wfh_id>/reject', methods=['POST'])
@jwt_required()
def reject_wfh(wfh_id):
    db = get_db()
    return reject_wfh_request(db, wfh_id)
