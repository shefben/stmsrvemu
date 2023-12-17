from sqlalchemy import TEXT, Table, MetaData, Column, BLOB, Integer, text
from sqlalchemy.sql import select, insert, update, literal_column
import logging
import logger

from utilities.database import dbengine
log = logging.getLogger('TRKRDB')


class beta2_dbdriver:

    def __init__(self, config):

        # Assuming you have a db_driver instance created and connected
        self.db_driver = dbengine.create_database_driver(config['database_type'])
        self.db_driver.connect()

        if not self.db_driver.check_table_exists('users') or not self.db_driver.check_table_exists('friend'):
            self.db_driver.create_tables()

    def get_user_by_email(self, email):
        # Convert email to string if it's bytes
        if isinstance(email, bytes):
            email = email.decode('latin-1')
        query = f"SELECT ROWID + 0x10000, email, username, firstname, lastname FROM users WHERE email = CAST('{email}' AS BLOB)"
        result = self.db_driver.execute_query(query)
        return result[0] if result else None

    def get_user_by_uid(self, uid):
        result = self.db_driver.execute_query(f"SELECT ROWID + 0x10000, email, username, firstname, lastname FROM users WHERE ROWID + 0x10000 = {uid}")
        return result[0] if result else None


    def search_users(self):
        result = self.db_driver.execute_query("SELECT ROWID + 0x10000, username, firstname, lastname FROM users")
        return result

    def auth(self, email, username):
        row = self.get_user_by_email(email)
        if row is None:

            if isinstance(email, bytes):
                email = email.decode('latin-1')
            if isinstance(username, bytes):
                username = username.decode('latin-1')

            log.info("created user with email %s username %s" % (email, username))
            self.db_driver.execute_query(f"INSERT INTO users VALUES (CAST('{email}' AS BLOB), CAST('{username}' AS BLOB), 'none', 'none')")

            row = self.get_user_by_email(email)
        else:
            log.info("found existing user with email %s" % email)

        return row[0]

    def update_details(self, uid, username, firstname, lastname):
        if isinstance(username, bytes):
            username = username.decode('latin-1')
        if isinstance(firstname, bytes):
            firstname = firstname.decode('latin-1')
        if isinstance(lastname, bytes):
            lastname = lastname.decode('latin-1')

        self.db_driver.execute_query(f"UPDATE users SET username = CAST('{username}' AS BLOB), firstname = CAST('{firstname}' AS BLOB), lastname = CAST('{lastname}' AS BLOB) WHERE ROWID + 0x10000 = {uid}")

    def request_friend(self, source, target):
        result = self.db_driver.execute_query(f"SELECT source, target FROM friend WHERE source = {source} and target = {target}")
        row = result[0]

        if row is None:
            self.db_driver.execute_query(f"INSERT INTO friend VALUES ({source}, {target})")
            return True
        else:
            return False

    def get_friends_by_source(self, uid):
        result = self.db_driver.execute_query(f"SELECT target FROM friend WHERE source = {uid}")
        return [x[0] for x in result]

    def get_friends_by_target(self, uid):
        result = self.db_driver.execute_query(f"SELECT source FROM friend WHERE target = {uid}")
        return [x[0] for x in result]

    def pending_friends(self, uid):
        wannabe = self.get_friends_by_target(uid)

        realfriends = self.get_friends_by_source(uid)

        res = []
        for friendid in wannabe:
            if friendid not in realfriends:
                res.append(friendid)

        return res

    def real_friends(self, uid):
        wannabe = self.get_friends_by_target(uid)

        realfriends = self.get_friends_by_source(uid)

        res = []
        for friendid in wannabe:
            if friendid in realfriends:
                res.append(friendid)

        return res