import binascii
import logging
import random

from sqlalchemy import text

import utils
from userregistry import UserRegistryBuilder

# OopCompanion:suppressRename

log = logging.getLogger("AuthDataBase")


class AuthDatabase(object):

    def __init__(self, db_instance):
        self.steam_id = None
        self.unique_id = None
        self.db = db_instance

    def create_user(self, username, salted_answer_to_question_digest, passphrase_salt, answer_to_question_salt, personal_question, salted_passphrase_digest, account_email_address):

        self.unique_id = self.db.get_next_available_id('userregistry', 'UniqueID')
        self.steam_id = self.db.get_next_available_id('userregistry', 'SteamLocalUserID')

        accountcreationtime = utils.get_current_datetime()

        expanded_numbers = []
        ranges = ["1-5", "11-25", "30-35", "40-45", "50-51", "56", "60-65", "70", "72-79", "81-89", "92", "104-111", "204", "205", "242-253", "0", "260", "80", "95", "100", "101-103", "200", "210", "241"]
        for r in ranges:
            if "-" in r:
                start, end = map(int, r.split("-"))
                expanded_numbers.extend(range(start, end + 1))
            else:
                expanded_numbers.append(int(r))

        DerivedSubscribedAppsRecord_value = ",".join(map(str, expanded_numbers))

        if self.check_username(username) != 0:
            return -1
        data = {'UniqueID':self.unique_id, 'UniqueUserName':username, 'subscriptionrecord_version':'4', 'AccountCreationTime':accountcreationtime, 'OptionalAccountCreationKey':'Egq-pe-y', 'SteamLocalUserID':self.steam_id, 'UserType':1, 'SaltedAnswerToQuestionDigest':binascii.b2a_hex(salted_answer_to_question_digest), 'PassphraseSalt':binascii.b2a_hex(passphrase_salt), 'AnswerToQuestionSalt':binascii.b2a_hex(answer_to_question_salt), 'PersonalQuestion':personal_question, 'SaltedPassphraseDigest':binascii.b2a_hex(salted_passphrase_digest), 'LastRecalcDerivedSubscribedAppsTime':accountcreationtime, 'Cellid':'1', 'AccountEmailAddress':account_email_address, 'Banned':'0', 'AccountLastModifiedTime':accountcreationtime, 'DerivedSubscribedAppsRecord':DerivedSubscribedAppsRecord_value}

        try:
            self.db.insert_data('userregistry', data)  # Process the result if there is no error
        except Exception as e:
            # Handle the exception here (e.g., print an error message)
            log.error("(SQLError)[Create User] Error occurred while inserting into userregistry:", e)
            return -1

        next_unique_sub_id = self.db.get_next_id('accountsubscriptionsrecord', 'UniqueID')

        data = {'UniqueID':                 next_unique_sub_id, 'UserRegistry_UniqueID':self.unique_id, 'SubscriptionID':'0', 'SubscribedDate':accountcreationtime, 'UnsubscribedDate':utils.add_100yrs(accountcreationtime), 'SubscriptionStatus':'1',  # Set the subscription status value here
                'StatusChangeFlag':         '0',  # Set the status change flag value here
                'PreviousSubscriptionState':'0'  # Set the previous subscription state value here
        }
        try:
            self.db.insert_data('accountsubscriptionsrecord', data)
        except Exception as e:
            # Handle the exception here (e.g., print an error message)
            log.error("(SQLError)[Create User] Error occurred while inserting into accountsubscriptionsrecord:", e)
            return -1

        next_unique_billing_id = self.db.get_next_id('accountsubscriptionsbillinginforecord', 'UniqueID')

        data = {'UniqueID':                    next_unique_billing_id, 'UserRegistry_UniqueID':self.unique_id, 'Subscriptionid':'0',  # subbillinginfo.SubscriptionID,
                'AccountPaymentCardInfoRecord':'7', }
        try:
            self.db.insert_data('accountsubscriptionsbillinginforecord', data)
        except Exception as e:
            # Handle the exception here (e.g., print an error message)
            log.error("(SQLError)[Create User] Error occurred while inserting into accountsubscriptionsbillinginforecord:", e)
            return -1

        log.info("New User Created & Added To Database: " + username)
        return 0

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

    def insert_subscription(self, username, SubscriptionID, paymenttype, tuple_paymentrecord = None):

        UserRegistry_UniqueID = self.get_uniqueuserid(username)

        current_time = utils.get_current_datetime()

        next_unique_sub_id = self.db.get_next_id('accountsubscriptionsrecord', 'UniqueID')

        data = {'UniqueID':                 next_unique_sub_id, 'UserRegistry_UniqueID':UserRegistry_UniqueID, 'SubscriptionID':SubscriptionID,  # Set the subscribed date value here
                'SubscribedDate':           current_time,  # Set the unsubscribed date value here
                'UnsubscribedDate':         utils.add_100yrs(current_time), 'SubscriptionStatus':'1',  # Set the subscription status value here
                'StatusChangeFlag':         '0',  # Set the status change flag value here
                'PreviousSubscriptionState':'0'  # Set the previous subscription state value here
        }
        try:
            self.db.insert_data('accountsubscriptionsrecord', data)
        except Exception as e:
            # Handle the exception here (e.g., print an error message)
            log.error("(SQLError)[Insert Sub] Error occurred while inserting into accountsubscriptionsrecord:", e)
            return -1

        if paymenttype == 6:
            next_unique_prepurchase_id = 0
            next_unique_prepurchase_id = self.db.get_next_id('accountprepurchasedinforecord', 'UniqueID')

            (TypeOfProofOfPurchase, BinaryProofOfPurchaseToken) = tuple_paymentrecord

            data = {'UniqueID':next_unique_prepurchase_id, 'UserRegistry_UniqueID':UserRegistry_UniqueID, 'TypeOfProofOfPurchase':TypeOfProofOfPurchase, 'BinaryProofOfPurchaseToken':BinaryProofOfPurchaseToken}
            try:
                self.db.insert_data('accountprepurchasedinforecord', data)
            except Exception as e:
                # Handle the exception here (e.g., print an error message)
                log.error("(SQLError)[Insert Sub] Error occurred while inserting into accountprepurchasedinforecord:", e)
                return -1
        elif paymenttype == 5:
            next_unique_paymentcard_recordID = 0
            next_unique_paymentcard_recordID = self.db.get_next_id('accountpaymentcardinforecord', 'UniqueID')

            (PaymentCardType, CardNumber, CardHolderName, CardExpYear, CardExpMonth, CardCVV2, BillingAddress1, BillingAddress2, BillingCity, BillinZip, BillingState, BillingCountry, BillingPhone, BillinEmailAddress, PriceBeforeTax, TaxAmount) = tuple_paymentrecord

            data = {'UniqueID':next_unique_paymentcard_recordID, 'UserRegistry_UniqueID':UserRegistry_UniqueID, 'PaymentCardType':PaymentCardType, 'CardNumber':CardNumber, 'CardHolderName':CardHolderName, 'CardExpYear':CardExpYear, 'CardExpMonth':CardExpMonth, 'CardCVV2':CardCVV2, 'BillingAddress1':BillingAddress1, 'BillingAddress2':BillingAddress2, 'BillingCity':BillingCity, 'BillingZip':BillinZip, 'BillingState':BillingState, 'BillingCountry':BillingCountry, 'BillingPhone':BillingPhone, 'BillinEmailAddress':BillinEmailAddress, 'PriceBeforeTax':PriceBeforeTax, 'TaxAmount':TaxAmount, }
            try:
                self.db.insert_data('accountpaymentcardinforecord', data)
            except Exception as e:
                # Handle the exception here (e.g., print an error message)
                log.error("(SQLError)[Insert Sub] Error occurred while inserting into accountpaymentcardinforecord:", e)
                return -1
        else:  # Payment id must either be 7 or unknown
            if paymenttype != 7:
                log.error(username + "Has an invalid payment type id! PaymentTypeID: " + str(paymenttype))
            pass

        paymenttype = 5 if paymenttype == 1 else (6 if paymenttype == 2 else 7)  # Set the result id (4-7) instead of using the request id (1-3)

        next_unique_billing_id = 0
        next_unique_billing_id = self.db.get_next_id('accountsubscriptionsbillinginforecord', 'UniqueID')
        data = {'UniqueID':next_unique_billing_id, 'UserRegistry_UniqueID':UserRegistry_UniqueID, 'SubscriptionID':SubscriptionID, 'AccountPaymentCardInfoRecord':paymenttype, }

        if paymenttype == 5:
            data['AccountPaymentCardReceiptRecord_recordID'] = next_unique_paymentcard_recordID
        elif paymenttype == 6:
            data['AccountPrepurchasedInfoRecord_UniqueID'] = next_unique_prepurchase_id
        try:
            self.db.insert_data('accountsubscriptionsbillinginforecord', data)
        except Exception as e:
            # Handle the exception here (e.g., print an error message)
            log.error("(SQLError)[Insert Sub] Error occurred while inserting into accountsubscriptionsbillinginforecord:", e)
            return -1
        log.info("Successfully inserted new Subscription To Database, Subscription ID: " + str(SubscriptionID) + " Username: " + username)

    #############################################################
    #  Get Database Info for user trying to log in.
    #  Notes:  Deal with Payment Record Types 1-4, currently only deal with 5, 6 and 7
    #############################################################
    def get_user_dictionary(self, username):

        user_registry_builder = UserRegistryBuilder()

        userrecord_dbdata = self.db.select_data('userregistry', condition = "UniqueUserName = '{}'".format(username))

        userrecord_dbdata_variables = userrecord_dbdata[0]

        subscription_record_variables = None
        billing_info_variables = None

        if len(userrecord_dbdata) > 1:

            log.error("More than 1 row returned when loading user from database! user: " + username)
            return 2
        elif len(userrecord_dbdata) > 0:

            user_registry_builder.add_entry(b"\x00\x00\x00\x00", utils.to_hex_16bit(userrecord_dbdata_variables['subscriptionrecord_version']))
            user_registry_builder.add_entry(b"\x01\x00\x00\x00", bytes(userrecord_dbdata_variables['UniqueUserName'] + b"\x00"))
            user_registry_builder.add_entry(b"\x02\x00\x00\x00", str(utils.datetime_to_steamtime(userrecord_dbdata_variables['AccountCreationTime'])))
            user_registry_builder.add_entry(b"\x03\x00\x00\x00", str(userrecord_dbdata_variables['OptionalAccountCreationKey'] + b'\x00'))

            Numbers = str(userrecord_dbdata_variables['DerivedSubscribedAppsRecord'])
            numbers_list = Numbers.split(',')
            sub_dict = {utils.to_hex_32bit(number):'' for number in numbers_list}
            user_registry_builder.add_entry(b"\x08\x00\x00\x00", sub_dict)

            user_registry_builder.add_entry(b"\x09\x00\x00\x00", str(utils.datetime_to_steamtime(userrecord_dbdata_variables['LastRecalcDerivedSubscribedAppsTime'])))
            user_registry_builder.add_entry(b"\x0a\x00\x00\x00", str(utils.to_hex_32bit(userrecord_dbdata_variables['Cellid'])))
            user_registry_builder.add_entry(b"\x0b\x00\x00\x00", str(userrecord_dbdata_variables['AccountEmailAddress'] + b"\x00"))
            user_registry_builder.add_entry(b"\x0e\x00\x00\x00", str(utils.datetime_to_steamtime(userrecord_dbdata_variables['AccountLastModifiedTime'])))

            username = b""
            username = userrecord_dbdata_variables['UniqueUserName']
            # Assuming userrecord_dbdata_variables is a dictionary with your data
            # Assuming userrecord_dbdata_variables['SteamLocalUserID'] is an integer
            steam_local_user_id = userrecord_dbdata_variables['SteamLocalUserID']

            hex_string = '%x' % steam_local_user_id
            user_registry_builder.AccountUsersRecord(username.encode("ascii"), {b"\x01\x00\x00\x00":utils.to_hex_32bit(userrecord_dbdata_variables['SteamLocalUserID']) + b"\x00\x00\x00\x00", b"\x02\x00\x00\x00":utils.to_hex_16bit(userrecord_dbdata_variables['UserType']), b"\x03\x00\x00\x00":{}, })

            i = 0
            subscriptionsbilling_record_data = self.db.select_data('accountsubscriptionsbillinginforecord', condition = "UserRegistry_UniqueID = '{}'".format(userrecord_dbdata_variables['UniqueID']))
            num_subscriptionsbilling_record_rows = len(subscriptionsbilling_record_data)

            if len(subscriptionsbilling_record_data) > 0:
                while (i < num_subscriptionsbilling_record_rows):

                    SubscriptionBillingInfoTypeid = subscriptionsbilling_record_data[i]['SubscriptionID']
                    AccountPaymentCardInfoRecord = subscriptionsbilling_record_data[i]['AccountPaymentCardInfoRecord']

                    if AccountPaymentCardInfoRecord == '7':
                        user_registry_builder.add_account_subscriptions_billing_info(utils.to_hex_32bit(SubscriptionBillingInfoTypeid), utils.to_hex_8bit(AccountPaymentCardInfoRecord))

                    elif AccountPaymentCardInfoRecord == '6':
                        subprepurchase_record_data = self.db.select_data('accountprepurchasedinforecord', condition = "UniqueID = '{}'".format(subscriptionsbilling_record_data[i]['AccountPrepurchasedInfoRecord_UniqueID']))
                        user_registry_builder.add_account_subscriptions_billing_info(utils.to_hex_32bit(SubscriptionBillingInfoTypeid), utils.to_hex_8bit(AccountPaymentCardInfoRecord), subprepurchase_record_data[0]['TypeOfProofOfPurchase'] + "\x00", subprepurchase_record_data[0]['BinaryProofOfPurchaseToken'] + "\x00")

                    elif AccountPaymentCardInfoRecord == '5':
                        subpaymentcard_record_data = self.db.select_data('accountpaymentcardinforecord', condition = "UniqueID = '{}'".format(subscriptionsbilling_record_data[i]['AccountPaymentCardReceiptRecord_UniqueID']))
                        paymentcard_dbdata_variables = subpaymentcard_record_data[0]

                        user_registry_builder.add_account_subscriptions_billing_info(utils.to_hex_32bit(SubscriptionBillingInfoTypeid), utils.to_hex_8bit(AccountPaymentCardInfoRecord), utils.to_hex_8bit(paymentcard_dbdata_variables['PaymentCardType']),
                                paymentcard_dbdata_variables['CardNumber'] + b'\x00', paymentcard_dbdata_variables['CardHolderName'] + b'\x00', paymentcard_dbdata_variables['CardExpYear'] + b'\x00', paymentcard_dbdata_variables['CardExpMonth'] + b'\x00', paymentcard_dbdata_variables['CardCVV2'] + b'\x00', paymentcard_dbdata_variables['BillingAddress1'] + b'\x00', paymentcard_dbdata_variables['BillingAddress2'] + b'\x00', paymentcard_dbdata_variables['BillingCity'] + b'\x00', paymentcard_dbdata_variables['BillingZip'] + b'\x00', paymentcard_dbdata_variables['BillingState'] + b'\x00', paymentcard_dbdata_variables['BillingCountry'] + b'\x00', paymentcard_dbdata_variables['BillingPhone'] + b'\x00', paymentcard_dbdata_variables['BillinEmailAddress'] + b'\x00', utils.to_hex_16bit(paymentcard_dbdata_variables['PriceBeforeTax']), utils.to_hex_16bit(paymentcard_dbdata_variables['TaxAmount']), )

                    else:
                        log.error("User Has No Subscriptions!  Should have atleast subscription 0!")

                    i = i + 1

            # Retrieve the inserted variables from the 'accountsubscriptionsrecord' table
            subscription_record_variables = self.db.select_data('accountsubscriptionsrecord', condition = "UserRegistry_UniqueID = '{}'".format(userrecord_dbdata_variables['UniqueID']))
            num_subscription_record_rows = len(subscription_record_variables)

            i = 0
            if num_subscription_record_rows > 0:
                while (i < num_subscription_record_rows):
                    user_registry_builder.add_account_subscription(utils.to_hex_32bit(subscription_record_variables[i]['SubscriptionID']), str(utils.datetime_to_steamtime(subscription_record_variables[i]['SubscribedDate'])), str(utils.datetime_to_steamtime(subscription_record_variables[i]['UnsubscribedDate'])), utils.to_hex_16bit(subscription_record_variables[i]['SubscriptionStatus']), utils.to_hex_8bit(subscription_record_variables[i]['StatusChangeFlag']), utils.to_hex_16bit(subscription_record_variables[i]['PreviousSubscriptionState']))
                    i = i + 1

            # Build the user_registry dictionary
            built_user_registry = user_registry_builder.build()

            return built_user_registry
        else:
            log.error("(SQLError)[Get_Dictionary] User Does Not Exist!  Should Not Have Gotten This Far!")
            return 1  # User does not exist

    #############################################################
    #  Get Database Info for Beta1
    #  Notes:  Deal with Payment Record Types 1-4, currently only deal with 5, 6 and 7
    #############################################################

    def insert_subscription_beta1(self, username, SubscriptionID):
        UserRegistry_UniqueID = self.get_uniqueuserid(username)

        current_time = utils.get_current_datetime()

        next_unique_sub_id = self.db.get_next_id('beta1_subscriptions', 'UniqueID')

        data = {'UniqueID':      next_unique_sub_id, 'UserRegistry_UniqueID':UserRegistry_UniqueID, 'SubscriptionID':SubscriptionID,  # Set the subscribed date value here
                'SubscribedDate':current_time,  # Set the unsubscribed date value here
        }
        try:
            self.db.insert_data('accountsubscriptionsrecord', data)
        except Exception as e:
            # Handle the exception here (e.g., print an error message)
            log.error("(SQLError)[Insert Sub] Error occurred while inserting into accountsubscriptionsrecord:", e)
            return -1

    def get_user_dictionary_beta1(self, username):

        user_registry_builder = UserRegistryBuilder()

        userrecord_dbdata = self.db.select_data('userregistry', condition = "UniqueUserName = '{}'".format(username))

        userrecord_dbdata_variables = userrecord_dbdata[0]

        subscription_record_variables = None

        if len(userrecord_dbdata) > 1:

            log.error("More than 1 row returned when loading user from database! user: " + username)
            return 2
        elif len(userrecord_dbdata) > 0:

            user_registry_builder.add_entry(b"\x00\x00\x00\x00", "\x01\x00")  # Record Version, beta1 = v1

            user_registry_builder.add_entry(b"\x01\x00\x00\x00", bytes(userrecord_dbdata_variables['UniqueUserName'] + b"\x00"))

            user_registry_builder.add_entry(b"\x02\x00\x00\x00", str(utils.datetime_to_steamtime(userrecord_dbdata_variables['AccountCreationTime'])))

            user_registry_builder.add_entry(b"\x03\x00\x00\x00", str(userrecord_dbdata_variables['OptionalAccountCreationKey'] + b'\x00'))

            Numbers = str(userrecord_dbdata_variables['DerivedSubscribedAppsRecord'])
            numbers_list = Numbers.split(',')
            sub_dict = {utils.to_hex_32bit(number):'' for number in numbers_list}
            user_registry_builder.add_entry(b"\x08\x00\x00\x00", sub_dict)

            user_registry_builder.add_entry(b"\x09\x00\x00\x00", str(utils.datetime_to_steamtime(userrecord_dbdata_variables['LastRecalcDerivedSubscribedAppsTime'])))

            user_registry_builder.add_entry(b"\x0a\x00\x00\x00", str(utils.to_hex_32bit(userrecord_dbdata_variables['Cellid'])))

            username = ""
            username = userrecord_dbdata_variables['UniqueUserName']
            steam_local_user_id = userrecord_dbdata_variables['SteamLocalUserID']

            hex_string = '%x' % steam_local_user_id
            user_registry_builder.AccountUsersRecord(username.encode("ascii"), {b"\x01\x00\x00\x00":utils.to_hex_32bit(userrecord_dbdata_variables['SteamLocalUserID']), b"\x02\x00\x00\x00":utils.to_hex_16bit(1), b"\x03\x00\x00\x00":{}, })

            # Retrieve the inserted variables from the 'accountsubscriptionsrecord' table
            subscription_record_variables = self.db.select_data('accountsubscriptionsrecord', condition = "UserRegistry_UniqueID = '{}'".format(userrecord_dbdata_variables['UniqueID']))
            num_subscription_record_rows = len(subscription_record_variables)

            i = 0
            if num_subscription_record_rows > 0:
                while i < num_subscription_record_rows:
                    user_registry_builder.add_account_subscription_beta1(utils.to_hex_32bit(subscription_record_variables[i]['SubscriptionID']), str(utils.datetime_to_steamtime(subscription_record_variables[i]['SubscribedDate'])), str(utils.datetime_to_steamtime(subscription_record_variables[i]['UnsubscribedDate'])))
                    i += 1

            # Build the user_registry dictionary
            built_user_registry = user_registry_builder.build_beta1()

            return built_user_registry
        else:
            log.error("(SQLError)[Get_Dictionary] User Does Not Exist!  Should Not Have Gotten This Far!")
            return 0  # User does not exist

    def update_subscription_records(self, username, status, flag, state):
        try:
            # Get the 'UniqueID' for the given 'UniqueUserName' (assuming 'UniqueUserName' is unique)
            user_query = "SELECT UniqueID FROM userregistry WHERE UniqueUserName = :username"
            user_result = self.db.execute_query_with_result(user_query, {'username':username})

            if not user_result:
                print("User not found.")
                return False

            unique_id = user_result[0]['UniqueID']

            # Update subscription records for the user with the retrieved 'UniqueID'
            update_query = """
                UPDATE accountsubscriptionsrecord
                SET SubscriptionStatus = :status, StatusChangeFlag = :flag, PreviousSubscriptionState = :state
                WHERE UserRegistry_UniqueID = :unique_id
            """

            parameters = {'status':status, 'flag':flag, 'state':state, 'unique_id':unique_id}

            self.db.execute_query(update_query, parameters)

            return True  # Update was successful
        except Exception as e:
            log.error("(SQLError)[Update_Subscription] Error updating subscription records:")
            return False  # Update failed

    def generate_and_insert_verification_code(self, username):
        try:
            # Generate a random verification code
            verification_code = str(random.randint(100000, 999999))

            # Update the 'userregistry' table with the verification code
            update_query = text("UPDATE userregistry SET email_verificationcode = :verification_code WHERE UniqueUserName = :username")

            self.db.session.execute(update_query, {"verification_code":verification_code, "username":username}, )

            # Retrieve the 'AccountEmailAddress' and 'PersonalQuestion' for the same row
            select_query = text("SELECT AccountEmailAddress, PersonalQuestion FROM userregistry WHERE UniqueUserName = :username")

            result = self.db.session.execute(select_query, {"username":username}).fetchone()

            self.db.session.commit()

            if result:
                return {"AccountEmailAddress":result[0], "PersonalQuestion":result[1], "VerificationCode":verification_code, }
            else:
                return -1
        except Exception as e:
            log.error("(SQLError)[insert Verification] Error when inserting generated verification code or retreiving user email.")
            return None

    def reset_verification_code(self, username):
        try:
            # Update the 'userregistry' table to set 'email_verificationcode' to null
            update_query = text("UPDATE userregistry SET email_verificationcode = NULL WHERE UniqueUserName = :username")

            self.db.session.execute(update_query, {"username":username})
            self.db.session.commit()

            return True  # Success
        except Exception as e:
            print("Error:", e)
            return False  # Failed to reset verification code

    def check_username(self, username, namecheck = 0):
        rows = self.db.select_data('userregistry', '*', "UniqueUserName = '{}'".format(username))
        if rows:
            banned_value = rows[0]['Banned']
            if banned_value == 1 and namecheck == 1:
                return -1
            return 1
        else:
            return 0

    def check_userpw(self, username):
        user_registry_data = self.db.select_data('userregistry', condition = "UniqueUserName = '{}'".format(username))
        if len(user_registry_data) > 0:
            return user_registry_data[0]['SaltedPassphraseDigest']
        else:
            return 0

    def get_uniqueuserid(self, username):
        user_registry_data = self.db.select_data('userregistry', condition = "UniqueUserName = '{}'".format(username))
        if len(user_registry_data) > 0:
            return user_registry_data[0]['UniqueID']
        else:
            return 0

    def get_questionsalt(self, username):
        user_registry_data = self.db.select_data('userregistry', condition = "UniqueUserName = '{}'".format(username))
        if len(user_registry_data) > 0:
            return user_registry_data[0]['AnswerToQuestionSalt']
        else:
            return 0

    def get_userpass_stuff(self, username):
        user_registry_data = self.db.select_data('userregistry', condition = "UniqueUserName = '{}'".format(username))
        if len(user_registry_data) > 0:
            return user_registry_data[0]['SaltedPassphraseDigest'], user_registry_data[0]['PassphraseSalt']
        else:
            return 0

    def get_numaccts_with_email(self, email):
        rows = self.db.select_data("userregistry", "*", "AccountEmailAddress = '{}'".format(email))
        # print(len(rows))
        if rows:
            return len(rows)
        else:
            return 0

    def check_resetemail(self, email):
        user_registry_data = self.db.select_data('userregistry', condition = "AccountEmailAddress = '{}'".format(email))
        if len(user_registry_data) > 0:
            return True
        else:
            return False

    def check_resetcdkey(self, cdkey):
        checkkey_dbdata = self.db.select_data('accountprepurchasedinforecord', condition = "BinaryProofOfPurchaseToken = '{}'".format(cdkey))
        if checkkey_dbdata:
            return True
        else:
            return False

    def change_password(self, username, pass_salt, salted_digest):
        # Dictionary containing data to be updated
        data = {'SaltedPassphraseDigest':salted_digest, 'PassphraseSalt':pass_salt}

        # Condition for the update (where clause)
        condition = "Username = '{}'".format(username)

        # Use the update_data method to change the email
        success = self.db.update_data('userregistry', data, condition)

        return success

    def change_email(self, username, new_email):
        # Dictionary containing data to be updated
        data = {'UserEmailAddress':new_email}

        # Condition for the update (where clause)
        condition = "Username = '{}'".format(username)

        # Use the update_data method to change the email
        success = self.db.update_data('userregistry', data, condition)

        return success

    def change_question(self, username, question, saltedanswer, answertoquestionsalt):
        # Dictionary containing data to be updated
        data = {'PersonalQuestion':question, 'SaltedAnswerToQuestionDigest':saltedanswer, 'AnswerToQuestionSalt':answertoquestionsalt}

        # Condition for the update (where clause)
        condition = "Username = '{}'".format(username)

        # Use the update_data method to change the email
        success = self.db.update_data('userregistry', data, condition)

        return success