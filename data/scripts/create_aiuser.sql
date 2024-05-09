# In master
CREATE LOGIN aiuser WITH PASSWORD = '#######';
GO


# In DEMO DB

CREATE SCHEMA aidemo;
GO

CREATE USER [aidemo] FOR LOGIN [aiuser] WITH DEFAULT_SCHEMA=[dbo]
GO
ALTER AUTHORIZATION ON SCHEMA::[aidemo] TO [aidemo]
GO
USE [RedisAiDb]
GO
EXEC sp_addrolemember N'db_datareader', N'aidemo'
GO
USE [RedisAiDb]
GO
EXEC sp_addrolemember N'db_datawriter', N'aidemo'
GO

grant CREATE TABLE to aidemo;
grant CREATE VIEW to aidemo;
grant CREATE FUNCTION to aidemo;
grant CREATE PROCEDURE to aidemo;
