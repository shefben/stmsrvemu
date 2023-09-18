import MySQLdb
import sqlite3
from datetime import datetime
import database

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


class SubscriberAccount_Record(object):
    UniqueID = 0
    Version = ""
    UniqueUserName = ""
    AccountCreationTime = ""
    OptionalAccountCreationKey = ""
    UserType = ""
    SteamLocalUserID = ""
    LastRecalcDerivedSubscribedAppsTime = ""
    CellId = ""
    AccountEmailAddress = ""
    AccountStatus = ""
    AccountLastModifiedTime = ""
    
    subscriptions_0f = ""
    subscriptions_07 = ""

    def get_blob_dict(self ):
        
    def generate_user_registry_string(self):
        userreg_first = (
        'user_registry = {'
                '"\\x00\\x00\\x00\\x00": "' + self.Version + '",'
                '"\\x01\\x00\\x00\\x00": "' + self.UniqueUserName + '\\x00",'
                '"\\x02\\x00\\x00\\x00": "' + self.AccountCreationTime + '\\x00",'
                '"\\x03\\x00\\x00\\x00": "' + OptionalAccountCreationKey + '\\x00",'
                '"\\x06\\x00\\x00\\x00:"'
                    '{'
                        '" + username + ":'
                        '{'
                            '"\\x02\\x00\\x00\\x00": "' + self.UserType + '",'
                            '"\\x03\\x00\\x00\\x00": {},'
                            '"\\x01\\x00\\x00\\x00": "' + self.SteamLocalUserID + '",'
                        '}'
                    '},'
                '"\\x07\\x00\\x00\\x00": {'  # Add more entries as needed
        )

        return userreg_first
        
    def generate_subscriptions_string(self, subscriptionid, StatusChangeFlag, PreviousSubscriptionState, UnsubscribedDate, SubscriptionStatus, SubscribedDate):
        sub_07 = (
            '"' + subscriptionid + '":'
                '{'
                    '"\\x05\\x00\\x00\\x00": "' + StatusChangeFlag + '",'
                    '"\\x06\\x00\\x00\\x00": "' + PreviousSubscriptionState + '",'
                    '"\\x02\\x00\\x00\\x00": "' + UnsubscribedDate + '",'
                    '"\\x03\\x00\\x00\\x00": "' + SubscriptionStatus + '",'
            #        '\\t\\x00\\x00\\x00': '" + "',"  # You need to provide a value for this field
                    '"\\x01\\x00\\x00\\x00": "' + SubscribedDate + '",'
                '},'
        )
        subscriptions_07 += sub_07
        return sub_07

    def generate_userreg_second(self):
        userreg_second = (
            '"},'
            '"\\x08\\x00\x00\x00": {},'
            '"\\x09\x00\x00\x00": "' + self.LastRecalcDerivedSubscribedAppsTime + '",'
            '"\\x0a\x00\x00\x00": "' + self.CellId + '",'
            '"\\x0b\x00\x00\x00": "' + self.AccountEmailAddress + '",'
            '"\\x0c\x00\x00\x00": "' + self.AccountStatus + '",'
            '"\\x0e\x00\x00\x00": "' + self.AccountLastModifiedTime + '",'
            '"\\x0f\x00\x00\x00":'
            '{"'
        )
        return userreg_second


    def generate_subscriptions_0f_string(self, subscriptionid, AccountPaymentType, cdkey=None, cdkey_type=None, PaymentCardType=None, CardNumber=None, CardHolderName=None, CardExpYear=None, CardExpMonth=None, CardCVV2=None, BillingAddress1=None, BillingAddress2=None, BillingCity=None, BillinZip=None, BillingState=None, BillingCountry=None, BillingPhone=None, BillinEmailAddress=None, PriceBeforeTax=None, TaxAmount=None):
        subscriptions_0f = (
            '"' + subscriptionid + '":'
            '{'
            '"\\x01\\x00\\x00\\x00": "' + (AccountPaymentType or "") + '",'
            '"\\x02\\x00\\x00\\x00": {'
        )

        if AccountPaymentType == "x06":
            subscriptions_0f += (
                '"\\x02\\x00\\x00\\x00": "' + (cdkey or "") + '",'
                '"\\x01\\x00\\x00\\x00": "' + (cdkey_type or "") + '"'
            )
        elif AccountPaymentType == "x05":
            subscriptions_0f += (
                '"\\x01\\x00\\x00\\x00": "' + (PaymentCardType or "") + '",'
                '"\\x02\\x00\\x00\\x00": "' + (CardNumber or "") + '",'
                '"\\x03\\x00\\x00\\x00": "' + (CardHolderName or "") + '\\x00",'
                '"\\x04\\x00\\x00\\x00": "' + (CardExpYear or "") + '\\x00",'
                '"\\x05\\x00\\x00\\x00": "' + (CardExpMonth or "") + '\\x00",'
                '"\\x06\\x00\\x00\\x00": "' + (CardCVV2 or "") + '\\x00",'
                '"\\x07\\x00\\x00\\x00": "' + (BillingAddress1 or "") + '\\x00",'
                '"\\x08\\x00\\x00\\x00": "' + (BillingAddress2 or "") + '\\x00",'
                '"\\x09\\x00\\x00\\x00": "' + (BillingCity or "") + '\\x00",'
                '"\\x0a\\x00\\x00\\x00": "' + (BillinZip or "") + '\\x00",'
                '"\\x0b\\x00\\x00\\x00": "' + (BillingState or "") + '\\x00",'
                '"\\x0c\\x00\\x00\\x00": "' + (BillingCountry or "") + '\\x00",'
                '"\\x0d\\x00\\x00\\x00": "' + (BillingPhone or "") + '\\x00",'
                '"\\x0e\\x00\\x00\\x00": "' + (BillinEmailAddress or "") + '\\x00",'
                '"\\x14\\x00\\x00\\x00": "' + (PriceBeforeTax or "") + '",'
                '"\\x15\\x00\\x00\\x00": "' + (TaxAmount or "") + '"'
            )
        else:
            subscriptions_0f += ''

        subscriptions_0f += '},},'
        self.subscriptions_0f += subscriptions_0f
        return subscriptions_0f
