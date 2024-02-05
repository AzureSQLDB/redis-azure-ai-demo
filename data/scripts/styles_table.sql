create table [aidemo].[styles] (
    id              int NOT NULL PRIMARY KEY CLUSTERED,
    gender          nvarchar(50) NOT NULL,
    masterCategory  nvarchar(100) NOT NULL,
    subCategory     nvarchar(100) NOT NULL,
    articleType     nvarchar(100) NOT NULL,
    baseColour      nvarchar(50) NOT NULL,
    season          nvarchar(50) NOT NULL,
    year            int NOT NULL,
    usage           nvarchar(100) NOT NULL,
    productDisplayName  nvarchar(2000) NOT NULL
)
