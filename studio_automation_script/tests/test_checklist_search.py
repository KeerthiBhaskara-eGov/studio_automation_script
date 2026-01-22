import pytest
import json
import requests
from utils.auth import get_auth_token
from utils.request_info import get_request_info
from utils.data_loader import load_payload
from utils.config import tenantId, BASE_URL

MDMS_FILE = "output/mdms_response.json"
CHECKLIST_SEARCH_URL = "/health-service-request/service/definition/v1/_search"


def load_json(path):
    return json.load(open(path))


def get_token():
    return get_auth_token("user")


def get_headers(token):
    return {
        "Content-Type": "application/json",
        "auth-token": token,
        "x-tenant-id": tenantId
    }


def get_checklists_from_payload():
    """Get checklist definitions from MDMS payload file."""
    try:
        payload = load_payload("mdms", "mdms_service_create.json")
    except FileNotFoundError:
        return []
    
    return payload.get("Mdms", {}).get("data", {}).get("checklist", [])


def search_checklist_by_code(code, token):
    """Search checklist by exact code."""
    url = f"{BASE_URL}{CHECKLIST_SEARCH_URL}"
    
    payload = {
        "ServiceDefinitionCriteria": {
            "code": [code],
            "tenantId": tenantId
        },
        "includeDeleted": True,
        "RequestInfo": get_request_info(token)
    }
    
    res = requests.post(url, json=payload, headers=get_headers(token))
    
    if res.status_code == 200:
        data = res.json()
        definitions = (
            data.get("ServiceDefinitions") or 
            data.get("serviceDefinitions") or 
            data.get("ServiceDefinition") or 
            data.get("serviceDefinition") or 
            []
        )
        definitions = definitions if isinstance(definitions, list) else [definitions]
        
        if definitions and len(definitions) > 0:
            return {
                "found": True,
                "id": definitions[0].get("id"),
                "code": definitions[0].get("code"),
                "is_active": definitions[0].get("isActive")
            }
    
    return {"found": False, "id": None, "code": None, "is_active": None}


def test_checklist_search(request):
    """Search and verify all checklists are created for the service."""
    token = get_token()
    mdms = load_json(MDMS_FILE)
    
    module = mdms["module"]
    service = mdms["service"]
    
    # Get checklist definitions from payload
    checklists = get_checklists_from_payload()
    
    print(f"\n📋 Module: {module}")
    print(f"📋 Service: {service}")
    print(f"📋 Checklists in payload: {len(checklists)}")
    
    for c in checklists:
        print(f"   - {c.get('name')} @ {c.get('state')}")
    
    if not checklists:
        if request:
            request.node._test_result = {
                "Module": module,
                "Service": service,
                "Status": "⚠️ No checklists in payload"
            }
        return {"module": module, "service": service, "total_defined": 0, "total_found": 0}
    
    checklist_results = []
    
    for checklist in checklists:
        name = checklist.get("name", "")
        state = checklist.get("state", "")
        
        if not name or not state:
            continue
        
        # Build checklist code: {service}.{state}.{checklist_name}
        code = f"{service}.{state}.{name}"
        
        print(f"\n🔍 Searching: {code}")
        result = search_checklist_by_code(code, token)
        
        if result["found"]:
            print(f"   ✅ Found! ID: {result['id']}")
        else:
            print(f"   ❌ Not found")
        
        checklist_results.append({
            "name": name,
            "state": state,
            "code": code,
            "found": result["found"],
            "id": result["id"],
            "is_active": result["is_active"]
        })
    
    found_count = sum(1 for c in checklist_results if c["found"])
    total_count = len(checklist_results)
    
    print(f"\n📊 Result: {found_count}/{total_count} checklists found")
    
    # Store for HTML report
    if request:
        status = "✅ All Found" if found_count == total_count else f"⚠️ {found_count}/{total_count} Found"
        report = {
            "Module": module,
            "Service": service,
            "Total Defined": str(total_count),
            "Total Found": str(found_count),
            "Status": status
        }
        for c in checklist_results:
            icon = "✅" if c["found"] else "❌"
            report[c["state"]] = f"{icon} {c['name']}"
        
        request.node._test_result = report
    
    return {
        "module": module,
        "service": service,
        "total_defined": total_count,
        "total_found": found_count,
        "checklists": checklist_results
    }