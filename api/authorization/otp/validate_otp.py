import os
import logging
import smtplib

import uuid

from datetime import datetime

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from database.PostgresConnection import DatabaseConnection
from dotenv import load_dotenv
load_dotenv()



def fetch_user_data(DB_conn, email):
    query_dict = f"""SELECT 
                        u.user_id,
                        u.username,
                        u.email,
                        lt.otp
                    FROM 
                        users u
                    INNER JOIN 
                        login_token lt
                    ON 
                        u.user_id = lt.user_id
                    WHERE
                        u.email = '{email}'
                        AND u.is_user_active = TRUE
                        AND lt.is_otp_active = TRUE;
                    """
    result = DB_conn.execute_query(query_dict)
    return result

def check_in_db(username, email, user_otp, request_id):
    try:
        response = {
                    "status_code": 500,
                    "status": "failed",
                    "data": None,
                    "message": "Internal Server Error",
                    }
        DB_conn = DatabaseConnection()
        user_data = fetch_user_data(DB_conn, email)
        current_time = datetime.now()
        if user_data:
            user_id = user_data[0]['user_id']
            db_otp = user_data[0]['otp']
            if str(user_otp) == str(db_otp):
                access_token = str(uuid.uuid4())
                expire_user_otp = {
                                    "query": "UPDATE login_token SET is_otp_active = %s, access_token = %s, updated_at = %s WHERE user_id = %s",
                                    "data": ('false', access_token, current_time, user_id)
                                }
                update_user_table = {
                                    "query": "UPDATE users SET username = %s, updated_at = %s, last_login_at = %s WHERE user_id = %s",
                                    "data": (username, current_time, current_time, user_id)
                                }
                query_output = DB_conn.insert_user_data([expire_user_otp, update_user_table])
                response = {
                            "status_code": 200,
                            "status": "success",
                            "data": [
                                {
                                    "access_token": access_token,
                                    "user_id": user_id,
                                    "username": username,
                                    "email": email,
                                    "request_id": request_id
                                }
                            ],
                            "message": "OTP verified successfully"
                        }
            else:
                response = {
                    "status_code": 401,
                    "status": "failed",
                    "data": None,
                    "message": "Invalid OTP!"
                }
        else:
                response = {
                    "status_code": 404,
                    "status": "failed",
                    "data": None,
                    "message": "User email not found!"
                }
    except Exception as err:
        logging.error(f"An error occurred: {err}")
    finally:
        DB_conn.close_connection()
        return response

def validate_user_otp(username, email: str, otp: str, request_id: str):
    """
    Sends an OTP to the specified email address.
    """
    try:
        response = check_in_db(username, email, otp, request_id)
        logging.info(f"DB response {response}")
    except Exception as err:
        logging.error(f"An error occurred: {err}")
    finally:
        return response
        