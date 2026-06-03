import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL")

API_HOST = os.getenv("API_HOST")
API_PORT = int(os.getenv("API_PORT"))
API_DEBUG = os.getenv("API_DEBUG").lower() == "true"
API_PREFIX = "/api/v1"
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS", "http://localhost:8501,http://localhost:3000"
).split(",")

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL")

MCP_PROTOCOL_VERSION = "2025-03-26"
MCP_SERVER_VERSION = "1.0.0"
JSON_RPC_VERSION = "2.0"
