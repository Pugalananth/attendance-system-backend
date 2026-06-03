from datetime import datetime
from bson import ObjectId
from flask import current_app, request
from utils.db import get_db
from utils.jwt_utils import (
    require_auth,
    require_employee,
    require_hr,
)

# ═════════════════════════════════════════════
# WFH REQUEST SUBMISSION
# ═════════════════════════════════════════════

@require_employee
def request_wfh():
    """Submit WFH request"""
    current_user = request.current_user
    data = request.get_json() or {}

    try:
        db = get_db()
        
        # Get full employee document
        employee = db["users"].find_one({
            "employee_id": current_user["employee_id"],
            "is_active": True,
        })

        if not employee:
            return {
                'success': False,
                'message': 'Employee not found'
            }, 404
        
        # Validate fields
        required = ['wfh_type', 'start_date', 'end_date', 'work_location', 'reason']
        missing = [f for f in required if not data.get(f)]
        
        if missing:
            return {
                'success': False,
                'message': f'Missing fields: {", ".join(missing)}'
            }, 400

        # Parse dates
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()

        if end_date < start_date:
            return {
                'success': False,
                'message': 'End date cannot be before start date'
            }, 400

        # Calculate days
        delta = end_date - start_date
        total_days = delta.days + 1

        # Create WFH request
        wfh_request = {
            'employee_id': current_user["employee_id"],
            'employee_name': employee.get('name', ''),
            'employee_email': employee.get('email', ''),
            'department': employee.get('department', 'Not Assigned'),
            'wfh_type': data['wfh_type'],
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'total_days': total_days,
            'work_location': data['work_location'],
            'reason': data['reason'],
            'status': 'pending',
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
        }

        result = db.wfh_requests.insert_one(wfh_request)

        return {
            'success': True,
            'message': 'WFH request submitted successfully',
            'data': {
                'wfh_id': str(result.inserted_id),
                'status': 'pending'
            }
        }, 201

    except ValueError as e:
        return {
            'success': False,
            'message': f'Invalid date format: {str(e)}'
        }, 400
    except Exception as e:
        current_app.logger.error(f'WFH submission error: {str(e)}')
        return {
            'success': False,
            'message': f'Server error: {str(e)}'
        }, 500


# ═════════════════════════════════════════════
# GET MY WFH REQUESTS
# ═════════════════════════════════════════════

@require_auth
def get_my_wfh_requests():
    """Get current user's WFH requests"""
    current_user = request.current_user

    try:
        db = get_db()
        
        requests_list = list(db.wfh_requests.find({
            'employee_id': current_user["employee_id"]
        }))

        for req in requests_list:
            req['_id'] = str(req['_id'])
            req['employee_id'] = str(req['employee_id'])

        return {
            'success': True,
            'data': requests_list
        }, 200

    except Exception as e:
        current_app.logger.error(f'Get WFH requests error: {str(e)}')
        return {
            'success': False,
            'message': f'Server error: {str(e)}'
        }, 500


# ═════════════════════════════════════════════
# GET ALL WFH REQUESTS (HR/ADMIN)
# ═════════════════════════════════════════════

@require_hr
def get_all_wfh_requests():
    """Get all pending WFH requests (HR view)"""
    try:
        db = get_db()
        status = request.args.get('status')
        query = {}

        if status and status != 'all':
            query['status'] = status
        
        requests_list = list(db.wfh_requests.find(
            query
        ).sort('created_at', -1))

        for req in requests_list:
            req['_id'] = str(req['_id'])
            req['employee_id'] = str(req['employee_id'])

        return {
            'success': True,
            'data': requests_list
        }, 200

    except Exception as e:
        current_app.logger.error(f'Get all WFH requests error: {str(e)}')
        return {
            'success': False,
            'message': f'Server error: {str(e)}'
        }, 500


# ═════════════════════════════════════════════
# APPROVE WFH REQUEST
# ═════════════════════════════════════════════

@require_hr
def approve_wfh(wfh_id):
    """Approve WFH request"""
    try:
        db = get_db()
        
        result = db.wfh_requests.update_one(
            {'_id': ObjectId(wfh_id)},
            {
                '$set': {
                    'status': 'approved',
                    'updated_at': datetime.utcnow().isoformat()
                }
            }
        )

        if result.matched_count == 0:
            return {
                'success': False,
                'message': 'WFH request not found'
            }, 404

        return {
            'success': True,
            'message': 'WFH request approved'
        }, 200

    except Exception as e:
        current_app.logger.error(f'Approve WFH error: {str(e)}')
        return {
            'success': False,
            'message': f'Server error: {str(e)}'
        }, 500


# ═════════════════════════════════════════════
# REJECT WFH REQUEST
# ═════════════════════════════════════════════

@require_hr
def reject_wfh(wfh_id):
    """Reject WFH request"""
    data = request.get_json() or {}
    reason = data.get('reason', 'Rejected by HR')

    try:
        db = get_db()
        
        result = db.wfh_requests.update_one(
            {'_id': ObjectId(wfh_id)},
            {
                '$set': {
                    'status': 'rejected',
                    'rejection_reason': reason,
                    'updated_at': datetime.utcnow().isoformat()
                }
            }
        )

        if result.matched_count == 0:
            return {
                'success': False,
                'message': 'WFH request not found'
            }, 404

        return {
            'success': True,
            'message': 'WFH request rejected'
        }, 200

    except Exception as e:
        current_app.logger.error(f'Reject WFH error: {str(e)}')
        return {
            'success': False,
            'message': f'Server error: {str(e)}'
        }, 500


# ═════════════════════════════════════════════
# CANCEL WFH REQUEST
# ═════════════════════════════════════════════

@require_auth
def cancel_wfh(wfh_id):
    """Cancel own WFH request"""
    current_user = request.current_user

    try:
        db = get_db()
        
        # Check if user owns this request
        wfh_req = db.wfh_requests.find_one({'_id': ObjectId(wfh_id)})
        
        if not wfh_req:
            return {
                'success': False,
                'message': 'WFH request not found'
            }, 404

        if str(wfh_req['employee_id']) != str(current_user['employee_id']):
            return {
                'success': False,
                'message': 'Unauthorized'
            }, 403

        if wfh_req['status'] != 'pending':
            return {
                'success': False,
                'message': f'Cannot cancel {wfh_req["status"]} request'
            }, 400

        result = db.wfh_requests.update_one(
            {'_id': ObjectId(wfh_id)},
            {
                '$set': {
                    'status': 'cancelled',
                    'updated_at': datetime.utcnow().isoformat()
                }
            }
        )

        return {
            'success': True,
            'message': 'WFH request cancelled'
        }, 200

    except Exception as e:
        current_app.logger.error(f'Cancel WFH error: {str(e)}')
        return {
            'success': False,
            'message': f'Server error: {str(e)}'
        }, 500


# ═════════════════════════════════════════════
# GET WFH SUMMARY
# ═════════════════════════════════════════════

@require_auth
def get_wfh_summary():
    """Get WFH summary for current user"""
    current_user = request.current_user

    try:
        db = get_db()
        
        pipeline = [
            {'$match': {'employee_id': current_user["employee_id"]}},
            {
                '$group': {
                    '_id': '$status',
                    'count': {'$sum': 1},
                    'total_days': {'$sum': '$total_days'}
                }
            }
        ]

        results = list(db.wfh_requests.aggregate(pipeline))

        summary = {
            'pending': 0,
            'approved': 0,
            'rejected': 0,
            'cancelled': 0,
            'pending_days': 0,
            'approved_days': 0
        }

        for result in results:
            status = result['_id']
            if status in summary:
                summary[status] = result['count']
                if status == 'pending':
                    summary['pending_days'] = result['total_days']
                elif status == 'approved':
                    summary['approved_days'] = result['total_days']

        return {
            'success': True,
            'data': summary
        }, 200

    except Exception as e:
        current_app.logger.error(f'Get WFH summary error: {str(e)}')
        return {
            'success': False,
            'message': f'Server error: {str(e)}'
        }, 500
