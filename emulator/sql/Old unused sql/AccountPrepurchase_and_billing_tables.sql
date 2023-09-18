CREATE TABLE CAccountSubscriptionsRecord (
  recordID INT AUTO_INCREMENT PRIMARY KEY,
  CAccountPaymentCardInfoRecord VARCHAR(255),
  CAccountPrepurchaseInfoRecord VARCHAR(255),
  field3 VARCHAR(255) DEFAULT NULL,
  field4 VARCHAR(255) DEFAULT NULL,
  field5 VARCHAR(255) DEFAULT NULL,
  field6 VARCHAR(255) DEFAULT NULL,
  field7 VARCHAR(255) DEFAULT NULL
);

CREATE TABLE CAccountPrepurchaseInfoRecord (
  recordID INT AUTO_INCREMENT PRIMARY KEY,
  TypeOfProofOfPurchase VARCHAR(255),
  BinaryProofOfPurchaseToken VARCHAR(255),
  TokenRejectionReason VARCHAR(255),
  AStoBBSTxnId VARCHAR(255),
  SubsId VARCHAR(255),
  AcctName VARCHAR(255),
  CustSupportName VARCHAR(255)
);
CREATE TABLE CAccountPrepurchaseReceiptRecord (
  recordID INT AUTO_INCREMENT PRIMARY KEY,
  receiptid INT,
  TypeOfProofOfPurchase VARCHAR(255),
  AStoBBSTxnId VARCHAR(255)
);

CREATE TABLE AccountExternalBillingInfoRecord (
  recordID INT AUTO_INCREMENT PRIMARY KEY,
  ExternalAccountName VARCHAR(255),
  ExternalAccountPassword VARCHAR(255)
);