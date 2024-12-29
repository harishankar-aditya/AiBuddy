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
    query_dict = f"SELECT user_id, username, email FROM users WHERE email = '{email}' AND is_user_active = true"
    result = DB_conn.execute_query(query_dict)
    return result

def insert_in_db(username, email, otp, request_id):
    DB_conn = DatabaseConnection()
    user_data = fetch_user_data(DB_conn, email)
    current_time = datetime.now()
    if user_data:
        user_id = user_data[0]['user_id']
        expire_otp_query = {
                            "query": "UPDATE login_token SET is_otp_active = %s, updated_at = %s WHERE user_id = %s",
                            "data": ('false', current_time, user_id)
                        }
                    
        token_query = {
                            "query": "INSERT INTO login_token (user_id, email, otp, request_id) VALUES (%s, %s, %s, %s)",
                            "data": (user_id, email, otp, request_id)
                        }
                    
        response = DB_conn.insert_user_data([expire_otp_query, token_query])

        # user_query = {
        #                     "query": "UPDATE users SET username = %s, updated_at = %s, last_login_at = %s WHERE user_id = %s",
        #                     "data": (username, current_time, current_time, user_id)
        #                 }
            
        # response = DB_conn.insert_user_data([expire_otp_query, token_query, user_query])
    else:
        user_id = str(uuid.uuid4())
        create_user_query = {
                            "query": "INSERT INTO users (user_id, username, email) VALUES (%s, %s, %s)",
                            "data": (user_id, username, email)
                        }
                    
        token_query = {
                            "query": "INSERT INTO login_token (user_id, email, otp, request_id) VALUES (%s, %s, %s, %s)",
                            "data": (user_id, email, otp, request_id)
                        }
        
        response = DB_conn.insert_user_data([create_user_query, token_query])

    return response

def send_otp_to_email(username, email: str, otp: str, request_id: str):
    """
    Sends an OTP to the specified email address.
    """
    try:
        response = {
            "status_code": 400,
            "message": "Invalid Email!"
        }
        sender_email = os.getenv("adminEmail", "")
        receiver_email = email
        password = os.getenv("adminPassword", "")
        msg = MIMEMultipart()
        msg.set_unixfrom('author')
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = 'Login OTP for Sophius Buddy'
        message = f'Your OTP to login to Sophius Buddy is {otp}.'
        msg.attach(MIMEText(message))

        # Connect to the server
        mailserver = smtplib.SMTP_SSL('smtpout.secureserver.net', 465)
        mailserver.ehlo()  # Say hello to the server
        # Login to the server
        mailserver.login(sender_email, password)
        # Send the email
        mailserver.sendmail(sender_email, receiver_email, msg.as_string())
        # Disconnect from the server
        mailserver.quit()

        logging.info("Email sent successfully!")
        
        response = {
            "status_code": 200,
            "message": "OTP sent successfully"
            }

    except smtplib.SMTPServerDisconnected as e:
        logging.error(f"SMTPServerDisconnected: {e}")
    except smtplib.SMTPAuthenticationError as e:
        logging.error(f"SMTPAuthenticationError: {e}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        output = insert_in_db(username, email, otp, request_id)
        logging.info(f"DB response {output}")
        return response
        