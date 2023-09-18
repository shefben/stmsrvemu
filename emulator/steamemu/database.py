import MySQLdb
import sqlite3
import time
import utilities
import binascii
import logging
import config, base64
import steamemu.logger
import struct
from userregistry import UserRegistryBuilder
from datetime import datetime
from subscriberaccount_record import SubscriberAccount_Record
from steamemu.config import read_config
from sqlalchemy import create_engine


db_connection = None
log = logging.getLogger("AuthenticationSRV")

class GenericDatabase(object):
    def __init__(self, config):
        self.config = config
        self.connection = None

    def connect(self):
        raise NotImplementedError(
            "connect() method must be implemented in derived classes")

    def disconnect(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    """def execute_query(self, query, parameters=None):
        cursor = self.connection.cursor()
        if parameters:
            cursor.execute(query, parameters)
        else:
            cursor.execute(query)
        cursor.close()

    def execute_query_with_result(self, query, parameters=None):
        cursor = self.connection.cursor()
        if parameters:
            cursor.execute(query, parameters)
        else:
            cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return result"""
    def execute_query(self, query, parameters=None):
        with self.connection.connect() as connection:
            if parameters:
                connection.execute(str(query), parameters)
            else:
                connection.execute(str(query))

    def execute_query_with_result(self, query, parameters=None):
        with self.connection.connect() as connection:
            if parameters:
                result = connection.execute(str(query), parameters)
            else:
                result = connection.execute(str(query))
            return [dict(row) for row in result]

    def insert_data(self, table, data):
        columns = ', '.join(data.keys())
        values = ', '.join(['%s'] * len(data)) if isinstance(
            self, MySQLDatabase) else ', '.join(['?'] * len(data))
        query = "INSERT INTO {} ({}) VALUES ({})".format(
            table, columns, values)
        parameters = tuple(data.values())
        try:
            self.execute_query(query, parameters)
            return True  # Insertion was successful
        except Exception as e:
            print("Error inserting data:", e)
            return False  # Insertion failed

    def update_data(self, table, data, condition):
        set_values = ', '.join([
            '{} = %s'.format(column) for column in data.keys()
        ]) if isinstance(self, MySQLDatabase) else ', '.join(
            ['{} = ?'.format(column) for column in data.keys()])
        query = "UPDATE {} SET {} WHERE {}".format(
            table, set_values, condition)
        parameters = tuple(data.values())
        try:
            self.execute_query(query, parameters)
            return True  # Update was successful
        except Exception as e:
            print("Error updating data:", e)
            return False  # Update failed

    def delete_data(self, table, condition):
        query = "DELETE FROM {} WHERE {}".format(table, condition)
        try:
            self.execute_query(query)
            return True  # Deletion was successful
        except Exception as e:
            print("Error deleting data:", e)
            return False  # Deletion failed

    """def select_data(self, table, columns='*', condition=''):
        query = "SELECT {} FROM {} WHERE {}".format(
            columns, table, condition)
        if isinstance(self, MySQLDatabase):
            cursor = self.connection.cursor()
        else:
            return self.connection.execute(query)
        try:
            cursor.execute(query)
            column_names = [desc[0] for desc in cursor.description]
            result = [dict(zip(column_names, row))
                      for row in cursor.fetchall()]
            cursor.close()
            return result
        except Exception as e:
            cursor.close()
            print("Error executing select query:", e)
            return []"""

    def select_data(self, table, columns='*', condition=''):
        query = "SELECT {} FROM {} WHERE {}".format(
            columns, table, condition)
        return self.execute_query_with_result(query)

    def get_next_id(self, table, column):
        query = "SELECT COALESCE(MAX({}), 0) + 1 FROM {}".format(column, table)
        try:
            result = self.execute_query_with_result(query)
            next_id = result[0][0] if result else 1
            return next_id
        except Exception as e:
            print("Error getting next ID:", e)
            return None  # Return None if an error occurred during the query execution

    def get_row_by_date(self, table, date_column, date_to_search):
        date_to_search_str = date_to_search.strftime('%Y-%m-%d')
        query = "SELECT * FROM {} WHERE {} = %s LIMIT 1".format(
            table, date_column)
        parameters = (date_to_search_str,)
        try:
            result = self.execute_query_with_result(query, parameters)
            if result:
                # Return the fetched row
                return result[0]
            return None  # No rows found for the specified date
        except Exception as e:
            print("Error getting row by date:", e)
            return None  # Return None if an error occurred during the query execution


    def insert_activity(self, activity, steamid, username, ip_address, notes = ""):
        next_unique_activity_id = self.get_next_id('useractivities', 'UniqueID')
        current_date = datetime.now().date()  # Get the current date
        current_time = datetime.now().time()  # Get the current time
        data = {
            'UniqueID': next_unique_activity_id,
            'SteamID': steamid,
            'UserName': username,
            'LogDate': current_date,
            'LogTime': current_time,
            'Activity': activity,
            'Notes': notes
        }
        self.insert_data('useractivities', data)

    def create_user(self, username, SaltedAnswerToQuestionDigest, PassphraseSalt, AnswerToQuestionSalt,
                PersonalQuestion, SaltedPassphraseDigest, AccountEmailAddress):

        next_unique_user_id = self.get_next_id('userregistry', 'UniqueID')
        self.UniqueID = next_unique_user_id
        next_steam_id = self.get_next_id('userregistry', 'SteamLocalUserID')
        self.SteamID = next_steam_id

        accountcreationtime = utilities.get_current_datetime()

        expanded_numbers = []
        ranges = ["1-5", "11-25", "30-35", "40-45", "50-51", "56", "60-65", "70", "72-79", "81-89", "92", "104-111", "204", "205", "242-253", "0", "260", "80", "95", "100", "101-103", "200", "210", "241"]
        for r in ranges:
            if "-" in r:
                start, end = map(int, r.split("-"))
                expanded_numbers.extend(range(start, end + 1))
            else:
                expanded_numbers.append(int(r))

        DerivedSubscribedAppsRecord_value = ",".join(map(str, expanded_numbers))

        if self.check_username(username) is not 0:
            return -1
        data = {
            'UniqueID': next_unique_user_id,
            'UniqueUserName': username,
            'subscriptionrecord_version': '4',
            'AccountCreationTime': accountcreationtime,
            'OptionalAccountCreationKey': 'Egq-pe-y',
            'SteamLocalUserID': next_steam_id,
            'UserType': 1,
            'SaltedAnswerToQuestionDigest': binascii.b2a_hex(SaltedAnswerToQuestionDigest),
            'PassphraseSalt': binascii.b2a_hex(PassphraseSalt),
            'AnswerToQuestionSalt': binascii.b2a_hex(AnswerToQuestionSalt),
            'PersonalQuestion': PersonalQuestion,
            'SaltedPassphraseDigest': binascii.b2a_hex(SaltedPassphraseDigest),
            'LastRecalcDerivedSubscribedAppsTime': accountcreationtime,
            'Cellid': '1',
            'AccountEmailAddress': AccountEmailAddress,
            'Banned': '0',
            'AccountLastModifiedTime': accountcreationtime,
            'DerivedSubscribedAppsRecord': DerivedSubscribedAppsRecord_value
        }

        try:
            self.insert_data('userregistry', data)
            # Process the result if there is no error
        except Exception as e:
            # Handle the exception here (e.g., print an error message)
            log.debug("Error occurred:", e)
            return -1

        next_unique_sub_id = self.get_next_id('accountsubscriptionsrecord', 'UniqueID')

        data = {
            'UniqueID': next_unique_sub_id,
            'UserRegistry_UniqueID': next_unique_user_id,
            'SubscriptionID': '0',
            'SubscribedDate': accountcreationtime,
            'UnsubscribedDate':  utilities.add_100yrs(accountcreationtime),
            'SubscriptionStatus':  '1',  #  Set the subscription status value here
            'StatusChangeFlag':  '0',  #  Set the status change flag value here 
            'PreviousSubscriptionState':  '0' #  Set the previous subscription state value here
        }
        self.insert_data('accountsubscriptionsrecord', data)

        next_unique_billing_id = self.get_next_id('accountsubscriptionsbillinginforecord', 'UniqueID')

        data = {
            'UniqueID': next_unique_billing_id,
            'UserRegistry_UniqueID': next_unique_user_id,
            'Subscriptionid': '0',  # subbillinginfo.SubscriptionID,
            'AccountPaymentCardInfoRecord': '7',
        }
        self.insert_data('accountsubscriptionsbillinginforecord', data)

        log.info("New User Created & Added To Database: " + username)

# to set prepurchase record for type 6, use the same tuple as below
#     Except only use tuple_variable = (PaymentCardType = TypeOfProofOfPurchase, CardNumber= BinaryProofOfPurchaseToken)

# to set payment record info for type 5, use this tuple:
#           tuple_variable = (PaymentCardType, CardNumber, CardHolderName, CardExpYear, CardExpMonth, CardCVV2, BillingAddress1, BillingAddress2,
#                               BillingCity, BillinZip, BillingState, BillingCountry, BillingPhone, BillinEmailAddress, PriceBeforeTax, TaxAmount)
#############################################################
#  Add Subscription to User Account
#  Notes:
#  1: AccountPaymentCardInfoRecord
#  2: AccountPrepurchaseInfoRecord
#############################################################
    def insert_subscription(self, username, SubscriptionID, paymenttype, tuple_paymentrecord=None) :
        UserRegistry_UniqueID = self.get_uniqueuserid(username)

        current_time = utilities.get_current_datetime()

        next_unique_sub_id = self.get_next_id('accountsubscriptionsrecord', 'UniqueID')

        data = {
            'UniqueID': next_unique_sub_id,
            'UserRegistry_UniqueID': UserRegistry_UniqueID,
            'SubscriptionID': SubscriptionID , # Set the subscribed date value here
            'SubscribedDate': current_time, # Set the unsubscribed date value here
            'UnsubscribedDate':  utilities.add_100yrs(current_time),
            'SubscriptionStatus':  '1',  # Set the subscription status value here
            'StatusChangeFlag':  '0',  # Set the status change flag value here
            'PreviousSubscriptionState':  '0' # Set the previous subscription state value here
        }
        self.insert_data('accountsubscriptionsrecord', data)

        if paymenttype is 6 :
            next_unique_prepurchase_id = 0
            next_unique_prepurchase_id = self.get_next_id('accountprepurchasedinforecord', 'UniqueID')

            (TypeOfProofOfPurchase, BinaryProofOfPurchaseToken) = tuple_paymentrecord

            data = {
                'UniqueID': next_unique_prepurchase_id,
                'UserRegistry_UniqueID': UserRegistry_UniqueID,
                'TypeOfProofOfPurchase': TypeOfProofOfPurchase,
                'BinaryProofOfPurchaseToken': BinaryProofOfPurchaseToken
            }
            self.insert_data('accountprepurchasedinforecord', data)

        elif paymenttype is 5 :
            next_unique_paymentcard_recordID = 0
            next_unique_paymentcard_recordID = self.get_next_id('accountpaymentcardinforecord', 'uniqueid')

            (PaymentCardType, CardNumber, CardHolderName, CardExpYear, CardExpMonth, CardCVV2, BillingAddress1, BillingAddress2,
            BillingCity, BillinZip, BillingState, BillingCountry, BillingPhone, BillinEmailAddress, PriceBeforeTax, TaxAmount) = tuple_paymentrecord

            data = {
                'UniqueID': next_unique_paymentcard_recordID,
                'UserRegistry_UniqueID': UserRegistry_UniqueID,
                'PaymentCardType': PaymentCardType,
                'CardNumber': CardNumber,
                'CardHolderName': CardHolderName,
                'CardExpYear': CardExpYear,
                'CardExpMonth': CardExpMonth,
                'CardCVV2': CardCVV2,
                'BillingAddress1': BillingAddress1,
                'BillingAddress2': BillingAddress2,
                'BillingCity': BillingCity,
                'BillingZip': BillinZip,
                'BillingState': BillingState,
                'BillingCountry': BillingCountry,
                'BillingPhone': BillingPhone,
                'BillinEmailAddress': BillinEmailAddress,
                'PriceBeforeTax': PriceBeforeTax,
                'TaxAmount': TaxAmount,
            }
            self.insert_data('accountpaymentcardinforecord', data)
        else : #  Payment id must either be 7 or unknown
            if paymenttype is not 7 :
                log.error(username + "Has an invalid payment type id! PaymentTypeID: " + paymenttype)
            pass

        paymenttype = 5 if paymenttype == 1 else (6 if paymenttype == 2 else 7) #Set the result id (4-7) instead of using the request id (1-3)

        next_unique_billing_id = 0
        next_unique_billing_id = self.get_next_id('accountsubscriptionsbillinginforecord', 'UniqueID')
        data = {
            'UniqueID': next_unique_billing_id,
            'UserRegistry_UniqueID': UserRegistry_UniqueID,
            'SubscriptionID': SubscriptionID,
            'AccountPaymentCardInfoRecord': paymenttype,
        }

        if paymenttype is 5 :
            data['AccountPaymentCardReceiptRecord_recordID'] = next_unique_paymentcard_recordID
        elif paymenttype is 6 :
            data['AccountPrepurchasedInfoRecord_UniqueID'] = next_unique_prepurchase_id

        self.insert_data('accountsubscriptionsbillinginforecord', data)
        log.info("Successfully inserted new Subscription To Database, Subscription ID: " + subscriptionid + " Username: " + username)

    #############################################################
    #  Get Database Info for user trying to log in.
    #  Notes:  Deal with Payment Record Types 1-4, currently only deal with 5, 6 and 7
    #############################################################
    def get_user_dictionary(self, username) :

        user_registry_builder = UserRegistryBuilder()

        userrecord_dbdata = self.select_data('userregistry', condition="UniqueUserName = '{}'".format(username))

        userrecord_dbdata_variables = userrecord_dbdata[0]

        subscription_record_variables = None
        billing_info_variables = None

        if len(userrecord_dbdata) > 1 :

            log.error("More than 1 row returned when loading user from database! user: " + username)
            return 2
        elif len(userrecord_dbdata) > 0 :

            user_registry_builder.add_entry(b"\x00\x00\x00\x00", utilities.decimal_to_16hex(userrecord_dbdata_variables['subscriptionrecord_version']))
            user_registry_builder.add_entry(b"\x01\x00\x00\x00", bytes(userrecord_dbdata_variables['UniqueUserName'] + b"\x00"))

            user_registry_builder.add_entry(b"\x02\x00\x00\x00", str(utilities.datetime_to_steamtime(userrecord_dbdata_variables['AccountCreationTime'])))
            user_registry_builder.add_entry(b"\x03\x00\x00\x00", str(userrecord_dbdata_variables['OptionalAccountCreationKey'] + b'\x00'))

            Numbers = str(userrecord_dbdata_variables['DerivedSubscribedAppsRecord'])
            numbers_list = Numbers.split(',')
            sub_dict = {utilities.decimal_to_32hex(number): '' for number in numbers_list}
            user_registry_builder.add_entry(b"\x08\x00\x00\x00", sub_dict)

            user_registry_builder.add_entry(b"\x09\x00\x00\x00", str(utilities.datetime_to_steamtime(userrecord_dbdata_variables['LastRecalcDerivedSubscribedAppsTime'])))
            user_registry_builder.add_entry(b"\x0a\x00\x00\x00", str(utilities.decimal_to_32hex(userrecord_dbdata_variables['Cellid'])))
            user_registry_builder.add_entry(b"\x0b\x00\x00\x00", str(userrecord_dbdata_variables['AccountEmailAddress'] + b"\x00"))

            user_registry_builder.add_entry(
                b"\x0e\x00\x00\x00",
                str(utilities.datetime_to_steamtime(userrecord_dbdata_variables['AccountLastModifiedTime'])))

            username = ""
            username = userrecord_dbdata_variables['UniqueUserName']
            # Assuming userrecord_dbdata_variables is a dictionary with your data
            # Assuming userrecord_dbdata_variables['SteamLocalUserID'] is an integer
            steam_local_user_id = userrecord_dbdata_variables['SteamLocalUserID']

            hex_string = '%x' % steam_local_user_id
            user_registry_builder.AccountUsersRecord(
                username.encode("ascii"), {
                    b"\x01\x00\x00\x00": utilities.decimal_to_32hex(userrecord_dbdata_variables['SteamLocalUserID']) + b"\x00\x00\x00\x00",
                    b"\x02\x00\x00\x00": utilities.decimal_to_16hex(userrecord_dbdata_variables['UserType']),
                    b"\x03\x00\x00\x00": {},
                })

            i = 0
            subscriptionsbilling_record_data = self.select_data('accountsubscriptionsbillinginforecord', condition="UserRegistry_UniqueID = '{}'".format(userrecord_dbdata_variables['UniqueID']))
            num_subscriptionsbilling_record_rows = len(subscriptionsbilling_record_data)

            if len(subscriptionsbilling_record_data) > 0 :
                while (i < num_subscriptionsbilling_record_rows) :

                    SubscriptionBillingInfoTypeid = subscriptionsbilling_record_data[i]['SubscriptionID']
                    AccountPaymentCardInfoRecord = subscriptionsbilling_record_data[i]['AccountPaymentCardInfoRecord']

                    if AccountPaymentCardInfoRecord == '7' :
                        user_registry_builder.add_account_subscriptions_billing_info(
                            utilities.decimal_to_32hex(SubscriptionBillingInfoTypeid),
                            utilities.decimal_to_8hex(AccountPaymentCardInfoRecord)
                            )

                    elif AccountPaymentCardInfoRecord == '6' :
                        subprepurchase_record_data = self.select_data('accountprepurchasedinforecord', condition="UniqueID = '{}'".format(subscriptionsbilling_record_data[i]['AccountPrepurchasedInfoRecord_UniqueID']))
                        user_registry_builder.add_account_subscriptions_billing_info(
                            utilities.decimal_to_32hex(SubscriptionBillingInfoTypeid),
                            utilities.decimal_to_8hex(AccountPaymentCardInfoRecord),
                            subprepurchase_record_data[0]['TypeOfProofOfPurchase'] + "\x00",
                            subprepurchase_record_data[0]['BinaryProofOfPurchaseToken'] + "\x00"
                            )

                    elif AccountPaymentCardInfoRecord == '5' :
                        subpaymentcard_record_data = self.select_data('accountpaymentcardinforecord', condition="UniqueID = '{}'".format(subscriptionsbilling_record_data[i]['AccountPaymentCardReceiptRecord_UniqueID']))
                        paymentcard_dbdata_variables = subpaymentcard_record_data[0]
                        user_registry_builder.add_account_subscriptions_billing_info(
                            utilities.decimal_to_32hex(SubscriptionBillingInfoTypeid),
                            utilities.decimal_to_8hex(AccountPaymentCardInfoRecord),
                            utilities.decimal_to_8hex(paymentcard_dbdata_variables['PaymentCardType']),
                            paymentcard_dbdata_variables['CardNumber'] +
                            b'\x00',
                            paymentcard_dbdata_variables['CardHolderName'] +
                            b'\x00',
                            paymentcard_dbdata_variables['CardExpYear'] +
                            b'\x00',
                            paymentcard_dbdata_variables['CardExpMonth'] +
                            b'\x00',
                            paymentcard_dbdata_variables['CardCVV2'] +
                            b'\x00',
                            paymentcard_dbdata_variables['BillingAddress1'] +
                            b'\x00',
                            paymentcard_dbdata_variables['BillingAddress2'] +
                            b'\x00',
                            paymentcard_dbdata_variables['BillingCity'] +
                            b'\x00',
                            paymentcard_dbdata_variables['BillingZip'] +
                            b'\x00',
                            paymentcard_dbdata_variables['BillingState'] +
                            b'\x00',
                            paymentcard_dbdata_variables['BillingCountry'] +
                            b'\x00',
                            paymentcard_dbdata_variables['BillingPhone'] +
                            b'\x00',
                            paymentcard_dbdata_variables['BillinEmailAddress'] +
                            b'\x00',
                            utilities.decimal_to_16hex(paymentcard_dbdata_variables['PriceBeforeTax']),
                            utilities.decimal_to_16hex(paymentcard_dbdata_variables['TaxAmount']),
                        )

                    else :
                        log.error(clientid + "User Has No Subscriptions!  Should have atleast subscription 0!")

                    i = i + 1

            # Retrieve the inserted variables from the 'accountsubscriptionsrecord' table
            subscription_record_variables = self.select_data('accountsubscriptionsrecord', condition="UserRegistry_UniqueID = '{}'".format(userrecord_dbdata_variables['UniqueID']))
            num_subscription_record_rows = len(subscription_record_variables)

            i = 0
            if num_subscription_record_rows > 0 :
                while (i < num_subscription_record_rows) :
                    user_registry_builder.add_account_subscription(
                            utilities.decimal_to_32hex(subscription_record_variables[i]['SubscriptionID']),
                            str(utilities.datetime_to_steamtime(subscription_record_variables[i]['SubscribedDate'])),
                            str(utilities.datetime_to_steamtime(subscription_record_variables[i]['UnsubscribedDate'])),
                            utilities.decimal_to_16hex(subscription_record_variables[i]['SubscriptionStatus']),
                            utilities.decimal_to_8hex(subscription_record_variables[i]['StatusChangeFlag']),
                            utilities.decimal_to_16hex(subscription_record_variables[i]['PreviousSubscriptionState'])
                            )
                    i = i + 1

            # Build the user_registry dictionary
            built_user_registry = user_registry_builder.build()

            return built_user_registry
        else :
            log.error(clientid + "User Does Not Exist!  Should Not Have Gotten This Far!")
            return 1  # User does not exist

    def check_username(self, username, namecheck=0):
        rows = self.select_data('userregistry', '*', "UniqueUserName = '{}'".format(username))
        if rows:
            banned_value = rows[0]['Banned']
            if banned_value == 1 and namecheck == 1:
                return -1
            return 1
        else:
            return 0

    def check_userpw(self, username):
        user_registry_data = self.select_data('userregistry', condition="UniqueUserName = '{}'".format(username))
        if len(user_registry_data) > 0:
            return user_registry_data[0]['SaltedPassphraseDigest']
        else:
            return 0

    def get_uniqueuserid(self, username):
        user_registry_data = self.select_data('userregistry', condition="UniqueUserName = '{}'".format(username))
        if len(user_registry_data) > 0:
            return user_registry_data[0]['UniqueID']
        else:
            return 0

    def get_userpass_stuff(self, username):
        user_registry_data = self.select_data('userregistry', condition="UniqueUserName = '{}'".format(username))
        if len(user_registry_data) > 0:
            return user_registry_data[0]['SaltedPassphraseDigest'], user_registry_data[0]['PassphraseSalt']
        else:
            return 0

    def get_numaccts_with_email(self, email):
        rows = self.select_data("userregistry", "*", "AccountEmailAddress = '{}'".format(email))
        print len(rows)
        if rows:
            return len(rows)
        else:
            return 0

    def change_password(self, username, hash, salted_hash):
        pass

    def change_email(self, username, old_email, new_email):
        pass
    def change_personalquestion(self, username, personalquestion):
        pass

class MySQLDatabase(GenericDatabase):
    def connect(self, config):
        self.connection = MySQLdb.connect(
            host=config['mysql_host'],
            user=config['mysql_username'],
            passwd=config['mysql_password'],
            db=config['database'],
            charset='utf8'
        )
        mysql_url = "mysql://"+user+":"+passwd+"@"+host+"/"+database

        self.connect = create_engine(mysql_url)


class SQLiteDatabase(GenericDatabase):
    def connect(self, config):
        sqlite_url = "sqlite:///stmserver.db" #+config['database']
        self.connection = create_engine(sqlite_url)



def initialize_database_connection(config, db_type):
    global db_connection
    if db_connection:
        print "already connected"
        return db_connection
    if db_type == 'mysql':
        print "mysql"
        db = MySQLDatabase(config)
    elif db_type == 'sqlite':
        print "sqlite"
        db = SQLiteDatabase(config)
    else:
        raise ValueError("Unsupported database type: {}".format(db_type))

    db.connect(config)
    db_connection = db
    return db

def get_database_connection():
    if not db_connection:
        raise ValueError("Database connection has not been initialized. Call initialize_database_connection() first.")
    return db_connection
