import MySQLdb
import sqlite3
import time
import utilities
import binascii
import logging
import config
import steamemu.logger
from userregistry import UserRegistryBuilder
from datetime import datetime
from subscriberaccount_record import SubscriberAccount_Record
from steamemu.config import read_config

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

    def execute_query(self, query, parameters=None):
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
        return result

    def insert_data(self, table, data):
        columns = ', '.join(data.keys())
        values = ', '.join(['%s'] * len(data)) if isinstance(self.connection,
                           MySQLdb.connections.Connection) else ', '.join(['?'] * len(data))
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
        set_values = ', '.join(['{} = %s'.format(column) for column in data.keys()]) if isinstance(
            self.connection, MySQLdb.connections.Connection) else ', '.join(['{} = ?'.format(column) for column in data.keys()])
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

    def select_data(self, table, columns='*', condition=''):
        query = "SELECT {} FROM {} WHERE {}".format(columns, table, condition) if isinstance(
            self.connection, MySQLdb.connections.Connection) else "SELECT {} FROM {} {}".format(columns, table, condition)
        cursor = self.connection.cursor()

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
            return []


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
        #DerivedSubscribedAppsRecord_list = ['1', '2', '3', '4', '5', '11', '12', '13', '14', '15', '16', '21', '22', '23', '24', '25',
        #'31', '61', '62', '63', '64', '65', '66', '67', '68', '69', '104', '105', '106', '107', '108',
        #'109', '110', '111', '112', '104', '105', '106', '107', '108', '109', '110', '111', '112',
        #'104', '105', '106', '107', '108', '109', '110', '111', '112', '104', '105', '106', '107',
        #'108', '109', '110', '111', '112']
        
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
            # Set the subscribed date value here
            'SubscribedDate': accountcreationtime,
            'UnsubscribedDate':  utilities.add_100yrs(accountcreationtime),
            'SubscriptionStatus':  '1',  # Set the subscription status value here
            'StatusChangeFlag':  '0',  # Set the status change flag value here
            # Set the previous subscription state value here
            'PreviousSubscriptionState':  '0'
        }
        self.insert_data('accountsubscriptionsrecord', data)


        data = {
            'UniqueID': next_unique_sub_id,
            'UserRegistry_UniqueID': next_unique_user_id,
            'SubscriptionID': '1',
            # Set the subscribed date value here
            'SubscribedDate': accountcreationtime,
            'UnsubscribedDate':  utilities.add_100yrs(accountcreationtime),
            'SubscriptionStatus':  '1',  # Set the subscription status value here
            'StatusChangeFlag':  '0',  # Set the status change flag value here
            # Set the previous subscription state value here
            'PreviousSubscriptionState':  '0'
        }
        self.insert_data('accountsubscriptionsrecord', data)

        
        #next_unique_prepurchase_id = self.get_next_id('accountprepurchasedinforecord', 'UniqueID')
        
       #data = {
        #    'UniqueID': next_unique_prepurchase_id,
            # 'TypeOfProofOfPurchase': None,
            # 'BinaryProofOfPurchaseToken': None, #subbillinginfo.SubscriptionID,
            # 'AcctName':  username + '\x00'#subbillinginfo.AccountPaymentCardInfoRecord["value"]
        #}
        #self.insert_data('accountprepurchasedinforecord', data)


        next_unique_billing_id = self.get_next_id('accountsubscriptionsbillinginforecord', 'UniqueID')
        
        data = {
            'UniqueID': next_unique_billing_id,
            'UserRegistry_UniqueID': next_unique_user_id,
            'Subscriptionid': '0',  # subbillinginfo.SubscriptionID,
            # subbillinginfo.AccountPaymentCardInfoRecord["value"]
            'AccountPaymentCardInfoRecord': '7',
            # subbillinginfo.AccountPaymentCardInfoRecord["value"]
            # 'AccountPrepurchasedInfoRecord_UniqueID':  next_unique_prepurchase_id
            # 'AccountExternalBillingInfoRecord_UniqueID':  None, #subbillinginfo.AccountPaymentCardInfoRecord["value"]
            # 'AccountPaymentCardReceiptRecord_recordID':  None #subbillinginfo.AccountPaymentCardInfoRecord["value"]
        }
        self.insert_data('accountsubscriptionsbillinginforecord', data)
        
        log.info("New User Created & Added To Database: " + username)

# to set payment record info, use this tuple:
 #           tuple_variable = (PaymentCardTypeID, CardNumber, CardHolderName, field4, field5,
 #                           field6, BillingAddress1, BillingAddress2, BillingCity, BillingZip, BillingState, BillingCountry,
 #                           CCApprovalCode, PriceBeforeTax, TaxAmount, TransDate, TransTime, AStoBBSTxnId, ShippingCost)

    def insert_subscription(self, username, subscriptionid, typeofproof="", proof_binary="", paymenttype='7', rejectreasion="", tuple_paymentrecord=None):
        unique_userid = self.get_uniqueuserid(username)
        
        current_time = utilities.get_current_datetime()

        
        next_unique_sub_id = self.get_next_id('accountsubscriptionsrecord', 'UniqueID')
        
        data = {
            'UniqueID': next_unique_sub_id,
            'UserRegistry_UniqueID': unique_userid,
            'SubscriptionID': subscriptionid ,
            # Set the subscribed date value here
            'SubscribedDate': current_time,
            # Set the unsubscribed date value here
            'UnsubscribedDate':  utilities.add_100yrs(current_time),
            'SubscriptionStatus':  '1',  # Set the subscription status value here
            'StatusChangeFlag':  '0',  # Set the status change flag value here
            # Set the previous subscription state value here
            'PreviousSubscriptionState':  '0'
        }
        self.insert_data('accountsubscriptionsrecord', data)

        if paymenttype is not '7':
            next_unique_prepurchase_id = self.get_next_id('accountprepurchasedinforecord', 'UniqueID')

            data = {
                'UniqueID': next_unique_prepurchase_id,
                # subbillinginfo.AccountPaymentCardInfoRecord["value"]
                'UserRegistry_UniqueID': unique_userid, 
                # 'TokenRejectionReason': rejectreasion + '\x00'
            }
            if paymenttype is not '\x07':
                data['TypeOfProofOfPurchase'] = typeofproof
                data['BinaryProofOfPurchaseToken'] = proof_binary 
            self.insert_data('accountprepurchasedinforecord', data)


        next_unique_recordID = 0
        if paymenttype is not '7' or paymenttype is not '6':
            next_unique_recordID = self.get_next_id(
                'accountpaymentcardreceiptrecord', 'recordID')

            (PaymentCardTypeID, CardNumber, CardHolderName, field4, field5, field6, BillingAddress1, BillingAddress2,
            BillingCity, BillingZip, BillingState, BillingCountry, CCApprovalCode, PriceBeforeTax, TaxAmount, TransDate,
            TransTime, AStoBBSTxnId, ShippingCost) = tuple_paymentrecord

            data = {
                'recordID': recordID,
                'TypeOfProofOfPurchase': PaymentCardTypeID,
                'CardNumber': CardNumber,
                'CardHolderName': CardHolderName,
                'field4': field4,
                'field5': field5,
                'field6': field6,
                'BillingAddress1': BillingAddress1,
                'BillingAddress2': BillingAddress2,
                'BillingCity': BillingCity,
                'BillingZip': BillingZip,
                'BillingState': BillingState,
                'BillingCountry': BillingCountry,
                'CCApprovalCode': CCApprovalCode,
                'PriceBeforeTax': PriceBeforeTax,
                'TaxAmount': TaxAmount,
                'TransDate': TransDate,
                'TransTime': TransTime,
                'AStoBBSTxnId': AStoBBSTxnId,
                'ShippingCost': ShippingCost
            }
            self.insert_data('accountpaymentcardreceiptrecord', data)

        if paymenttype is not '7':
            next_unique_billing_id = None
        else:
            next_unique_billing_id = self.get_next_id(
                'accountsubscriptionsbillinginforecord', 'UniqueID')
        data = {
            'UniqueID': next_unique_billing_id,
            'UserRegistry_UniqueID': unique_userid,
            'Subscriptionid': subscriptionid,  # subbillinginfo.SubscriptionID,
            # subbillinginfo.AccountPaymentCardInfoRecord["value"]
            'AccountPaymentCardInfoRecord': paymenttype,
            # subbillinginfo.AccountPaymentCardInfoRecord["value"]           
            'AccountPrepurchasedInfoRecord_UniqueID':  next_unique_prepurchase_id,
            # subbillinginfo.AccountPaymentCardInfoRecord["value"]
            'AccountExternalBillingInfoRecord_UniqueID':  None,
            # subbillinginfo.AccountPaymentCardInfoRecord["value"]
            'AccountPaymentCardReceiptRecord_recordID':  None if next_unique_recordID == 0 else next_unique_recordID
        }
        self.insert_data('accountsubscriptionsbillinginforecord', data)
        log.info("Successfully inserted new Subscription To Database, Subscription ID: " + subscriptionid + " Username: " + username)

    # This function retrieves the comma seperated list of DerivedSubscribedAppsRecord. 
    # It then converts the comma seperated integers to 8 byte little endian hex bytes.
    # Then it outputs a nicely formated (hopefully correct) dictionary for use when we send the blob to the user
    def retrieve_data_from_sql(self, username):
        user_registry_data = self.select_data('userregistry', condition="UniqueUserName = '{}'".format(username))
        
        try:
            # Split the comma-separated values into a list of integers
            values_list = [int(val) for val in user_registry_data[0]['DerivedSubscribedAppsRecord'].split(',')]

            # Convert each value to little-endian 4-byte hex and create the dictionary
            result_dict = {utilities.decimal_to_32hex(value): '' for value in values_list}
            
            return result_dict
        except (IndexError, ValueError):  # Handle both IndexError and ValueError
            return 0


    def get_user_dictionary(self, username):
        
        user_registry_builder = UserRegistryBuilder()
        
        userrecord_dbdata = self.select_data('userregistry', condition="UniqueUserName = '{}'".format(username))

        # Access individual variables from the retrieved data
        # Assuming only one row is retrieved
        userrecord_dbdata_variables = userrecord_dbdata[0]
        # apprights_data = self.select_data('UserAppAccessRightsRecord', condition="UniqueID = '{}'".format(user_registry_variables['UniqueID']))
        # if len(apprights_data) > 0:
        subscription_record_variables = None
        billing_info_variables = None
        if len(user_registry_data) < 1:
            log.error("More than 1 row returned when loading user from database! user: " + username)
            return 2
        elif len(user_registry_data) > 0:
            user_registry_builder.add_entry("\x00\x00\x00\x00", utilities.decimal_to_16hex(user_registry_variables['subscriptionrecord_version'])
            user_registry_builder.add_entry("\x01\x00\x00\x00", user_registry_variables['UniqueUserName'] + "\x00")
            user_registry_builder.add_entry("\x02\x00\x00\x00", utilities.datetime_to_steamtime(user_registry_variables['AccountCreationTime']))
            user_registry_builder.add_entry("\x03\x00\x00\x00", user_registry_variables['OptionalAccountCreationKey'])
            # AccountUserPasswordsRecord
            # AccountUsersRecord
            user_registry_builder.AccountUsersRecord({
                user_registry_variables['UniqueUserName']: {
                    "\x01\x00\x00\x00": utilities.decimal_to_64hex(user_registry_variables['SteamLocalUserID']),
                    "\x02\x00\x00\x00": utilities.decimal_to_16hex(user_registry_variables['UserType']),
                    "\x03\x00\x00\x00": {},
                },
            })

            user_registry_builder.add_account_subscription("\x07\x00\x00\x00", subscribed_date, unsubscribed_date, subscription_status, status_change_flag, previous_subscription_state, price_before_tax)

            Numbers = str(user_registry_variables['DerivedSubscribedAppsRecord'])
            numbers_list = Numbers.split(',')
            sub_dict = {utilities.decimal_to_32hex(number): '' for number in numbers_list}
            user_registry_builder.add_entry("\x08\x00\x00\x00", sub_dict)

            user_registry_builder.add_entry("\x09\x00\x00\x00", utilities.datetime_to_steamtime(user_registry_variables['LastRecalcDerivedSubscribedAppsTime']))
            user_registry_builder.add_entry("\x0a\x00\x00\x00", utilities.decimal_to_32hex(user_registry_variables['Cellid']))
            user_registry_builder.add_entry("\x0b\x00\x00\x00", user_registry_variables['AccountEmailAddress'] + "\x00")
            user_registry_builder.add_entry("\x0e\x00\x00\x00", utilities.datetime_to_steamtime(user_registry_variables['AccountLastModifiedTime']))
            
            user_registry_builder.add_account_subscriptions_billing_info("\x01\x00\x00\x00", "\x06", card_number="WONCDKey\x00", card_holder_name="2199807727546")
            user_registry_builder.add_account_subscriptions_billing_info("\x07\x00\x00\x00", "\x05", card_number="5044658124903867\x00", card_holder_name="dsf sdfas\x00", card_exp_year="2015\x00", card_exp_month="07\x00", card_cvv2="476\x00", billing_address1="w154 marvel dr.\x00", billing_city="menomonee falls\x00", billing_zip="53051\x00", billing_state="WI\x00", billing_country="United States\x00", billing_phone="2622523747\x00", billing_email_address="test@test.com\x00", price_before_tax="\xb3\x0b\x00\x00")

            # Build the user_registry dictionary
            built_user_registry = user_registry_builder.build()

            # Convert bytes to escape sequences
            encoded_registry = {key.encode("string-escape"): value.encode("string-escape") if isinstance(value, str) else value for key, value in built_user_registry.items()}
        
        else :
            return 1  # User does not exist

    def get_fulluserblob(self, username):

        UserAccount_Record = SubscriberAccount_Record()

        # Retrieve the inserted variables from the 'userregistry' table
        user_registry_data = self.select_data('userregistry', condition="UniqueUserName = '{}'".format(username))

        # Access individual variables from the retrieved data
        # Assuming only one row is retrieved
        user_registry_variables = user_registry_data[0]
        # apprights_data = self.select_data('UserAppAccessRightsRecord', condition="UniqueID = '{}'".format(user_registry_variables['UniqueID']))
        # if len(apprights_data) > 0:
        subscription_record_variables = None
        billing_info_variables = None

        # Access individual variables from the retrieved data
        if len(user_registry_data) > 0:
            # Access specific variables from the dictionaries
            UserAccount_Record.UniqueID = user_registry_variables['UniqueID']
            UserAccount_Record.Version['value'] = utilities.decimal_to_16hex(user_registry_variables['subscriptionrecord_version'])
            UserAccount_Record.UniqueUserName['value'] = user_registry_variables['UniqueUserName'] + "\x00"
            UserAccount_Record.AccountCreationTime['value'] = utilities.datetime_to_steamtime(user_registry_variables['AccountCreationTime'])
            UserAccount_Record.OptionalAccountCreationKey['value'] = user_registry_variables['OptionalAccountCreationKey']
            UserAccount_Record.LastRecalcDerivedSubscribedAppsTime['value'] = utilities.datetime_to_steamtime(user_registry_variables['LastRecalcDerivedSubscribedAppsTime'])
            UserAccount_Record.Cellid['value'] = utilities.decimal_to_32hex(user_registry_variables['Cellid'])
            UserAccount_Record.AccountEmailAddress['value'] = user_registry_variables['AccountEmailAddress'] + "\x00"
            UserAccount_Record.Banned['value'] = utilities.decimal_to_16hex(user_registry_variables['Banned'])
            UserAccount_Record.AccountLastModifiedTime['value'] = utilities.datetime_to_steamtime(user_registry_variables['AccountLastModifiedTime'])
            
            
            Numbers = str(user_registry_variables['DerivedSubscribedAppsRecord'])
            numbers_list = Numbers.split(',')
            sub_dict = {utilities.decimal_to_32hex(number): '' for number in numbers_list}
            UserAccount_Record.DerivedSubscribedAppsRecord['value'] = sub_dict
            
            UserAccount_Record.set_accountuser(
                utilities.decimal_to_64hex(user_registry_variables['SteamLocalUserID']), utilities.decimal_to_16hex(
                    user_registry_variables['UserType']), None)  # user_registry_variables['UserAppAccessRightsRecord'])
            
        elif len(user_registry_data) < 1:
            log.error("More than 1 row returned when loading user from database! user: " + username)
            return 2
        else:
            return 1  # User does not exist

        i = 0
        subscriptionsbilling_record_data = self.select_data('accountsubscriptionsbillinginforecord', condition="UserRegistry_UniqueID = '{}'".format(UserAccount_Record.UniqueID))
        num_subscriptionsbilling_record_rows = len(subscriptionsbilling_record_data)
        subscription_billing_record_tuple = {}

        if len(subscriptionsbilling_record_data) > 0:
            while (i < num_subscriptionsbilling_record_rows):

                SubscriptionBillingInfoTypeid = subscriptionsbilling_record_data[i]['SubscriptionID']
                AccountPaymentCardInfoRecord = subscriptionsbilling_record_data[i]['AccountPaymentCardInfoRecord']

                subprepurchase_record_data = self.select_data('accountprepurchasedinforecord', condition="UniqueID = '{}'".format(subscriptionsbilling_record_data[i]['AccountPrepurchasedInfoRecord_UniqueID']))
                if AccountPaymentCardInfoRecord == '7':
                    UserAccount_Record.set_subscriptions_billing_info(
                        utilities.decimal_to_32hex(SubscriptionBillingInfoTypeid), utilities.decimal_to_8hex(AccountPaymentCardInfoRecord))
                else:
                    #if len(subprepurchase_record_data) == 1:
                    UserAccount_Record.set_subscriptions_billing_info(utilities.decimal_to_32hex(SubscriptionBillingInfoTypeid), utilities.decimal_to_8hex(AccountPaymentCardInfoRecord), subprepurchase_record_data[0]['TypeOfProofOfPurchase'] + "\x00",
                                                                                                        subprepurchase_record_data[0]['BinaryProofOfPurchaseToken'] + "\x00")
                i = i + 1
                 
        # Retrieve the inserted variables from the 'accountsubscriptionsrecord' table
        subscription_record_variables = self.select_data('accountsubscriptionsrecord', condition="UserRegistry_UniqueID = '{}'".format(UserAccount_Record.UniqueID))
        num_subscription_record_rows = len(subscription_record_variables)
        
        i = 0
        
        if num_subscription_record_rows > 0:
            while (i < num_subscription_record_rows) :
                UserAccount_Record.set_subscription(utilities.decimal_to_32hex(subscription_record_variables[i]['SubscriptionID']), utilities.datetime_to_steamtime(subscription_record_variables[i]['SubscribedDate']), utilities.datetime_to_steamtime(subscription_record_variables[i]['UnsubscribedDate']),
                                                    utilities.decimal_to_16hex(subscription_record_variables[i]['SubscriptionStatus']), utilities.decimal_to_8hex(subscription_record_variables[i]['StatusChangeFlag']), utilities.decimal_to_16hex(subscription_record_variables[i]['PreviousSubscriptionState']))
                i = i + 1
                
        return UserAccount_Record

    def check_username(self, username, namecheck=0):
        rows = self.select_data('userregistry', '*',
                              "UniqueUserName = '{}'".format(username))
        if rows:
            # Access the first result's column by name
            banned_value = rows[0]['Banned']
            if banned_value == 1 and namecheck == 1:
                return -1
            return 1
        else:
            return 0


    def check_userpw(self, username):
        user_registry_data = self.select_data(
            'userregistry', condition="UniqueUserName = '{}'".format(username))
        if len(user_registry_data) > 0:
            return user_registry_data[0]['SaltedPassphraseDigest']
        else:
            return 0


    def get_uniqueuserid(self, username):
        user_registry_data = self.select_data(
            'userregistry', condition="UniqueUserName = '{}'".format(username))
        if len(user_registry_data) > 0:
            return user_registry_data[0]['UniqueID']
        else:
            return 0
        
    def get_userpass_stuff(self, username):
        user_registry_data = self.select_data(
            'userregistry', condition="UniqueUserName = '{}'".format(username))
        if len(user_registry_data) > 0:
            return user_registry_data[0]['SaltedPassphraseDigest'], user_registry_data[0]['PassphraseSalt']
        else:
            return 0


    def get_numaccts_with_email(self, email):
        rows = self.select_data("userregistry", "*",
                                "AccountEmailAddress = '{}'".format(email))
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
        self.connection.autocommit(True)

class SQLiteDatabase(GenericDatabase):
    def connect(self, config):
        self.connection = sqlite3.connect(config['database'])


def initialize_database_connection(config, db_type):
    global db_connection
    if db_connection:
        return db_connection
    if db_type == 'mysql':
        db = MySQLDatabase(config)
    elif db_type == 'sqlite':
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
