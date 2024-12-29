import os
import pandas as pd
import psycopg2
from psycopg2 import sql, errors
import logging
from dotenv import load_dotenv
load_dotenv()


class DatabaseConnection():
    def __init__(self):
        try:
            self.conn = psycopg2.connect(
                user=os.getenv('DB_USERNAME'),
                password=os.getenv('DB_PASSWORD'),
                host=os.getenv('DB_HOST'),
                database=os.getenv('DB_DATABASE'),
                port=os.getenv('DB_PORT')
            )
            self.conn.autocommit = True
            self.cursor = self.conn.cursor()
            logging.info('Database connection established')
        except Exception as err:
            logging.error(f"Something went wrong in establishing DB connection - ConnectSQL(__init__): {err}")

    def insert_user_data(self, query_dict):
        try:
            response = {
                        "status_code": 500,
                        "status": "failed",
                        "message": None,
                        "reason": None
                        }
            self.conn.autocommit = False
            for query in query_dict:
                self.cursor.execute(query["query"], query["data"])
            last_row_id = self.cursor.lastrowid
            self.conn.commit()
            response = {
                        "status_code": 200,
                        "status": "success",
                        "message": "User signed up successfully",
                        "last_insert_id": last_row_id,
                        "reason": None
                        }
            logging.info(f"User signed up successfully: {last_row_id}")
        except psycopg2.Error as err:
            self.conn.rollback()
            if isinstance(err, errors.UniqueViolation):
                if 'users.email' in str(err):
                    logging.error(f"Duplicate entry error occurred for email: {err}")
                    response = {
                                "status_code": 409,
                                "status": "failed",
                                "message": "Email already exists",
                                "reason": "duplicate_email"
                                }
                else:
                    logging.exception(f"Unexpected duplicate entry error: {err}")
                    response = {
                                "status_code": 503,
                                "status": "failed",
                                "message": "Something went wrong",
                                "reason": "unexpected_error"
                                }
        except Exception as err:
            self.conn.rollback()
            logging.exception(f"Something went wrong in inserting data - ConnectSQL.insert_user_data(): {err}")
        finally:
            # print(err)
            self.conn.autocommit = True
            return response

    def insert_data(self, query_dict):
        try:
            response = {
                        "status_code": 500,
                        "status": "failed",
                        "message": None,
                        "reason": None
                        }
            self.conn.autocommit = False
            for query in query_dict:
                self.cursor.execute(query["query"], query["data"])
            self.conn.commit()
            response = {
                        "status_code": 200,
                        "status": "success",
                        "message": "Data inserted successfully",
                        "reason": None
                        }
            logging.info(f"Data inserted successfully")
        except Exception as err:
            self.conn.rollback()
            logging.exception(f"Something went wrong in inserting data - ConnectSQL.insert_data(): {err}")
        finally:
            return response

    def execute_query(self, query):
        result = None
        try:
            self.cursor.execute(query)
            # for query in query_dict:
            #     self.cursor.execute(query["query"], query["data"])
            rows = self.cursor.fetchall()
            if self.cursor.description is not None:
                columns = [col[0] for col in self.cursor.description]
                result = [dict(zip(columns, row)) for row in rows]
                # self.table = pd.DataFrame(database_table, columns=columns)
                logging.info(f'{len(result)} rows fetched')
        except Exception as err:
            logging.exception(f"Something went wrong in executing query {query} ConnectSQL.execute_query(): {err}")
        finally:
            return result

    def update_value(self, query):
        try:
            response = {
                        "status_code": 500,
                        "status": "failed",
                        "message": None,
                        "reason": None
                        }
            self.cursor.execute(query)
            self.conn.commit()
            response = {
                        "status_code": 200,
                        "status": "success",
                        "message": "Values updated successfully",
                        "reason": None
                        }
            logging.info(f"Token updated successfully")
        except Exception as err:
            logging.exception(f"Something went wrong in updating data - ConnectSQL.update_value(): {err}")
        finally:
            return response


    def close_connection(self):
        if self.cursor is not None:
            self.cursor.close()
        if self.conn is not None:
            self.conn.close()
        logging.info('Database connection closed')
