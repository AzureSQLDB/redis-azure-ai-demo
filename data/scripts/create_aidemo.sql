# In master
USE [master]
GO

CREATE LOGIN aidemo WITH PASSWORD = '#######';
GO


# In DEMO DB
USE [RedisAiDb]
GO

CREATE SCHEMA aidemo;
GO

CREATE USER [aidemo] FOR LOGIN [aidemo] WITH DEFAULT_SCHEMA=[dbo]
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
grant CREATE SCHEMA to aidemo;
