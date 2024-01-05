import struct
from dataclasses import dataclass


class UserRegistry:
    VERSION_NUM = b"\x00\x00\x00\x00"
    UNIQUE_ACCOUNT_NAME = b"\x01\x00\x00\x00"
    ACCOUNT_CREATION_TIME = b"\x02\x00\x00\x00"
    OPTIONAL_ACCOUNT_CREATION_KEY = b"\x03\x00\x00\x00"
    ACCOUNT_USERS_RECORD = b"\x06\x00\x00\x00"
    ACCOUNT_SUBSCRIPTIONS_RECORD = b"\x07\x00\x00\x00"
    DERIVED_SUBSCRIBED_APPS_RECORD = b"\x08\x00\x00\x00"
    LAST_RECALC_TIME = b"\x09\x00\x00\x00"
    CELL_ID = b"\x0a\x00\x00\x00"

    @dataclass
    class BlobData:
        username: bytes
        createtime: int
        accountkey: bytes
        userid: int
        subrows: list
        CDR: dict
        cellid: int
        utils: object
        log: object

        def to_blob(self, k_v1, k):
            blob = {UserRegistry.VERSION_NUM:struct.pack("<H", 1), UserRegistry.UNIQUE_ACCOUNT_NAME:self.username + b"\x00", UserRegistry.ACCOUNT_CREATION_TIME:self.utils.unixtime_to_steamtime(self.createtime), UserRegistry.OPTIONAL_ACCOUNT_CREATION_KEY:self.accountkey + b"\x00", # Skipping OptionalBillingInfoRecord and AccountUserPasswordsRecord as they are not included
            }

            # AccountUsersRecord
            entry = {b"\x01\x00\x00\x00":k_v1(self.userid) if self.utils.version == 1 else k(self.userid), b"\x02\x00\x00\x00":struct.pack("<H", 1), b"\x03\x00\x00\x00":{}}
            blob[UserRegistry.ACCOUNT_USERS_RECORD] = {self.username:entry}

            # AccountSubscriptionsRecord
            subs = {}
            for _, subid, subtime in self.subrows:
                entry = {b"\x01\x00\x00\x00":self.utils.unixtime_to_steamtime(subtime), b"\x02\x00\x00\x00":b"\x00" * 8}
                subs[struct.pack('<I', subid)] = entry

            blob[UserRegistry.ACCOUNT_SUBSCRIPTIONS_RECORD] = subs

            # DerivedSubscribedAppsRecord
            apps = {}
            for _, subid, _ in self.subrows:
                subid_bytes = struct.pack('<I', subid)
                for key in self.CDR[UserRegistry.ACCOUNT_CREATION_TIME][subid_bytes][UserRegistry.ACCOUNT_USERS_RECORD]:
                    self.log.info(f"Added app {struct.unpack('<I', key)[0]} for sub {subid}")
                    apps[key] = b""

            blob[UserRegistry.DERIVED_SUBSCRIBED_APPS_RECORD] = apps

            # LastRecalcDerivedSubscribedAppsTime
            blob[UserRegistry.LAST_RECALC_TIME] = self.utils.unixtime_to_steamtime(time.time())

            # CellId
            blob[UserRegistry.CELL_ID] = b"\x00\x00" + struct.pack('<h', self.cellid)

            return blob

    @staticmethod
    def parse_blob(blob):
        # Example parsing logic, assuming all necessary keys are present
        parsed_data = {'version_num':struct.unpack("<H", blob[UserRegistry.VERSION_NUM])[0], 'unique_account_name':blob[UserRegistry.UNIQUE_ACCOUNT_NAME].decode().rstrip('\x00'), # Additional parsing logic for other fields...
        }
        return parsed_data


# Usage Example
# Assuming the necessary utility functions, logging, CDR, etc. are defined and available
user_registry_data = UserRegistry.BlobData(username = b"user123", createtime = 1620000000, accountkey = b"key123", userid = 12345, subrows = [(None, 1001, 1620000000)],  # Example data for subrows
        CDR = {UserRegistry.ACCOUNT_CREATION_TIME:{struct.pack('<I', 1001):{UserRegistry.ACCOUNT_USERS_RECORD:[b'\x01\x02\x03\x04']}}}, cellid = 1001, utils = utils,  # Utility functions, including 'unixtime_to_steamtime' and 'version'
        log = log  # Logging object
)

blob = user_registry_data.to_blob(k_v1, k)  # Assuming k_v1 and k functions are provided
parsed_data = UserRegistry.parse_blob(blob)