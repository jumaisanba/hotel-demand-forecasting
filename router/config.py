import os
from dotenv import load_dotenv

load_dotenv()

PREDICTION_SERVICE_URL = os.getenv("PREDICTION_SERVICE_URL", "http://prediction_service:8001")
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8002")
DATA_INTERFACE_SERVICE_URL = os.getenv("DATA_INTERFACE_SERVICE_URL", "http://data-interface-service:8003")

SECRET_KEY = os.getenv("SECRET_KEY", "super-secret")
ALGORITHM = os.getenv("ALGORITHM", "HS256")