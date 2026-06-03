"""
Enterprise MongoDB Database Layer
AI Attendance Management System
"""

import os
import logging

from pymongo import MongoClient

from pymongo.errors import (
    ConnectionFailure,
    ServerSelectionTimeoutError,
)

from dotenv import load_dotenv

# =========================================================
# LOAD ENV
# =========================================================

load_dotenv()

# =========================================================
# LOGGER
# =========================================================

logger = logging.getLogger(__name__)

# =========================================================
# CONFIG
# =========================================================

MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb://localhost:27017"
)

DATABASE_NAME = os.getenv(
    "DATABASE_NAME",
    "ai_attendance_system"
)

# =========================================================
# GLOBALS
# =========================================================

mongo_client = None

database = None

# =========================================================
# CONNECT DATABASE
# =========================================================

def connect_db():

    global mongo_client
    global database

    try:

        # =============================================
        # CREATE CLIENT
        # =============================================

        mongo_client = MongoClient(

            MONGO_URI,

            serverSelectionTimeoutMS=5000,

            maxPoolSize=50,

            minPoolSize=5,

            retryWrites=True,

        )

        # =============================================
        # TEST CONNECTION
        # =============================================

        mongo_client.admin.command(
            "ping"
        )

        # =============================================
        # DATABASE
        # =============================================

        database = mongo_client[
            DATABASE_NAME
        ]

        logger.info(
            "MongoDB connected successfully"
        )

        # =============================================
        # CREATE INDEXES
        # =============================================

        create_indexes(database)

        return database

    except (

        ConnectionFailure,
        ServerSelectionTimeoutError

    ) as e:

        logger.error(
            f"MongoDB connection failed: {e}"
        )

        raise Exception(
            "Database connection failed"
        )

# =========================================================
# GET DATABASE
# =========================================================

def get_db():

    global database

    if database is None:

        connect_db()

    return database

# =========================================================
# CREATE INDEXES
# =========================================================

def create_indexes(db):

    """
    Create enterprise indexes
    """

    try:

        # =============================================
        # USERS
        # =============================================

        db["users"].create_index(

            "email",

            unique=True

        )

        db["users"].create_index(

            "employee_id",

            unique=True

        )

        db["users"].create_index(
            "role"
        )

        # =============================================
        # ATTENDANCE
        # =============================================

        db["attendance"].create_index(
            "employee_id"
        )

        db["attendance"].create_index(
            "date"
        )

        db["attendance"].create_index(
            "department"
        )

        db["attendance"].create_index(
            "status"
        )

        db["attendance"].create_index([

            ("employee_id", 1),

            ("date", 1),

        ])

        # =============================================
        # LEAVE REQUESTS
        # =============================================

        db["leave_requests"].create_index(
            "employee_id"
        )

        db["leave_requests"].create_index(
            "status"
        )

        # =============================================
        # REPORTS
        # =============================================

        db["reports"].create_index(
            "created_at"
        )

        logger.info(
            "MongoDB indexes created successfully"
        )

    except Exception as e:

        logger.error(
            f"Index creation failed: {e}"
        )

# =========================================================
# DATABASE HEALTH
# =========================================================

def db_health():

    try:

        db = get_db()

        db.command("ping")

        return {

            "success": True,

            "database":
                DATABASE_NAME,

            "status":
                "connected",

        }

    except Exception as e:

        logger.error(
            f"Database health failed: {e}"
        )

        return {

            "success": False,

            "status":
                "disconnected",

            "error":
                str(e),

        }

# =========================================================
# CLOSE DATABASE
# =========================================================

def close_db():

    global mongo_client

    try:

        if mongo_client:

            mongo_client.close()

            logger.info(
                "MongoDB connection closed"
            )

    except Exception as e:

        logger.error(
            f"Database close failed: {e}"
        )

# =========================================================
# COLLECTION HELPERS
# =========================================================

def users_collection():

    return get_db()["users"]

def attendance_collection():

    return get_db()["attendance"]

def leave_collection():

    return get_db()["leave_requests"]

def reports_collection():

    return get_db()["reports"]