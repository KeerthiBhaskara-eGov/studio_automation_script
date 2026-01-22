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


def test_actions_search():
    """Search and verify actions-test are created for the service"""
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
            "schemaCode": "ACCESSCONTROL-ACTIONS-TEST.actions-test",
            "limit": 10000000
        }
    }
    
    res = requests.post(url, json=payload, headers=headers)
    assert res.status_code == 200, f"Actions search failed: {res.text}"
    
    data = res.json()
    mdms_data = data.get("mdms") or data.get("Mdms") or []
    
    # Look for actions related to our service (check url and sidebarURL)
    service_actions = []
    for item in mdms_data:
        action_data = item.get("data", {})
        action_url = action_data.get("url") or ""
        sidebar_url = action_data.get("sidebarURL") or ""
        
        # Check if url OR sidebarURL contains module or service (case-insensitive)
        url_match = (
            module.lower() in action_url.lower() or 
            service.lower() in action_url.lower()
        )
        sidebar_match = (
            module.lower() in sidebar_url.lower() or 
            service.lower() in sidebar_url.lower()
        )
        
        if url_match or sidebar_match:
            service_actions.append({
                "url": action_url,
                "sidebarURL": sidebar_url,
                "displayName": action_data.get("displayName"),
                "id": action_data.get("id")
            })
    
    return {
        "module": module,
        "service": service,
        "total_actions": len(mdms_data),
        "service_actions_count": len(service_actions),
        "service_actions": service_actions[:5]  # First 5 for display
    }


def test_roleactions_search():
    """Search and verify roleactions are created for the service"""
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
            "schemaCode": "ACCESSCONTROL-ROLEACTIONS.roleactions",
            "limit": 10000000
        }
    }
    
    res = requests.post(url, json=payload, headers=headers)
    assert res.status_code == 200, f"Roleactions search failed: {res.text}"
    
    data = res.json()
    mdms_data = data.get("mdms") or data.get("Mdms") or []
    
    # Find roleactions where role code contains module AND service
    service_roleactions = []
    found_roles = set()
    
    for item in mdms_data:
        roleaction_data = item.get("data", {})
        role_code = roleaction_data.get("rolecode") or roleaction_data.get("roleCode") or ""
        action_id = roleaction_data.get("actionid") or roleaction_data.get("actionId")
        
        # Check if role code contains both module and service (case-insensitive)
        if module.upper() in role_code.upper() and service.upper() in role_code.upper():
            service_roleactions.append(roleaction_data)
            found_roles.add(role_code)
    
    return {
        "module": module,
        "service": service,
        "total_roleactions": len(mdms_data),
        "found_roles": list(found_roles),
        "service_roleactions_count": len(service_roleactions)
    }