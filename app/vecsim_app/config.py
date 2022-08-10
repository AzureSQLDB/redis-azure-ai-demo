import os

PROJECT_NAME = "vecsim_app"
API_DOCS = "/api/docs"
OPENAPI_DOCS = "/api/openapi.json"
INDEX_TYPE = os.environ.get("VECSIM_INDEX_TYPE", "HNSW")
REDIS_HOST = os.environ.get("REDIS_HOST", "redis-vector-db")
REDIS_PORT = os.environ.get("REDIS_PORT", 6379)
REDIS_DB = os.environ.get("REDIS_DB", 0)
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", "testing123")
REDIS_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
os.environ["REDIS_DATA_URL"] = REDIS_URL
os.environ["REDIS_OM_URL"] = REDIS_URL
API_V1_STR = "/api/v1"
DATA_LOCATION = os.environ.get("DATA_LOCATION", "../../data")
SUPERUSER_EMAIL = os.environ.get("SUPER_EMAIL", "s@p.com")
SUPERUSER_PASS = os.environ.get("SUPER_PASS", "secret")
SUPERUSER_FIRST = os.environ.get("SUPER_FIRST", "sam")
SUPERUSER_LAST = os.environ.get("SUPER_LAST", "lastname")
SECRET_KEY = os.environ.get("SECRET_KEY", "supersecretkey")
