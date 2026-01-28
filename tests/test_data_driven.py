"""
Data-Driven Negative Tests
Reads scenarios from test_scenarios_config.json and runs them automatically.
"""
import pytest
import json
import requests
from utils.auth import get_auth_token
from utils.request_info import get_request_info
from utils.data_loader import load_payload
from utils.config import tenantId, BASE_URL

SCENARIOS_FILE = "test_scenarios_config.json"
MDMS_FILE = "output/mdms_response.json"
APP_FILE = "output/application_response.json"


def load_json(path):
    try:
        return json.load(open(path))
    except FileNotFoundError:
        return {}


def load_scenarios():
    return load_json(SCENARIOS_FILE)


def get_token():
    return get_auth_token("user")


def get_headers(token):
    return {
        "Content-Type": "application/json",
        "auth-token": token,
        "x-tenant-id": tenantId
    }


def get_mdms_headers(token):
    """Headers for MDMS create endpoints - requires Authorization Bearer format"""
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "x-tenant-id": tenantId
    }


def expand_placeholder(value):
    """Expand placeholders like {{REPEAT_A_1000}}"""
    if isinstance(value, str):
        if value == "{{REPEAT_A_1000}}":
            return "A" * 1000
        elif value == "{{REPEAT_A_10000}}":
            return "A" * 10000
    return value


def is_rejected(res, expected_status=None):
    """Check if request was properly rejected."""
    if expected_status:
        if isinstance(expected_status, list):
            return res.status_code in expected_status
        return res.status_code == expected_status
    return res.status_code >= 400 or "error" in res.text.lower()


def print_result(passed, total, bugs):
    """Print test result summary."""
    print(f"\n📊 RESULT: {passed}/{total} passed")
    if bugs:
        print(f"\n🐛 BUGS FOUND ({len(bugs)}):")
        for bug in bugs:
            print(f"   - {bug}")


# =============================================================================
# MDMS DRAFT NEGATIVE TESTS
# =============================================================================
class TestMDMSDraftNegative:
    """Test MDMS Draft creation failure scenarios."""
    
    def test_mdms_draft_scenarios(self, request):
        """Run all MDMS draft negative scenarios."""
        scenarios = load_scenarios().get("mdms_draft_scenarios", [])
        if not scenarios:
            pytest.skip("No MDMS draft scenarios")
        
        token = get_token()
        url = f"{BASE_URL}/egov-mdms-service/v2/_create/Studio.Checklists?tenantId={tenantId}"
        
        results = []
        passed = 0
        bugs = []
        
        print(f"\n{'='*60}")
        print(f"📝 MDMS DRAFT NEGATIVE TESTS ({len(scenarios)} scenarios)")
        print(f"{'='*60}")
        
        for scenario in scenarios:
            name = scenario.get("name")
            data = scenario.get("data", {})
            expected = scenario.get("expected", {})
            test_type = scenario.get("type", "negative")
            
            print(f"\n📋 {name}")
            
            # Handle special cases
            if data.get("_empty_body"):
                payload = {}
            elif data.get("_no_request_info"):
                payload = {
                    "Mdms": {
                        "tenantId": data.get("tenant_id", tenantId),
                        "schemaCode": data.get("schema_code", "Studio.ServiceConfigurationDrafts"),
                        "uniqueIdentifier": f"test-draft-{name[:10]}",
                        "data": {"module": data.get("module"), "service": data.get("service")}
                    }
                }
            else:
                module = expand_placeholder(data.get("module", "TestModule"))
                service = expand_placeholder(data.get("service", "TestService"))
                
                payload = {
                    "Mdms": {
                        "tenantId": data.get("tenant_id", tenantId),
                        "schemaCode": data.get("schema_code", "Studio.ServiceConfigurationDrafts"),
                        "uniqueIdentifier": data.get("unique_id", f"test-draft-{name[:10]}"),
                        "data": {
                            "module": module,
                            "service": service,
                            "workflow": data.get("workflow", [{"state": "TEST", "actions": ["APPLY"]}])
                        },
                        "isActive": True
                    },
                    "RequestInfo": get_request_info(token)
                }
                
                # Handle missing data object
                if data.get("_no_data"):
                    del payload["Mdms"]["data"]
            
            res = requests.post(url, json=payload, headers=get_mdms_headers(token))
            
            if test_type == "security":
                is_safe = res.status_code in [400, 403, 422] or "<script>" not in res.text
                if is_safe:
                    print(f"   ✅ Safe ({res.status_code})")
                    passed += 1
                else:
                    print(f"   ⚠️ Check response ({res.status_code})")
                    bugs.append(name)
            elif test_type == "boundary":
                print(f"   ℹ️ Observed: {res.status_code}")
                passed += 1
            else:
                rejected = is_rejected(res, expected.get("status"))
                if rejected:
                    print(f"   ✅ Correctly rejected ({res.status_code})")
                    passed += 1
                else:
                    print(f"   ❌ BUG! Should reject but got {res.status_code}")
                    bugs.append(name)
            
            results.append({"name": name, "status": res.status_code})
        
        print_result(passed, len(scenarios), bugs)
        
        if request:
            request.node._test_result = {"Total": len(scenarios), "Passed": passed, "Bugs": len(bugs)}


# =============================================================================
# MDMS SERVICE CREATE NEGATIVE TESTS
# =============================================================================
class TestMDMSServiceCreateNegative:
    """Test MDMS Service Create failure scenarios."""
    
    def test_mdms_service_create_scenarios(self, request):
        """Run all MDMS service create negative scenarios."""
        scenarios = load_scenarios().get("mdms_service_create_scenarios", [])
        if not scenarios:
            pytest.skip("No MDMS service create scenarios")
        
        mdms = load_json(MDMS_FILE)
        token = get_token()
        url = f"{BASE_URL}/egov-mdms-service/v2/_create/Studio.Checklists?tenantId={tenantId}"
        
        results = []
        passed = 0
        bugs = []
        
        print(f"\n{'='*60}")
        print(f"📝 MDMS SERVICE CREATE NEGATIVE TESTS ({len(scenarios)} scenarios)")
        print(f"{'='*60}")
        
        for scenario in scenarios:
            name = scenario.get("name")
            data = scenario.get("data", {})
            expected = scenario.get("expected", {})
            test_type = scenario.get("type", "negative")
            
            print(f"\n📋 {name}")
            
            if data.get("_empty_body"):
                payload = {}
            elif data.get("_no_request_info"):
                payload = {
                    "Mdms": {
                        "tenantId": tenantId,
                        "schemaCode": "Studio.ServiceConfigurationDrafts",
                        "uniqueIdentifier": f"test-svc-{name[:10]}",
                        "data": {}
                    }
                }
            else:
                module = expand_placeholder(data.get("module", "TestModule"))
                service = expand_placeholder(data.get("service", "TestService"))
                
                # Replace placeholder for existing service code
                service_code = data.get("service_code")
                if service_code == "{{existing_service_code}}":
                    service_code = mdms.get("service_code", "existing-svc")
                
                mdms_data = {
                    "module": module,
                    "service": service
                }
                
                # Add workflow if specified
                if "workflow" in data:
                    mdms_data["workflow"] = data["workflow"]
                else:
                    mdms_data["workflow"] = [
                        {"state": "PENDING_FOR_ASSIGNMENT", "actions": ["ASSIGN", "REJECT"]},
                        {"state": "PENDING_AT_LME", "actions": ["RESOLVE"]},
                        {"state": "RESOLVED", "actions": []}
                    ]
                
                # Add checklist if specified
                if "checklist" in data:
                    mdms_data["checklist"] = data["checklist"]
                else:
                    mdms_data["checklist"] = [{"name": "Test Checklist", "state": "PENDING_FOR_ASSIGNMENT"}]
                
                # Add roleactions if specified
                if "roleactions" in data:
                    mdms_data["roleactions"] = data["roleactions"]
                else:
                    mdms_data["roleactions"] = [{"role": "EMPLOYEE", "actions": ["VIEW"]}]
                
                # Add idgen if specified
                if "idgen" in data:
                    mdms_data["idgen"] = data["idgen"]
                else:
                    mdms_data["idgen"] = [{"idname": "test.id", "format": "TEST-[cy:yyyy-MM-dd]-[SEQ]"}]
                
                # Add localization if specified
                if "localization" in data:
                    mdms_data["localization"] = data["localization"]
                else:
                    mdms_data["localization"] = [{"code": "TEST_CODE", "message": "Test Message"}]
                
                payload = {
                    "Mdms": {
                        "tenantId": data.get("tenant_id", tenantId),
                        "schemaCode": "Studio.ServiceConfigurationDrafts",
                        "uniqueIdentifier": service_code or f"test-svc-{name[:10]}",
                        "data": mdms_data,
                        "isActive": True
                    },
                    "RequestInfo": get_request_info(token)
                }
            
            res = requests.post(url, json=payload, headers=get_mdms_headers(token))
            
            if test_type == "security":
                is_safe = res.status_code in [400, 403, 422] or "<script>" not in res.text
                if is_safe:
                    print(f"   ✅ Safe ({res.status_code})")
                    passed += 1
                else:
                    print(f"   ⚠️ Check response ({res.status_code})")
                    bugs.append(name)
            else:
                rejected = is_rejected(res, expected.get("status"))
                if rejected:
                    print(f"   ✅ Correctly rejected ({res.status_code})")
                    passed += 1
                else:
                    print(f"   ❌ BUG! Should reject but got {res.status_code}")
                    bugs.append(name)
            
            results.append({"name": name, "status": res.status_code})
        
        print_result(passed, len(scenarios), bugs)
        
        if request:
            request.node._test_result = {"Total": len(scenarios), "Passed": passed, "Bugs": len(bugs)}


# =============================================================================
# PUBLIC SERVICE INIT NEGATIVE TESTS
# =============================================================================
class TestPublicServiceInitNegative:
    """Test Public Service Init failure scenarios."""
    
    def test_public_service_init_scenarios(self, request):
        """Run all public service init negative scenarios."""
        scenarios = load_scenarios().get("public_service_init_scenarios", [])
        if not scenarios:
            pytest.skip("No public service init scenarios")
        
        mdms = load_json(MDMS_FILE)
        token = get_token()
        url = f"{BASE_URL}/public-service-init/v1/service"
        
        results = []
        passed = 0
        bugs = []
        
        print(f"\n{'='*60}")
        print(f"🚀 PUBLIC SERVICE INIT NEGATIVE TESTS ({len(scenarios)} scenarios)")
        print(f"{'='*60}")
        
        for scenario in scenarios:
            name = scenario.get("name")
            data = scenario.get("data", {})
            expected = scenario.get("expected", {})
            test_type = scenario.get("type", "negative")
            
            print(f"\n📋 {name}")
            
            if data.get("_empty_body"):
                payload = {}
            elif data.get("_no_request_info"):
                module = data.get("module", "TestModule")
                service = data.get("service", "TestService")

                # Replace placeholders
                if module == "{{existing_module}}":
                    module = mdms.get("module", "TestModule")
                if service == "{{existing_service}}":
                    service = mdms.get("service", "TestService")

                module = expand_placeholder(module)
                service = expand_placeholder(service)

                payload = {
                    "service": {
                        "module": module,
                        "businessService": service,
                        "tenantId": data.get("tenant_id", tenantId),
                        "status": "ACTIVE",
                        "additionalDetails": {
                            "note": "test automation"
                        }
                    }
                }
            else:
                # Get module and service from data
                module = data.get("module", "TestModule")
                service = data.get("service", "TestService")

                # Replace placeholders with existing MDMS data
                if module == "{{existing_module}}":
                    module = mdms.get("module", "TestModule")
                if service == "{{existing_service}}":
                    service = mdms.get("service", "TestService")

                # Expand special placeholders like {{REPEAT_A_1000}}
                module = expand_placeholder(module)
                service = expand_placeholder(service)

                # Handle auth token scenarios
                auth_token = data.get("auth_token")
                if auth_token is None and "auth_token" in data:
                    # Explicitly null token
                    req_info = get_request_info(token)
                    req_info["authToken"] = None
                elif auth_token:
                    req_info = get_request_info(token)
                    req_info["authToken"] = auth_token
                else:
                    req_info = get_request_info(token)

                payload = {
                    "RequestInfo": req_info,
                    "service": {
                        "module": module,
                        "businessService": service,
                        "tenantId": data.get("tenant_id", tenantId),
                        "status": "ACTIVE",
                        "additionalDetails": {
                            "note": "test automation"
                        }
                    }
                }
            
            # Handle custom headers for auth tests
            headers = get_headers(token)
            if data.get("auth_token") == "invalid-token":
                headers["auth-token"] = "invalid-token"
            elif data.get("auth_token") is None and "auth_token" in data:
                headers.pop("auth-token", None)

            res = requests.post(url, json=payload, headers=headers)
            
            if test_type == "security":
                is_safe = res.status_code in [400, 403, 404, 422] or "<script>" not in res.text
                if is_safe:
                    print(f"   ✅ Safe ({res.status_code})")
                    passed += 1
                else:
                    print(f"   ⚠️ Check response ({res.status_code})")
                    bugs.append(name)
            elif test_type == "boundary":
                print(f"   ℹ️ Observed: {res.status_code}")
                passed += 1
            else:
                rejected = is_rejected(res, expected.get("status"))
                if rejected:
                    print(f"   ✅ Correctly rejected ({res.status_code})")
                    passed += 1
                else:
                    print(f"   ❌ BUG! Should reject but got {res.status_code}")
                    bugs.append(name)
            
            results.append({"name": name, "status": res.status_code})
        
        print_result(passed, len(scenarios), bugs)
        
        if request:
            request.node._test_result = {"Total": len(scenarios), "Passed": passed, "Bugs": len(bugs)}


# =============================================================================
# AUTHENTICATION TESTS
# =============================================================================
class TestAuthenticationNegative:
    """Test authentication failure scenarios."""
    
    def test_authentication_scenarios(self, request):
        """Run all authentication negative scenarios."""
        scenarios = load_scenarios().get("authentication_scenarios", [])
        if not scenarios:
            pytest.skip("No authentication scenarios")
        
        url = f"{BASE_URL}/egov-mdms-service/v2/_search/Studio.Checklists?tenantId={tenantId}"
        results = []
        passed = 0
        bugs = []
        
        print(f"\n{'='*60}")
        print(f"🔐 AUTHENTICATION NEGATIVE TESTS ({len(scenarios)} scenarios)")
        print(f"{'='*60}")
        
        for scenario in scenarios:
            name = scenario.get("name")
            data = scenario.get("data", {})
            expected = scenario.get("expected", {})
            
            print(f"\n📋 {name}")
            
            auth_token = data.get("auth_token")
            
            headers = {"Content-Type": "application/json", "x-tenant-id": tenantId}
            if auth_token:
                headers["auth-token"] = auth_token
            
            payload = {
                "MdmsCriteria": {"tenantId": tenantId, "schemaCode": "Studio.ServiceConfigurationDrafts"},
                "RequestInfo": {"apiId": "Rainmaker", "authToken": auth_token}
            }
            
            res = requests.post(url, json=payload, headers=headers)
            
            rejected = is_rejected(res, expected.get("status"))
            
            if rejected:
                print(f"   ✅ Correctly rejected ({res.status_code})")
                passed += 1
            else:
                print(f"   ❌ Should reject! Got {res.status_code}")
                bugs.append(name)
            
            results.append({"name": name, "passed": rejected, "status": res.status_code})
        
        print_result(passed, len(scenarios), bugs)
        
        if request:
            request.node._test_result = {"Total": len(scenarios), "Passed": passed, "Bugs": len(bugs)}


# =============================================================================
# APPLICATION TESTS
# =============================================================================
class TestApplicationNegative:
    """Test application creation failure scenarios."""
    
    def test_application_scenarios(self, request):
        """Run all application negative scenarios."""
        scenarios = load_scenarios().get("application_scenarios", [])
        if not scenarios:
            pytest.skip("No application scenarios")
        
        mdms = load_json(MDMS_FILE)
        if not mdms.get("module") or not mdms.get("service"):
            pytest.skip("No MDMS data - run service setup first")

        # Load application data to get the actual service_code
        app_data = load_json(APP_FILE)
        if not app_data.get("service_code"):
            pytest.skip("No application data - run application creation first")

        service_code = app_data.get("service_code")

        token = get_token()
        url = f"{BASE_URL}/public-service/v1/application/{service_code}"
        
        results = []
        passed = 0
        bugs = []
        
        print(f"\n{'='*60}")
        print(f"📝 APPLICATION NEGATIVE TESTS ({len(scenarios)} scenarios)")
        print(f"{'='*60}")
        
        for scenario in scenarios:
            name = scenario.get("name")
            data = scenario.get("data", {})
            expected = scenario.get("expected", {})

            print(f"\n📋 {name}")

            if data.get("_empty_body"):
                payload = {}
            else:
                # Prepare applicant name
                applicant_name = expand_placeholder(data.get("name", "Test User"))

                # Prepare mobile number - keep as integer if it's an integer, otherwise string
                # If "mobile" key exists in data, use its value (even if None/null)
                # Otherwise, use a default valid mobile
                if "mobile" in data:
                    mobile_value = data["mobile"]  # Keep original type: int, str, or None
                else:
                    mobile_value = "9876543210"  # Default valid mobile

                # Handle service code - replace placeholder with invalid but similar format
                test_service_code = data.get("service_code", service_code)
                if test_service_code == "{{service_code_invalid}}":
                    # Modify the actual service code slightly (insert "kjhg" before the last part)
                    # e.g., "xxx-2026-01-22-022001" -> "xxx-2026-01-22-0kjhg22001"
                    if "-0" in service_code:
                        test_service_code = service_code.replace("-0", "-0kjhg", 1)
                    else:
                        test_service_code = service_code + "-invalid"

                payload = {
                    "Application": {
                        "tenantId": data.get("tenant_id", tenantId),
                        "module": mdms.get("module", "TestModule"),
                        "businessService": mdms.get("service", "TestService"),
                        "serviceCode": test_service_code,
                        "status": "ACTIVE",
                        "channel": "counter",
                        "reference": None,
                        "workflowStatus": "applied",
                        "serviceDetails": {},
                        "applicants": [
                            {
                                "type": "individual",
                                "active": True,
                                "prefix": "91",
                                "additionalFields": {
                                    "schema": None,
                                    "version": None,
                                    "fields": [
                                        {
                                            "key": "email",
                                            "value": data.get("email", "test@example.com")
                                        }
                                    ]
                                },
                                "name": applicant_name if applicant_name else None,
                                "mobileNumber": mobile_value,
                                "emailId": data.get("email", "test@example.com")
                            }
                        ],
                        "address": {
                            "tenantId": data.get("tenant_id", tenantId),
                            "latitude": 0,
                            "longitude": 0,
                            "addressNumber": "1",
                            "addressLine1": "",
                            "addressLine2": "",
                            "landmark": "",
                            "city": "",
                            "pincode": "",
                            "hierarchyType": "ADMIN",
                            "boundarylevel": "VILLAGE",
                            "additionalFields": {
                                "schema": None,
                                "version": None,
                                "fields": []
                            }
                        },
                        "documents": [],
                        "additionalDetails": {
                            "ref1": "val1"
                        },
                        "Workflow": {
                            "action": "APPLIED",
                            "comment": "",
                            "assignees": [],
                            "businessService": f"{mdms.get('module', 'TestModule')}.{mdms.get('service', 'TestService')}"
                        }
                    },
                    "RequestInfo": get_request_info(token)
                }

            res = requests.post(url, json=payload, headers=get_headers(token))
            
            rejected = is_rejected(res, expected.get("status"))
            
            if rejected:
                print(f"   ✅ Correctly rejected ({res.status_code})")
                passed += 1
            else:
                print(f"   ❌ BUG! Should reject but got {res.status_code}")
                bugs.append(name)
            
            results.append({"name": name, "passed": rejected, "status": res.status_code})
        
        print_result(passed, len(scenarios), bugs)
        
        if request:
            request.node._test_result = {"Total": len(scenarios), "Passed": passed, "Bugs": len(bugs)}


# =============================================================================
# WORKFLOW TESTS
# =============================================================================
class TestWorkflowNegative:
    """Test workflow transition failure scenarios."""
    
    def test_workflow_scenarios(self, request):
        """Run all workflow negative scenarios."""
        scenarios = load_scenarios().get("workflow_scenarios", [])
        if not scenarios:
            pytest.skip("No workflow scenarios")
        
        app_data = load_json(APP_FILE)
        if not app_data.get("application_number") or not app_data.get("service_code"):
            pytest.skip("No application - run application tests first")

        token = get_token()
        service_code = app_data.get("service_code")

        # First, fetch the full application details using GET with query params
        search_url = f"{BASE_URL}/public-service/v1/application/{service_code}"
        search_params = {
            "tenantId": tenantId,
            "applicationNumber": app_data.get("application_number"),
            "limit": 10,
            "offset": 0
        }
        search_res = requests.get(search_url, params=search_params, headers=get_headers(token))

        if search_res.status_code != 200:
            pytest.skip(f"Could not fetch application details: {search_res.status_code}")

        response_data = search_res.json()

        # Debug: print response type and structure
        print(f"   🔍 Response type: {type(response_data)}")
        if isinstance(response_data, dict):
            print(f"   🔍 Response keys: {list(response_data.keys())}")
        elif isinstance(response_data, list):
            print(f"   🔍 Response is a list with {len(response_data)} items")

        # GET endpoint may return: direct array, wrapped object, or keyed array
        if isinstance(response_data, list):
            # Direct array response
            if not response_data:
                pytest.skip("Application not found in search")
            full_application = response_data[0]
        elif isinstance(response_data, dict) and ("application" in response_data or "Application" in response_data):
            app_value = response_data.get("Application") or response_data.get("application")
            print(f"   🔍 Application value type: {type(app_value)}")
            # Check if it's an array or single object
            if isinstance(app_value, list):
                if not app_value:
                    pytest.skip("Application not found in search")
                full_application = app_value[0]
            else:
                full_application = app_value
        elif isinstance(response_data, dict) and response_data.get("id"):
            # Direct application object
            full_application = response_data
        else:
            # Try array format (Applications/applications)
            applications = response_data.get("Applications") or response_data.get("applications") or []
            if not applications:
                print(f"   ⚠️ Unexpected response format")
                pytest.skip("Application not found in search")
            full_application = applications[0]

        results = []
        passed = 0
        bugs = []

        print(f"\n{'='*60}")
        print(f"🔄 WORKFLOW NEGATIVE TESTS ({len(scenarios)} scenarios)")
        print(f"{'='*60}")

        for scenario in scenarios:
            name = scenario.get("name")
            action = scenario.get("action")
            app_number = scenario.get("application_number", app_data.get("application_number"))
            expected = scenario.get("expected", {})

            print(f"\n📋 {name}")

            # Use the correct PUT endpoint with service code
            url = f"{BASE_URL}/public-service/v1/application/{service_code}"

            # Clone the full application object
            application_update = full_application.copy()

            # Override application number if specified in scenario
            if "application_number" in scenario:
                application_update["applicationNumber"] = app_number

            # Set the workflow action
            application_update["workflow"] = {
                "action": action,
                "businessService": f"{full_application.get('module')}.{full_application.get('businessService')}"
            }

            payload = {
                "Application": application_update,
                "RequestInfo": get_request_info(token)
            }

            res = requests.put(url, json=payload, headers=get_headers(token))
            
            rejected = is_rejected(res, expected.get("status"))
            
            if rejected:
                print(f"   ✅ Correctly rejected ({res.status_code})")
                passed += 1
            else:
                print(f"   ❌ BUG! Should reject but got {res.status_code}")
                bugs.append(name)
            
            results.append({"name": name, "passed": rejected, "status": res.status_code})
        
        print_result(passed, len(scenarios), bugs)
        
        if request:
            request.node._test_result = {"Total": len(scenarios), "Passed": passed, "Bugs": len(bugs)}


# =============================================================================
# CHECKLIST TESTS
# =============================================================================
class TestChecklistNegative:
    """Test checklist submission failure scenarios."""
    
    def test_checklist_scenarios(self, request):
        """Run all checklist negative scenarios."""
        scenarios = load_scenarios().get("checklist_scenarios", [])
        if not scenarios:
            pytest.skip("No checklist scenarios")
        
        app_data = load_json(APP_FILE)
        if not app_data.get("application_id"):
            pytest.skip("No application - run application tests first")
        
        token = get_token()
        url = f"{BASE_URL}/health-service-request/service/v1/_create"
        
        req_info = get_request_info(token)
        user_uuid = req_info.get("userInfo", {}).get("uuid", "")
        
        results = []
        passed = 0
        bugs = []
        
        print(f"\n{'='*60}")
        print(f"☑️ CHECKLIST NEGATIVE TESTS ({len(scenarios)} scenarios)")
        print(f"{'='*60}")
        
        for scenario in scenarios:
            name = scenario.get("name")
            attributes = scenario.get("attributes", [])
            service_def_id = scenario.get("service_def_id", "test-def-id")
            account_id = scenario.get("account_id", app_data.get("application_id"))
            expected = scenario.get("expected", {})
            
            print(f"\n📋 {name}")
            
            for attr in attributes:
                attr["value"] = expand_placeholder(attr.get("value"))
            
            payload = {
                "Service": {
                    "clientId": user_uuid,
                    "serviceDefId": service_def_id,
                    "accountId": account_id,
                    "tenantId": tenantId,
                    "attributes": attributes,
                    "additionalFields": [{"action": "SUBMIT"}]
                },
                "apiOperation": "CREATE",
                "RequestInfo": req_info
            }
            
            res = requests.post(url, json=payload, headers=get_headers(token))
            
            rejected = is_rejected(res, expected.get("status"))
            
            if rejected:
                print(f"   ✅ Correctly rejected ({res.status_code})")
                passed += 1
            else:
                print(f"   ❌ BUG! Should reject but got {res.status_code}")
                bugs.append(name)
            
            results.append({"name": name, "passed": rejected, "status": res.status_code})
        
        print_result(passed, len(scenarios), bugs)
        
        if request:
            request.node._test_result = {"Total": len(scenarios), "Passed": passed, "Bugs": len(bugs)}


# =============================================================================
# SEARCH TESTS
# =============================================================================
class TestSearchNegative:
    """Test search with invalid parameters."""
    
    def test_search_scenarios(self, request):
        """Run all search negative scenarios."""
        scenarios = load_scenarios().get("search_scenarios", [])
        if not scenarios:
            pytest.skip("No search scenarios")
        
        token = get_token()
        url = f"{BASE_URL}/public-service/application/v1/_search"
        
        results = []
        passed = 0
        bugs = []
        
        print(f"\n{'='*60}")
        print(f"🔍 SEARCH NEGATIVE TESTS ({len(scenarios)} scenarios)")
        print(f"{'='*60}")
        
        for scenario in scenarios:
            name = scenario.get("name")
            criteria = scenario.get("criteria", {})
            expected = scenario.get("expected", {})
            
            print(f"\n📋 {name}")
            
            search_criteria = {**criteria, "tenantId": tenantId}
            
            payload = {
                "ApplicationSearchCriteria": search_criteria,
                "RequestInfo": get_request_info(token)
            }
            
            res = requests.post(url, json=payload, headers=get_headers(token))
            data = res.json()
            
            applications = data.get("Applications") or data.get("applications") or []
            count = len(applications)
            
            max_results = expected.get("max_results", 0)
            test_passed = count <= max_results
            
            if test_passed:
                print(f"   ✅ Correct - found {count} results")
                passed += 1
            else:
                print(f"   ❌ Expected 0 results, found {count}")
                bugs.append(name)
            
            results.append({"name": name, "passed": test_passed, "count": count})
        
        print_result(passed, len(scenarios), bugs)
        
        if request:
            request.node._test_result = {"Total": len(scenarios), "Passed": passed, "Bugs": len(bugs)}


# =============================================================================
# SECURITY TESTS
# =============================================================================
# # class TestSecurityScenarios:
#     """Test security scenarios - XSS, SQL Injection, etc."""
    
#     def test_security_scenarios(self, request):
#         """Run all security scenarios."""
#         scenarios = load_scenarios().get("security_scenarios", [])
#         if not scenarios:
#             pytest.skip("No security scenarios")
        
#         mdms = load_json(MDMS_FILE)
#         app_data = load_json(APP_FILE)
#         token = get_token()

#         # Get the actual service_code from application data
#         if not app_data.get("service_code"):
#             pytest.skip("No service_code in application data")

#         service_code = app_data.get("service_code")

#         results = []
#         passed = 0
#         warnings = []
        
#         print(f"\n{'='*60}")
#         print(f"🔒 SECURITY TESTS ({len(scenarios)} scenarios)")
#         print(f"{'='*60}")
        
#         for scenario in scenarios:
#             name = scenario.get("name")
#             api = scenario.get("api")
#             data = scenario.get("data", {})
#             criteria = scenario.get("criteria", {})
#             attributes = scenario.get("attributes", [])
            
#             print(f"\n📋 {name}")
            
#             if api == "application":
#                 url = f"{BASE_URL}/public-service/v1/application/{service_code}"
#                 payload = {
#                     "Application": {
#                         "tenantId": tenantId,
#                         "serviceCode": mdms.get("service_code", "test"),
#                         "applicant": {
#                             "name": {"givenName": data.get("name", "Test")},
#                             "mobileNumber": data.get("mobile", "9876543210")
#                         },
#                         "address": {"city": "Test", "locality": {"code": "SL001"}}
#                     },
#                     "RequestInfo": get_request_info(token)
#                 }
#             elif api == "search":
#                 url = f"{BASE_URL}/public-service/application/v1/_search"
#                 payload = {
#                     "ApplicationSearchCriteria": {**criteria, "tenantId": tenantId},
#                     "RequestInfo": get_request_info(token)
#                 }
#             elif api == "checklist":
#                 url = f"{BASE_URL}/health-service-request/service/v1/_create"
#                 req_info = get_request_info(token)
#                 payload = {
#                     "Service": {
#                         "clientId": req_info.get("userInfo", {}).get("uuid", ""),
#                         "serviceDefId": "test-def",
#                         "accountId": app_data.get("application_id", "test-account"),
#                         "tenantId": tenantId,
#                         "attributes": attributes,
#                         "additionalFields": [{"action": "SUBMIT"}]
#                     },
#                     "apiOperation": "CREATE",
#                     "RequestInfo": req_info
#                 }
#             else:
#                 continue
            
#             res = requests.post(url, json=payload, headers=get_headers(token))
            
#             is_safe = res.status_code in [400, 403, 422] or "<script>" not in res.text
            
#             if is_safe:
#                 print(f"   ✅ Safe ({res.status_code})")
#                 passed += 1
#             else:
#                 print(f"   ⚠️ Check response ({res.status_code})")
#                 warnings.append(name)
            
#             results.append({"name": name, "passed": is_safe, "status": res.status_code})
        
#         print_result(passed, len(scenarios), warnings)
        
#         if request:
#             request.node._test_result = {"Total": len(scenarios), "Safe": passed, "Review": len(warnings)}


# =============================================================================
# SUMMARY
# =============================================================================
class TestAllNegativeScenarios:
    """Summary of all negative scenarios."""
    
    def test_summary(self, request):
        """Print summary of all scenarios."""
        scenarios = load_scenarios()
        
        print(f"\n{'='*60}")
        print(f"📊 NEGATIVE TEST SCENARIOS SUMMARY")
        print(f"{'='*60}")
        
        total = 0
        for key in scenarios:
            if key != "_comment" and isinstance(scenarios[key], list):
                count = len(scenarios[key])
                total += count
                print(f"   {key}: {count}")
        
        print(f"\n   TOTAL: {total}")
        
        print(f"\n📋 RUN COMMANDS:")
        print(f"   pytest tests/test_data_driven.py::TestMDMSDraftNegative -v -s")
        print(f"   pytest tests/test_data_driven.py::TestMDMSServiceCreateNegative -v -s")
        print(f"   pytest tests/test_data_driven.py::TestPublicServiceInitNegative -v -s")
        print(f"   pytest tests/test_data_driven.py::TestApplicationNegative -v -s")
        print(f"   pytest tests/test_data_driven.py::TestWorkflowNegative -v -s")
        print(f"   pytest tests/test_data_driven.py::TestChecklistNegative -v -s")
        print(f"   pytest tests/test_data_driven.py -v -s  # Run ALL")
        
        if request:
            request.node._test_result = {
                "MDMS Draft": len(scenarios.get("mdms_draft_scenarios", [])),
                "MDMS Create": len(scenarios.get("mdms_service_create_scenarios", [])),
                "Public Service Init": len(scenarios.get("public_service_init_scenarios", [])),
                "Application": len(scenarios.get("application_scenarios", [])),
                "Workflow": len(scenarios.get("workflow_scenarios", [])),
                "Checklist": len(scenarios.get("checklist_scenarios", [])),
                "Search": len(scenarios.get("search_scenarios", [])),
                "Security": len(scenarios.get("security_scenarios", [])),
                "Boundary": len(scenarios.get("boundary_scenarios", [])),
                "TOTAL": total
            }