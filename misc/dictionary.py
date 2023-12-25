# this file is for holding all the definitions of the different record fields



#=============================================================================================================
#-------------------------------------------------------------------------------------------------------------
#                            Current Content Record (firstblob.bin/py) Dictionary                             
#-------------------------------------------------------------------------------------------------------------
#=============================================================================================================
currentcontent_record = {
    'Version': {'key': r'\x00\x00\x00\x00', 'value': r''},
    'ClientBootstrapVersion': {'key': r'\x01\x00\x00\x00', 'value': r''},
    'ClientAppPackageVersion': {'key': r'\x02\x00\x00\x00', 'value': r''},
    'LinuxClientAppVersion': {'key': r'\x03\x00\x00\x00', 'value': r''},
    'Win32HldsUpdateToolVersion': {'key': r'\x04\x00\x00\x00', 'value': r''},
    'LinuxHldsUpdateToolVersion': {'key': r'\x05\x00\x00\x00', 'value': r''},
    'BetaClientBootstrapVersion': {'key': r'\x06\x00\x00\x00', 'value': r''},
    'BetaClientBootstrapPassword': {'key': r'\x07\x00\x00\x00', 'value': r''},
    'BetaClientAppPackageVersion': {'key': r'\x08\x00\x00\x00', 'value': r''},
    'BetaClientAppPackagePassword': {'key': r'\x09\x00\x00\x00', 'value': r''},
    'BetaWin32HldsUpdateToolVersion': {'key': r'\x0a\x00\x00\x00', 'value': r''},
    'BetaWin32HldsUpdateToolPassword': {'key': r'\x0b\x00\x00\x00', 'value': r''},
    'BetaLinuxHldsUpdateToolVersion': {'key': r'\x0c\x00\x00\x00', 'value': r''},
    'BetaLinuxHldsUpdateToolPassword': {'key': r'\x0d\x00\x00\x00', 'value': r''},
    'CafeBlock': {
        'key': r'\x0e\x00\x00\x00',
        'value': [] # List of entries from cafeblock dictionary
        },
    'CustomPackageVersion': {'key': r'\x0f\x00\x00\x00', 'value': r''}
}
cafeblock = {
    'SteamClientGameUpdater': {'key': r'SteamGameUpdater', 'value': r''},
    'CafeAdministrationClientVersion': {'key': r'cac', 'value': r''},
    'CafeAdministrationServerVersion': {'key': r'cas', 'value': r''},
}

def output_ccrblob():
    for key, value in currentcontent_record.items():
        if key in cafeblock:
            currentcontent_record[key]['value'] = cafeblock[key]['value']

# Print the updated currentcontent_record in the desired format
    print("blob = {")
    for key, value in currentcontent_record.items():
        print(f"    '{value['key']}': '{value['value']}'")
    print("}")


    #######################OR for py 2.7...

def output_ccrblob_2_7():
    # Update the 'value' in currentcontent_record using values from cafeblock
    for key, value in currentcontent_record.items():
        if key in cafeblock:
            currentcontent_record[key]['value'] = cafeblock[key]['value']

    # Print the updated currentcontent_record in the desired format
    print("blob = {")
    for key, value in currentcontent_record.items():
        print("    '{}': '{}'".format(value['key'], value['value']))
    print("}")
#===================================================
# Example of adding 2/3 cafeblock{} entries to blob:
#===================================================
#if 'CafeBlock' in blob:
#    blob['CafeBlock']['value'] = [
#        cafeblock['CafeAdministrationClientVersion'],
#        cafeblock['CafeAdministrationServerVersion']
#    ]
#else:
#    blob['CafeBlock'] = {
#        'key': r'\x0e\x00\x00\x00',
#        'value': [
#            cafeblock['CafeAdministrationClientVersion'],
#            cafeblock['CafeAdministrationServerVersion']
#        ]
#    }


#=============================================================================================================
#-------------------------------------------------------------------------------------------------------------
#                            Content Description Record (secondblob.bin/py) Dictionary                             
#-------------------------------------------------------------------------------------------------------------
#=============================================================================================================

CDRlaunchoptions_record = { # before this comes the id, usually starts at 0 and goes up by one for ever launch option record added
    'Description': {'key': r'\x01\x00\x00\x00', 'value': r''},
    'CommandLine': {'key': r'\x02\x00\x00\x00', 'value': r''},
    'IconIndex': {'key': r'\x03\x00\x00\x00', 'value': r''},
    'NoDesktopShortcut': {'key': r'\x04\x00\x00\x00', 'value': r''},
    'NoStartMenuShortcut': {'key': r'\x05\x00\x00\x00', 'value': r''},
    'LongRunningUnattended': {'key': r'\x06\x00\x00\x00', 'value': r''},
}
CDRapplicationversion_record = {
    'Description': {'key': r'\x01\x00\x00\x00', 'value': r''},
    'VersionId': {'key': r'\x02\x00\x00\x00', 'value': r''},
    'IsNotAvailable': {'key': r'\x03\x00\x00\x00', 'value': r''},
    'LaunchOptionIdsRecord': {'key': r'\x04\x00\x00\x00', 'value': {} },
    'DepotEncryptionKey': {'key': r'\x05\x00\x00\x00', 'value': r''},
    'IsEncryptionKeyAvailable': {'key': r'\x06\x00\x00\x00', 'value': r''},
    'IsRebased': {'key': r'\x07\x00\x00\x00', 'value': r''},
    'IsLongVersionRoll': {'key': r'\x08\x00\x00\x00', 'value': r''}
}

CDRfilesystem_record = {
    'AppId': {'key': r'\x01\x00\x00\x00', 'value': r''},
    'MountName': {'key': r'\x02\x00\x00\x00', 'value': r''},
    'IsOptional': {'key': r'\x03\x00\x00\x00', 'value': r''}
}

CDRapplication_record = {
    'AppId': {'key': r'\x01\x00\x00\x00', 'value': r''},
    'Name': {'key': r'\x02\x00\x00\x00', 'value': r''},
    'InstallDirName': {'key': r'\x03\x00\x00\x00', 'value': r''},
    'MinCacheFileSizeMB': {'key': r'\x04\x00\x00\x00', 'value': r''},
    'MaxCacheFileSizeMB': {'key': r'\x05\x00\x00\x00', 'value': r''},
    'LaunchOptionsRecord': {'key': r'\x06\x00\x00\x00', 'value': [CDRlaunchoptions_record] },
    'AppIconsRecord': {'key': r'\x07\x00\x00\x00', 'value': [] },
    'OnFirstLaunch': {'key': r'\x08\x00\x00\x00', 'value': r''},
    'IsBandwidthGreedy': {'key': r'\x09\x00\x00\x00', 'value': r''},
    'VersionsRecord': {'key': r'\x0a\x00\x00\x00', 'value': {} },
    'CurrentVersionId': {'key': r'\x0b\x00\x00\x00', 'value': r''},
    'FilesystemsRecord': {'key': r'\x0c\x00\x00\x00', 'value': {} },
    'TrickleVersionId': {'key': r'\x0d\x00\x00\x00', 'value': r''},
    'UserDefinedRecord': {'key': r'\x0e\x00\x00\x00', 'value': {} },
    'BetaVersionPassword': {'key': r'\x0f\x00\x00\x00', 'value': r''},
    'BetaVersionId': {'key': r'\x10\x00\x00\x00', 'value': r''},
    'LegacyInstallDirName': {'key': r'\x11\x00\x00\x00', 'value': r''},
    'SkipMFPOverwrite': {'key': r'\x12\x00\x00\x00', 'value': r''},
    'UseFilesystemDvr': {'key': r'\x13\x00\x00\x00', 'value': r''},
    'ManifestOnlyApp': {'key': r'\x14\x00\x00\x00', 'value': r''},
    'AppOfManifestOnlyCache': {'key': r'\x15\x00\x00\x00', 'value': r''},
}
contentdescription_record = {
    'VersionNumber': {'key': r'\x00\x00\x00\x00', 'value': r''},
    'ApplicationsRecord': {'key': r'\x01\x00\x00\x00', 'value': {} },
    'SubscriptionsRecord': {'key': r'\x02\x00\x00\x00', 'value': {} },
    'LastChangedExistingAppOrSubscriptionTime': {'key': r'\x03\x00\x00\x00', 'value': r''},
    'IndexAppIdToSubscriptionIdsRecord': {'key': r'\x04\x00\x00\x00', 'value': {} },
    'AllAppsPublicKeysRecord': {'key': r'\x05\x00\x00\x00', 'value': {} },
    'AllAppsEncryptedPrivateKeysRecord': {'key': r'\x06\x00\x00\x00', 'value': {} }
}



class BillingTypeVar(object):
    NoCost = 0
    BillOnceOnly = 1
    BillMonthly = 2
    ProofOfPrepurchaseOnly = 3
    GuestPass = 4
    HardwarePromo = 5
    Gift = 6
    AutoGrant = 7

CDRsubscription_record = {
    'SubscriptionId': {'key': '\x01\x00\x00\x00', 'value': ''},
    'Name': {'key': '\x02\x00\x00\x00', 'value': ''},
    'BillingType': {'key': '\x03\x00\x00\x00', 'value': ''},
    'CostInCents': {'key': '\x04\x00\x00\x00', 'value': ''},
    'PeriodInMinutes': {'key': '\x05\x00\x00\x00', 'value': ''},
    'AppIdsRecord': {'key': '\x06\x00\x00\x00', 'value': ''},
    'RunAppId': {'key': '\x07\x00\x00\x00', 'value': ''},
    'OnSubscribeRunLaunchOptionIndex': {'key': '\x08\x00\x00\x00', 'value': ''},
    'OptionalRateLimitRecord': {'key': '\x09\x00\x00\x00', 'value': ''},
    'DiscountsRecord': {'key': '\x0a\x00\x00\x00', 'value': ''},
    'IsPreorder': {'key': '\x0b\x00\x00\x00', 'value': ''},
    'RequiresShippingAddress': {'key': '\x0c\x00\x00\x00', 'value': ''},
    'DomesticCostInCents': {'key': '\x0d\x00\x00\x00', 'value': ''},
    'InternationalCostInCents': {'key': '\x0e\x00\x00\x00', 'value': ''},
    'RequiredKeyType': {'key': '\x0f\x00\x00\x00', 'value': ''},
    'IsCyberCafe': {'key': '\x10\x00\x00\x00', 'value': ''},
    'GameCode': {'key': '\x11\x00\x00\x00', 'value': ''},
    'GameCodeDescription': {'key': '\x12\x00\x00\x00', 'value': ''},
    'IsDisabled': {'key': '\x13\x00\x00\x00', 'value': ''},
    'RequiresCD': {'key': '\x14\x00\x00\x00', 'value': ''},
    'TerritoryCode': {'key': '\x15\x00\x00\x00', 'value': ''},
    'IsSteam3Subscription': {'key': '\x16\x00\x00\x00', 'value': ''},
    'ExtendedInfoRecord': {'key': '\x17\x00\x00\x00', 'value': []},
}

CDRdiscountqualifier_record = {
    'Name': {'key': '\x01\x00\x00\x00', 'value': ''},
    'SubscriptionId': {'key': '\x02\x00\x00\x00', 'value': ''},
}

CDRdiscount_record = {
    'Name': {'key': '\x01\x00\x00\x00', 'value': ''},
    'DiscountInCents': {'key': '\x02\x00\x00\x00', 'value': ''},
    'DiscountQualifiersRecord': {'key': '\x03\x00\x00\x00', 'value': ''},
}

CDRextendedinfo_record = {
    'key': {'key': '\x01\x00\x00\x00', 'value': 'test'},
    'value': {'key': '\x00\x00\x00\x00', 'value': r'testvalue'}
}

#=============================================================================================================
#-------------------------------------------------------------------------------------------------------------
#                            Subscription Account Record (User.py) Dictionary                             
#-------------------------------------------------------------------------------------------------------------
#=============================================================================================================
subscriptionaccount_record = {
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
    },
    
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
    },
    
    'AccountSubscriptionsRecord': {  # \x07 = AccountSubscriptionsRecord
        'key': r'\x07\x00\x00\x00',
        'value': []  # list of AccountSubscriptions_Record
    },
    
    'DerivedSubscribedAppsRecord': {  # \x08 = DerivedSubscribedAppsRecord
        'key': r'\x08\x00\x00\x00',
        'value': [] # appid dictionary format: <appid> : ''
    },
     
    'LastRecalcDerivedSubscribedAppsTime': {'key': r'\x09\x00\x00\x00', 'value': ''},
    'CellID': {'key': r'\x0a\x00\x00\x00', 'value': ''},
    'AccountEmailAddress': {'key': r'\x0b\x00\x00\x00', 'value': ''},
    'AccountStatus': {'key': r'\x0c\x00\x00\x00', 'value': ''},
    # \x0d = nothing??
    'AccountLastModifiedTime': {'key': r'\x0e\x00\x00\x00', 'value': ''},
    
    'AccountSubscriptionsBillingInfoRecord': {  # \x0f = AccountSubscriptionsBillingInfoRecord 
        'key': r'\x0f\x00\x00\x00',
        'value': [] # list of AccountSubscriptionsBillingInfoRecord_record
    }
},
AccountSubscriptions_Record  ={
    'key': r'\x07\x00\x00\x00',
    subscriptionid : { #               <---------Subscription id here
        'SubscribedDate': {'key': r'\x01\x00\x00\x00', 'value': ''},
        'UnsubscribedDate': {'key': r'\x02\x00\x00\x00', 'value': ''},
        'SubscriptionStatus': {'key': r'\x03\x00\x00\x00', 'value': ''},
        'StatusChangeFlag': {'key': r'\x05\x00\x00\x00', 'value': ''},
        'PreviousSubscriptionState': {'key': r'\x06\x00\x00\x00', 'value': ''},
        'OptionalBillingStatus' : {'key': r'\x07\x00\x00\x00', 'value' : ''},
		'UserIP' : { 'key' :  r'\x08\x00\x00\x00', 'value' : ''},
		'UserCountryCode' : { 'key' : r'\x09\x00\x00\x00', 'value' : 'US\x00'}
    }
},

AccountSubscriptionsBillingInfoRecord_record = {
    'key': r'\x0f\x00\x00\x00',  
    subscriptionid : {  # <---------Subscription id here
        'AccountPaymentCardInfoRecord': {'key': r'\x01\x00\x00\x00', 'value': ''},
        'AccountPrepurchasedInfoRecord': {
            'key': r'\x02\x00\x00\x00', 
            'value': [] or None #list of AccountPrepurchasedInfoRecord_record
        }   
    }
},

AccountPrepurchasedInfoRecord_record = {
    'TypeOfProofOfPurchase': {'key': r'\x01\x00\x00\x00', 'value': ''},
    'BinaryProofOfPurchaseToken': {'key': r'\x02\x00\x00\x00', 'value': ''}
},

AccountSubscriptions_Record  ={
    'key': r'\x07\x00\x00\x00',
    subscriptionid : { #               <---------Subscription id here
        'SubscribedDate': {'key': r'\x01\x00\x00\x00', 'value': ''},
        'UnsubscribedDate': {'key': r'\x02\x00\x00\x00', 'value': ''},
        'SubscriptionStatus': {'key': r'\x03\x00\x00\x00', 'value': ''},
        'StatusChangeFlag': {'key': r'\x05\x00\x00\x00', 'value': ''},
        'PreviousSubscriptionState': {'key': r'\x06\x00\x00\x00', 'value': ''},
        'OptionalBillingStatus' : {'key': r'\x07\x00\x00\x00', 'value' : ''},
		'UserIP' : { 'key' :  r'\x08\x00\x00\x00', 'value' : ''},
		'UserCountryCode' : { 'key' : r'\x09\x00\x00\x00', 'value' : 'US\x00'}
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

class UserSubscriptionField :
    def __init__(self, blob_data, key) :
        self.blob_data = blob_data
        self.key = key.encode('latin1')

    def getValue(self) :
        return self.blob_data.get(self.key)

    def setValue(self, value) :
        self.blob_data[self.key] = value

class UserSubscriptionRecord :
    subscriptionaccount_record = {
        # ... (Include the entire definition of subscriptionaccount_record here)
    }

    def __init__(self, blob_data) :
        self.blob_data = blob_data

    def __getattr__(self, item) :
        if item in self.subscriptionaccount_record :
            key = self.subscriptionaccount_record[item]['key']
            return UserSubscriptionField(self.blob_data, key)
        else :
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{item}'")

# Usage
# Assuming blob_data is the dictionary parsed from the blob or an empty dictionary for creating from scratch
blob_data = {}
subscription_record = UserSubscriptionRecord(blob_data)

# Set a value
subscription_record.UniqueUsername.setValue('new_username')

# Get a value
unique_username = subscription_record.UniqueUsername.getValue( )