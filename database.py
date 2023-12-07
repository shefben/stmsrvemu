from __future__ import absolute_import

import logging
import os
import sys

from builtins import object
from builtins import str

if sys.version_info[0] == 2:
    pass
else:
    pass

from datetime import datetime
from sqlalchemy.orm import Session, sessionmaker, scoped_session
from sqlalchemy import create_engine, func, select, MetaData, Table

db_connection = None
log = logging.getLogger("DatabaseEngine")

class GenericDatabase(object):
    def __init__(self, config):
        self.config = config
        self.connection = None
        self.session = None  # Add a session attribute

    def connect(self):
        raise NotImplementedError("connect() method must be implemented in derived classes")

    def disconnect(self):
        if self.connection:
            self.connection.close()
            self.connection = None


    def execute_query(self, query, parameters=None):
        if parameters:
            self.connection.execute(str(query), parameters)
        else:
            self.connection.execute(str(query))

    def execute_query_with_result(self, query, parameters=None):
        if parameters:
            result = self.connection.execute(str(query), parameters)
        else:
            result = self.connection.execute(str(query))
        return [dict(row) for row in result]

    def insert_data(self, table, data):
        columns = ', '.join(list(data.keys()))
        values = ', '.join(['%s'] * len(data)) if isinstance(
            self, MySQLDatabase) else ', '.join(['?'] * len(data))
        query = "INSERT INTO {} ({}) VALUES ({})".format(
            table, columns, values)
        parameters = tuple(data.values())
        try:
            self.execute_query(query, parameters)
            return True  # Insertion was successful
        except Exception as e:
            print("Error inserting data:", data, table)
            return False  # Insertion failed

    def update_data(self, table, data, condition):
        set_values = ', '.join([
            '{} = %s'.format(column) for column in list(data.keys())
        ]) if isinstance(self, MySQLDatabase) else ', '.join(
            ['{} = ?'.format(column) for column in list(data.keys())])
        query = "UPDATE {} SET {} WHERE {}".format(
            table, set_values, condition)
        parameters = tuple(data.values())
        try:
            self.execute_query(query, parameters)
            return True  # Update was successful
        except Exception as e:
            print("Error updating data:", e)
            return False  # Update failed

    def delete_data(self, table, condition):
        query = "DELETE FROM {} WHERE {}".format(table, condition)
        try:
            self.execute_query(query)
            return True  # Deletion was successful
        except Exception as e:
            print("Error deleting data:", e)
            return False  # Deletion failed

    def select_data(self, table, columns='*', condition=''):
        query = "SELECT {} FROM {} WHERE {}".format(
            columns, table, condition)
        return self.execute_query_with_result(query)


    def get_next_id(self, table_name, column):
        try:
            # Create a metadata object and a table object
            metadata = MetaData()
            table_obj = Table(table_name,
                              metadata,
                              autoload=True,
                              autoload_with=self.engine)

            # Build a query to retrieve the maximum value of the specified column
            query = select(
                [func.coalesce(func.max(getattr(table_obj.c, column)), 0)])
            max_value = self.connection.execute(query).scalar()

            # Calculate the next available ID
            next_id = max_value + 1

            return next_id
        except Exception as e:
            print("Error getting next ID:", e)
            return 0  # Return 0 if an error occurred during the query execution

    def get_row_by_date(self, table, date_column, date_to_search):
        date_to_search_str = date_to_search.strftime('%Y-%m-%d')
        query = "SELECT * FROM {} WHERE {} = %s LIMIT 1".format(
            table, date_column)
        parameters = (date_to_search_str,)
        try:
            result = self.execute_query_with_result(query, parameters)
            if result:
                # Return the fetched row
                return result[0]
            return None  # No rows found for the specified date
        except Exception as e:
            print("Error getting row by date:", e)
            return None  # Return None if an error occurred during the query execution


    def insert_activity(self, activity, steamid, username, ip_address, notes = ""):
        next_unique_activity_id = self.get_next_id('useractivities', 'UniqueID')
        current_date = datetime.now().date()  # Get the current date
        current_time = datetime.now().time()  # Get the current time
        data = {
            'UniqueID': next_unique_activity_id,
            'SteamID': steamid,
            'UserName': username,
            'LogDate': current_date,
            'LogTime': current_time,
            'Activity': activity,
            'Notes': notes
        }
        self.insert_data('useractivities', data)


class MySQLDatabase(GenericDatabase):
    def connect(self, config):
        mysql_url = "mysql://" + config['mysql_username'] + ":" + config[
            'mysql_password'] + "@" + config['mysql_host'] + "/" + config[
                'database']

        self.engine = create_engine(mysql_url)
        self.session = Session(self.engine)
        self.connection = self.session.connection()


class SQLiteDatabase(GenericDatabase):
    def connect(self, config):
        # Ensure that the database configuration is present
        if 'database' not in config:
            raise ValueError("Database configuration is missing")

        # Extract the database path from the configuration
        database_path = config['database']

        # Check if the database path already has the "sqlite:///" prefix
        if not database_path.startswith("sqlite:///"):
            database_path = "sqlite:///" + database_path

        # Check if the database path has the ".db" extension
        if not database_path.endswith(".db"):
            database_path = os.path.splitext(database_path)[0] + ".db"
        self.engine = create_engine(database_path, connect_args={'check_same_thread': False})
        self.session = scoped_session(sessionmaker(bind=self.engine))
        self.connection = self.engine.connect()


def initialize_database_connection(config, db_type):
    global db_connection
    if db_connection:
        print("already connected")
        return db_connection
    if db_type == 'mysql':
        print("mysql")
        db = MySQLDatabase(config)
    elif db_type == 'sqlite':
        print("sqlite")
        db = SQLiteDatabase(config)
    else:
        raise ValueError("Unsupported database type: {}".format(db_type))

    db.connect(config)
    db_connection = db
    return db

def get_database_connection():
    global db_connection
    if not db_connection:
        raise ValueError("Database connection has not been initialized. Call initialize_database_connection() first.")
    return db_connection
