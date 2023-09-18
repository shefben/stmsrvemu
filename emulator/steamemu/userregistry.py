import ast


class UserRegistryBuilder(object):

    def __init__(self):
        self.registry = {}


    def add_entry(self, key, value):
        if key in self.registry:
            # If key exists, append the value to a list under that key
            if not isinstance(self.registry[key], list):
                self.registry[key] = [self.registry[key]]
            self.registry[key].append(value)
        else:
            if not isinstance(value, dict):
                self.registry[key] = value
            else:
                self.registry[key] = value


    def add_subdict(self, parent_key, subdict_key, subdict):

        if parent_key in self.registry:
            # If parent key exists, store the sub-dictionary under it with a unique key
            if not isinstance(self.registry[parent_key], dict):
                self.registry[parent_key] = {self.registry[parent_key]: None}
            self.registry[parent_key][subdict_key] = subdict
        else:
            # If parent key doesn't exist, create a dictionary with the sub-dictionary
            self.registry[parent_key] = {
                subdict_key: subdict
            }

    def to_bytes(self, item):
        if isinstance(item, str):
            return item
        elif isinstance(item, dict):
            return {
                self.to_bytes(key): self.to_bytes(value)
                for key, value in item.items()
            }
        elif isinstance(item, list):
            return [self.to_bytes(value) for value in item]
        return item

    def add_entry_as_bytes(self, key, value):
        self.add_entry(self.to_bytes(key), self.to_bytes(value))

    # def AccountUserPasswordsRecord(self, username, value_dict):
    #   self.add_subdict("\x05\x00\x00\x00", username, value_dict)

    def AccountUsersRecord(self, username, value_dict):
        self.add_subdict(b"\x06\x00\x00\x00", username, value_dict)

    def DerivedSubscribedAppsRecord(self, value_dict):
        self.add_subdict(b"\x08\x00\x00\x00", "", value_dict)



    def InsertBaseUserRegistryInformation(self, **kwargs):
        for key, value in kwargs.items():
            self.add_entry(key, value)

    def InsertBaseUserRegistryInformation(self, Version, UniqueUsername, AccountCreationTime, OptionalAccountCreationKey,
                                          LastRecalcDerivedSubscribedAppsTime, Cellid, AccountEmailAddress, AccountLastModifiedTime):
        self.add_entry(b"\x00\x00\x00\x00", Version)
        self.add_entry(b"\x01\x00\x00\x00", UniqueUsername)
        self.add_entry(b"\x02\x00\x00\x00", AccountCreationTime)
        self.add_entry(b"\x03\x00\x00\x00", OptionalAccountCreationKey)
        self.add_entry(b"\x09\x00\x00\x00", LastRecalcDerivedSubscribedAppsTime)
        self.add_entry(b"\x0a\x00\x00\x00", Cellid)
        self.add_entry(b"\x0b\x00\x00\x00", AccountEmailAddress)
        self.add_entry(b"\x0e\x00\x00\x00", AccountLastModifiedTime)

    def InsertAccountUserRecord(self, UniqueUserName, SteamLocalUserID, UserType, UserAppAccessRightsRecord = '' ):
        self.AccountUsersRecord(UniqueUserName, {
                 b"\x01\x00\x00\x00": SteamLocalUserID,
                 b"\x02\x00\x00\x00": UserType,
                 b"\x03\x00\x00\x00": UserAppAccessRightsRecord if UserAppAccessRightsRecord != '' else {},
         })

    def add_account_subscription(self, subscription_id,
                                 subscribed_date, unsubscribed_date,
                                 subscription_status, status_change_flag,
                                 previous_subscription_state, OptionalBillingStatus = 00, UserIP = 00, UserCountryCode = 00):
        subscription_entry = {
            # subscription_id: {
                b"\x01\x00\x00\x00": subscribed_date,
                b"\x02\x00\x00\x00": unsubscribed_date,
                b"\x03\x00\x00\x00": subscription_status,
                b"\x05\x00\x00\x00": status_change_flag,
                b"\x06\x00\x00\x00": previous_subscription_state,
           # '\x07\x00\x00\x00': OptionalBillingStatus,
           #'\x08\x00\x00\x00': UserIP,
           #  "\x09\x00\x00\x00": UserCountryCode,
           #  }
        }
        self.add_subdict(b"\x07\x00\x00\x00", subscription_id,
                         subscription_entry)

    def add_account_subscriptions_billing_info(self,
                                               subscription_id,
                                               payment_card_type="\x07",
                                               card_number="",
                                               card_holder_name="",
                                               ccard_type="",
                                               card_exp_year="",
                                               card_exp_month="",
                                               card_cvv2="",
                                               billing_address1="",
                                               billing_address2="",
                                               billing_city="",
                                               billing_zip="",
                                               billing_state="",
                                               billing_country="",
                                               billing_phone="",
                                               billing_email_address="",
                                               price_before_tax="",
                                               tax_amount="") :
        print repr(payment_card_type)
        if payment_card_type == b'\x07' :
            payment_card_info_record = {
                b"\x01\x00\x00\x00": payment_card_type,
                b"\x02\x00\x00\x00": {},
            }
        elif payment_card_type == b'\x06' :
            payment_card_info_record = {
                "\x01\x00\x00\x00": payment_card_type,
                "\x02\x00\x00\x00": {
                    "\x01\x00\x00\x00": card_number,
                    "\x02\x00\x00\x00": card_holder_name,
                },
            }
        elif payment_card_type == b'\x05' :
            payment_card_info_record = {
                "\x01\x00\x00\x00": payment_card_type,
                "\x02\x00\x00\x00": {
                    "\x01\x00\x00\x00": ccard_type,     #  8bit
                    "\x02\x00\x00\x00": card_number,    #  Everything else is null terminated string
                    "\x03\x00\x00\x00": card_holder_name,
                    "\x04\x00\x00\x00": card_exp_year,
                    "\x05\x00\x00\x00": card_exp_month,
                    "\x06\x00\x00\x00": card_cvv2,
                    "\x07\x00\x00\x00": billing_address1,
                    "\x08\x00\x00\x00": billing_address2,
                    "\x09\x00\x00\x00": billing_city,
                    "\x0a\x00\x00\x00": billing_zip,
                    "\x0b\x00\x00\x00": billing_state,
                    "\x0c\x00\x00\x00": billing_country,
                    "\x0d\x00\x00\x00": billing_phone,
                    "\x0e\x00\x00\x00": billing_email_address,
                    "\x14\x00\x00\x00": price_before_tax, #  32bit
                    "\x15\x00\x00\x00": tax_amount,       #  32bit
                },
            }

        self.add_subdict(b"\x0f\x00\x00\x00", subscription_id,
                         payment_card_info_record)

    def build(self):
        self.add_entry(b'\x0c\x00\x00\x00', b'\x00\x00')
        return self.registry