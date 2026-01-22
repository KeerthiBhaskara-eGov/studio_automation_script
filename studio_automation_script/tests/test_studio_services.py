import pytest
from utils.api_client import APIClient
from utils.data_loader import load_payload
from utils.auth import get_auth_token
from utils.request_info import get_request_info
from utils.config import tenantId
import random, string, json, os

# Output file paths
MDMS_DRAFT_FILE = "output/mdms_draft_response.json"
MDMS_FILE = "output/mdms_response.json"
SERVICE_FILE = "output/public_service_response.json"


# =============================================================================
# Utility Functions
# =============================================================================
def random_name(prefix):
    """Generate a random name with given prefix."""
    return f"{prefix}{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"

def save_json(data, path):
    """Save data to JSON file."""
    os.makedirs("output", exist_ok=True)
    json.dump(data, open(path, "w"), indent=2)

def load_json(path):
    """Load data from JSON file."""
    return json.load(open(path))

def replace_placeholders(payload, replacements):
    """Replace placeholders in payload with actual values."""
    payload_str = json.dumps(payload)
    for k, v in replacements.items():
        payload_str = payload_str.replace(k, str(v))
    return json.loads(payload_str)

def get_client():
    """Get authenticated API client."""
    token = get_auth_token("user")
    client = APIClient(token=token)
    client.headers["x-tenant-id"] = tenantId
    return token, client


# =============================================================================
# Helper Functions (used internally by tests)
# =============================================================================
def _mdms_draft_create():
    """Internal: Create MDMS draft."""
    token, client = get_client()
    module, service = random_name("Module"), random_name("Service")
    
    payload = load_payload("mdms", "mdms_draft_create.json")
    payload = replace_placeholders(payload, {
        "{{tenantId}}": tenantId,
        "{{module}}": module,
        "{{service}}": service,
        "{{businessService}}": f"{module}.{service}"
    })
    
    payload["RequestInfo"] = get_request_info(token)
    payload["Mdms"]["tenantId"] = tenantId
    payload["Mdms"]["schemaCode"] = "Studio.ServiceConfigurationDrafts"
    payload["Mdms"]["data"]["module"] = module
    payload["Mdms"]["data"]["service"] = service
    payload["Mdms"]["data"]["workflow"]["businessService"] = f"{module}.{service}"
    
    res = client.post("/egov-mdms-service/v2/_create/Studio.Checklists", payload)
    assert res.status_code in [200, 201, 202], f"MDMS Draft Create Failed: {res.text}"
    
    mdms = (res.json().get("Mdms") or res.json().get("mdms"))
    mdms = mdms[0] if isinstance(mdms, list) else mdms
    
    result = {
        "module": module, 
        "service": service, 
        "draft_id": mdms.get("id"),
        "schemaCode": "Studio.ServiceConfigurationDrafts",
        "status": "DRAFT"
    }
    save_json(result, MDMS_DRAFT_FILE)
    return result


def _mdms_service_create(module, service):
    """Internal: Publish MDMS service configuration."""
    token, client = get_client()
    
    payload = load_payload("mdms", "mdms_service_create.json")
    payload = replace_placeholders(payload, {
        "{{tenantId}}": tenantId,
        "{{module}}": module,
        "{{service}}": service,
        "{{businessService}}": f"{module}.{service}"
    })
    
    payload["RequestInfo"] = get_request_info(token)
    payload["Mdms"]["tenantId"] = tenantId
    payload["Mdms"]["schemaCode"] = "Studio.ServiceConfiguration"
    payload["Mdms"]["data"]["module"] = module
    payload["Mdms"]["data"]["service"] = service
    payload["Mdms"]["data"]["workflow"]["businessService"] = f"{module}.{service}"
    
    res = client.post("/egov-mdms-service/v2/_create/Studio.ServiceConfiguration", payload)
    assert res.status_code in [200, 201, 202], f"MDMS Service Create Failed: {res.text}"
    
    mdms = (res.json().get("Mdms") or res.json().get("mdms"))
    mdms = mdms[0] if isinstance(mdms, list) else mdms
    
    result = {
        "module": module, 
        "service": service, 
        "id": mdms.get("id"),
        "schemaCode": "Studio.ServiceConfiguration",
        "status": "PUBLISHED"
    }
    save_json(result, MDMS_FILE)
    return result


def _public_service_init(mdms):
    """Internal: Initialize public service."""
    token, client = get_client()
    module, service = mdms["module"], mdms["service"]
    
    payload = load_payload("public_service", "public_service_init.json")
    payload = replace_placeholders(payload, {
        "{{tenantId}}": tenantId,
        "{{module}}": module,
        "{{businessService}}": service
    })
    
    payload["RequestInfo"] = get_request_info(token)
    payload["service"]["tenantId"] = tenantId
    payload["service"]["businessService"] = service
    payload["service"]["module"] = module
    
    res = client.post("/public-service-init/v1/service", payload)
    assert res.status_code in [200, 201, 202], f"Public Service Init Failed: {res.text}"
    
    data = res.json()
    svc = data.get("Services") or data.get("services") or data.get("Service") or data.get("service") or data
    svc = svc[0] if isinstance(svc, list) else svc
    
    result = {
        "module": module, 
        "service": service, 
        "service_code": svc.get("serviceCode"),
        "id": svc.get("id"),
        "status": svc.get("status")
    }
    save_json(result, SERVICE_FILE)
    return result


# =============================================================================
# Tests
# =============================================================================
def test_mdms_draft_create(request):
    """Step 1: Create MDMS Draft"""
    result = _mdms_draft_create()
    
    request.node._test_result = {
        "Module": result["module"],
        "Service": result["service"],
        "Business Service": f"{result['module']}.{result['service']}",
        "Draft ID": result["draft_id"],
        "Schema Code": result["schemaCode"],
        "Status": "✅ Draft Created"
    }
    return result


def test_mdms_service_create(request):
    """Step 2: Publish MDMS Service Configuration"""
    try:
        draft = load_json(MDMS_DRAFT_FILE)
    except FileNotFoundError:
        draft = _mdms_draft_create()
    
    result = _mdms_service_create(draft["module"], draft["service"])
    
    request.node._test_result = {
        "Module": result["module"],
        "Service": result["service"],
        "Business Service": f"{result['module']}.{result['service']}",
        "MDMS ID": result["id"],
        "Schema Code": result["schemaCode"],
        "Status": "✅ Published"
    }
    return result


def test_public_service_init(request):
    """Step 3: Initialize Public Service"""
    mdms = load_json(MDMS_FILE)
    result = _public_service_init(mdms)
    
    request.node._test_result = {
        "Module": result["module"],
        "Service": result["service"],
        "Service Code": result["service_code"],
        "Service ID": result["id"],
        "Status": result["status"]
    }
    return result


def test_complete_studio_setup(request):
    """
    Complete Studio Setup Flow (All 3 steps):
    1. Create MDMS Draft
    2. Publish MDMS Service Configuration
    3. Initialize Public Service
    """
    # Step 1: Create Draft
    draft = _mdms_draft_create()
    
    # Step 2: Publish MDMS
    mdms = _mdms_service_create(draft["module"], draft["service"])
    
    # Step 3: Initialize Public Service
    svc = _public_service_init(mdms)
    
    request.node._test_result = {
        "Module": draft["module"],
        "Service": draft["service"],
        "Business Service": f"{draft['module']}.{draft['service']}",
        "Draft ID": draft["draft_id"],
        "MDMS ID": mdms["id"],
        "Service Code": svc["service_code"],
        "Service Status": svc["status"],
        "Complete Setup": "✅ Success"
    }
    
    return {
        "draft": draft,
        "mdms": mdms,
        "public_service": svc
    }