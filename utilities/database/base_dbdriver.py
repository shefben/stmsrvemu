from sqlalchemy import Column, Integer, String, Date, Time, Text, ForeignKey, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base( )


"""standalone, without needing databasedriver class:
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, Date, Time

metadata = MetaData()

# Define the table structure
firstblob_table = Table('firstblob', metadata,
    Column('id', Integer, primary_key=True),
    Column('ccr_blobdate', Date),
    Column('version', Integer),
    Column('bootstrapper', Integer),
    # ... include other columns as per your requirement ...
    Column('client_date', Date),
    Column('client_time', Time)
)

def create_table_mysql(connection_string):
    "" Create table in a MySQL database ""
    engine = create_engine(connection_string)
    metadata.create_all(engine)

def create_table_sqlite(connection_string):
    " Create table in a SQLite database "
    engine = create_engine(connection_string)
    metadata.create_all(engine)
"""
class BaseDatabaseDriver :
    def create_tables(self):

        Base.metadata.create_all(self.engine)

    class FirstBlob(Base) :
        __tablename__ = 'firstblob'
        id = Column(Integer, primary_key=True)
        ccr_blobdate = Column(Date)
        version = Column(Integer)
        bootstrapper = Column(Integer)
        client = Column(Integer)
        linux_client = Column(Integer)
        hlds = Column(Integer)
        linux_hlds = Column(Integer)
        beta_bootstrapper = Column(Integer)
        beta_bootstrapper_pwd = Column(String)
        beta_client = Column(Integer)
        beta_client_pwd = Column(String)
        beta_hlds = Column(Integer)
        beta_hlds_pwd = Column(String)
        beta_linux_hlds = Column(Integer)
        steam_game_updater = Column(Integer)
        cafe_admin_client = Column(Integer)
        cafe_admin_server = Column(Integer)
        custom_pkg = Column(Integer)
        client_date = Column(Date)
        client_time = Column(Time)

    class UserActivities(Base) :
        __tablename__ = 'useractivities'
        LogID = Column(Integer, primary_key=True, autoincrement=True)
        SteamID = Column(String(50), nullable=False)
        UserName = Column(String(100))
        UserIP = Column(String(15))
        LogDate = Column(Date)
        LogTime = Column(Time)
        Activity = Column(String(255))
        Notes = Column(Text)

    class AccountExternalBillingInfoRecord(Base) :
        __tablename__ = 'accountexternalbillinginforecord'
        UniqueID = Column(Integer, primary_key=True, nullable=False)
        ExternalAccountName = Column(String(256))
        ExternalAccountPassword = Column(String(256))

    class AccountPaymentCardInfoRecord(Base) :
        __tablename__ = 'accountpaymentcardinforecord'
        UniqueID = Column(Integer, primary_key=True, nullable=False)
        UserRegistry_UniqueID = Column(Integer)
        PaymentCardType = Column(Integer)
        CardNumber = Column(String(255))
        CardHolderName = Column(String(255))
        CardExpYear = Column(Integer)
        CardExpMonth = Column(Integer)
        CardCVV2 = Column(String(255))
        BillingAddress1 = Column(String(255))
        BillingAddress2 = Column(String(255))
        BillingCity = Column(String(255))
        BillingZip = Column(String(255))
        BillingState = Column(String(255))
        BillingCountry = Column(String(255))
        BillingPhone = Column(String(255))
        BillinEmailAddress = Column(String(255))
        CCApprovalDate = Column(Date)
        CCApprovalCode = Column(String(255))
        CDenialDate = Column(Date)
        CDenialCode = Column(String(255))
        UseAVS = Column(Integer)
        PriceBeforeTax = Column(DECIMAL(10, 2))
        TaxAmount = Column(DECIMAL(10, 2))
        TransactionType = Column(String(255))
        AuthComments = Column(String(255))
        AuthStatus = Column(String(255))
        AuthSource = Column(String(255))
        AuthResponse = Column(String(255))
        TransDate = Column(Date)
        TransTime = Column(Time)
        PS2000Data = Column(Text)
        SettlementDate = Column(Date)
        SettlementCode = Column(String(255))
        CCTSResponseCode = Column(String(255))
        SettlementBatchId = Column(Integer)
        SettlementBatchSeq = Column(Integer)
        SettlementApprovalCode = Column(String(255))
        SettlementComments = Column(String(255))
        SettlementStatus = Column(String(255))
        AStoBBSTxnId = Column(Integer)
        SubsId = Column(Integer)
        AcctName = Column(String(255))
        CC1TimeChargeTxnSeq = Column(Integer)
        CustSupportName = Column(String(255))
        ChargeBackCaseNumber = Column(String(255))
        GetCreditForceTxnSeq = Column(Integer)
        ShippingInfoRecord = Column(Integer)

    class AccountPrepurchasedInfoRecord(Base) :
        __tablename__ = 'accountprepurchasedinforecord'
        UniqueID = Column(Integer, primary_key=True, nullable=False)
        UserRegistry_UniqueID = Column(Integer)
        TypeOfProofOfPurchase = Column(String(45))
        BinaryProofOfPurchaseToken = Column(String(45))
        TokenRejectionReason = Column(String(45))
        SubsId = Column(String(45))
        CustSupportName = Column(String(45))

    class AccountSubscriptionsBillingInfoRecord(Base) :
        __tablename__ = 'accountsubscriptionsbillinginforecord'
        UniqueID = Column(Integer, primary_key=True, nullable=False)
        UserRegistry_UniqueID = Column(Integer)
        SubscriptionID = Column(String(45))
        AccountPaymentCardInfoRecord = Column(String(45))
        AccountPrepurchasedInfoRecord_UniqueID = Column(Integer)
        AccountExternalBillingInfoRecord_UniqueID = Column(Integer)
        AccountPaymentCardReceiptRecord_UniqueID = Column(Integer)

    class AccountSubscriptionsRecord(Base) :
        __tablename__ = 'accountsubscriptionsrecord'
        UniqueID = Column(Integer, primary_key=True, nullable=False)
        UserRegistry_UniqueID = Column(Integer)
        SubscriptionID = Column(String(45))
        SubscribedDate = Column(String(45))
        UnsubscribedDate = Column(String(45))
        SubscriptionStatus = Column(String(45))
        StatusChangeFlag = Column(String(45))
        PreviousSubscriptionState = Column(String(45))
        OptionalBillingStatus = Column(String(4))
        UserIP = Column(String(4))
        UserCountryCode = Column(String(16))

    class CCardType(Base) :
        __tablename__ = 'ccardtype'
        uniqueid = Column(Integer, primary_key=True, nullable=False)
        card_type = Column(String(255))

    class CustSupportAccountRecord(Base) :
        __tablename__ = 'custsupportaccountrecord'
        UniqueID = Column(Integer, primary_key=True, nullable=False)
        AccountSubscriptionsRecord_UniqueID = Column(Integer)
        UserRegistry_UniqueID = Column(Integer)
        AccountStatus = Column(String(45))

    class DerivedSubscribedAppsRecord(Base) :
        __tablename__ = 'derivedsubscribedappsrecord'
        UniqueID = Column(Integer, primary_key=True, nullable=False)
        UserRegistry_UniqueID = Column(Integer)
        AppID = Column(Integer)
        Field2 = Column(String(45))

    class SteamApplications(Base) :
        __tablename__ = 'steamapplications'
        AppID = Column(Integer, primary_key=True, nullable=False)
        Name = Column(String(256))