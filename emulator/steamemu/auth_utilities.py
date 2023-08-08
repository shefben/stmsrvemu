import os, re

def search_email_in_files(directory, email):
    email_exists = False
    directory = "files\users"
    for root, dirs, files in os.walk(directory):
        for file_name in files:
            if file_name.endswith('.py'):
                file_path = os.path.join(root, file_name)
                with open(file_path, 'r') as f:
                    content = f.read()
                    if email in content:
                        email_exists = True
                        break
        if email_exists:
            break

    return email_exists

def count_email_in_files(email):
    email_count = 0
    directory = "files\users"

    for root, dirs, files in os.walk(directory):
        for file_name in files:
            if file_name.endswith('.py'):
                file_path = os.path.join(root, file_name)
                with open(file_path, 'r') as f:
                    content = f.read()
                    email_count += content.count(email)

    return email_count

def check_email(email_str, clientsocket):
    if re.match(r'^[\w\.-]+@[\w\.-]+$', email_str):
        return 0
    else:
        return 3

def check_username(username_str, clientsocket):
    if re.match(r'^[a-zA-Z0-9_]+$', username_str):
        return 0
    else:
        return 2
    

def check_username_exists(string):
    directory = "files\users"
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.startswith(string) and file.endswith('.py'):
                return 1
    return 0

def decimal_to_4byte_hex(decimal_number):
    # Convert decimal to a 4-byte hex string
    hex_string = '%08X' % decimal_number

    # Ensure that the hex string is exactly 8 characters long (4 bytes).
    if len(hex_string) > 8:
        raise ValueError("Decimal number is too large to fit in 4 bytes.")

    if len(hex_string) < 8:
        padding_length = 8 - len(hex_string)
        hex_string = '0' * padding_length + hex_string

    return hex_string
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

