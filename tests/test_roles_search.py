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


def test_roles_search():
    """Search and verify roles are created for the service"""
    token = get_token()
    mdms = load_json(MDMS_FILE)
    
    module = mdms["module"]
    service = mdms["service"]
    
    url = f"{BASE_URL}/egov-mdms-service/v2/_search"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "RequestInfo": get_request_info(token),
        "MdmsCriteria": {
            "tenantId": tenantId,
            "schemaCode": "ACCESSCONTROL-ROLES.roles",
            "limit": 10000000
        }
    }
    
    res = requests.post(url, json=payload, headers=headers)
    assert res.status_code == 200, f"Roles search failed: {res.text}"
    
    data = res.json()
    mdms_data = data.get("mdms") or data.get("Mdms") or []
    
    # Find roles where code contains module AND service (case-insensitive)
    found_roles = []
    
    for item in mdms_data:
        role_data = item.get("data", {})
        role_code = role_data.get("code") or role_data.get("rolecode") or ""
        
        # Check if role code contains both module and service
        if module.upper() in role_code.upper() and service.upper() in role_code.upper():
            found_roles.append(role_code)
    
    return {
        "module": module,
        "service": service,
        "total_roles": len(mdms_data),
        "found_roles": found_roles,
        "service_roles_count": len(found_roles)
    }