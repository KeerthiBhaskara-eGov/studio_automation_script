from utils.api_client import APIClient
from utils.auth import get_auth_token
from utils.config import tenantId, BASE_URL
import json
import requests

APP_FILE = "output/application_response.json"

def load_json(path):
    return json.load(open(path))

def get_token():
    return get_auth_token("user")


def test_application_search():
    """Search and validate application exists"""
    token = get_token()
    app_data = load_json(APP_FILE)
    
    service_code = app_data["service_code"]
    application_number = app_data["application_number"]
    
    url = f"{BASE_URL}/public-service/v1/application/{service_code}?tenantId={tenantId}&applicationNumber={application_number}&limit=10&offset=0"
    
    # Use auth-token header (not Bearer)
    headers = {
        "Content-Type": "application/json",
        "auth-token": token,
        "x-tenant-id": tenantId
    }
    
    res = requests.get(url, headers=headers)
    assert res.status_code == 200, f"Search failed: {res.text}"
    
    data = res.json()
    apps = data.get("Application") or data.get("application") or data.get("applications") or []
    apps = apps if isinstance(apps, list) else [apps]
    
    assert len(apps) > 0, f"Application not found: {application_number}"
    
    app = apps[0]
    assert app.get("applicationNumber") == application_number, "Application number mismatch"
    assert app.get("serviceCode") == service_code, "Service code mismatch"
    assert app.get("tenantId") == tenantId, "Tenant ID mismatch"
    
    return {
        "application_number": application_number,
        "service_code": service_code,
        "found": True,
        "status": app.get("workflowStatus")
    }


def test_application_search_by_service_code():
    """Search applications by service code only"""
    token = get_token()
    app_data = load_json(APP_FILE)
    
    service_code = app_data["service_code"]
    
    url = f"{BASE_URL}/public-service/v1/application/{service_code}?tenantId={tenantId}&limit=10&offset=0"
    
    headers = {
        "Content-Type": "application/json",
        "auth-token": token,
        "x-tenant-id": tenantId
    }
    
    res = requests.get(url, headers=headers)
    assert res.status_code == 200, f"Search failed: {res.text}"
    
    data = res.json()
    apps = data.get("Application") or data.get("application") or data.get("applications") or []
    apps = apps if isinstance(apps, list) else [apps]
    
    assert len(apps) > 0, f"No applications found for service: {service_code}"
    
    return {
        "service_code": service_code,
        "total_found": len(apps)
    }