import pytest
from utils.auth import get_auth_token
from utils.request_info import get_request_info
from utils.config import tenantId, BASE_URL
import json
import requests

MDMS_FILE = "output/mdms_response.json"

def load_json(path):
    return json.load(open(path))

def get_token():
    return get_auth_token("user")


def test_localization_search(request):
    """Search localization messages by module"""
    token = get_token()
    mdms = load_json(MDMS_FILE)
    
    module = mdms["module"]
    service = mdms["service"]
    
    # Localization module pattern (lowercase)
    loc_module = f"rainmaker-studio-{module.lower()}"
    
    url = f"{BASE_URL}/localization/messages/v1/_search?locale=en_IN&tenantId={tenantId}&module={loc_module}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "RequestInfo": get_request_info(token)
    }
    
    res = requests.post(url, json=payload, headers=headers)
    assert res.status_code == 200, f"Localization search failed: {res.text}"
    
    data = res.json()
    messages = data.get("messages") or []
    
    result = {
        "module": module,
        "service": service,
        "localization_module": loc_module,
        "total_messages": len(messages),
        "messages": [{"code": m.get("code"), "message": m.get("message")} for m in messages[:10]]
    }
    
    # Store for HTML report
    if request:
        request.node._test_result = {
            "Module": module,
            "Service": service,
            "Localization Module": loc_module,
            "Total Messages": len(messages),
            "Status": "✅ Found" if len(messages) > 0 else "⚠️ Not Found"
        }
    
    return result