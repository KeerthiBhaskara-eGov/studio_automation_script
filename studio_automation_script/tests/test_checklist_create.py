import pytest
import json
import requests
from utils.auth import get_auth_token
from utils.request_info import get_request_info
from utils.data_loader import load_payload
from utils.config import tenantId, BASE_URL

MDMS_FILE = "output/mdms_response.json"
APP_FILE = "output/application_response.json"
CHECKLIST_OUTPUT_FILE = "output/checklist_response.json"

CHECKLIST_DEF_SEARCH_URL = "/health-service-request/service/definition/v1/_search"
CHECKLIST_SERVICE_SEARCH_URL = "/health-service-request/service/v1/_search"
CHECKLIST_CREATE_URL = "/health-service-request/service/v1/_create"
CHECKLIST_UPDATE_URL = "/health-service-request/service/v1/_update"


def load_json(path):
    return json.load(open(path))


def save_json(data, path):
    import os
    os.makedirs("output", exist_ok=True)
    json.dump(data, open(path, "w"), indent=2)


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


def get_checklist_for_state(state):
    """Get checklist definition for a specific state."""
    checklists = get_checklists_from_payload()
    for checklist in checklists:
        if checklist.get("state") == state:
            return checklist
    return None


def search_checklist_definition(code, token):
    """Search checklist definition by code."""
    url = f"{BASE_URL}{CHECKLIST_DEF_SEARCH_URL}"
    
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
        definitions = data.get("ServiceDefinitions") or data.get("serviceDefinitions") or []
        definitions = definitions if isinstance(definitions, list) else [definitions]
        
        if definitions and len(definitions) > 0:
            return definitions[0]
    
    return None


def search_checklist_service(service_def_id, account_id, token):
    """Search existing checklist service by serviceDefId and accountId."""
    url = f"{BASE_URL}{CHECKLIST_SERVICE_SEARCH_URL}"
    
    payload = {
        "ServiceCriteria": {
            "serviceDefIds": [service_def_id],
            "accountId": account_id,
            "tenantId": tenantId
        },
        "RequestInfo": get_request_info(token)
    }
    
    res = requests.post(url, json=payload, headers=get_headers(token))
    
    if res.status_code == 200:
        data = res.json()
        services = data.get("Services") or data.get("services") or []
        services = services if isinstance(services, list) else [services]
        
        if services and len(services) > 0:
            return services[0]
    
    return None


def normalize_data_type(data_type):
    """
    Normalize dataType to match UI format.
    UI uses: 'text' (lowercase), 'SingleValueList', 'MultiValueList', 'Number'
    """
    if data_type and data_type.lower() == "text":
        return "text"  # lowercase for Text type
    return data_type  # Keep others as-is (SingleValueList, etc.)


def build_attributes_from_definition(definition, existing_attrs=None):
    """Build attributes payload from definition with correct dataType and values."""
    attributes = []
    def_attributes = definition.get("attributes") or []
    
    # Map existing attribute IDs by code
    existing_map = {}
    if existing_attrs:
        for attr in existing_attrs:
            code = attr.get("attributeCode") or attr.get("code", "")
            existing_map[code] = attr.get("id")
    
    for def_attr in def_attributes:
        attr_code = def_attr.get("code", "")
        data_type = def_attr.get("dataType", "Text")
        values = def_attr.get("values") or []
        
        # Normalize dataType (lowercase 'text' for Text type)
        data_type = normalize_data_type(data_type)
        
        # Get valid value based on dataType
        if data_type == "SingleValueList":
            value = values[0] if values else "yes"
        elif data_type == "MultiValueList":
            value = [values[0]] if values else ["option1"]
        elif data_type == "Number":
            value = "0"
        else:  # text
            value = "automation test"
        
        attr_payload = {
            "attributeCode": attr_code,
            "tenantId": tenantId,
            "dataType": data_type,
            "value": value
        }
        
        # Add ID if exists (required for update)
        if attr_code in existing_map and existing_map[attr_code]:
            attr_payload["id"] = existing_map[attr_code]
        
        attributes.append(attr_payload)
    
    return attributes


def create_checklist(service_def_id, account_id, attributes, token, user_uuid, action="SAVE_AS_DRAFT"):
    """Create checklist response."""
    url = f"{BASE_URL}{CHECKLIST_CREATE_URL}"
    
    payload = {
        "Service": {
            "clientId": user_uuid,
            "serviceDefId": service_def_id,
            "accountId": account_id,
            "tenantId": tenantId,
            "attributes": attributes,
            "additionalFields": [{"action": action}]
        },
        "apiOperation": "CREATE",
        "RequestInfo": get_request_info(token)
    }
    
    return requests.post(url, json=payload, headers=get_headers(token))


def update_checklist(service_id, service_def_id, account_id, attributes, token, user_uuid, action="SUBMIT"):
    """Update checklist response."""
    url = f"{BASE_URL}{CHECKLIST_UPDATE_URL}"
    
    payload = {
        "Service": {
            "id": service_id,
            "clientId": user_uuid,
            "serviceDefId": service_def_id,
            "accountId": account_id,
            "tenantId": tenantId,
            "attributes": attributes,
            "additionalFields": [{"action": action}]
        },
        "apiOperation": "UPDATE",
        "RequestInfo": get_request_info(token)
    }
    
    return requests.post(url, json=payload, headers=get_headers(token))


def extract_service(data):
    """Extract service object from response."""
    services = data.get("Services") or data.get("Service") or data.get("service") or []
    if isinstance(services, list) and services:
        return services[0]
    elif isinstance(services, dict):
        return services
    return None


def create_and_submit_checklist_for_state(state, token, service, account_id, user_uuid):
    """Create and submit checklist for a specific state."""
    
    checklist = get_checklist_for_state(state)
    if not checklist:
        return {"success": False, "error": f"No checklist defined for state {state}"}
    
    name = checklist.get("name", "")
    code = f"{service}.{state}.{name}"
    
    print(f"\n🔍 Checklist: {code}")
    
    definition = search_checklist_definition(code, token)
    if not definition:
        return {"success": False, "error": f"Definition not found for {code}"}
    
    service_def_id = definition.get("id")
    print(f"   ✅ Definition ID: {service_def_id}")
    
    # Check if exists
    existing_service = search_checklist_service(service_def_id, account_id, token)
    
    if existing_service:
        service_id = existing_service.get("id")
        existing_attrs = existing_service.get("attributes") or []
        print(f"   ⚠️ Already exists: {service_id}")
        
        # Build update attributes with IDs
        update_attrs = build_attributes_from_definition(definition, existing_attrs)
        
        print(f"   📋 Update Attributes:")
        for attr in update_attrs:
            print(f"      - {attr['attributeCode']}: {attr['value']} ({attr['dataType']})")
        
        # Submit existing
        print(f"   🚀 Submitting existing checklist...")
        res = update_checklist(service_id, service_def_id, account_id, update_attrs, token, user_uuid, "SUBMIT")
        
        if res.status_code not in [200, 201, 202]:
            return {"success": False, "error": f"Submit failed: {res.text[:200]}"}
        
        print(f"   ✅ Submitted!")
        return {
            "success": True,
            "state": state,
            "code": code,
            "service_id": service_id,
            "service_def_id": service_def_id,
            "created": False
        }
    
    # Create new with SUBMIT action directly (like UI does)
    attributes = build_attributes_from_definition(definition)
    
    print(f"   📋 Attributes:")
    for attr in attributes:
        print(f"      - {attr['attributeCode']}: {attr['value']} ({attr['dataType']})")
    
    print(f"   🚀 Creating checklist with SUBMIT...")
    res = create_checklist(service_def_id, account_id, attributes, token, user_uuid, "SUBMIT")
    
    if res.status_code not in [200, 201, 202]:
        return {"success": False, "error": f"Create failed: {res.text[:200]}"}
    
    data = res.json()
    service_obj = extract_service(data)
    service_id = service_obj.get("id") if service_obj else None
    
    print(f"   ✅ Created & Submitted! ID: {service_id}")
    
    return {
        "success": True,
        "state": state,
        "code": code,
        "service_id": service_id,
        "service_def_id": service_def_id,
        "created": True
    }


def test_checklist_for_current_state(request):
    """
    Create and submit checklist for the CURRENT application state.
    Reads workflow_status from application_response.json and submits matching checklist.
    """
    token = get_token()
    mdms = load_json(MDMS_FILE)
    app_data = load_json(APP_FILE)
    
    module = mdms["module"]
    service = mdms["service"]
    account_id = app_data.get("application_id")
    current_state = app_data.get("workflow_status")
    
    req_info = get_request_info(token)
    user_uuid = req_info.get("userInfo", {}).get("uuid", "")
    
    print(f"\n📋 Module: {module}")
    print(f"📋 Service: {service}")
    print(f"📋 Account ID: {account_id}")
    print(f"📋 Current State: {current_state}")
    print(f"📋 User UUID: {user_uuid}")
    
    result = create_and_submit_checklist_for_state(current_state, token, service, account_id, user_uuid)
    
    if not result["success"]:
        print(f"\n❌ Failed: {result['error']}")
        if request:
            request.node._test_result = {
                "Module": module,
                "Service": service,
                "State": current_state,
                "Status": f"❌ {result['error'][:50]}"
            }
        assert False, result["error"]
    
    save_json({
        "module": module,
        "service": service,
        "state": current_state,
        "checklist_code": result["code"],
        "service_id": result["service_id"],
        "service_def_id": result["service_def_id"],
        "account_id": account_id,
        "status": "submitted"
    }, CHECKLIST_OUTPUT_FILE)
    
    if request:
        request.node._test_result = {
            "Module": module,
            "Service": service,
            "State": current_state,
            "Checklist Code": result["code"],
            "Service ID": result["service_id"],
            "Create": "✅ Created" if result["created"] else "⚠️ Existed",
            "Submit": "✅ Submitted"
        }
    
    return result


def test_checklist_create_all_and_submit(request):
    """Create and submit checklists for ALL states."""
    token = get_token()
    mdms = load_json(MDMS_FILE)
    app_data = load_json(APP_FILE)
    
    module = mdms["module"]
    service = mdms["service"]
    account_id = app_data.get("application_id")
    
    req_info = get_request_info(token)
    user_uuid = req_info.get("userInfo", {}).get("uuid", "")
    
    print(f"\n📋 Module: {module}")
    print(f"📋 Service: {service}")
    print(f"📋 Account ID: {account_id}")
    
    checklists = get_checklists_from_payload()
    
    results = []
    submitted_count = 0
    
    for checklist in checklists:
        name = checklist.get("name", "")
        state = checklist.get("state", "")
        
        if not name or not state:
            continue
        
        print(f"\n{'='*50}")
        print(f"📋 State: {state}")
        print(f"{'='*50}")
        
        result = create_and_submit_checklist_for_state(state, token, service, account_id, user_uuid)
        
        if result["success"]:
            submitted_count += 1
            results.append({
                "state": state,
                "submitted": True,
                "service_id": result["service_id"],
                "created": result["created"]
            })
        else:
            results.append({
                "state": state,
                "submitted": False,
                "error": result["error"]
            })
    
    print(f"\n{'='*50}")
    print(f"📊 Result: {submitted_count}/{len(checklists)} checklists submitted")
    print(f"{'='*50}")
    
    if request:
        status = "✅ All Submitted" if submitted_count == len(checklists) else f"⚠️ {submitted_count}/{len(checklists)}"
        report = {
            "Module": module,
            "Service": service,
            "Total": str(len(checklists)),
            "Submitted": str(submitted_count),
            "Status": status
        }
        for r in results:
            icon = "✅" if r.get("submitted") else "❌"
            value = r.get('service_id') or r.get('error') or 'N/A'
            report[r["state"]] = f"{icon} {str(value)[:30]}"
        
        request.node._test_result = report
    
    return {
        "module": module,
        "service": service,
        "total": len(checklists),
        "submitted": submitted_count,
        "results": results
    }