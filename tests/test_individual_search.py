import pytest
from utils.auth import get_auth_token
from utils.request_info import get_request_info
from utils.config import tenantId, BASE_URL
import json
import requests

APP_FILE = "output/application_response.json"
MDMS_FILE = "output/mdms_response.json"

def load_json(path):
    return json.load(open(path))

def get_token():
    return get_auth_token("user")


def test_individual_search(request):
    """Search individual by mobile number from application details"""
    token = get_token()
    
    # Load application and mdms data
    app_data = load_json(APP_FILE)
    mdms = load_json(MDMS_FILE)
    
    module = mdms["module"]
    service = mdms["service"]
    application_number = app_data.get("application_number")
    
    # Get mobile number from application
    mobile_number = app_data.get("mobile_number")
    
    if not mobile_number:
        result = {
            "module": module,
            "service": service,
            "application_number": application_number,
            "message": "Mobile number not found in application",
            "individual_found": False
        }
        
        if request:
            request.node._test_result = {
                "Module": module,
                "Service": service,
                "Application Number": application_number,
                "Status": "⚠️ Mobile number not found"
            }
        
        return result
    
    # Search individual by mobile number
    url = f"{BASE_URL}/health-individual/v1/_search?limit=1000&offset=0&tenantId={tenantId}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "RequestInfo": {
            "apiId": "",
            "ver": "",
            "ts": 0,
            "action": "",
            "did": "",
            "key": "",
            "msgId": "",
            "requesterId": "",
            "authToken": token,
            "userInfo": {
                "uuid": "00000000-0000-0000-0000-000000000000",
                "userName": "",
                "name": "",
                "mobileNumber": "",
                "emailId": None,
                "locale": None,
                "type": "",
                "roles": None,
                "active": False,
                "tenantId": tenantId,
                "permanentCity": None
            }
        },
        "Individual": {
            "tenantId": tenantId,
            "mobileNumber": [int(mobile_number) if str(mobile_number).isdigit() else mobile_number]
        }
    }
    
    res = requests.post(url, json=payload, headers=headers)
    assert res.status_code == 200, f"Individual search failed: {res.text}"
    
    data = res.json()
    individuals = data.get("Individual") or data.get("individual") or []
    individuals = individuals if isinstance(individuals, list) else [individuals]
    
    individual_found = len(individuals) > 0
    
    result = {
        "module": module,
        "service": service,
        "application_number": application_number,
        "mobile_number": mobile_number,
        "individual_found": individual_found,
        "total_individuals": len(individuals)
    }
    
    if individual_found:
        ind = individuals[0]
        result["individual_id"] = ind.get("id")
        result["individual_uuid"] = ind.get("individualId")
        result["name"] = ind.get("name", {}).get("givenName") if isinstance(ind.get("name"), dict) else ind.get("name")
    
    # Store for HTML report
    if request:
        report_data = {
            "Module": module,
            "Service": service,
            "Application Number": application_number,
            "Mobile Number": mobile_number,
            "Individual Found": "✅ Yes" if individual_found else "❌ No",
            "Total Individuals": len(individuals)
        }
        
        if individual_found:
            report_data["Individual ID"] = result.get("individual_id")
            report_data["Name"] = result.get("name")
        
        request.node._test_result = report_data
    
    return result