"""
Task Routes - Work Assignment
"""

from flask import Blueprint
from utils.jwt_utils import (
    require_auth,
    require_teamleader,
)
from controllers.task_controller import (
    create_task,
    get_team_tasks,
    get_my_tasks,
    update_task_status,
    delete_task,
)
from utils.db import get_db

task_bp = Blueprint(
    'task',
    __name__,
    url_prefix='/api/task'
)

@task_bp.route('/create', methods=['POST'])
@require_teamleader
def create():
    return create_task()

@task_bp.route('/team', methods=['GET'])
@require_teamleader
def team_tasks():
    return get_team_tasks()

@task_bp.route('/my-tasks', methods=['GET'])
@require_auth
def my_tasks():
    return get_my_tasks()

@task_bp.route('/<task_id>/status', methods=['PUT'])
@require_auth
def update_status(task_id):
    return update_task_status(task_id)

@task_bp.route('/<task_id>', methods=['DELETE'])
@require_teamleader
def delete(task_id):
    return delete_task(task_id)
