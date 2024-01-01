import time
import struct
import logging
import logging
from sqlalchemy import text
import globalvars
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
		self.db_driver = dbengine.create_database_driver(globalvars.db_type)
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

		if userblob[b"\x00\x00\x00\x00"] != struct.pack("<H", 1) :
			raise Exception( )

		username = userblob[b"\x01\x00\x00\x00"]
		if username[-1] != 0 :
			raise Exception( )

		username = username[:-1]

		createtime = utils.steamtime_to_unixtime(userblob[b"\x02\x00\x00\x00"])

		accountkey = userblob[b"\x03\x00\x00\x00"]
		if accountkey[-1] != 0 :
			raise Exception( )

		accountkey = accountkey[:-1]


		pwddetails = userblob[b"\x05\x00\x00\x00"][username]

		if len(pwddetails) != 2 :
			raise Exception( )

		hash = pwddetails[b"\x01\x00\x00\x00"]

		salt = pwddetails[b"\x02\x00\x00\x00"]

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
		blob[b"\x00\x00\x00\x00"] = struct.pack("<H", 1)

		# UniqueAccountName
		blob[b"\x01\x00\x00\x00"] = username + b"\x00"

		# AccountCreationTime
		blob[b"\x02\x00\x00\x00"] = utils.unixtime_to_steamtime(createtime)

		# OptionalAccountCreationKey
		blob[b"\x03\x00\x00\x00"] = accountkey + b"\x00"

		# OptionalBillingInfoRecord - not in client blob

		# AccountUserPasswordsRecord - not in client blob

		# AccountUsersRecord
		entry = {}

		# SteamLocalUserID
		entry[b"\x01\x00\x00\x00"] = k_v1(userid) if version == 1 else k(userid)

		# UserType
		entry[b"\x02\x00\x00\x00"] = struct.pack("<H", 1)

		# UserAppAccessRightsRecord
		entry[b"\x03\x00\x00\x00"] = {}

		blob[b"\x06\x00\x00\x00"] = {username : entry}

		# AccountSubscriptionsRecord
		subs = {}
		for _, subid, subtime in subrows :
			entry = {}
			subid_bytes = struct.pack('<I', subid)

			# SubscribedDate
			entry[b"\x01\x00\x00\x00"] = utils.unixtime_to_steamtime(subtime)

			# UnsubscribedDate
			entry[b"\x02\x00\x00\x00"] = b"\x00" * 8

			subs[subid_bytes] = entry

		blob[b"\x07\x00\x00\x00"] = subs

		apps = {}
		for _, subid, subtime in subrows:
			subid_bytes = struct.pack('<I', subid)
			for key in CDR[b"\x02\x00\x00\x00"][subid_bytes][b"\x06\x00\x00\x00"] :
				log.info("Added app %d for sub %d" % (struct.unpack("<I", key)[0], subid))
				apps[key] = b""

		# DerivedSubscribedAppsRecord
		blob[b"\x08\x00\x00\x00"] = apps

		# LastRecalcDerivedSubscribedAppsTime
		blob[b"\x09\x00\x00\x00"] = utils.unixtime_to_steamtime(time.time( ))

		# CellId
		blob[b"\x0a\x00\x00\x00"] = b"\x00\x00" + struct.pack('<h', int(globalvars.cellid))

		blob[b"__slack__"] = b"\x00" * 256
		return blob