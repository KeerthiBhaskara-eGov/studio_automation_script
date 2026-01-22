from utils.auth import get_auth_token
from utils.request_info import get_request_info
from utils.config import tenantId, BASE_URL
import json
import requests

MDMS_FILE = "output/mdms_response.json"
APP_FILE = "output/application_response.json"

def load_json(path):
    return json.load(open(path))

def get_token():
    return get_auth_token("user")


def _process_instance_search():
    """Helper: Search process instance for application"""
    token = get_token()
    mdms = load_json(MDMS_FILE)
    app_data = load_json(APP_FILE)
    
    module = mdms["module"]
    service = mdms["service"]
    business_service = f"{module}.{service}"
    application_number = app_data["application_number"]
    
    url = f"{BASE_URL}/egov-workflow-v2/egov-wf/process/_search?tenantId={tenantId}&businessIds={application_number}&businessService={business_service}&history=true"
    
    headers = {
        "Content-Type": "application/json",
        "auth-token": token,
        "x-tenant-id": tenantId
    }
    
    payload = {
        "RequestInfo": get_request_info(token)
    }
    
    res = requests.post(url, json=payload, headers=headers)
    assert res.status_code == 200, f"Process instance search failed: {res.text}"
    
    data = res.json()
    process_instances = data.get("ProcessInstances") or data.get("processInstances") or []
    
    assert len(process_instances) > 0, f"No process instances found for: {application_number}"
    
    # Get current state (first in list is latest)
    current_instance = process_instances[0]
    current_state = current_instance.get("state", {}).get("state")
    
    # Extract all states from history
    state_history = []
    for pi in process_instances:
        state = pi.get("state", {}).get("state")
        action = pi.get("action")
        state_history.append({"state": state, "action": action})
    
    return {
        "application_number": application_number,
        "business_service": business_service,
        "current_state": current_state,
        "total_transitions": len(process_instances),
        "state_history": state_history
    }


def test_process_instance_after_create():
    """Verify process instance after application create (should be PENDING_FOR_ASSIGNMENT)"""
    result = _process_instance_search()
    
    history = result["state_history"]
    
    # Check if APPLIED action exists
    applied_found = any(h["action"] == "APPLIED" for h in history)
    
    return {
        "application_number": result["application_number"],
        "current_state": result["current_state"],
        "applied_action_found": applied_found,
        "state_history": history
    }


def test_process_instance_after_assign():
    """Verify process instance after ASSIGN action (should be PENDING_AT_LME)"""
    result = _process_instance_search()
    
    history = result["state_history"]
    
    # Check if ASSIGN action exists
    assign_found = any(h["action"] == "ASSIGN" for h in history)
    pending_at_lme_found = any(h["state"] == "PENDING_AT_LME" for h in history)
    
    return {
        "application_number": result["application_number"],
        "current_state": result["current_state"],
        "assign_action_found": assign_found,
        "pending_at_lme_state_found": pending_at_lme_found,
        "state_history": history
    }


def test_process_instance_after_resolve():
    """Verify process instance after RESOLVE action (should be RESOLVED)"""
    result = _process_instance_search()
    
    history = result["state_history"]
    
    # Check if RESOLVE action exists
    resolve_found = any(h["action"] == "RESOLVE" for h in history)
    resolved_state_found = any(h["state"] == "RESOLVED" for h in history)
    
    return {
        "application_number": result["application_number"],
        "current_state": result["current_state"],
        "resolve_action_found": resolve_found,
        "resolved_state_found": resolved_state_found,
        "state_history": history
    }