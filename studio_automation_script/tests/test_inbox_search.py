from utils.auth import get_auth_token
from utils.request_info import get_request_info
from utils.config import tenantId, BASE_URL
import json
import requests

MDMS_FILE = "output/mdms_response.json"
APP_FILE = "output/application_response.json"

def load_json(path):
    return json.load(open(path))

def get_token():
    return get_auth_token("user")


def test_inbox_search():
    """Search inbox for application"""
    token = get_token()
    mdms = load_json(MDMS_FILE)
    app_data = load_json(APP_FILE)
    
    module = mdms["module"]
    service = mdms["service"]
    application_number = app_data["application_number"]
    
    url = f"{BASE_URL}/inbox/v2/_search"
    
    headers = {
        "Content-Type": "application/json",
        "auth-token": token,
        "x-tenant-id": tenantId
    }
    
    payload = {
        "inbox": {
            "limit": 10,
            "offset": 0,
            "tenantId": tenantId,
            "processSearchCriteria": {
                "businessService": [f"{module}.{service}"],
                "moduleName": "public-services",
                "tenantId": tenantId
            },
            "moduleSearchCriteria": {
                "businessService": service,
                "module": module,
                "sortOrder": "ASC"
            }
        },
        "RequestInfo": get_request_info(token)
    }
    
    res = requests.post(url, json=payload, headers=headers)
    assert res.status_code == 200, f"Inbox search failed: {res.text}"
    
    data = res.json()
    items = data.get("items") or data.get("inbox") or []
    
    # Check if our application is in inbox
    found = False
    for item in items:
        business_object = item.get("businessObject") or {}
        if business_object.get("applicationNumber") == application_number:
            found = True
            break
    
    return {
        "application_number": application_number,
        "total_inbox_items": len(items),
        "application_in_inbox": found
    }