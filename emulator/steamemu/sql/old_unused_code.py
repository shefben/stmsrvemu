

        
    def create_user(self):
        next_unique_user_id = self.get_next_id('userregistry', 'UniqueID')
        self.UniqueID = next_unique_id
        next_steam_id = self.get_next_id('userregistry', 'SteamLocalUserID')
        self.SteamID = next_steam_id
        
        self.username['value'] = self.accountuser_record.username
        self.accountcreationtime['value'] = self.accountcreationtime

        data = {
            'UniqueID': next_unique_user_id,
            'UniqueUserName': self.username,
            'AccountCreationTime': self.accountcreationtime,
            'OptionalAccountCreationKey': self.optionalaccountcreationkey['value'],
            'SteamLocalUserID': next_steam_id,
            'UserType': self.accountuser_record.UserType['value'],
            'SaltedAnswerToQuestionDigest': self.passwordsrecord_record.SaltedAnswerToQuestionDigest['value'],
            'PassphraseSalt': self.passwordsrecord_record.PassphraseSalt['value'],
            'AnswerToQuestionSalt': self.passwordsrecord_record.AnswerToQuestionSalt['value'],
            'PersonalQuestion': self.passwordsrecord_record.PersonalQuestion['value'],
            'SaltedPassphraseDigest': self.passwordsrecord_record.SaltedPassphraseDigest['value'],
            'LastRecalcDerivedSubscribedAppsTime': self.LastRecalcDerivedSubscribedAppsTime['value'],
            'Cellid': self.Cellid['value'],
            'AccountEmailAddress': self.AccountEmailAddress['value'],
            'Banned': self.Banned['value'],
            'AccountLastModifiedTime': self.AccountLastModifiedTime['value']
        }
        self.insert_data('userregistry', data)

        # now add default subscription to table accountsubscriptionsrecord
        # UniqueID	UserRegistry_UniqueID	SubscriptionID	SubscribedDate	UnsubscribedDate	
        # SubscriptionStatus	StatusChangeFlag	PreviousSubscriptionState
        
        self.add_subscription() # keep arguments blank to use default subscription for account setup
        
        next_unique_sub_id = self.get_next_id('accountsubscriptionsrecord', 'UniqueID')

        subscription = self.subscription_records[0]
        
        data = {
            'UniqueID': next_unique_sub_id,
            'UserRegistry_UniqueID': next_unique_user_id,
            'SubscriptionID': subscription.SubscriptionID,
            'SubscribedDate': subscription.SubscribedDate["value"],  # Set the subscribed date value here
            'UnsubscribedDate':  subscription.UnsubscribedDate["value"],  # Set the unsubscribed date value here
            'SubscriptionStatus':  subscription.SubscriptionStatus["value"],  # Set the subscription status value here
            'StatusChangeFlag':  subscription.StatusChangeFlag["value"],  # Set the status change flag value here
            'PreviousSubscriptionState':  subscription.PreviousSubscriptionState["value"]  # Set the previous subscription state value here
        }
        self.insert_data('accountsubscriptionsrecord', data)

        subbillinginfo = self.accountsubscriptionbilling_record.SubscriptionsBillingInfoRecord[0]


        next_unique_billing_id = self.get_next_id('accountsubscriptionsbillinginforecord', 'UniqueID')
        data = 
        {
            'UniqueID': next_unique_billing_id,
            'UserRegistry_UniqueID': next_unique_user_id,
            'Subscriptionid': 0, #subbillinginfo.SubscriptionID,
            'AccountPaymentCardInfoRecord': 7 #subbillinginfo.AccountPaymentCardInfoRecord["value"]
        }
        self.insert_data('accountsubscriptionsbillinginforecord', data)

#table: accountsubscriptionsbillinginforecord :	UniqueID	UserRegistry_UniqueID	Subscriptionid	AccountPaymentCardInfoRecord	
# AccountPrepurchasedInfoRecord_UniqueID	AccountExternalBillingInfoRecord_UniqueID	AccountPaymentCardReceiptRecord_recordID




class SubscriberAccount_Record(object):
    
    def __init__(self, database):
        self.database = database
        self.username = ''
        self.email = ''
        self.password = ''

    def save_record(self):
        data = {
            'username': self.username,
            'email': self.email,
            'password': self.password
        }
        self.database.insert_data('subscriber_account', data)

    def load_record(self, username):
        condition = "username = '{}'".format(username)
        result = self.database.select_data('subscriber_account', '*', condition)
        if result:
            self.username = result[0][0]
            self.email = result[0][1]
            self.password = result[0][2]

    def update_password(self, new_password):
        condition = "username = '{}'".format(self.username)
        data = {'password': new_password}
        self.database.update_data('subscriber_account', data, condition)

    def delete_record(self):
        condition = "username = '{}'".format(self.username)
        self.database.delete_data('subscriber_account', condition)



    def __init__(self, UniqueID, version, username, creationtime, creationkey, derivedappsrecord, derivedappsrecord_time, cellid, email, banned, lastmodified,
                 steamid, uniqueid):
        self.subscription_records = []
        self.accountuser_record = None
        self.passwordsrecord_record = None
        self.accountsubscriptionbilling_record = None
        #self.accountcreationtime['value'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.UniqueID = UniqueID
        self.version['value'] = version
        self.UniqueUsername['value'] = username
        self.AccountCreationTime['value'] = creationtime
        self.OptionalAccountCreationKey['value'] = creationkey
        self.DerivedSubscribedAppsRecord['value'] = derivedappsrecord
        self.LastRecalcDerivedSubscribedAppsTime['value'] = derivedappsrecord_time
        self.Cellid['value'] = cellid
        self.AccountEmailAddress['value'] = email
        self.Banned['value'] = banned
        self.AccountLastModifiedTime['value'] = lastmodified









