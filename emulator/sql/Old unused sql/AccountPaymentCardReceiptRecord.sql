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
  ShippingCost DECIMAL(10, 2)
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