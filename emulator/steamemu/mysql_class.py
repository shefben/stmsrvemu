import MySQLdb, logging
import steamemu.logger

from steamemu.config import read_config

config = read_config()
log = logging.getLogger("MysqlDriver")

class MySQLConnector(object):
    def __init__(self):
        self.host = config['mysqlhost']
        self.username = config['mysqlusername']
        self.password = config['mysqlpassword']
        self.database = config['mysqldatabase']
        self.conn = None

    def connect(self):
        self.conn = MySQLdb.connect(
            host=self.host,
            user=self.username,
            passwd=self.password,
            db=self.database,
            charset='utf8'
        )
        self.conn.autocommit(True)

    def disconnect(self):
        if self.conn:
            self.conn.close()

    def execute_query(self, query):
        cursor = self.conn.cursor()
        cursor.execute(query)
        cursor.close()

    def execute_query_with_result(self, query):
        cursor = self.conn.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return result

    def insert_data(self, table, data):
        columns = ', '.join(data.keys())
        values = ', '.join(['%s'] * len(data))
        query = "INSERT INTO {} ({}) VALUES ({})".format(table, columns, values)
        cursor = self.conn.cursor()
        cursor.execute(query, tuple(data.values()))
        cursor.close()

    def update_data(self, table, data, condition):
        set_values = ', '.join(['{} = %s'.format(column) for column in data.keys()])
        query = "UPDATE {} SET {} WHERE {}".format(table, set_values, condition)
        cursor = self.conn.cursor()
        cursor.execute(query, tuple(data.values()))
        cursor.close()

    def delete_data(self, table, condition):
        query = "DELETE FROM {} WHERE {}".format(table, condition)
        cursor = self.conn.cursor()
        cursor.execute(query)
        cursor.close()

    def select_data(self, table, columns='*', condition=''):
        query = "SELECT {} FROM {} WHERE {}".format(columns, table, condition)
        return self.execute_query_with_result(query)
        
class SubscriberAccount_Record(object):
    version = {'key': r'\x00\x00\x00\x00', 'value': 4}
    username = {'key': r'\x01\x00\x00\x00', 'value': r''}
    accountcreationtime ={'key': r'\x02\x00\x00\x00', 'value': 0}
    optionalaccountcreationkey = {'key': r'\x03\x00\x00\x00', 'value': 'Egq-pe-y'}
    LastRecalcDerivedSubscribedAppsTime = {'key': r'\x09\x00\x00\x00', 'value': ''}
    Cellid = {'key': r'\x0a\x00\x00\x00', 'value': 0}
    AccountEmailAddress = {'key': r'\x0b\x00\x00\x00', 'value': ''}
    Banned = {'key': r'\x0c\x00\x00\x00', 'value': 0}
    AccountLastModifiedTime = {'key': r'\x0e\x00\x00\x00', 'value': ''}

    class AccountUserPasswords_Record(object): #  AccountUserPasswordsRecord Does not get sent
        key = r'\x05\x00\x00\x00',
        username = SubscriberAccount_Record.username['value']
        
        def __init__(self, saltedpassphrasedigest_str = '', passphrasesalt_str='', personalquestion_str='', saltedanswertoquestiondigest_str='', answertoquestionsalt_str=''):
            self.SaltedPassphraseDigest = {'key': r'\x01\x00\x00\x00', 'value': saltedpassphrasedigest_str}
            self.PassphraseSalt = {'key': r'\x02\x00\x00\x00', 'value': passphrasesalt_str}
            self.PersonalQuestion = {'key': r'\x03\x00\x00\x00', 'value': personalquestion_str}
            self.SaltedAnswerToQuestionDigest = {'key': r'\x04\x00\x00\x00', 'value': saltedanswertoquestiondigest_str}
            self.AnswerToQuestionSalt = {'key': r'\x05\x00\x00\x00', 'value': answertoquestionsalt_str}

    class AccountUsers_Record(object): 
        key = r'\x06\x00\x00\x00'
        username = SubscriberAccount_Record.username['value']
        
        def __init__(self, steamlocaluserid_str = '', usertype_str='', userappaccessrightsrecord_list=None):
            self.fSteamLocalUserID = {'key': r'\x01\x00\x00\x00', 'value': steamlocaluserid_str}
            self.UserType = {'key': r'\x02\x00\x00\x00', 'value': usertype_str}
            self.UserAppAccessRightsRecord = { 'key': r'\x03\x00\x00\x00', 'value': userappaccessrightsrecord_list or [] }# '<appid's>' i.e. '1', '2', '3', '4',...
        # account_users_record = AccountUsers_Record('SteamUserID123', 'TypeA', ['1', '2', '3'])

    class AccountSubscriptions_Record(object):
        key = r'\x07\x00\x00\x00'
        username = SubscriberAccount_Record.username['value']
        
        def __init__(self, subscriptionid_data = 0, subscribed_date='', unsubscribed_date='', subscription_status='', status_change_flag=''):
            self.SubscriptionID = subscriptionid_data
            self.SubscribedDate = {'key': r'\x01\x00\x00\x00', 'value': subscribed_date}
            self.UnsubscribedDate = {'key': r'\x02\x00\x00\x00', 'value': unsubscribed_date}
            self.SubscriptionStatus = {'key': r'\x03\x00\x00\x00', 'value': subscription_status}
            self.StatusChangeFlag = {'key': r'\x05\x00\x00\x00', 'value': status_change_flag}
            
    class AccountSubscriptionsBillingInfo_Record(object):
        key = r'\x0f\x00\x00\x00'
        SubscriptionsBillingInfoRecord = []


        class SubscriptionsBillingInfo_Record(object):
            key = r'\x02\x00\x00\x00'
            
            def __init__(self, subscription_id='', account_payment_card_info='', account_prepurchased_info='',
                        type_of_proof_of_purchase='', binary_proof_of_purchase_token=''):
                self.SubscriptionID = subscription_id
                self.AccountPaymentCardInfoRecord = {'key': r'\x01\x00\x00\x00', 'value': account_payment_card_info}
                self.TypeOfProofOfPurchase = {'key': r'\x01\x00\x00\x00', 'value': type_of_proof_of_purchase}
                self.BinaryProofOfPurchaseToken = {'key': r'\x02\x00\x00\x00', 'value': binary_proof_of_purchase_token}

        def add_subscriptions_billing_info(self, subscription_id='', account_payment_card_info='', account_prepurchased_info='',
                                        type_of_proof_of_purchase='', binary_proof_of_purchase_token=''):
            subscription_billing_info = self.SubscriptionsBillingInfo_Record(
                subscription_id, account_payment_card_info, account_prepurchased_info,
                type_of_proof_of_purchase, binary_proof_of_purchase_token
            )
            self.SubscriptionsBillingInfoRecord.append(subscription_billing_info)


    def __init__(self):
        self.subscription_records = []
        self.accountuser_record = None
        self.passwordsrecord_record = None
        self.accountsubscriptionbilling_record = None
        
    def add_subscription(self, subscriptionid_data = 0, subscribed_date='', unsubscribed_date='', subscription_status='', status_change_flag=''):
        subscription = self.AccountSubscriptions_Record(
            subscriptionid_data, subscribed_date, unsubscribed_date, subscription_status, status_change_flag
        )
        self.subscription_records.append(subscription)
        
    def add_accountusers(self, steamlocaluserid_str = '', usertype_str='', userappaccessrightsrecord_list=None):
        accountuser = self.AccountUsers_Record(
            steamlocaluserid_str, usertype_str, userappaccessrightsrecord_list
        )
        self.accountuser_record = accountuser     
        
    def add_password(self, saltedpassphrasedigest_str = '', passphrasesalt_str='', personalquestion_str='', saltedanswertoquestiondigest_str='', answertoquestionsalt_str=''):
        passwordsrecord = self.AccountUserPasswords_Record(
            saltedpassphrasedigest_str, passphrasesalt_str, personalquestion_str, saltedanswertoquestiondigest_str, answertoquestionsalt_str
        )
        self.passwordsrecord_record = passwordsrecord
        
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
