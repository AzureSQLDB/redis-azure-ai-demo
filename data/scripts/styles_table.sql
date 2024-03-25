create table [aidemo].[styles] (
    id              int NOT NULL PRIMARY KEY CLUSTERED,
    gender          nvarchar(50) NOT NULL,
    masterCategory  nvarchar(100) NOT NULL,
    subCategory     nvarchar(100) NOT NULL,
    articleType     nvarchar(100) NOT NULL,
    baseColour      nvarchar(50) NOT NULL,
    season          nvarchar(50) NOT NULL,
    year            int,
    usage           nvarchar(100) NOT NULL,
    productDisplayName  nvarchar(2000) NOT NULL
)

ALTER DATABASE CURRENT
SET CHANGE_TRACKING = ON
(CHANGE_RETENTION = 2 DAYS, AUTO_CLEANUP = ON);

ALTER TABLE [aidemo].[styles]
ENABLE CHANGE_TRACKING;
