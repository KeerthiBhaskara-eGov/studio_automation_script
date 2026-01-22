"""
Test checklist with EXACT same payload structure as UI curl.
Compare our script vs UI to find the difference.
"""
import json
import requests
from utils.auth import get_auth_token
from utils.request_info import get_request_info
from utils.data_loader import load_payload
from utils.config import tenantId, BASE_URL

MDMS_FILE = "output/mdms_response.json"
APP_FILE = "output/application_response.json"

CHECKLIST_DEF_SEARCH_URL = "/health-service-request/service/definition/v1/_search"
CHECKLIST_SERVICE_SEARCH_URL = "/health-service-request/service/v1/_search"
CHECKLIST_CREATE_URL = "/health-service-request/service/v1/_create"


def load_json(path):
    return json.load(open(path))


def get_token():
    return get_auth_token("user")


def test_checklist_exact_ui_format(request):
    """
    Send EXACT same format as UI curl.
    """
    token = get_token()
    mdms = load_json(MDMS_FILE)
    app_data = load_json(APP_FILE)
    
    service = mdms["service"]
    account_id = app_data.get("application_id")
    current_state = app_data.get("workflow_status")
    
    req_info = get_request_info(token)
    user_uuid = req_info.get("userInfo", {}).get("uuid", "")
    user_info = req_info.get("userInfo", {})
    
    print("\n" + "="*70)
    print("EXACT UI FORMAT TEST")
    print("="*70)
    
    print(f"\n📋 Service: {service}")
    print(f"📋 Account ID: {account_id}")
    print(f"📋 Current State: {current_state}")
    print(f"📋 User UUID: {user_uuid}")
    
    # Get checklist definition
    payload_data = load_payload("mdms", "mdms_service_create.json")
    checklists = payload_data.get("Mdms", {}).get("data", {}).get("checklist", [])
    
    checklist = None
    for c in checklists:
        if c.get("state") == current_state:
            checklist = c
            break
    
    if not checklist:
        print(f"\n❌ No checklist for state: {current_state}")
        return
    
    name = checklist.get("name", "")
    code = f"{service}.{current_state}.{name}"
    
    # Search definition
    def_url = f"{BASE_URL}{CHECKLIST_DEF_SEARCH_URL}"
    def_payload = {
        "ServiceDefinitionCriteria": {
            "code": [code],
            "tenantId": tenantId
        },
        "includeDeleted": True,
        "RequestInfo": req_info
    }
    
    headers = {
        "Content-Type": "application/json",
        "auth-token": token,
        "x-tenant-id": tenantId
    }
    
    res = requests.post(def_url, json=def_payload, headers=headers)
    data = res.json()
    definitions = data.get("ServiceDefinitions") or []
    
    if not definitions:
        print("❌ Definition not found!")
        return
    
    definition = definitions[0]
    service_def_id = definition.get("id")
    def_attributes = definition.get("attributes") or []
    
    print(f"\n📋 Definition ID: {service_def_id}")
    
    # Build attributes EXACTLY like UI
    attributes = []
    for attr in def_attributes:
        attr_code = attr.get("code", "")
        data_type = attr.get("dataType", "Text")
        values = attr.get("values") or []
        
        # Normalize dataType like UI
        if data_type.lower() == "text":
            data_type = "text"
            value = "automation test"
        elif data_type == "SingleValueList":
            value = values[0] if values else "yes"
        elif data_type == "MultiValueList":
            value = [values[0]] if values else ["option1"]
        else:
            value = "0"
        
        attributes.append({
            "attributeCode": attr_code,
            "tenantId": tenantId,
            "dataType": data_type,
            "value": value
        })
    
    # Build EXACT UI payload format
    ui_payload = {
        "Service": {
            "clientId": user_uuid,
            "serviceDefId": service_def_id,
            "accountId": account_id,
            "tenantId": tenantId,
            "attributes": attributes,
            "additionalFields": [{"action": "SUBMIT"}]
        },
        "apiOperation": "CREATE",
        "RequestInfo": {
            "apiId": "Rainmaker",
            "authToken": token,
            "userInfo": user_info,
            "msgId": f"{int(__import__('time').time() * 1000)}|en_IN",
            "plainAccessRequest": {}
        }
    }
    
    print("\n" + "-"*70)
    print("📤 EXACT UI PAYLOAD:")
    print("-"*70)
    print(json.dumps(ui_payload, indent=2))
    
    # Send request
    create_url = f"{BASE_URL}{CHECKLIST_CREATE_URL}"
    
    print("\n" + "-"*70)
    print("📤 SENDING REQUEST...")
    print("-"*70)
    
    res = requests.post(create_url, json=ui_payload, headers=headers)
    
    print(f"\n📥 Response Status: {res.status_code}")
    print(f"📥 Response Body:")
    print(json.dumps(res.json(), indent=2))
    
    # Verify by searching
    print("\n" + "-"*70)
    print("🔍 VERIFYING - Search for checklist...")
    print("-"*70)
    
    svc_url = f"{BASE_URL}{CHECKLIST_SERVICE_SEARCH_URL}"
    svc_payload = {
        "ServiceCriteria": {
            "serviceDefIds": [service_def_id],
            "accountId": account_id,
            "tenantId": tenantId
        },
        "RequestInfo": req_info
    }
    
    res = requests.post(svc_url, json=svc_payload, headers=headers)
    data = res.json()
    
    print(f"\n📥 Search Response:")
    print(json.dumps(data, indent=2))
    
    services = data.get("Services") or []
    if services:
        svc = services[0]
        additional = svc.get("additionalFields") or []
        print(f"\n📋 Service ID: {svc.get('id')}")
        print(f"📋 additionalFields: {additional}")
        
        for field in additional:
            action = field.get("action")
            if action == "SUBMIT":
                print("\n✅ STATUS IS SUBMIT!")
            else:
                print(f"\n⚠️ STATUS IS: {action}")
    
    print("\n" + "="*70)
    print("COMPARE WITH UI CURL")
    print("="*70)
    print("""
UI Curl had:
- clientId: user's uuid
- serviceDefId: definition id  
- accountId: application id
- attributes with dataType: "text" (lowercase) and "SingleValueList"
- additionalFields: [{"action": "SUBMIT"}]
- apiOperation: "CREATE"
- RequestInfo with plainAccessRequest: {}

Check if our payload matches!
""")