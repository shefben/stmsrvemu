user_registry = {
    "\x00\x00\x00\x00": "\x04\x00",                 #  VersionNum
    "\x01\x00\x00\x00": "test\x00",                 #  UniqueAccountName
    "\x02\x00\x00\x00": "`\x1e\xedMB\xc1\xe2\x00",  #  AccountCreationTime
    "\x03\x00\x00\x00": "Egq-pe-y\x00"              #  OptionalAccountCreationKey 
    # \x04: OptionalAccountBillingInfoRecord
    "\x05\x00\x00\x00":                             #  AccountUserPasswordsRecord
    {
        "test":
        {
            "\x01\x00\x00\x00": "\x11\x1c\xd7\xf9\x00}\x9fg\x01\x0e\xee\xdb@\x86\x98(\x94+o\x84",
            "\x02\x00\x00\x00": "\x83\xf4\x13\xbd\xd8\x92)\xcc",
            "\x03\x00\x00\x00": "What is your favorite team?\x00",
            "\x04\x00\x00\x00": "z}AJ\xcf\x95Z'{\xc0\x9e\xb3\x8ah\x9d\xa4\x82\x8b\x93l",
            "\x05\x00\x00\x00": "\x9eY\xd8\x108G\x7f\x81",     
        },
    },  
    "\x06\x00\x00\x00":                             #  AccountUsersRecord
    {
        "test":
        {
            "\x01\x00\x00\x00": "\xb8\xa0\x98\xf8\x00\x00\x00\x00",
            "\x02\x00\x00\x00": "\x01\x00",
            "\x03\x00\x00\x00":
            {
            }, 
        },
    },
    "\x07\x00\x00\x00":         #  AccountSubscriptionsRecord
    {
        "\x00\x00\x00\x00":
        {
            "\x01\x00\x00\x00": "\xe0\xe0\xe0\xe0\xe0\xe0\xe0\x00", #  SubscribedDate
            "\x02\x00\x00\x00": "\x00\x00\x00\x00\x00\x00\x00\x00", #  UnsubscribedDate
            "\x03\x00\x00\x00": "\x01\x00",                         #  SubscriptionStatus
            "\x05\x00\x00\x00": "\x00",                             #  StatusChangeFlag                         
            "\x06\x00\x00\x00": "\x1f\x00",                         #  PreviousSubscriptionState           
        },
        "\x01\x00\x00\x00":
        {
            "\x01\x00\x00\x00": "\xe0\xe0\xe0\xe0\xe0\xe0\xe0\x00", #  SubscribedDate
            "\x02\x00\x00\x00": "\x00\x00\x00\x00\x00\x00\x00\x00", #  UnsubscribedDate
            "\x03\x00\x00\x00": "\x01\x00",                         #  SubscriptionStatus
            "\x05\x00\x00\x00": "\x00",                             #  StatusChangeFlag
            "\x06\x00\x00\x00": "\x00\x00",                         #  PreviousSubscriptionState
            "\x09\x00\x00\x00": "\x00",            
        },
        "\x07\x00\x00\x00":
        {
            "\x01\x00\x00\x00": "\xe0\xe0\xe0\xe0\xe0\xe0\xe0\x00", #  SubscribedDate
            "\x02\x00\x00\x00": "\x00\x00\x00\x00\x00\x00\x00\x00", #  UnsubscribedDate
            "\x03\x00\x00\x00": "\x01\x00",                         #  SubscriptionStatus
            "\x05\x00\x00\x00": "\x00",                             #  StatusChangeFlag
            "\x06\x00\x00\x00": "\x00\x00",                         #  PreviousSubscriptionState
            "\x09\x00\x00\x00": "\x00",            
        },
    },
    "\x08\x00\x00\x00":                                             #  DerivedSubscribedAppsRecord
    {
    },
    "\x09\x00\x00\x00": "`\x1e\xedMB\xc1\xe2\x00",                  #  LastRecalcDerivedSubscribedAppsTime
    "\x0a\x00\x00\x00": "\x02\x00\x00\x00",                         #  CellId
    "\x0b\x00\x00\x00": "test@test.com\x00",                        #  AccountEmailAddress
    "\x0c\x00\x00\x00": "\x00\x00",                                 #  AccountStatus
    "\x0e\x00\x00\x00": "`\x1e\xedMB\xc1\xe2\x00",                  #  AccountLastModifiedTime
    "\x0f\x00\x00\x00":                                             #  AccountSubscriptionsBillingInfoRecord
    {
        "\x00\x00\x00\x00":                         #  SubscriptionId
        {
            "\x01\x00\x00\x00": "\x07",             #  AccountPaymentCardInfoRecord
            "\x02\x00\x00\x00":
            {
            },
        },
        "\x01\x00\x00\x00":                         #  SubscriptionId
        {
            "\x01\x00\x00\x00": "\x06",             #  AccountPaymentCardInfoRecord
            "\x02\x00\x00\x00":
            {
                "\x01\x00\x00\x00": "WONCDKey\x00",
                "\x02\x00\x00\x00": "2199807727546", 
            },
        },
        "\x07\x00\x00\x00":                         #  SubscriptionId
        {
            "\x01\x00\x00\x00": "\x05",             #  AccountPaymentCardInfoRecord
            "\x02\x00\x00\x00":
            {
                "\x01\x00\x00\x00": "\x02",                 #  PaymentCardType
                "\x02\x00\x00\x00": "5044658124903867\x00", #  CardNumber
                "\x03\x00\x00\x00": "dsf sdfas\x00",        #  CardHolderName
                "\x04\x00\x00\x00": "2015\x00",             #  CardExpYear
                "\x05\x00\x00\x00": "07\x00",               #  CardExpMonth
                "\x06\x00\x00\x00": "476\x00",              #  CardCVV2
                "\x07\x00\x00\x00": "w154 marvel dr.\x00",  #  BillingAddress1
                "\x08\x00\x00\x00": "\x00",                 #  BillingAddress2
                "\x09\x00\x00\x00": "menomonee falls\x00",  #  BillingCity      #\t = x09
                "\x0a\x00\x00\x00": "53051\x00",            #  BillinZip        #\n = x0a
                "\x0b\x00\x00\x00": "WI\x00",               #  BillingState
                "\x0c\x00\x00\x00": "United States\x00",    #  BillingCountry
                "\x0d\x00\x00\x00": "2622523747\x00",       #  BillingPhone     #\r = x0d
                "\x0e\x00\x00\x00": "test@test.com\x00",    #  BillinEmailAddress
                "\x14\x00\x00\x00": "\xb3\x0b\x00\x00",     #  PriceBeforeTax
                "\x15\x00\x00\x00": "\x00\x00\x00\x00",     #  TaxAmount
            },
            
        },

    },    
}
