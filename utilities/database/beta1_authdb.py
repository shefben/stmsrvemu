import time
import struct
import logging
import logging
from sqlalchemy import text
import logger
import struct

import utils
from utilities import blobs
from utilities.database import dbengine
from utilities.database.base_dbdriver import BaseDatabaseDriver

log = logging.getLogger("BETA1DB")

def k(n):
	return struct.pack("<I", n)
def k_v1(n):
	return struct.pack("<Q", n)
class beta1_dbdriver(object) :

	def __init__(self, config):
		# Assuming you have a db_driver instance created and connected
		self.db_driver = dbengine.create_database_driver(config['database_type'])
		self.db_driver.connect()

		if not self.db_driver.check_table_exists('beta1_users') or not self.db_driver.check_table_exists('beta1_subscriptions'):
			self.db_driver.create_tables()
			log.info("Inserting Beta 1 Default User Database Information")
			self.insert_user(b'test', 1697417979, b'Egq-pe-y', b'0102030405060708', b'6ac85e8ff2ba19345023be1de9948f9592917642')
			self.insert_subscription(b'test', 0x06, 1697417979)


	def insert_user(self, username, createtime, accountkey, salt, hash):
		# Prepare the data to insert
		user_data = {
			"username": username,
			"createtime": createtime,
			"accountkey": accountkey,
			"salt": salt,
			"hash": hash
		}
		# Insert the data
		self.db_driver.insert_data(BaseDatabaseDriver.Beta1_User, user_data)

	def insert_subscription(self, username, subid, subtime):
		# Prepare the data to insert
		subscription_data = {
			"username": username,
			"subid": subid,
			"subtime": subtime
		}
		# Insert the data
		self.db_driver.insert_data(BaseDatabaseDriver.Beta1_Subscriptions, subscription_data)

	def remove_subscription(self, username, subid):
		unsubscribe_data = {
			"username": username,
			"subid": subid,
		}
		self.db_driver.remove_data(BaseDatabaseDriver.Beta1_Subscriptions, unsubscribe_data)

	def get_user(self, username):
		if isinstance(username, bytes):
			username = username.decode('latin-1')
		result = self.db_driver.execute_query(f"SELECT username, createtime, accountkey, salt, hash, ROWID FROM beta1_users WHERE username = CAST('{username}' AS BLOB)")
		return result[0] if result else None

	def get_salt_and_hash(self, username):
		row = self.get_user(username)
		if row is None :
			return None, None
		print(repr(row))
		return bytes.fromhex(row[3].decode('latin-1')), bytes.fromhex(row[4].decode('latin-1'))

	def edit_subscription(self, username, subid, subtime = 0, remove_sub = False):
		subid = int(subid)
		subtime = int(subtime)
		if remove_sub:
			self.remove_subscription(username, subid)
		else:
			self.insert_subscription(username, subid, subtime)
			#self.db_driver.execute_query(f"INSERT INTO beta1_subscriptions VALUES ( CAST('{username}' AS BLOB), {subid}, {subtime})")

	def create_user(self, binblob, version) :
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
		if self.get_user(username) is not None :
			log.info(f"Username {username} already exists")
			return False
			# TODO BEN send suggested usernames?
		print(username, int(createtime), accountkey, salt.hex(), hash.hex())
		#self.db_driver.execute_query(f"INSERT INTO beta1_subscriptions VALUES (CAST('{username}' AS BLOB), {int(createtime)}, CAST('{accountkey}' AS BLOB), CAST('{salt.hex( )}' AS BLOB), CAST('{hash.hex( )}' AS BLOB))")
		self.insert_user(username, int(createtime), accountkey, salt.hex().encode('latin-1'), hash.hex().encode('latin-1'))
		log.info(f"User {username} Successfully Registered")
		return True

	def get_user_blob(self, username, CDR, version):
		subrows = self.db_driver.select_data(
					BaseDatabaseDriver.Beta1_Subscriptions,
					where_clause=BaseDatabaseDriver.Beta1_Subscriptions.username == username)
		print(subrows)
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
		if version == 1:
			entry[k(1)] = k_v1(userid)
		else:
			entry[k(1)] = k(userid)

		# UserType
		entry[k(2)] = struct.pack("<H", 1)

		# UserAppAccessRightsRecord
		entry[k(3)] = {}

		blob[k(6)] = {username : entry}

		# AccountSubscriptionsRecord
		subs = {}
		for _, subid, subtime in subrows :
			entry = {}

			# SubscribedDate
			entry[k(1)] = utils.unixtime_to_steamtime(subtime)

			# UnsubscribedDate
			entry[k(2)] = b"\x00" * 8

			subs[k(subid)] = entry

		blob[k(7)] = subs

		apps = {}
		for _, subid, subtime in subrows:
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