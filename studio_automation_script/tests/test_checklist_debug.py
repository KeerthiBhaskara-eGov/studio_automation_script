"""Debug checklist submission to find why UI doesn't show it."""
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
CHECKLIST_UPDATE_URL = "/health-service-request/service/v1/_update"


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


def test_checklist_debug_full(request):
    """Full debug output for checklist create and submit."""
    token = get_token()
    mdms = load_json(MDMS_FILE)
    app_data = load_json(APP_FILE)
    
    service = mdms["service"]
    account_id = app_data.get("application_id")
    current_state = app_data.get("workflow_status")
    
    req_info = get_request_info(token)
    user_uuid = req_info.get("userInfo", {}).get("uuid", "")
    
    print("\n" + "="*70)
    print("DEBUG: CHECKLIST SUBMISSION")
    print("="*70)
    
    print(f"\n📋 Service: {service}")
    print(f"📋 Account ID: {account_id}")
    print(f"📋 Current State: {current_state}")
    print(f"📋 User UUID: {user_uuid}")
    
    # Get checklist from payload
    payload_data = load_payload("mdms", "mdms_service_create.json")
    checklists = payload_data.get("Mdms", {}).get("data", {}).get("checklist", [])
    
    checklist = None
    for c in checklists:
        if c.get("state") == current_state:
            checklist = c
            break
    
    if not checklist:
        print(f"\n❌ No checklist found for state: {current_state}")
        return
    
    name = checklist.get("name", "")
    code = f"{service}.{current_state}.{name}"
    
    print(f"\n📋 Checklist Code: {code}")
    
    # Step 1: Search definition
    print("\n" + "-"*70)
    print("STEP 1: SEARCH DEFINITION")
    print("-"*70)
    
    def_url = f"{BASE_URL}{CHECKLIST_DEF_SEARCH_URL}"
    def_payload = {
        "ServiceDefinitionCriteria": {
            "code": [code],
            "tenantId": tenantId
        },
        "includeDeleted": True,
        "RequestInfo": req_info
    }
    
    res = requests.post(def_url, json=def_payload, headers=get_headers(token))
    print(f"\n📥 Response Status: {res.status_code}")
    
    data = res.json()
    definitions = data.get("ServiceDefinitions") or []
    
    if not definitions:
        print("❌ Definition not found!")
        return
    
    definition = definitions[0]
    service_def_id = definition.get("id")
    
    print(f"✅ Definition ID: {service_def_id}")
    print(f"\n📋 Definition Attributes:")
    for attr in definition.get("attributes") or []:
        print(f"   - Code: {attr.get('code')}")
        print(f"     DataType: {attr.get('dataType')}")
        print(f"     Values: {attr.get('values')}")
        print()
    
    # Step 2: Search existing service
    print("\n" + "-"*70)
    print("STEP 2: SEARCH EXISTING SERVICE")
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
    
    print(f"\n📤 Search Payload:")
    print(json.dumps(svc_payload, indent=2))
    
    res = requests.post(svc_url, json=svc_payload, headers=get_headers(token))
    print(f"\n📥 Response Status: {res.status_code}")
    print(f"📥 Response Body:")
    print(json.dumps(res.json(), indent=2)[:2000])
    
    data = res.json()
    services = data.get("Services") or data.get("Service") or []
    services = services if isinstance(services, list) else [services]
    
    existing_service = services[0] if services else None
    
    if existing_service:
        service_id = existing_service.get("id")
        existing_attrs = existing_service.get("attributes") or []
        print(f"\n⚠️ Service exists: {service_id}")
        print(f"📋 Existing Attributes:")
        for attr in existing_attrs:
            print(f"   - {attr.get('attributeCode')}: {attr.get('value')} (ID: {attr.get('id')})")
    else:
        print("\n📋 No existing service - need to create")
        
        # Step 3: Create
        print("\n" + "-"*70)
        print("STEP 3: CREATE CHECKLIST")
        print("-"*70)
        
        # Build attributes from definition
        attributes = []
        for attr in definition.get("attributes") or []:
            attr_code = attr.get("code", "")
            data_type = attr.get("dataType", "Text")
            values = attr.get("values") or []
            
            if data_type == "SingleValueList" and values:
                value = values[0]
            elif data_type == "Text":
                value = "automation test"
            else:
                value = "test"
            
            attributes.append({
                "attributeCode": attr_code,
                "tenantId": tenantId,
                "dataType": data_type,
                "value": value
            })
        
        create_payload = {
            "Service": {
                "clientId": user_uuid,
                "serviceDefId": service_def_id,
                "accountId": account_id,
                "tenantId": tenantId,
                "attributes": attributes,
                "additionalFields": [{"action": "SAVE_AS_DRAFT"}]
            },
            "apiOperation": "CREATE",
            "RequestInfo": req_info
        }
        
        print(f"\n📤 CREATE Payload:")
        print(json.dumps(create_payload, indent=2))
        
        create_url = f"{BASE_URL}{CHECKLIST_CREATE_URL}"
        res = requests.post(create_url, json=create_payload, headers=get_headers(token))
        
        print(f"\n📥 CREATE Response Status: {res.status_code}")
        print(f"📥 CREATE Response Body:")
        print(json.dumps(res.json(), indent=2)[:2000])
        
        if res.status_code not in [200, 201, 202]:
            print("❌ Create failed!")
            return
        
        data = res.json()
        services = data.get("Services") or data.get("Service") or []
        service_obj = services[0] if isinstance(services, list) and services else services
        service_id = service_obj.get("id")
        existing_attrs = service_obj.get("attributes") or []
        
        print(f"\n✅ Created! Service ID: {service_id}")
    
    # Step 4: Update/Submit
    print("\n" + "-"*70)
    print("STEP 4: SUBMIT CHECKLIST")
    print("-"*70)
    
    # Build update attributes with IDs
    update_attrs = []
    for attr in existing_attrs:
        attr_code = attr.get("attributeCode") or attr.get("code", "")
        data_type = attr.get("dataType", "Text")
        attr_id = attr.get("id", "")
        
        # Find valid value from definition
        def_attr = None
        for da in definition.get("attributes") or []:
            if da.get("code") == attr_code:
                def_attr = da
                break
        
        values = def_attr.get("values") if def_attr else []
        
        if data_type == "SingleValueList" and values:
            value = values[0]
        elif data_type == "Text":
            value = "automation submitted"
        else:
            value = attr.get("value", "test")
        
        update_attrs.append({
            "attributeCode": attr_code,
            "tenantId": tenantId,
            "id": attr_id,
            "dataType": data_type,
            "value": value
        })
    
    update_payload = {
        "Service": {
            "id": service_id,
            "clientId": user_uuid,
            "serviceDefId": service_def_id,
            "accountId": account_id,
            "tenantId": tenantId,
            "attributes": update_attrs,
            "additionalFields": [{"action": "SUBMIT"}]
        },
        "apiOperation": "UPDATE",
        "RequestInfo": req_info
    }
    
    print(f"\n📤 SUBMIT Payload:")
    print(json.dumps(update_payload, indent=2))
    
    update_url = f"{BASE_URL}{CHECKLIST_UPDATE_URL}"
    res = requests.post(update_url, json=update_payload, headers=get_headers(token))
    
    print(f"\n📥 SUBMIT Response Status: {res.status_code}")
    print(f"📥 SUBMIT Response Body:")
    print(json.dumps(res.json(), indent=2))
    
    # Step 5: Verify
    print("\n" + "-"*70)
    print("STEP 5: VERIFY SERVICE")
    print("-"*70)
    
    res = requests.post(svc_url, json=svc_payload, headers=get_headers(token))
    print(f"\n📥 Verify Response:")
    print(json.dumps(res.json(), indent=2)[:2000])
    
    print("\n" + "="*70)
    print("DEBUG COMPLETE")
    print("="*70)
    print("\n⚠️ Compare the SUBMIT payload above with the curl from UI!")
    print("Look for differences in:")
    print("   - attribute values")
    print("   - dataType casing (Text vs text)")
    print("   - any missing fields")