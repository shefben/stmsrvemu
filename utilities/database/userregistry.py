import logging

from utilities.blobs import BlobBuilder

log = logging.getLogger('UserRegBuilder')


class UserRegistryBuilder(BlobBuilder):

    def __init__(self):
        super(UserRegistryBuilder, self).__init__()

    # def AccountUserPasswordsRecord(self, username, value_dict):
    #   self.add_subdict("\x05\x00\x00\x00", username, value_dict)

    def AccountUsersRecord(self, username, value_dict):
        self.add_subdict(b"\x06\x00\x00\x00", username, value_dict)

    def DerivedSubscribedAppsRecord(self, value_dict):
        self.add_subdict(b"\x08\x00\x00\x00", "", value_dict)

    def InsertBaseRegistryInformation(self, **kwargs):
        for key, value in kwargs.items():
            self.add_entry(key, value)

    def InsertBaseUserRegistryInformation(self, Version, UniqueUsername, AccountCreationTime, OptionalAccountCreationKey, LastRecalcDerivedSubscribedAppsTime, Cellid, AccountEmailAddress, AccountLastModifiedTime):
        self.add_entry(b"\x00\x00\x00\x00", Version)
        self.add_entry(b"\x01\x00\x00\x00", UniqueUsername)
        self.add_entry(b"\x02\x00\x00\x00", AccountCreationTime)
        self.add_entry(b"\x03\x00\x00\x00", OptionalAccountCreationKey)
        self.add_entry(b"\x09\x00\x00\x00", LastRecalcDerivedSubscribedAppsTime)
        self.add_entry(b"\x0a\x00\x00\x00", Cellid)
        self.add_entry(b"\x0b\x00\x00\x00", AccountEmailAddress)
        self.add_entry(b"\x0e\x00\x00\x00", AccountLastModifiedTime)

    # The following functions are used for creating the Beta 1 Steam User Registry
    def beta1_InsertBaseUserRegistryInformation(self, UniqueUsername, AccountCreationTime, LastRecalcDerivedSubscribedAppsTime, Cellid):
        self.add_entry(b"\x00\x00\x00\x00", b'\x01\x00')
        self.add_entry(b"\x01\x00\x00\x00", UniqueUsername)
        self.add_entry(b"\x02\x00\x00\x00", AccountCreationTime)
        self.add_entry(b"\x03\x00\x00\x00", b'Egq-pe-y\x00')
        self.add_entry(b"\x09\x00\x00\x00", LastRecalcDerivedSubscribedAppsTime)
        self.add_entry(b"\x0a\x00\x00\x00", Cellid)

    def beta1_InsertAccountUserRecord(self, UniqueUserName, SteamLocalUserID, UserType, UserAppAccessRightsRecord = ''):
        self.AccountUsersRecord(UniqueUserName, {b"\x01\x00\x00\x00":SteamLocalUserID,  # 4 bytes
                b"\x02\x00\x00\x00":                                 b'\x01\x01',  # UserType, 0x01 0x01
                b"\x03\x00\x00\x00":                                 UserAppAccessRightsRecord if UserAppAccessRightsRecord != '' else {}, })

    def beta1_add_account_subscription(self, subscription_id, subscribed_date, unsubscribed_date):
        subscription_entry = {b"\x01\x00\x00\x00":subscribed_date, b"\x02\x00\x00\x00":unsubscribed_date, }
        self.add_subdict(b"\x07\x00\x00\x00", subscription_id, subscription_entry)

    def beta1_DerivedSubscribedAppsRecord(self, value_dict):
        self.add_subdict(b"\x08\x00\x00\x00", "", value_dict)  # b"\x42\x00\x00\x00": b"",

    def InsertAccountUserRecord(self, UniqueUserName, SteamLocalUserID, UserType, UserAppAccessRightsRecord = ''):
        self.AccountUsersRecord(UniqueUserName, {b"\x01\x00\x00\x00":SteamLocalUserID, b"\x02\x00\x00\x00":UserType, b"\x03\x00\x00\x00":UserAppAccessRightsRecord if UserAppAccessRightsRecord != '' else {}, })

    def add_account_subscription(self, subscription_id, subscribed_date, unsubscribed_date, subscription_status, status_change_flag, previous_subscription_state, OptionalBillingStatus = 00, UserIP = 00, UserCountryCode = 00):
        subscription_entry = {b"\x01\x00\x00\x00":subscribed_date, b"\x02\x00\x00\x00":unsubscribed_date, b"\x03\x00\x00\x00":subscription_status, b"\x05\x00\x00\x00":status_change_flag, b"\x06\x00\x00\x00":previous_subscription_state, #    "\x07\x00\x00\x00": OptionalBillingStatus,
                #    "\x08\x00\x00\x00": UserIP,
                #    "\x09\x00\x00\x00": UserCountryCode,
        }
        self.add_subdict(b"\x07\x00\x00\x00", subscription_id, subscription_entry)

    def add_account_subscription_beta1(self, subscription_id, subscribed_date, unsubscribed_date):
        subscription_entry = {b"\x01\x00\x00\x00":subscribed_date, b"\x02\x00\x00\x00":unsubscribed_date, }
        self.add_subdict(b"\x07\x00\x00\x00", subscription_id, subscription_entry)

    def add_account_subscriptions_billing_info(self, subscription_id, payment_card_type = "\x07", card_number = "", card_holder_name = "", ccard_type = "", card_exp_year = "", card_exp_month = "", card_cvv2 = "", billing_address1 = "", billing_address2 = "", billing_city = "", billing_zip = "", billing_state = "", billing_country = "", billing_phone = "", billing_email_address = "", price_before_tax = "", tax_amount = ""):
        # print(repr(payment_card_type))
        if payment_card_type == b'\x07':
            payment_card_info_record = {b"\x01\x00\x00\x00":payment_card_type, b"\x02\x00\x00\x00":{}, }
        elif payment_card_type == b'\x06':
            payment_card_info_record = {"\x01\x00\x00\x00":payment_card_type, "\x02\x00\x00\x00":{"\x01\x00\x00\x00":card_number, "\x02\x00\x00\x00":card_holder_name, }, }
        elif payment_card_type == b'\x05':
            payment_card_info_record = {"\x01\x00\x00\x00":payment_card_type, "\x02\x00\x00\x00":{"\x01\x00\x00\x00":ccard_type,  # 8bit
                    "\x02\x00\x00\x00":                                                                              card_number,  # Everything else is null terminated string
                    "\x03\x00\x00\x00":                                                                              card_holder_name, "\x04\x00\x00\x00":card_exp_year, "\x05\x00\x00\x00":card_exp_month, "\x06\x00\x00\x00":card_cvv2, "\x07\x00\x00\x00":billing_address1, "\x08\x00\x00\x00":billing_address2, "\x09\x00\x00\x00":billing_city, "\x0a\x00\x00\x00":billing_zip, "\x0b\x00\x00\x00":billing_state, "\x0c\x00\x00\x00":billing_country, "\x0d\x00\x00\x00":billing_phone, "\x0e\x00\x00\x00":billing_email_address, "\x14\x00\x00\x00":price_before_tax,  # 32bit
                    "\x15\x00\x00\x00":                                                                              tax_amount,  # 32bit
            }, }
        else:
            log.error(f"[UserRegistryBuilder] Error!!! add_account_subscriptions_billing_info() Incorrect Payment Card TypeID: {payment_card_type}")
        self.add_subdict(b"\x0f\x00\x00\x00", subscription_id, payment_card_info_record)

    def build(self):
        self.add_entry(b'\x0c\x00\x00\x00', b'\x00\x00')
        return self.registry

    def build_beta1(self):
        return self.registry