import time
import struct
import logging
import logging
import logger
import struct

import utils
from utilities import blobs

log = logging.getLogger("BETA1DB")

def k(n):
    return struct.pack("<I", n)

class Beta1AuthDatabase(object) :

    def __init__(self, db_instance) :
        self.db = db_instance

    def create_user(self, binblob) :
        userblob = blobs.blob_unserialize(binblob)
        if b"__slack__" in userblob :
            numkeys = 11
        else :
            numkeys = 10
        if len(userblob) != numkeys :
            raise Exception( )

        if userblob[k(0)] != struct.pack("<H", 1) :
            raise Exception( )

        username = userblob[k(1)]
        if username[-1] != 0 :
            raise Exception( )

        username = username[:-1]

        createtime = utils.steamtime_to_unixtime(userblob[k(2)])

        accountkey = userblob[k(3)]
        if accountkey[-1] != 0 :
            raise Exception( )

        accountkey = accountkey[:-1]


        pwddetails = userblob[k(5)][username]
        if len(pwddetails) != 2 :
            raise Exception( )

        hash = pwddetails[k(1)]

        salt = pwddetails[k(2)]



        # First we check if the name already exists
        if self.get_user(username) != None:
            log.info(f"Username {username} already exists")
            return False# Username already exists!

        user_data = {
            'username'   : username,
            'createtime' : createtime,
            'accountkey' : accountkey,
            'salt'       : salt.hex( ),
            'hash'       : hash.hex( )
        }
        log.info(f"User {username} Registered")
        self.db.insert_data("beta_userregistry", user_data)
        return True

    def get_user(self, username):
        query = "SELECT username, createtime, accountkey, salt, hash, ROWID FROM beta_userregistry WHERE username = :username"
        params = {'username': username}
        return self.db.execute_query(query, params)

    def get_salt_hash(self, username):
        row = self.get_user(username)
        if row is None :
            return None, None

        return bytes.fromhex(row[3]), bytes.fromhex(row[4])

    def get_user_blob(self, username, CDR):
        query = "SELECT subid, subtime FROM beta_subscriptions WHERE username = :username"
        params = {'username' : username}
        subrows = self.db.execute_query(query, params)
        row = self.get_user(username)
        if row is None :
            return None

        username, createtime, accountkey, _, _, userid = row
        blob = {}

        # VersionNum
        blob[k(0)] = struct.pack("<H", 1)

        # UniqueAccountName
        blob[k(1)] = username + b"\x00"

        # AccountCreationTime
        blob[k(2)] = utils.unixtime_to_steamtime(createtime)

        # OptionalAccountCreationKey
        blob[k(3)] = accountkey + b"\x00"

        # OptionalBillingInfoRecord - not in client blob

        # AccountUserPasswordsRecord - not in client blob

        # AccountUsersRecord
        entry = {}

        # SteamLocalUserID
        entry[k(1)] = k(userid)

        # UserType
        entry[k(2)] = struct.pack("<H", 1)

        # UserAppAccessRightsRecord
        entry[k(3)] = {}

        blob[k(6)] = {username : entry}

        # AccountSubscriptionsRecord
        subs = {}
        for subid, subtime in subrows :
            entry = {}

            # SubscribedDate
            entry[k(1)] = utils.unixtime_to_steamtime(subtime)

            # UnsubscribedDate
            entry[k(2)] = b"\x00" * 8

            subs[k(subid)] = entry

        blob[k(7)] = subs

        apps = {}
        for subid, subtime in subrows :
            for key in CDR[k(2)][k(subid)][k(6)] :
                log.info("Added app %d for sub %d" % (struct.unpack("<I", key)[0], subid))
                apps[key] = b""

        # DerivedSubscribedAppsRecord
        blob[k(8)] = apps

        # LastRecalcDerivedSubscribedAppsTime
        blob[k(9)] = utils.unixtime_to_steamtime(time.time( ))

        # CellId
        blob[k(10)] = k(0)

        blob[b"__slack__"] = b"\x00" * 256
        return blob


    def edit_subscription(self, username, subid, subtime = 0, remove_sub = False):

        if remove_sub:
            query = "DELETE FROM beta_subscriptions WHERE username = :username AND subid = :subid"
            params = {
                'username' : username,
                'subid'    : subid
            }
            self.db.execute_query(query, params)
        else:
            sub_data = {
                'username'   : username,
                'subid' : subid,
                'subytime' : subtime
            }
            self.db.insert_data("beta_subscriptions", sub_data)
        return