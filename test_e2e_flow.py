"""
End-to-End Test Flow
Each test runs separately and shows in report individually.
conftest.py handles the 15-minute wait after test_03_public_service_init.
"""
import pytest

# Import test functions with aliases (NOT starting with test_)
from tests.test_studio_services import (
    test_mdms_draft_create as _mdms_draft_create,
    test_mdms_service_create as _mdms_service_create,
    test_public_service_init as _public_service_init
)
from tests.test_actions_roleactions_search import (
    test_actions_search as _actions_search,
    test_roleactions_search as _roleactions_search
)
from tests.test_checklist_search import test_checklist_search as _checklist_search
from tests.test_idgen_search import test_idgen_search as _idgen_search
from tests.test_localization_search import test_localization_search as _localization_search
from tests.test_roles_search import test_roles_search as _roles_search
from tests.test_workflow_search import test_workflow_validate as _workflow_validate
from tests.test_application import (
    test_application_create as _application_create,
    test_application_assign as _application_assign,
    test_application_resolve as _application_resolve
)
from tests.test_individual_search import test_individual_search as _individual_search
from tests.test_process_instance_search import (
    test_process_instance_after_create as _process_instance_after_create,
    test_process_instance_after_assign as _process_instance_after_assign,
    test_process_instance_after_resolve as _process_instance_after_resolve
)
from tests.test_application_search import (
    test_application_search as _application_search,
    test_application_search_by_service_code as _application_search_by_service_code
)
from tests.test_inbox_search import test_inbox_search as _inbox_search


# =============================================================================
# PHASE 1: SERVICE SETUP
# =============================================================================
def test_01_mdms_draft_create(request):
    """Step 1: Create MDMS Draft"""
    return _mdms_draft_create(request)


def test_02_mdms_service_create(request):
    """Step 2: Publish MDMS Service Configuration"""
    return _mdms_service_create(request)


def test_03_public_service_init(request):
    """Step 3: Initialize Public Service"""
    return _public_service_init(request)


# =============================================================================
# PHASE 2: VERIFY SERVICE SETUP (after 15-min wait handled by conftest.py)
# =============================================================================
def test_04_actions_search(request):
    """Step 4: Verify Actions"""
    result = _actions_search()
    if request:
        request.node._test_result = {
            "Total Actions": result["total_actions"],
            "Service Actions": result["service_actions_count"],
            "Status": "✅ Found" if result["service_actions_count"] > 0 else "⚠️ Not Found"
        }
    return result


def test_05_roleactions_search(request):
    """Step 5: Verify Role Actions"""
    result = _roleactions_search()
    if request:
        request.node._test_result = {
            "Total Roleactions": result["total_roleactions"],
            "Found Roles": str(result["found_roles"]),
            "Service Roleactions": result["service_roleactions_count"],
            "Status": "✅ Found" if result["service_roleactions_count"] > 0 else "⚠️ Not Found"
        }
    return result


def test_06_checklist_search(request):
    """Step 6: Verify Checklists"""
    return _checklist_search(request)


def test_07_idgen_search(request):
    """Step 7: Verify ID Generation Formats"""
    result = _idgen_search()
    if request:
        request.node._test_result = {
            "Total Idgens": result["total_idgens"],
            "Found Idgens": str(result["found_idgens"]),
            "All Found": "✅ Yes" if result["all_idgens_found"] else "❌ No"
        }
    return result


def test_08_localization_search(request):
    """Step 8: Verify Localization"""
    return _localization_search(request)


def test_09_roles_search(request):
    """Step 9: Verify Roles"""
    result = _roles_search()
    if request:
        request.node._test_result = {
            "Total Roles": result["total_roles"],
            "Found Roles": str(result["found_roles"]),
            "Service Roles Count": result["service_roles_count"],
            "Status": "✅ Found" if result["service_roles_count"] > 0 else "⚠️ Not Found"
        }
    return result


def test_10_workflow_validate(request):
    """Step 10: Verify Workflow"""
    result = _workflow_validate()
    if request:
        request.node._test_result = {
            "Total States": result["total_states"],
            "Found States": str(result["found_states"]),
            "Found Actions": str(result["found_actions"]),
            "Workflow Valid": "✅ Yes" if result["workflow_valid"] else "❌ No"
        }
    return result


# =============================================================================
# PHASE 3: APPLICATION FLOW
# =============================================================================
def test_11_application_create(request):
    """Step 11: Create Application"""
    return _application_create(request)


def test_12_checklist_create_all_and_submit(request):
    """Step 12: Create and Submit Checklists"""
    from tests.test_checklist_create import test_checklist_create_all_and_submit
    return test_checklist_create_all_and_submit(request)


def test_13_individual_search(request):
    """Step 13: Verify Individual"""
    return _individual_search(request)


def test_14_process_instance_after_create(request):
    """Step 14: Verify Process Instance (After Create)"""
    result = _process_instance_after_create()
    if request:
        request.node._test_result = {
            "Application Number": result["application_number"],
            "Current State": result["current_state"],
            "Applied Action Found": "✅ Yes" if result["applied_action_found"] else "❌ No"
        }
    return result


def test_15_application_assign(request):
    """Step 15: Assign Application"""
    return _application_assign(request)


def test_16_process_instance_after_assign(request):
    """Step 16: Verify Process Instance (After Assign)"""
    result = _process_instance_after_assign()
    if request:
        request.node._test_result = {
            "Application Number": result["application_number"],
            "Current State": result["current_state"],
            "Assign Action Found": "✅ Yes" if result["assign_action_found"] else "❌ No"
        }
    return result


def test_17_application_resolve(request):
    """Step 17: Resolve Application"""
    return _application_resolve(request)


def test_18_process_instance_after_resolve(request):
    """Step 18: Verify Process Instance (After Resolve)"""
    result = _process_instance_after_resolve()
    if request:
        request.node._test_result = {
            "Application Number": result["application_number"],
            "Current State": result["current_state"],
            "Resolve Action Found": "✅ Yes" if result["resolve_action_found"] else "❌ No",
            "Flow Complete": "✅ Yes" if result["current_state"] == "RESOLVED" else "❌ No"
        }
    return result


# =============================================================================
# PHASE 4: FINAL VERIFICATION
# =============================================================================
def test_19_application_search(request):
    """Step 19: Application Search"""
    result = _application_search()
    if request:
        request.node._test_result = {
            "Application Number": result["application_number"],
            "Found": "✅ Yes" if result["found"] else "❌ No",
            "Status": result["status"]
        }
    return result


def test_20_application_search_by_service_code(request):
    """Step 20: Application Search by Service Code"""
    result = _application_search_by_service_code()
    if request:
        request.node._test_result = {
            "Service Code": result["service_code"],
            "Total Found": result["total_found"]
        }
    return result


def test_21_inbox_search(request):
    """Step 21: Verify Inbox"""
    result = _inbox_search()
    if request:
        request.node._test_result = {
            "Application Number": result["application_number"],
            "Total Inbox Items": result["total_inbox_items"],
            "Application In Inbox": "✅ Yes" if result["application_in_inbox"] else "❌ No"
        }
    return result