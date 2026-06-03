from flask import Blueprint
from controllers.wfh_controller import (
    request_wfh,
    get_my_wfh_requests,
    get_all_wfh_requests,
    approve_wfh,
    reject_wfh,
    cancel_wfh,
    get_wfh_summary,
)

# Create Blueprint
wfh_bp = Blueprint('wfh', __name__)

# ════════════════════════════════════════════════
# ROUTES
# ════════════════════════════════════════════════

# Health check
@wfh_bp.route('/health', methods=['GET'])
def wfh_health():
    return {
        'service': 'WFH',
        'status': 'running',
        'success': True
    }, 200


# Submit WFH request
@wfh_bp.route('/request', methods=['POST'])
def request_wfh_route():
    return request_wfh()


# Get my WFH requests
@wfh_bp.route('/my-requests', methods=['GET'])
def my_wfh_requests():
    return get_my_wfh_requests()


# Get all WFH requests (HR)
@wfh_bp.route('/all', methods=['GET'])
def all_wfh_requests():
    return get_all_wfh_requests()


# Approve WFH request
@wfh_bp.route('/approve/<wfh_id>', methods=['POST'])
def approve_wfh_route(wfh_id):
    return approve_wfh(wfh_id)


# Reject WFH request
@wfh_bp.route('/reject/<wfh_id>', methods=['POST'])
def reject_wfh_route(wfh_id):
    return reject_wfh(wfh_id)


# Cancel WFH request
@wfh_bp.route('/cancel/<wfh_id>', methods=['POST'])
def cancel_wfh_route(wfh_id):
    return cancel_wfh(wfh_id)


# Get WFH summary
@wfh_bp.route('/summary', methods=['GET'])
def wfh_summary():
    return get_wfh_summary()


# Routes list
@wfh_bp.route('/routes', methods=['GET'])
def wfh_routes_list():
    return {
        'success': True,
        'routes': [
            'POST /api/wfh/request',
            'GET /api/wfh/my-requests',
            'GET /api/wfh/all',
            'POST /api/wfh/approve/<wfh_id>',
            'POST /api/wfh/reject/<wfh_id>',
            'POST /api/wfh/cancel/<wfh_id>',
            'GET /api/wfh/summary',
        ]
    }, 200
