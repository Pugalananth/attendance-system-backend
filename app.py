"""
Enterprise AI Attendance Backend
Professional Corporate Edition
"""

import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from utils.db import connect_db, db_health

# =========================================================
# LOAD ENV & LOGGING
# =========================================================
load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# =========================================================
# CREATE APP
# =========================================================
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "ENTERPRISE_SECRET_KEY")

# =========================================================
# CORS
# =========================================================
CORS(app, resources={r"/api/*": {"origins": "*"}})

# =========================================================
# DATABASE INIT
# =========================================================
try:
    connect_db()
    logger.info("Database initialized")
except Exception as e:
    logger.error(f"Database startup failed: {e}")

# =========================================================
# IMPORT ROUTES
# =========================================================
from routes.auth_routes import auth_bp
from routes.attendance_routes import attendance_bp
from routes.face_routes import face_bp
from routes.leave_routes import leave_bp
from routes.employee_routes import employee_bp
from routes.wfh_routes import wfh_bp
from routes.admin_routes import admin_bp
from routes.team_routes import team_bp
from routes.permission_routes_new import permission_bp
from routes.task_routes import task_bp

# =========================================================
# REGISTER BLUEPRINTS
# =========================================================
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(attendance_bp, url_prefix='/api/attendance')
app.register_blueprint(face_bp, url_prefix='/api/face')
app.register_blueprint(leave_bp, url_prefix='/api/leave')
app.register_blueprint(employee_bp, url_prefix='/api/employee')
app.register_blueprint(wfh_bp, url_prefix='/api/wfh')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(team_bp, url_prefix='/api/team')
app.register_blueprint(permission_bp, url_prefix='/api/permission')
app.register_blueprint(task_bp, url_prefix='/api/task')

logger.info("All Enterprise Blueprints registered successfully")

# =========================================================
# ROOT & HEALTH
# =========================================================
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "success": True,
        "message": "Enterprise AI Attendance API Running",
        "status": "online",
    }), 200

@app.route("/api/health", methods=["GET"])
def health():
    db_status = db_health()
    return jsonify({
        "success": True,
        "server": "running",
        "database": db_status,
    }), 200

# =========================================================
# START SERVER
# =========================================================
if __name__ == "__main__":
    PORT = int(os.getenv("PORT", 5000))
    logger.info(f"Starting Enterprise API on port {PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=True, threaded=True)
