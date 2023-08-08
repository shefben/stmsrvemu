import MySQLdb
import sqlite3
from datetime import datetime
import database

def create_dict_from_buffer(buffer_string):
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

    return result_dict

class SubscriberAccount_Record(object):
    self.UniqueID = 0
    self.version = {'key': r'\x00\x00\x00\x00', 'value': r'\x04\x00'}
    self.UniqueUsername = {'key': r'\x01\x00\x00\x00', 'value': r''}
    self.AccountCreationTime = {'key': r'\x02\x00\x00\x00', 'value': r''}
    self.OptionalAccountCreationKey = {
        'key': r'\x03\x00\x00\x00', 'value': 'Egq-pe-y'}
    self.DerivedSubscribedAppsRecord = {
        'key': r'\x08\x00\x00\x00', 'value': r''}
    self.LastRecalcDerivedSubscribedAppsTime = {
        'key': r'\x09\x00\x00\x00', 'value': '\xe0\xe0\xe0\xe0\xe0\xe0\xe0'}
    self.Cellid = {'key': r'\x0a\x00\x00\x00', 'value': r'\x01\x00\x00\x00'}
    self.AccountEmailAddress = {'key': r'\x0b\x00\x00\x00', 'value': r''}
    self.Banned = {'key': r'\x0c\x00\x00\x00', 'value': r'\x00\x00'}
    self.AccountLastModifiedTime = {
        'key': r'\x0e\x00\x00\x00', 'value': r'\xe0\xe0\xe0\xe0\xe0\xe0\xe0\x00'}

    def __init__(self):
        self.accountsubscription_records_list = []

        self.accountuser_record = AccountUsers_Record()
        self.passwordsrecord_record = AccountUserPasswords_Record()
        self.accountsubscriptionbilling_record = AccountSubscriptionsBillingInfo_Record()

        #self.accountcreationtime['value'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
   # def __init__(self, userblob):
        

    #    if '\x05\x00\x00\x00' in plainblob:        
     #       plainblob['\x05\x00\x00\x00'][username_str]['\x01\x00\x00\x00'][0:16]
      #      plainblob['\x05\x00\x00\x00'][username_str]['\x02\x00\x00\x00']
       #     plainblob['\x05\x00\x00\x00'][username_str]['\x03\x00\x00\x00']
        #    plainblob['\x05\x00\x00\x00'][username_str]['\x04\x00\x00\x00']
         #   plainblob['\x05\x00\x00\x00'][username_str]['\x04\x00\x00\x00']

        
    # AccountUserPasswordsRecord Does not get sent
    class AccountUserPasswords_Record(object):
        key = r'\x05\x00\x00\x00',
        username = self.username['value']

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
        username = self.username['value']

        def __init__(self, steamlocaluserid_str='', usertype_str='', userappaccessrightsrecord_list=None):
            self.SteamID = steamlocaluserid_str
            self.SteamLocalUserID = {
                'key': r'\x01\x00\x00\x00', 'value': steamlocaluserid_str}
            self.UserType = {'key': r'\x02\x00\x00\x00', 'value': usertype_str}
            # '<appid's>' i.e. '1', '2', '3', '4',...
            self.UserAppAccessRightsRecord = {
                'key': r'\x03\x00\x00\x00', 'value': userappaccessrightsrecord_list or []}
        # account_users_record = AccountUsers_Record('SteamUserID123', 'TypeA', ['1', '2', '3'])

    class AccountSubscriptions_Record(object):
        key = r'\x07\x00\x00\x00'
        #username = self.username['value']

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

    class AccountSubscriptionsBillingInfo_Record(object):
        key = r'\x0f\x00\x00\x00'
        self.SubscriptionsBillingInfoRecord_list = []

        class SubscriptionsBillingInfo_Record(object):
            key = r'\x02\x00\x00\x00'

            def __init__(self, subscription_id, account_payment_card_info, type_of_proof_of_purchase=None, binary_proof_of_purchase_token=None):
                self.SubscriptionID = subscription_id
                self.AccountPaymentCardInfoRecord = {
                    'key': r'\x01\x00\x00\x00', 'value': account_payment_card_info}
                if len(TypeOfProofOfPurchase) > 0:
                    self.TypeOfProofOfPurchase = {
                        'key': r'\x01\x00\x00\x00', 'value': type_of_proof_of_purchase}
                    self.BinaryProofOfPurchaseToken = {
                        'key': r'\x02\x00\x00\x00', 'value': binary_proof_of_purchase_token}
                else:
                    self.TypeOfProofOfPurchase = None
                    self.BinaryProofOfPurchaseToken = None

        def set_subscriptions_billing_info(self, subscription_id, account_payment_card_info, type_of_proof_of_purchase=None, binary_proof_of_purchase_token=None):
            subscription_billing_info = self.SubscriptionsBillingInfo_Record(
                subscription_id, account_payment_card_info, type_of_proof_of_purchase, binary_proof_of_purchase_token)
            self.SubscriptionsBillingInfoRecord_list.append(
                subscription_billing_info)

    def set_subscription(self, subscription_id='', subscribed_date='\xe0\xe0\xe0\xe0\xe0\xe0\xe0', unsubscribed_date='\x00\x00\x00\x00\x00\x00\x00',
                         subscription_status='', status_change_flag='', previous_subscription_state='', paymentcardinfo='', typepof='',
                         binarypof=''):

        subscription = self.AccountSubscriptions_Record(
            subscription_id, subscribed_date, unsubscribed_date, subscription_status, status_change_flag
        )

        self.accountsubscription_records_list.append(subscription)
        #self.accountsubscriptionbilling_record.set_subscriptions_billing_info( subscription_id, paymentcardinfo, typepof, binarypof )

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

    def check_userexists(self, username):
        result = select_data("userregistry", "*",
                             "WHERE UniqueUserName = '{}'".format(username))
        if result != 0:
            return 1
        else:
            return 0

    def check_email_associatedwith(self, email):
        rows = select_data("userregistry", "*",
                           "where AccountEmailAddress = '{}'".format(email))
        if rows != 0:
            return rows
        else:
            return 0

    def load_user_from_db(self)
    pass
    '''# Creating an instance of subscriberaccountrecord
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
    print()'''
