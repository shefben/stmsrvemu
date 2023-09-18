import MySQLdb
import sqlite3
from datetime import datetime
import database
import ast

""" def create_dict_from_buffer(buffer_string):
    def parse_value(value):
        # Check if the value is a sub-dictionary
        if value.startswith('{') and value.endswith('}'):
            # Remove the outer curly braces and recursively parse the sub-dictionary
            return create_dict_from_buffer(value[1:-1])
        else:
            return value.strip()

    # Initialize an empty dictionary
    result_dict = {}

    # Split the buffer_string into key-value pairs based on commas
    key_value_pairs = buffer_string.split(',')

    # Iterate through each key-value pair and populate the dictionary
    for pair in key_value_pairs:
        key, value = pair.split(':')
        result_dict[key.strip()] = parse_value(value)

    return result_dict """
def print_nested_dict(d, indent='', is_last=False):
    for index, (key, value) in enumerate(d.items()):
        if isinstance(value, dict):
            print("%s'%s': {" % (indent, replace_backslashes(key)))
            print_nested_dict(value, indent + '    ', is_last=True)
        else:
            if isinstance(value, str):
                value = value.rstrip("'")
                value = replace_backslashes(value)
            if index < len(d) - 1:
                if key in {'\\x07\\x00\\x00\\x00', '\\x0f\\x00\\x00\\x00'}:
                    print("%s'%s': %s," % (indent, replace_backslashes(key), value))
                else:
                    print("%s'%s': '%s'," % (indent, replace_backslashes(key), value))
            else:
                print("%s'%s': '%s'" % (indent, replace_backslashes(key), value))
    if not is_last:
        pass
    else:
        print('%s}' % indent)

def replace_backslashes(input_string):
    return input_string.replace('\\\\', '\\')

def generate_nested_dict_string(d, is_last=False):
    result = ""
    for index, (key, value) in enumerate(d.items()):
        if isinstance(value, dict):
            result += "'%s':{" % (replace_backslashes(key))
            result += generate_nested_dict_string(value, is_last=True)
        else:
            if isinstance(value, str):
                value = value.rstrip("'")
                value = replace_backslashes(value)
               
            if index < len(d) - 1:
                if key in {'\\x07\\x00\\x00\\x00', '\\x0f\\x00\\x00\\x00'}:
                    result += "'%s':%s," % (replace_backslashes(key), value)
                else:
                    result += "'%s':'%s'," % (replace_backslashes(key), value)
            else:
                result += "'%s':'%s'" % (replace_backslashes(key), value)
    
    if not is_last:
        pass
    else:
        result += '}'
    return result

class SubscriberAccount_Record(object):
    UniqueID = 0
    Version = {'key': r'\x00\x00\x00\x00', 'value': r'\x04\x00'}
    UniqueUserName = {'key': r'\x01\x00\x00\x00', 'value': r''}
    AccountCreationTime = {'key': r'\x02\x00\x00\x00', 'value': r''}
    OptionalAccountCreationKey = {
        'key': r'\x03\x00\x00\x00', 'value': 'Egq-pe-y'}

    accountuser_record = None

    passwordsrecord_record = None

    accountsubscription_records = None

    DerivedSubscribedAppsRecord = {
        'key': r'\x08\x00\x00\x00',
        'value': {}
    }

    LastRecalcDerivedSubscribedAppsTime = {
        'key': r'\x09\x00\x00\x00', 'value': '\xe0\xe0\xe0\xe0\xe0\xe0\xe0'}
    Cellid = {'key': r'\x0a\x00\x00\x00', 'value': r'\x01\x00\x00\x00'}
    AccountEmailAddress = {'key': r'\x0b\x00\x00\x00', 'value': r''}
    Banned = {'key': r'\x0c\x00\x00\x00', 'value': r'\x00\x00'}
    AccountLastModifiedTime = {'key': r'\x0e\x00\x00\x00',
                               'value': r'\xe0\xe0\xe0\xe0\xe0\xe0\xe0\x00'}

    accountsubscriptionbilling_record = None

    def __init__(self):
        self.accountsubscription_records = self.AccountSubscriptions_Record()
        self.accountuser_record = self.AccountUsers_Record()
        self.passwordsrecord_record = self.AccountUserPasswords_Record()
        self.accountsubscriptionbilling_record = self.AccountSubscriptionsBillingInfo_Record()

    # Rest of the code remains the same

    # Inner classes
    class AccountUserPasswords_Record(object):
        key = r'\x05\x00\x00\x00'
        SaltedPassphraseDigest = {}
        PassphraseSalt = {}
        PersonalQuestion = {}
        SaltedAnswerToQuestionDigest = {}
        AnswerToQuestionSalt = {}

        def __init__(self, saltedpassphrasedigest_str='', passphrasesalt_str='', personalquestion_str='', saltedanswertoquestiondigest_str='', answertoquestionsalt_str=''):
            self.SaltedPassphraseDigest = {
                'key': r'\x01\x00\x00\x00', 'value': saltedpassphrasedigest_str}
            self.PassphraseSalt = {
                'key': r'\x02\x00\x00\x00', 'value': passphrasesalt_str}
            self.PersonalQuestion = {
                'key': r'\x03\x00\x00\x00', 'value': personalquestion_str}
            self.SaltedAnswerToQuestionDigest = {
                'key': r'\x04\x00\x00\x00', 'value': saltedanswertoquestiondigest_str}
            self.AnswerToQuestionSalt = {
                'key': r'\x05\x00\x00\x00', 'value': answertoquestionsalt_str}

    class AccountUsers_Record(object):
        key = r'\x06\x00\x00\x00'

        def __init__(self, steamlocaluserid_str='', usertype_str='', userappaccessrightsrecord_list={}):
            self.SteamID = steamlocaluserid_str
            self.SteamLocalUserID = {
                'key': r'\x01\x00\x00\x00', 'value': steamlocaluserid_str}
            self.UserType = {'key': r'\x02\x00\x00\x00', 'value': usertype_str}
            # '<appid's>' i.e. '1', '2', '3', '4',...
            self.UserAppAccessRightsRecord = {
                'key': r'\x03\x00\x00\x00', 'value': userappaccessrightsrecord_list}

    class AccountSubscriptions_Record(object):
        key = r'\x07\x00\x00\x00'
        accountsubscription_records_list = []

        class SubscriptionsInfo_Record(object):
            SubscriptionID = r''

            def __init__(self, subscriptionid_data=0, subscribed_date='', unsubscribed_date='', subscription_status='', status_change_flag='', previous_subscription_state=0):
                self.SubscriptionID = subscriptionid_data
                self.SubscribedDate = {
                    'key': r'\x01\x00\x00\x00', 'value': subscribed_date}
                self.UnsubscribedDate = {
                    'key': r'\x02\x00\x00\x00', 'value': unsubscribed_date}
                self.SubscriptionStatus = {
                    'key': r'\x03\x00\x00\x00', 'value': subscription_status}
                self.StatusChangeFlag = {
                    'key': r'\x05\x00\x00\x00', 'value': status_change_flag}
                self.PreviousSubscriptionState = {
                    'key': r'\x06\x00\x00\x00', 'value': previous_subscription_state}

        def to_dict(self):
            data_dict = {}
            for record in self.accountsubscription_records_list:
                sub_dict = {
                    record.SubscriptionID: {
                        record.SubscribedDate['key']: record.SubscribedDate['value'],
                        record.UnsubscribedDate['key']: record.UnsubscribedDate['value'],
                        record.SubscriptionStatus['key']: record.SubscriptionStatus['value'],
                        record.StatusChangeFlag['key']: record.StatusChangeFlag['value'],
                        record.PreviousSubscriptionState['key']: record.PreviousSubscriptionState['value']
                    }
                }
                data_dict.update(sub_dict)

            return str(data_dict)

    class AccountSubscriptionsBillingInfo_Record(object):
        key = r'\x0f\x00\x00\x00'
        SubscriptionsBillingInfoRecord_list = []

        class SubscriptionsBillingInfo_Record(object):
            key = r'\x02\x00\x00\x00'

            def __init__(self, subscription_id, account_payment_card_info, type_of_proof_of_purchase=None, binary_proof_of_purchase_token=None):
                self.SubscriptionID = subscription_id
                self.AccountPaymentCardInfoRecord = {
                    'key': r'\x01\x00\x00\x00', 'value': account_payment_card_info}
                if type_of_proof_of_purchase is not None and len(type_of_proof_of_purchase) > 0:
                    self.TypeOfProofOfPurchase = {
                        'key': r'\x01\x00\x00\x00', 'value': type_of_proof_of_purchase}
                    self.BinaryProofOfPurchaseToken = {
                        'key': r'\x02\x00\x00\x00', 'value': binary_proof_of_purchase_token}
                else:
                    self.TypeOfProofOfPurchase = None
                    self.BinaryProofOfPurchaseToken = None

        # Function to convert SubscriptionsBillingInfo_Record objects to dictionaries
        def to_dict(self):
            data_dict = {}
            for record in self.SubscriptionsBillingInfoRecord_list:
                subscription_id = record.SubscriptionID
                sub_dict = {
                    '\x01\x00\x00\x00': record.AccountPaymentCardInfoRecord['value'],
                    '\x02\x00\x00\x00': {}
                }
                if record.TypeOfProofOfPurchase is not None:
                    sub_dict['\x02\x00\x00\x00']['\x01\x00\x00\x00'] = record.TypeOfProofOfPurchase['value']
                    sub_dict['\x02\x00\x00\x00']['\x02\x00\x00\x00'] = record.BinaryProofOfPurchaseToken['value']

                data_dict[subscription_id] = sub_dict
               # data_dict.update(sub_dict)

            return str(data_dict)

    def set_accountuser(self, steamlocaluserid_str='', usertype_str='', userappaccessrightsrecord_list=None):

        accountuser = self.AccountUsers_Record(
            steamlocaluserid_str, usertype_str, userappaccessrightsrecord_list
        )
        self.accountuser_record = accountuser

    def set_password(self, saltedpassphrasedigest_str='', passphrasesalt_str='', personalquestion_str='', saltedanswertoquestiondigest_str='', answertoquestionsalt_str=''):

        passwordsrecord = self.AccountUserPasswords_Record(
            saltedpassphrasedigest_str, passphrasesalt_str, personalquestion_str, saltedanswertoquestiondigest_str, answertoquestionsalt_str
        )

        self.passwordsrecord_record = passwordsrecord

    def set_subscriptions_billing_info(self, subscription_id, account_payment_card_info, type_of_proof_of_purchase=None, binary_proof_of_purchase_token=None):

        subscription_billing_info = self.accountsubscriptionbilling_record.SubscriptionsBillingInfo_Record(
            subscription_id, account_payment_card_info, type_of_proof_of_purchase, binary_proof_of_purchase_token
        )

        self.accountsubscriptionbilling_record.SubscriptionsBillingInfoRecord_list.append(
            subscription_billing_info)

    def set_subscription(self, subscription_id='', subscribed_date='\xe0\xe0\xe0\xe0\xe0\xe0\xe0', unsubscribed_date='\x00\x00\x00\x00\x00\x00\x00',
                         subscription_status='', status_change_flag='', previous_subscription_state=''): #, paymentcardinfo='', typepofproof='',
                         #binaryproof=''):

        subscription = self.accountsubscription_records.SubscriptionsInfo_Record(
            subscription_id, subscribed_date, unsubscribed_date, subscription_status, status_change_flag, previous_subscription_state
        )

        self.accountsubscription_records.accountsubscription_records_list.append(
            subscription)
        #self.set_subscriptions_billing_info(
        #    subscription_id, paymentcardinfo, typepofproof, binaryproof)
    def to_dict(self):
        # Create a dictionary to hold the data
        data_dict = {}

        data_dict.update({
            self.Version['key']: self.Version['value'],
            self.UniqueUserName['key']: self.UniqueUserName['value'],
            self.AccountCreationTime['key']: self.AccountCreationTime['value'],
            self.OptionalAccountCreationKey['key']: self.OptionalAccountCreationKey['value'],
        })

        data_dict.update({
            self.accountuser_record.key: {
                self.UniqueUserName['value']: {
                    self.accountuser_record.SteamLocalUserID['key']: self.accountuser_record.SteamLocalUserID['value'],
                    self.accountuser_record.UserType['key']: self.accountuser_record.UserType['value'],
                    self.accountuser_record.UserAppAccessRightsRecord['key']: self.accountuser_record.UserAppAccessRightsRecord['value']
                }
            }
        })

        data_dict.update({
            self.AccountSubscriptions_Record.key: self.accountsubscription_records.to_dict()
        })

        data_dict.update({
            self.DerivedSubscribedAppsRecord['key']: self.DerivedSubscribedAppsRecord['value'],
            self.LastRecalcDerivedSubscribedAppsTime['key']: self.LastRecalcDerivedSubscribedAppsTime['value'],
            self.Cellid['key']: self.Cellid['value'],
            self.AccountEmailAddress['key']: self.AccountEmailAddress['value'],
            self.Banned['key']: self.Banned['value'],
            self.AccountLastModifiedTime['key']: self.AccountLastModifiedTime['value']
        })

        data_dict.update({
            self.accountsubscriptionbilling_record.key: self.accountsubscriptionbilling_record.to_dict()
        })


        generated_dict = "{"+ generate_nested_dict_string(data_dict) + "}"
        print repr(data_dict)
        execdict = ast.literal_eval(data_dict)
        return execdict
    
    
    
    
    #   """ data_dict.update({
     #       self.passwordsrecord_record.key: {
      #          self.UniqueUserName['value']: {
       #             self.passwordsrecord_record.SaltedPassphraseDigest['key']: self.passwordsrecord_record.SaltedPassphraseDigest['value'],
        #            self.passwordsrecord_record.PassphraseSalt['key']: self.passwordsrecord_record.PassphraseSalt['value'],
         #           self.passwordsrecord_record.PersonalQuestion['key']: self.passwordsrecord_record.PersonalQuestion['value'],
          #          self.passwordsrecord_record.SaltedAnswerToQuestionDigest['key']: self.passwordsrecord_record.SaltedAnswerToQuestionDigest['value'],
           #         self.passwordsrecord_record.AnswerToQuestionSalt['key']: self.passwordsrecord_record.AnswerToQuestionSalt['value']
            #    }
            #}
       # })"""

    """def to_dict(self):
        # Create a dictionary to hold the data
        data_dict = {
            self.Version['key']: self.Version['value'],
            self.UniqueUserName['key']: self.UniqueUserName['value'],
            self.AccountCreationTime['key']: self.AccountCreationTime['value'],
            self.OptionalAccountCreationKey['key']: self.OptionalAccountCreationKey['value'],

            self.accountuser_record.key: {
                self.UniqueUserName['value']: {
                    self.accountuser_record.SteamLocalUserID['key']: self.accountuser_record.SteamLocalUserID['value'],
                    self.accountuser_record.UserType['key']: self.accountuser_record.UserType['value'],
                    self.accountuser_record.UserAppAccessRightsRecord['key']: self.accountuser_record.UserAppAccessRightsRecord['value']
                }
            },

            self.passwordsrecord_record.key: {
                self.UniqueUserName['value']: {
                    self.passwordsrecord_record.SaltedPassphraseDigest['key']: self.passwordsrecord_record.SaltedPassphraseDigest['value'],
                    self.passwordsrecord_record.PassphraseSalt['key']: self.passwordsrecord_record.PassphraseSalt['value'],
                    self.passwordsrecord_record.PersonalQuestion['key']: self.passwordsrecord_record.PersonalQuestion['value'],
                    self.passwordsrecord_record.SaltedAnswerToQuestionDigest['key']: self.passwordsrecord_record.SaltedAnswerToQuestionDigest['value'],
                    self.passwordsrecord_record.AnswerToQuestionSalt['key']: self.passwordsrecord_record.AnswerToQuestionSalt['value']
                }
            },

            self.AccountSubscriptions_Record.key: {

                self.accountsubscription_records.to_dict()

            },
            # Include user account record here (accountuser_record)
            self.DerivedSubscribedAppsRecord['key']: self.DerivedSubscribedAppsRecord['value'],
            self.LastRecalcDerivedSubscribedAppsTime['key']: self.LastRecalcDerivedSubscribedAppsTime['value'],
            self.Cellid['key']: self.Cellid['value'],
            self.AccountEmailAddress['key']: self.AccountEmailAddress['value'],
            self.Banned['key']: self.Banned['value'],
            self.AccountLastModifiedTime['key']: self.AccountLastModifiedTime['value'],

            self.accountsubscriptionbilling_record.key: {

                self.accountsubscriptionbilling_record.to_dict()

            }
        }
       # print repr(data_dict)
        print_nested_dict(data_dict)
        return str(data_dict)
"""
# base user record
""" test_record = SubscriberAccount_Record()
test_record.UniqueUsername['value'] = "ben\x00"
test_record.AccountCreationTime['value'] = "\xe0\xe0\xe0\xe0\xe0\xe0\xe0\x00"
test_record.DerivedSubscribedAppsRecord['value'] = ""
test_record.Cellid['value'] = "\x09\x00\x00\x00"
test_record.AccountEmailAddress['value'] = "ben@ben.com\x00"
test_record.Banned['value'] = "\x00\x00"
# password record
test_record.set_password(saltedpassphrasedigest_str="\xe0\xe0\xe0\xe0\xe0\xe0\xe0\x00", passphrasesalt_str="\xe0\xe0\xe0\xe0\xe0\xe0\xe0\x00", personalquestion_str="this is a test\x00", saltedanswertoquestiondigest_str="\xe0\xe0\xe0\xe0\xe0\x00", answertoquestionsalt_str="\xe0\xe0\\x00")
# user account record
test_record.set_accountuser(2, "\x00\x00", ['1','2','3','4'])
# Add multiple subscriptions to the SubscriptionsBillingInfoRecord_list
test_record.AccountSubscriptionsBillingInfo_Record.set_subscriptions_billing_info('subscription_id_1', 'payment_card_info_1', 'proof_of_purchase_1', 'binary_pof_1')
test_record.AccountSubscriptionsBillingInfo_Record.set_subscriptions_billing_info('subscription_id_2', 'payment_card_info_2', 'proof_of_purchase_2', 'binary_pof_2')
test_record.AccountSubscriptionsBillingInfo_Record.set_subscriptions_billing_info('subscription_id_3', 'payment_card_info_3')
test_record.add_subscription(subscription_id='1', subscribed_date='2023-01-01', unsubscribed_date='2023-02-01', subscription_status='Active', status_change_flag='Flagged')
test_record.add_subscription(subscription_id='3', subscribed_date='2023-03-01', unsubscribed_date='2023-04-01', subscription_status='Expired', status_change_flag='No Flag')

    pass """
"""     # Creating an instance of subscriberaccountrecord
account = subscriberaccountrecord()

# Adding subscriptions with values
account.add_subscription('2023-01-01', '2023-02-01', 'Active', 'Flagged')
account.add_subscription('2023-03-01', '2023-04-01', 'Expired', 'No Flag')

# Accessing the subscriptions
for subscription in account.subscriptions:
    print(subscription.SubscribedDate['value'])
    print(subscription.UnsubscribedDate['value'])
    print(subscription.SubscriptionStatus['value'])
    print(subscription.StatusChangeFlag['value'])
    print() """






