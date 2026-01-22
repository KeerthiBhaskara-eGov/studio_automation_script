import pytest
from utils.api_client import APIClient
from utils.data_loader import load_payload
from utils.auth import get_auth_token
from utils.request_info import get_request_info
from utils.config import tenantId
import time, json, os

MDMS_FILE = "output/mdms_response.json"
SERVICE_FILE = "output/public_service_response.json"
APP_FILE = "output/application_response.json"

def save_json(data, path):
    os.makedirs("output", exist_ok=True)
    json.dump(data, open(path, "w"), indent=2)

def load_json(path):
    return json.load(open(path))

def get_client():
    token = get_auth_token("user")
    client = APIClient(token=token)
    client.headers["x-tenant-id"] = tenantId
    return token, client


def test_application_create(request):
    token, client = get_client()
    mdms, svc = load_json(MDMS_FILE), load_json(SERVICE_FILE)
    module, service, service_code = mdms["module"], mdms["service"], svc["service_code"]
    
    payload = load_payload("Application", "create_application.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["Application"]["tenantId"] = tenantId
    payload["Application"]["module"] = module
    payload["Application"]["businessService"] = service
    payload["Application"]["serviceCode"] = service_code
    payload["Application"]["Workflow"]["businessService"] = f"{module}.{service}"
    
    # Also update address tenantId
    if "address" in payload["Application"]:
        payload["Application"]["address"]["tenantId"] = tenantId
    
    res = client.post(f"/public-service/v1/application/{service_code}", payload)
    assert res.status_code in [200, 201, 202], f"Failed: {res.text}"
    
    app = res.json().get("Application") or res.json().get("application")
    app = app[0] if isinstance(app, list) else app
    audit = app.get("auditDetails", {})
    
    # Extract applicant details including mobile number
    applicants = app.get("applicants") or []
    applicant = applicants[0] if applicants else {}
    
    # Get mobile number from applicant (can be int or string)
    mobile_number = (
        applicant.get("mobileNumber") or 
        applicant.get("mobilenumber") or 
        applicant.get("mobile")
    )
    # Convert to string if it's an integer
    if mobile_number is not None:
        mobile_number = str(mobile_number)
    
    result = {
        "module": module, 
        "service": service, 
        "service_code": service_code,
        "application_id": app.get("id"), 
        "application_number": app.get("applicationNumber"),
        "workflow_status": app.get("workflowStatus"),
        "status": app.get("status"),
        "applicant_id": applicant.get("id"), 
        "user_id": applicant.get("userId"),
        "mobile_number": mobile_number,  # Store mobile number as string
        "address_id": (app.get("address") or {}).get("id"),
        "created_by": audit.get("createdBy"), 
        "last_modified_by": audit.get("lastModifiedBy"),
        "created_time": audit.get("createdTime"), 
        "last_modified_time": audit.get("lastModifiedTime")
    }
    save_json(result, APP_FILE)
    
    # Store for HTML report
    if request:
        request.node._test_result = {
            "Module": module,
            "Service": service,
            "Service Code": service_code,
            "Application Number": app.get("applicationNumber"),
            "Mobile Number": mobile_number,
            "Workflow Status": app.get("workflowStatus") or "PENDING_FOR_ASSIGNMENT"
        }
    
    return result


def _update_application(action, request=None):
    token, client = get_client()
    mdms, app_data = load_json(MDMS_FILE), load_json(APP_FILE)
    module, service = mdms["module"], mdms["service"]
    
    payload = load_payload("Application", "update_application.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["Application"]["id"] = app_data["application_id"]
    payload["Application"]["tenantId"] = tenantId
    payload["Application"]["module"] = module
    payload["Application"]["businessService"] = service
    payload["Application"]["applicationNumber"] = app_data["application_number"]
    payload["Application"]["serviceCode"] = app_data["service_code"]
    
    if "Workflow" in payload["Application"]:
        payload["Application"]["Workflow"]["action"] = action
        payload["Application"]["Workflow"]["businessService"] = f"{module}.{service}"
    elif "workflow" in payload["Application"]:
        payload["Application"]["workflow"]["action"] = action
        payload["Application"]["workflow"]["businessService"] = f"{module}.{service}"
    
    payload["Application"]["applicants"][0]["id"] = app_data["applicant_id"]
    payload["Application"]["applicants"][0]["userId"] = app_data["user_id"] or ""
    
    if "address" in payload["Application"]:
        payload["Application"]["address"]["id"] = app_data["address_id"]
        payload["Application"]["address"]["tenantId"] = tenantId
    
    payload["Application"]["auditDetails"]["createdBy"] = app_data["created_by"]
    payload["Application"]["auditDetails"]["lastModifiedBy"] = app_data["last_modified_by"]
    payload["Application"]["auditDetails"]["createdTime"] = app_data["created_time"] or int(time.time()*1000)
    payload["Application"]["auditDetails"]["lastModifiedTime"] = app_data["last_modified_time"] or int(time.time()*1000)
    
    res = client.put(f"/public-service/v1/application/{app_data['service_code']}", payload)
    assert res.status_code in [200, 201, 202], f"Failed: {res.text}"
    
    app = res.json().get("Application") or res.json().get("application")
    app = app[0] if isinstance(app, list) else app
    
    audit = app.get("auditDetails", {})
    app_data["last_modified_by"] = audit.get("lastModifiedBy")
    app_data["last_modified_time"] = audit.get("lastModifiedTime")
    save_json(app_data, APP_FILE)
    
    result = {"application_number": app.get("applicationNumber"), "action": action, "status": app.get("workflowStatus")}
    
    # Store for HTML report
    if request:
        request.node._test_result = {
            "Application Number": app.get("applicationNumber"),
            "Action": action,
            "New Status": app.get("workflowStatus"),
            "Module": module,
            "Service": service
        }
    
    return result


def test_application_assign(request):
    return _update_application("ASSIGN", request)

def test_application_resolve(request):
    return _update_application("RESOLVE", request)

def test_complete_application_flow(request):
    """Complete flow: Create -> Assign -> Resolve"""
    create = test_application_create(request)
    assign = _update_application("ASSIGN")
    resolve = _update_application("RESOLVE")
    
    # Store for HTML report
    if request:
        request.node._test_result = {
            "Application Number": create["application_number"],
            "Module": create["module"],
            "Service": create["service"],
            "Service Code": create["service_code"],
            "Mobile Number": create.get("mobile_number"),
            "Create → Status": "PENDING_FOR_ASSIGNMENT",
            "Assign → Status": assign["status"],
            "Resolve → Status": resolve["status"],
            "Flow Complete": "✅ Yes" if resolve["status"] == "RESOLVED" else "❌ No"
        }
    
    return {"create": create, "assign": assign, "resolve": resolve}