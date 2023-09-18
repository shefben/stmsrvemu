
accountrecord_dictionary = {
    'Version:': {'key': r'\x00\x00\x00\x00', 'value': 4}, # Always: \x04\x00
    'UniqueUsername': {'key': r'\x01\x00\x00\x00', 'value': username},
    'AccountCreationTime': {'key': r'\x02\x00\x00\x00', 'value': 0}, 
    'OptionalAccountCreationKey': {'key': r'\x03\x00\x00\x00', 'value': 'Egq-pe-y'}, #Always: Egq-pe-y
    #'OptionalBillingInfoRecord': {'key': r'\x04\x00\x00\x00', 'value': ''}, # \x04 = OptionalBillingInfoRecord  
    'AccountUserPasswordsRecord': { # \x05 = AccountUserPasswordsRecord Does not get sent
        'key': r'\x05\x00\x00\x00',
        'value': {
            username : { #           <---------User Name Here
                'SaltedPassphraseDigest': {'key': r'\x01\x00\x00\x00', 'value': ''},
                'PassphraseSalt': {'key': r'\x02\x00\x00\x00', 'value': ''},
                'PersonalQuestion': {'key': r'\x03\x00\x00\x00', 'value': ''},
                'SaltedAnswerToQuestionDigest': {'key': r'\x04\x00\x00\x00', 'value': ''},
                'AnswerToQuestionSalt': {'key': r'\x05\x00\x00\x00', 'value': ''}
            }
        }
    }
    
    'AccountUsersRecord': { # \x06 = AccountUsersRecord r'\x06\x00\x00\x00'
        'key': r'\x06\x00\x00\x00',
        'value': { 
            username : {  #           <---------User Name Here
                'SteamLocalUserID': {'key': r'\x01\x00\x00\x00', 'value': ''},
                'UserType': {'key': r'\x02\x00\x00\x00', 'value': ''},
                'UserAppAccessRightsRecord':{
                    'key': r'\x03\x00\x00\x00',
                    'value': [] # '<appid's>' i.e. '1', '2', '3', '4',...
                }
            }
        }     
    }
    
    'AccountSubscriptionsRecord': { # \x07 = AccountSubscriptionsRecord
        'key': r'\x07\x00\x00\x00',
        'value': [] # list of AccountSubscriptions_Record
    }
    
    'DerivedSubscribedAppsRecord': { # \x08 = DerivedSubscribedAppsRecord
        'key:' r'\x08\x00\x00\x00', 
            'value': {}
    } 
     
    'LastRecalcDerivedSubscribedAppsTime': {'key': r'\x09\x00\x00\x00', 'value': ''},
    'CellID': {'key': r'\x0a\x00\x00\x00', 'value': ''},
    'AccountEmailAddress': {'key': r'\x0b\x00\x00\x00', 'value': ''},
    'AccountStatus': {'key': r'\x0c\x00\x00\x00', 'value': ''},
    # \x0d = nothing??
    'AccountLastModifiedTime': {'key': r'\x0e\x00\x00\x00', 'value': ''},
    
    'AccountSubscriptionsBillingInfoRecord': { # \x0f = AccountSubscriptionsBillingInfoRecord 
        'key': r'\x0f\x00\x00\x00',
        'value': [] # list of AccountSubscriptionsBillingInfoRecord_record
    }
}

AccountSubscriptionsBillingInfoRecord_record = {
    'key': r'', # <---------Subscription id here
    'value': {  
        'AccountPaymentCardInfoRecord': {'key': r'\x01\x00\x00\x00', 'value': ''},
        'AccountPrepurchasedInfoRecord': {
            'key': r'\x02\x00\x00\x00', 
            'value': [] #list of AccountPrepurchasedInfoRecord_record
        }   
    }
}

AccountPrepurchasedInfoRecord_record = {
    'TypeOfProofOfPurchase': {'key': r'\x01\x00\x00\x00', 'value': ''},
    'BinaryProofOfPurchaseToken': {'key': r'\x02\x00\x00\x00', 'value': ''}
} 

AccountSubscriptions_Record  ={
    'key': r'',
    'value': { #               <---------Subscription id here
        'SubscribedDate': {'key': r'\x01\x00\x00\x00', 'value': ''},
        'UnsubscribedDate': {'key': r'\x02\x00\x00\x00', 'value': ''},
        'SubscriptionStatus': {'key': r'\x03\x00\x00\x00', 'value': ''},
        'StatusChangeFlag': {'key': r'\x05\x00\x00\x00', 'value': ''},
        'PreviousSubscriptionState': {'key': r'\x06\x00\x00\x00', 'value': ''}
    }
}


def print_nested_dict(d, indent=''):
    for key, value in d.items():
        if isinstance(value, dict):
            print(f"{indent}'{key}': {{")
            print_nested_dict(value, indent + '    ')
            print(f"{indent}}}")
        else:
            print(f"{indent}'{key}': '{value}'")
'''
# Look up the value for a given username
username = 'Unique username'
value = username_mapping.get(username)
if value is not None:
    print(value)
else:
    print("Username not found")'''
# Print the account_user_passwords_record dictionary
# print_nested_dict(account_user_passwords_record)

#how to create copies of the dictionaries so there can be multiple listings:

'''num_copies = 3  # Define the number of copies you want

copies = []  # List to store the copies of the dictionary

for _ in range(num_copies):
    copy = account_subscriptions_billing_info_record.copy()  # Create a new copy of the dictionary
    copies.append(copy)  # Add the copy to the list

# Access the copies
for i, copy in enumerate(copies):
    print(f"Copy {i+1}: {copy}")'''
    
    '''0=versionnum(Always: 4)
 1=unique username
 2=account creation time
 3=OptionalAccountCreationKey (Always: Egq-pe-y)
 4=OptionalBillingInfoRecord
	AccountPaymentCardInfoRecord
 5=AccountUserPasswordsRecord
	<username>/AccountUserPasswordRecord
	1=SaltedPassphraseDigest
	2=PassphraseSalt
	3=PersonalQuestion
	4=SaltedAnswerToQuestionDigest
	5=AnswerToQuestionSalt
 6=AccountUsersRecord
	<Username>/AccountUserRecord 
   		 1=SteamLocalUserID
  		 2=UserType (admin or regular user)
    	 3=UserAppAccessRightsRecord
 7=AccountSubscriptionsRecord
	<subscription#>/AccountSubscriptionRecord
		1=SubscribedDate
		2=UnsubscribedDate
		3=SubscriptionStatus
		5=StatusChangeFlag
		6=PreviousSubscriptionState
		7=BillingStatus ---not used on server?
		8=UserIP   ---not used on server?
 8=DerivedSubscribedAppsRecord
	appid

 15=AccountSubscriptionsBillingInfoRecord
	<billing id>
		1=AccountPaymentCardInfoRecord
		2=AccountPrepurchasedInfoRecord
			1=cdkeyname/product type name
			2=cdkey
		3=AccountBillingInfoRecord
		4=AccountExternalBillingInfoRecord
	5=AccountPaymentCardReceiptRecord
	6=AccountPrepurchaseReceiptRecord
	7=EmptyReceiptRecord'''