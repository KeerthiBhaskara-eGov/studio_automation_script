import os
from dotenv import load_dotenv

load_dotenv(override=True)  # This forces reloading of updated values

BASE_URL = os.getenv("BASE_URL")
tenantId = os.getenv("TENANTID", "st")

if not BASE_URL:
    raise ValueError("BASE_URL not found in .env")


# Define reusable params dict
search_params = {
    "tenantId": tenantId
}

individual=os.getenv("SERVICE_INDIVIDUAL")
project=os.getenv("SERVICE_PROJECT")
mdms=os.getenv("SERVICE_MDMS")