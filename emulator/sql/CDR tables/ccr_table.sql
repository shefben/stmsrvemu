CREATE TABLE ClientContentRecord (
    UniqueID INT NOT NULL AUTO_INCREMENT,
    BlobDate DATE,
    version VARCHAR(255),
    ClientBootstrapVersion VARCHAR(255),
    ClientAppPackageVersion VARCHAR(255),
    LinuxClientAppVersion VARCHAR(255),
    Win32HldsUpdateToolVersion VARCHAR(255), 
    LinuxHldsUpdateToolVersion VARCHAR(255),
    BetaClientBootstrapVersion VARCHAR(255),
    BetaClientBootstrapPassword VARCHAR(255),
    BetaClientAppPackageVersion VARCHAR(255),
    BetaClientAppPackagePassword VARCHAR(255),
    BetaWin32HldsUpdateToolVersion VARCHAR(255),
    BetaWin32HldsUpdateToolPassword VARCHAR(255),
    BetaLinuxHldsUpdateToolVersion VARCHAR(255),
    BetaLinuxHldsUpdateToolPassword VARCHAR(255),
    CafeAdministrationClientVersion VARCHAR(255),
    CafeAdministrationServerVersion VARCHAR(255),
    CustomPackageVersion VARCHAR(255),
    SteamGameUpdaterVersion VARCHAR(255),
    PRIMARY KEY (UniqueID)
);