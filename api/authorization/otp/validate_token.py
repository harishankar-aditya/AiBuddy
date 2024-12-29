import os
import logging


from database.PostgresConnection import DatabaseConnection
from dotenv import load_dotenv
load_dotenv()



def fetch_user_data(DB_conn, access_token):
    query_dict = f"""SELECT 
                        u.user_id,
                        u.username,
                        u.email,
                        lt.request_id
                    FROM 
                        users u
                    INNER JOIN 
                        login_token lt
                    ON 
                        u.user_id = lt.user_id
                    WHERE
                        u.is_user_active = TRUE
                        AND lt.access_token = '{access_token}'
                    LIMIT 1;
                    """
    result = DB_conn.execute_query(query_dict)
    print(result)
    return result

def check_in_db(access_token):
    try:
        response = {
                    "status_code": 500,
                    "status": "failed",
                    "data": None,
                    "message": "Internal Server Error",
                    }
        DB_conn = DatabaseConnection()
        user_data = fetch_user_data(DB_conn, access_token)
        if user_data:
            user_id = user_data[0]['user_id']
            username = user_data[0]['username']
            email = user_data[0]['email']
            request_id = user_data[0]['request_id']
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
                        "message": "Token verified successfully"
                    }
        else:
            response = {
                "status_code": 401,
                "status": "failed",
                "data": None,
                "message": "Invalid token!"
            }
    except Exception as err:
        logging.error(f"An error occurred: {err}")
    finally:
        DB_conn.close_connection()
        return response

def validate_access_token(access_token):
    """
    Sends an OTP to the specified email address.
    """
    try:
        response = check_in_db(access_token)
        logging.info(f"DB response {response}")
    except Exception as err:
        logging.error(f"An error occurred: {err}")
    finally:
        return response
        