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


def test_idgen_search():
    """Search and verify idgen formats are created for the service"""
    token = get_token()
    mdms = load_json(MDMS_FILE)
    
    module = mdms["module"]
    service = mdms["service"]
    
    # Expected idgen names based on service configuration
    expected_idgens = [
        f"{module}-{service}.application.{service}.applicationapp.id",
        f"{module}-{service}.application.{service}.applicationservice.id"
    ]
    
    url = f"{BASE_URL}/egov-mdms-service/v2/_search"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "RequestInfo": get_request_info(token),
        "MdmsCriteria": {
            "tenantId": tenantId,
            "schemaCode": "common-masters.IdFormat",
            "limit": 10000000
        }
    }
    
    res = requests.post(url, json=payload, headers=headers)
    assert res.status_code == 200, f"Idgen search failed: {res.text}"
    
    data = res.json()
    mdms_data = data.get("mdms") or data.get("Mdms") or []
    
    # Extract all idgen names
    all_idgens = []
    for item in mdms_data:
        idgen_data = item.get("data", {})
        idname = idgen_data.get("idname") or idgen_data.get("idName")
        if idname:
            all_idgens.append(idname)
    
    # Check if expected idgens exist
    found_idgens = []
    missing_idgens = []
    
    for idgen in expected_idgens:
        if idgen in all_idgens:
            found_idgens.append(idgen)
        else:
            missing_idgens.append(idgen)
    
    return {
        "module": module,
        "service": service,
        "total_idgens": len(mdms_data),
        "expected_idgens": expected_idgens,
        "found_idgens": found_idgens,
        "missing_idgens": missing_idgens,
        "all_idgens_found": len(missing_idgens) == 0
    }