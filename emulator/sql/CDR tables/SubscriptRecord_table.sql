-- Table: SubscriptionRecords
CREATE TABLE SubscriptionRecords (
    UniqueID INT NOT NULL AUTO_INCREMENT,
    SubscriptionId INT,
    Name VARCHAR(255),
    BillingType VARCHAR(255),
    CostInCents INT,
    ApplicationIds VARCHAR(255),
    RunApplicationId INT,
    RunLaunchOption VARCHAR(255),
    IsPreOrder BOOL,
    RequiresShippingAddress BOOL,
    DomesticCostInCents INT,
    InternationalCostInCents INT,
    RequiredKeyType INT,
    IsCyberCafe BOOL,
    GameCode INT,
    GameCodeDescription VARCHAR(255),
    IsDisabled BOOL,
    RequiresCD BOOL,
    TerritoryCode INT,
    IsSteam3Subscription BOOL,
    PRIMARY KEY (UniqueID),
    CONSTRAINT Unique_SubscriptionId UNIQUE (SubscriptionId)
);

-- Table: SubscriptionExtendedInfoRecord
CREATE TABLE SubscriptionExtendedInfoRecord (
    UniqueID INT NOT NULL AUTO_INCREMENT,
    SubscriptionRecords_UniqueID INT,
    Key VARCHAR(255),
    Value VARCHAR(255),
    PRIMARY KEY (UniqueID),
    CONSTRAINT FK_SubscriptionRecords_UniqueID
        FOREIGN KEY (SubscriptionRecords_UniqueID) 
        REFERENCES SubscriptionRecords (UniqueID)
        ON DELETE CASCADE
);

-- Table: SubscriptionDiscounts
CREATE TABLE SubscriptionDiscounts (
    UniqueID INT NOT NULL AUTO_INCREMENT,
    SubscriptionRecords_UniqueID INT,
    SubscriptionDiscountID INT,
    Name VARCHAR(255),
    DiscountInCents INT,
    PRIMARY KEY (UniqueID),
    CONSTRAINT FK_SubscriptionRecords_UniqueID_Discounts
        FOREIGN KEY (SubscriptionRecords_UniqueID)
        REFERENCES SubscriptionRecords (UniqueID)
        ON DELETE CASCADE
);

-- Table: SubscriptionDiscountQualifiers
CREATE TABLE SubscriptionDiscountQualifiers (
    UniqueID INT NOT NULL AUTO_INCREMENT,
    Discount_UniqueID INT,
    DiscountQualifiersID INT,
    Name VARCHAR(255),
    SubscriptionID INT,
    PRIMARY KEY (UniqueID),
    CONSTRAINT FK_Discount_UniqueID_DiscountQualifiers
        FOREIGN KEY (Discount_UniqueID)
        REFERENCES SubscriptionDiscounts (UniqueID)
        ON DELETE CASCADE
);