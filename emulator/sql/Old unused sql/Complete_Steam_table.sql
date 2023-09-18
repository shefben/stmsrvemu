CREATE TABLE DerivedSubscribedAppsRecord (
  uniqueid INT AUTO_INCREMENT PRIMARY KEY,
  appid INT
);

CREATE TABLE AccountUsersRecord (
  uniqueid INT AUTO_INCREMENT PRIMARY KEY,
  SteamLocalUserID INT,
  UserType VARCHAR(20),
  UserAppAccessRightsRecord INT
);

CREATE TABLE UserAppAccessRightsRecord (
  uniqueid INT AUTO_INCREMENT PRIMARY KEY,
  appid INT,
  user_rights VARCHAR(255)
);

CREATE TABLE AccountSubscriptionsRecord (
  uniqueid INT AUTO_INCREMENT PRIMARY KEY,
  SubscribedDate DATE,
  UnsubscribedDate DATE,
  SubscriptionStatus VARCHAR(20),
  StatusChangeFlag INT,
  PreviousSubscriptionState INT,
  BillingStatus VARCHAR(255) DEFAULT NULL,
  UserIP VARCHAR(255) DEFAULT NULL
);

CREATE TABLE AccountUserPasswordsRecord (
  uniqueid INT AUTO_INCREMENT PRIMARY KEY,
  SaltedPassphraseDigest VARCHAR(255),
  PassphraseSalt VARCHAR(255),
  PersonalQuestion VARCHAR(255),
  SaltedAnswerToQuestionDigest VARCHAR(255),
  AnswerToQuestionSalt VARCHAR(255)
);

CREATE TABLE AccountPaymentCardInfoRecord (
  uniqueid INT AUTO_INCREMENT PRIMARY KEY,
  PaymentCardType VARCHAR(255),
  CardNumber VARCHAR(255),
  CardHolderName VARCHAR(255),
  CardExpYear INT,
  CardExpMonth INT,
  CardCVV2 INT,
  BillingAddress1 VARCHAR(255),
  BillingAddress2 VARCHAR(255),
  BillingCity VARCHAR(255),
  BillinZip VARCHAR(255),
  BillingState VARCHAR(255),
  BillingCountry VARCHAR(255),
  BillingPhone VARCHAR(255),
  BillinEmailAddress VARCHAR(255),
  CCApprovalDate DATE,
  CCApprovalCode VARCHAR(255),
  CDenialDate DATE,
  CDenialCode VARCHAR(255),
  UseAVS VARCHAR(255),
  PriceBeforeTax DECIMAL(10, 2),
  TaxAmount DECIMAL(10, 2),
  TransactionType VARCHAR(255),
  AuthComments VARCHAR(255),
  AuthStatus VARCHAR(255),
  AuthSource VARCHAR(255),
  AuthResponse VARCHAR(255),
  TransDate DATE,
  TransTime TIME,
  PS2000Data VARCHAR(255),
  SettlementDate DATE,
  SettlementCode VARCHAR(255),
  CCTSResponseCode VARCHAR(255),
  SettlementBatchId VARCHAR(255),
  SettlementBatchSeq VARCHAR(255),
  SettlementApprovalCode VARCHAR(255),
  SettlementComments VARCHAR(255),
  SettlementStatus VARCHAR(255),
  AStoBBSTxnId VARCHAR(255),
  SubsId VARCHAR(255),
  AcctName VARCHAR(255),
  CC1TimeChargeTxnSeq VARCHAR(255),
  CustSupportName VARCHAR(255),
  ChargeBackCaseNumber VARCHAR(255),
  GetCreditForceTxnSeq VARCHAR(255),
  ShippingInfoRecord VARCHAR(255),
  CVV2Response VARCHAR(255)
);

CREATE TABLE AccountExternalBillingInfoRecord (
  uniqueid INT AUTO_INCREMENT PRIMARY KEY,
  ExternalAccountName VARCHAR(255),
  ExternalAccountPassword VARCHAR(255)
);

CREATE TABLE CAccountPrepurchaseReceiptRecord (
  uniqueid INT AUTO_INCREMENT PRIMARY KEY,
  prepurchaseid INT,
  TypeOfProofOfPurchase VARCHAR(255),
  AStoBBSTxnId VARCHAR(255)
);

CREATE TABLE AccountPrepurchaseInfoRecord (
  uniqueid INT AUTO_INCREMENT PRIMARY KEY,
  TypeOfProofOfPurchase VARCHAR(255),
  BinaryProofOfPurchaseToken VARCHAR(255),
  TokenRejectionReason VARCHAR(255),
  AStoBBSTxnId VARCHAR(255),
  SubsId VARCHAR(255),
  AcctName VARCHAR(255),
  CustSupportName VARCHAR(255)
);

CREATE TABLE AccountSubscriptionsRecord (
  uniqueid INT AUTO_INCREMENT PRIMARY KEY,
  AccountPaymentCardInfoRecord INT,
  AccountPrepurchaseInfoRecord INT,
  field3 VARCHAR(255),
  field4 VARCHAR(255),
  field5 VARCHAR(255),
  field6 VARCHAR(255),
  field7 VARCHAR(255),
  FOREIGN KEY (AccountPaymentCardInfoRecord) REFERENCES AccountPaymentCardInfoRecord(uniqueid),
  FOREIGN KEY (AccountPrepurchaseInfoRecord) REFERENCES AccountPrepurchaseInfoRecord(uniqueid)
);

CREATE TABLE AccountPaymentCardReceiptRecord (
  recordID INT AUTO_INCREMENT PRIMARY KEY,
  PaymentCardTypeID INT,
  CardNumber VARCHAR(255),
  CardHolderName VARCHAR(255),
  field4 VARCHAR(255) DEFAULT NULL,
  field5 VARCHAR(255) DEFAULT NULL,
  field6 VARCHAR(255) DEFAULT NULL,
  BillingAddress1 VARCHAR(255),
  BillingAddress2 VARCHAR(255),
  BillingCity VARCHAR(255),
  BillingZip VARCHAR(255),
  BillingState VARCHAR(255),
  BillingCountry VARCHAR(255),
  CCApprovalCode VARCHAR(255),
  PriceBeforeTax DECIMAL(10, 2),
  TaxAmount DECIMAL(10, 2),
  TransDate DATE,
  TransTime TIME,
  AStoBBSTxnId VARCHAR(255),
  ShippingCost DECIMAL(10, 2),
  FOREIGN KEY (PaymentCardTypeID) REFERENCES ccCardType(uniqueid)
);

CREATE TABLE ccCardType (
  uniqueid INT PRIMARY KEY,
  card_type VARCHAR(255)
);

INSERT INTO ccCardType (uniqueid, card_type) VALUES
(1, 'Visa'),
(2, 'MasterCard'),
(3, 'American Express'),
(4, 'Discover'),
(5, 'Diners Club'),
(6, 'JCB');

CREATE TABLE AccountSubscriptionsBillingInfoRecord (
  uniqueid INT AUTO_INCREMENT PRIMARY KEY,
  SubscriptionBillingInfoTypeid INT DEFAULT 3,
  AccountPaymentCardInfoRecord INT,
  AccountPrepurchasedInfoRecord INT,
  AccountBillingInfoRecord INT,
  AccountExternalBillingInfoRecord INT,
  AccountPaymentCardReceiptRecord INT,
  AccountPrepurchaseReceiptRecord INT,
  EmptyReceiptRecord INT,
  SubscriptionId INT,
  FOREIGN KEY (AccountPaymentCardInfoRecord) REFERENCES AccountPaymentCardInfoRecord(uniqueid),
  FOREIGN KEY (AccountPrepurchasedInfoRecord) REFERENCES AccountPrepurchaseInfoRecord(uniqueid),
  FOREIGN KEY (AccountBillingInfoRecord) REFERENCES AccountBillingInfoRecord(uniqueid),
  FOREIGN KEY (AccountExternalBillingInfoRecord) REFERENCES AccountExternalBillingInfoRecord(uniqueid),
  FOREIGN KEY (AccountPaymentCardReceiptRecord) REFERENCES AccountPaymentCardReceiptRecord(uniqueid),
  FOREIGN KEY (AccountPrepurchaseReceiptRecord) REFERENCES AccountPrepurchaseReceiptRecord(uniqueid)
);

CREATE TABLE CSubscriberAccountRecord (
  uniqueid INT AUTO_INCREMENT PRIMARY KEY,
  versionnum INT DEFAULT 4,
  username VARCHAR(255),
  account_creation_time DATETIME,
  OptionalAccountCreationKey VARCHAR(255) DEFAULT 'Egq-pe-y',
  OptionalBillingInfoRecord INT,
  AccountUserPasswordsRecord INT,
  AccountUsersRecord INT,
  AccountSubscriptionsRecord INT,
  DerivedSubscribedAppsRecord INT,
  LastRecalcDerivedSubscribedAppsTime DATETIME,
  Cellid INT,
  AccountEmailAddress VARCHAR(255),
  AccountStatus INT,
  field13 VARCHAR(255),
  AccountLastModifiedTime TIME,
  AccountSubscriptionsBillingInfoRecord INT,
  FOREIGN KEY (OptionalBillingInfoRecord) REFERENCES AccountPaymentCardInfoRecord(uniqueid),
  FOREIGN KEY (AccountUserPasswordsRecord) REFERENCES AccountUserPasswordsRecord(uniqueid),
  FOREIGN KEY (AccountUsersRecord) REFERENCES AccountUsersRecord(uniqueid),
  FOREIGN KEY (AccountSubscriptionsRecord) REFERENCES AccountSubscriptionsRecord(uniqueid),
  FOREIGN KEY (DerivedSubscribedAppsRecord) REFERENCES DerivedSubscribedAppsRecord(uniqueid),
  FOREIGN KEY (AccountSubscriptionsBillingInfoRecord) REFERENCES AccountSubscriptionsBillingInfoRecord(uniqueid)
);