import logging

from sqlalchemy import text

from utilities.database import dbengine

log = logging.getLogger('TRKRDB')


class beta2_dbdriver:

    def __init__(self, config):

        # Assuming you have a db_driver instance created and connected
        self.db_driver = dbengine.create_database_driver(globalvars.db_type)
        self.db_driver.connect()

        if not self.db_driver.check_table_exists('users') or not self.db_driver.check_table_exists('friend'):
            self.db_driver.create_tables()

    def get_user_by_email(self, email):
        query = "SELECT ROWID + 0x10000, email, username, firstname, lastname FROM users WHERE email = :email"
        params = {'email':email}
        result = self.db_driver.execute_query(query, params)
        return result[0] if result else None

    def get_user_by_uid(self, uid):
        # Construct a raw SQL query with the calculation
        uid = uid - 0x10000
        query = text("SELECT ROWID + 0x10000, email, username, firstname, lastname FROM users WHERE ROWID = :uid")
        params = {'uid':uid}
        result = self.db_driver.execute_query(query, params)
        return result[0] if result else None

    def search_users(self):
        query = text("SELECT ROWID + 0x10000, username, firstname, lastname FROM users")
        result = self.db_driver.execute_query(query)

        return result if result else []

    def auth(self, email, username):
        row = self.get_user_by_email(email)
        if row is None:
            log.info(f"Creating user with email {email} and username {username}")
            new_user = {"email":email, "username":username, "firstname":b'none', "lastname":b'none'}
            self.db_driver.insert_data(self.db_driver.User, new_user)

            row = self.get_user_by_email(email)
        else:
            log.info(f"Found existing user with email {email}")

        return row[0]

    def update_details(self, uid, username, firstname, lastname):
        # Find the user's email first
        user_row = self.get_user_by_uid(uid)
        if user_row:
            email = user_row[1]  # Assuming email is the second column in the result
            where_clause = self.db_driver.User.email == email
            new_values = {'username':username, 'firstname':firstname, 'lastname':lastname}
            self.db_driver.update_data(self.db_driver.User, where_clause, new_values)

    def request_friend(self, source, target):
        query = text("SELECT source, target FROM friend WHERE source = :source and target = :target")
        params = {'source':source, 'target':target}
        result = self.db_driver.execute_query(query, params)
        row = result[0] if result else None
        if row is None:
            new_friend = {"source":source, "target":target}
            self.db_driver.insert_data(self.db_driver.Friend, new_friend)
            return True
        else:
            return False

    def get_friends_by_source(self, uid):
        where_clause = self.db_driver.Friend.source == uid
        result = self.db_driver.select_data(self.db_driver.Friend, where_clause)
        return [x[1] for x in result]  # Assuming target is the second column

    def get_friends_by_target(self, uid):
        where_clause = self.db_driver.Friend.target == uid
        result = self.db_driver.select_data(self.db_driver.Friend, where_clause)
        return [x[0] for x in result]  # Assuming source is the first column

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