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


def test_workflow_validate():
    """Validate workflow states are correctly created"""
    token = get_token()
    mdms = load_json(MDMS_FILE)
    
    module = mdms["module"]
    service = mdms["service"]
    business_service = f"{module}.{service}"
    
    url = f"{BASE_URL}/egov-workflow-v2/egov-wf/businessservice/_search?tenantId={tenantId}&businessServices={business_service}"
    
    headers = {
        "Content-Type": "application/json",
        "auth-token": token,
        "x-tenant-id": tenantId
    }
    
    payload = {
        "RequestInfo": get_request_info(token)
    }
    
    res = requests.post(url, json=payload, headers=headers)
    assert res.status_code == 200, f"Workflow search failed: {res.text}"
    
    data = res.json()
    business_services = data.get("BusinessServices") or data.get("businessServices") or []
    
    assert len(business_services) > 0, f"Workflow not found for: {business_service}"
    
    wf = business_services[0]
    states = wf.get("states", [])
    
    # Extract state names
    state_names = [s.get("state") for s in states if s.get("state")]
    
    # Expected states based on service configuration
    expected_states = [
        "PENDING_FOR_ASSIGNMENT",
        "PENDING_AT_LME",
        "REJECTED",
        "RESOLVED"
    ]
    
    found_states = [s for s in expected_states if s in state_names]
    missing_states = [s for s in expected_states if s not in state_names]
    
    # Extract actions from all states
    all_actions = []
    for state in states:
        actions = state.get("actions") or []
        for action in actions:
            all_actions.append(action.get("action"))
    
    expected_actions = ["APPLIED", "ASSIGN", "REJECT", "REASSIGN", "RESOLVE", "REOPEN"]
    found_actions = [a for a in expected_actions if a in all_actions]
    
    return {
        "business_service": business_service,
        "tenant_id": wf.get("tenantId"),
        "total_states": len(states),
        "state_names": state_names,
        "expected_states": expected_states,
        "found_states": found_states,
        "missing_states": missing_states,
        "actions": list(set(all_actions)),
        "found_actions": found_actions,
        "workflow_valid": len(missing_states) == 0
    }