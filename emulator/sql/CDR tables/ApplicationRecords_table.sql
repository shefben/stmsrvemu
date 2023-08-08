-- Table: ApplicationRecords
CREATE TABLE ApplicationRecords (
    UniqueID INT NOT NULL,
    ApplicationID INT,
    Name VARCHAR(255),
    InstallDirName VARCHAR(255),
    MinCacheFileSizeMB INT,
    MaxCacheFileSizeMB INT,
    OnFirstLaunch INT,
    IsBandwidthGreedy BOOL,
    CurrentVersionId INT,
    TrickleVersionId INT,
    BetaVersionPassword VARCHAR(255),
    BetaVersionId INT,
    UseFilesystemDvr BOOL,
    ManifestOnlyApp BOOL,
    AppOfManifestOnlyCache INT,
    PRIMARY KEY (UniqueID)
);

-- Table: ApplicationLaunchOptionRecord
CREATE TABLE ApplicationLaunchOptionRecord (
    UniqueID INT NOT NULL,
    ApplicationRecords_UniqueID INT,
    Description VARCHAR(255),
    CommandLine VARCHAR(255),
    IconIndex INT,
    NoDesktopShortcut BOOL,
    NoStartMenuShortcut BOOL,
    LongRunningUnattended BOOL,
    PRIMARY KEY (UniqueID),
    CONSTRAINT FK_ApplicationRecords_UniqueID_LaunchOption
        FOREIGN KEY (ApplicationRecords_UniqueID)
        REFERENCES ApplicationRecords (UniqueID)
        ON DELETE CASCADE
);

-- Table: ApplicationVersionsRecords
CREATE TABLE ApplicationVersionsRecords (
    UniqueID INT NOT NULL,
    ApplicationRecords_UniqueID INT,
    ApplicationVersionRecordID INT,
    Description VARCHAR(255),
    IsNotAvailable BOOL,
    LaunchOptionIdRecords VARCHAR(255),
    DepotEncryptionKey VARCHAR(255),
    IsEncryptionKeyAvailable BOOL,
    IsRebase BOOL,
    IsLongVersionRoll BOOL,
    PRIMARY KEY (UniqueID),
    CONSTRAINT FK_ApplicationRecords_UniqueID_VersionRecords
        FOREIGN KEY (ApplicationRecords_UniqueID)
        REFERENCES ApplicationRecords (UniqueID)
        ON DELETE CASCADE
);

-- Table: ApplicationUserDefinedRecords
CREATE TABLE ApplicationUserDefinedRecords (
    UniqueID INT NOT NULL,
    ApplicationRecords_UniqueID INT,
    Key VARCHAR(255),
    Value VARCHAR(255),
    PRIMARY KEY (UniqueID),
    CONSTRAINT FK_ApplicationRecords_UniqueID_UserDefined
        FOREIGN KEY (ApplicationRecords_UniqueID)
        REFERENCES ApplicationRecords (UniqueID)
        ON DELETE CASCADE
);

-- Table: ApplicationFilesystemRecords
CREATE TABLE ApplicationFilesystemRecords (
    UniqueID INT NOT NULL,
    ApplicationRecords_UniqueID INT,
    Appid INT,
    MountName VARCHAR(255),
    IsOptional BOOL,
    PRIMARY KEY (UniqueID),
    CONSTRAINT FK_ApplicationRecords_UniqueID_FilesystemRecords
        FOREIGN KEY (ApplicationRecords_UniqueID)
        REFERENCES ApplicationRecords (UniqueID)
        ON DELETE CASCADE
);