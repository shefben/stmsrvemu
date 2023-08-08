-- Table: PublicKeysRecords
CREATE TABLE PublicKeysRecords (
    UniqueID INT NOT NULL AUTO_INCREMENT,
    PublicKeyRecordID INT,
    Exponent VARCHAR(255),
    Modulus VARCHAR(255),
    PRIMARY KEY (UniqueID),
    CONSTRAINT Unique_PublicKeyRecordID UNIQUE (PublicKeyRecordID)
);