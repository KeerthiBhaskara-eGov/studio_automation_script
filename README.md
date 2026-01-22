# DIGIT Studio Automation Test Suite

Automated testing framework for DIGIT Studio Services - covering MDMS configuration, public service initialization, application workflows, and checklist management.

## 📁 Project Structure

```
studio_automation_script/
├── test_e2e_flow.py              # Main E2E test orchestrator (21 tests)
├── conftest.py                   # Pytest configuration & 15-min wait logic
├── pytest.ini                    # Pytest settings
│
├── tests/                        # Individual test modules
│   ├── test_studio_services.py   # MDMS & Public Service Init
│   ├── test_application.py       # Application Create/Assign/Resolve
│   ├── test_checklist_create.py  # Checklist submission
│   ├── test_checklist_search.py  # Checklist verification
│   ├── test_actions_roleactions_search.py
│   ├── test_roles_search.py
│   ├── test_workflow_search.py
│   ├── test_idgen_search.py
│   ├── test_localization_search.py
│   ├── test_individual_search.py
│   ├── test_process_instance_search.py
│   ├── test_application_search.py
│   └── test_inbox_search.py
│
├── utils/                        # Utility modules
│   ├── auth.py                   # Authentication (get_auth_token)
│   ├── config.py                 # Configuration (BASE_URL, tenantId)
│   ├── request_info.py           # RequestInfo payload builder
│   └── data_loader.py            # JSON payload loader
│
├── payloads/                     # JSON request payloads
│   ├── mdms/
│   │   ├── mdms_draft_create.json
│   │   └── mdms_service_create.json
│   ├── application/
│   │   ├── application_create.json
│   │   └── workflow_update.json
│   └── checklist/
│       ├── create_checklist.json
│       └── update_checklist.json
│
├── output/                       # Runtime output files
│   ├── mdms_response.json        # Service configuration details
│   ├── application_response.json # Application details
│   └── checklist_response.json   # Checklist submission details
│
└── reports/                      # HTML test reports
    └── e2e_report.html
```

## 🔧 Setup

### Prerequisites

- Python 3.10+
- pip

### Installation

```bash
# Clone or download the project
cd studio_automation_script

# Install dependencies
pip install pytest requests pytest-html pytest-metadata
```

### Configuration

Edit `utils/config.py`:

```python
BASE_URL = "https://unified-uat.digit.org"
tenantId = "st"
```

Edit `utils/auth.py` with your credentials:

```python
users = {
    "user": {
        "username": "your_username",
        "password": "your_password"
    }
}
```

Edit `utils/request_info.py` with your user details:

```python
def get_request_info(token: str) -> dict:
    return {
        "apiId": "Rainmaker",
        "authToken": token,
        "userInfo": {
            "id": 120641,
            "userName": "YourUser",
            "uuid": "your-user-uuid",
            "tenantId": "st",
            "roles": [...]
        }
    }
```

## 🚀 Running Tests

### Full E2E Flow (Recommended)

Runs all 21 tests in sequence with 15-minute wait after service initialization:

```bash
pytest test_e2e_flow.py -v -s --html=reports/e2e_report.html --self-contained-html
```

### Individual Test Phases

#### Phase 1: Service Setup
```bash
# Create MDMS Draft
pytest tests/test_studio_services.py::test_mdms_draft_create -v -s

# Publish MDMS Service
pytest tests/test_studio_services.py::test_mdms_service_create -v -s

# Initialize Public Service
pytest tests/test_studio_services.py::test_public_service_init -v -s

# Complete setup (all 3)
pytest tests/test_studio_services.py::test_complete_studio_setup -v -s
```

#### Phase 2: Verification (after 15-min wait)
```bash
pytest tests/test_actions_roleactions_search.py -v -s
pytest tests/test_checklist_search.py -v -s
pytest tests/test_idgen_search.py -v -s
pytest tests/test_localization_search.py -v -s
pytest tests/test_roles_search.py -v -s
pytest tests/test_workflow_search.py -v -s
```

#### Phase 3: Application Flow
```bash
# Create application
pytest tests/test_application.py::test_application_create -v -s

# Submit checklists for current state
pytest tests/test_checklist_create.py::test_checklist_for_current_state -v -s

# Assign application
pytest tests/test_application.py::test_application_assign -v -s

# Resolve application
pytest tests/test_application.py::test_application_resolve -v -s

# Complete flow (Create → Assign → Resolve)
pytest tests/test_application.py::test_complete_application_flow -v -s
```

#### Phase 4: Search & Verification
```bash
pytest tests/test_individual_search.py -v -s
pytest tests/test_process_instance_search.py -v -s
pytest tests/test_application_search.py -v -s
pytest tests/test_inbox_search.py -v -s
```

## 📋 Test Flow Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 1: SERVICE SETUP                       │
├─────────────────────────────────────────────────────────────────┤
│ 1. test_01_mdms_draft_create      → Create MDMS draft           │
│ 2. test_02_mdms_service_create    → Publish service config      │
│ 3. test_03_public_service_init    → Initialize public service   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ⏳ 15-MINUTE WAIT
                  (System initialization)
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                 PHASE 2: VERIFY SERVICE SETUP                   │
├─────────────────────────────────────────────────────────────────┤
│ 4. test_04_actions_search         → Verify actions created      │
│ 5. test_05_roleactions_search     → Verify role-actions         │
│ 6. test_06_checklist_search       → Verify checklist defs       │
│ 7. test_07_idgen_search           → Verify ID generation        │
│ 8. test_08_localization_search    → Verify localizations        │
│ 9. test_09_roles_search           → Verify roles                │
│ 10. test_10_workflow_validate     → Verify workflow states      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  PHASE 3: APPLICATION FLOW                      │
├─────────────────────────────────────────────────────────────────┤
│ 11. test_11_application_create    → Create application          │
│     State: APPLIED → PENDING_FOR_ASSIGNMENT                     │
│                                                                 │
│ 12. test_12_checklist_submit      → Submit all checklists       │
│                                                                 │
│ 13. test_13_individual_search     → Verify applicant            │
│                                                                 │
│ 14. test_14_process_instance      → Verify process (create)     │
│                                                                 │
│ 15. test_15_application_assign    → Assign application          │
│     State: PENDING_FOR_ASSIGNMENT → PENDING_AT_LME              │
│                                                                 │
│ 16. test_16_process_instance      → Verify process (assign)     │
│                                                                 │
│ 17. test_17_application_resolve   → Resolve application         │
│     State: PENDING_AT_LME → RESOLVED                            │
│                                                                 │
│ 18. test_18_process_instance      → Verify process (resolve)    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                 PHASE 4: FINAL VERIFICATION                     │
├─────────────────────────────────────────────────────────────────┤
│ 19. test_19_application_search    → Search by app number        │
│ 20. test_20_search_by_service     → Search by service code      │
│ 21. test_21_inbox_search          → Verify inbox                │
└─────────────────────────────────────────────────────────────────┘
```

## 📊 Output Files

### `output/mdms_response.json`
```json
{
  "module": "ModuleXYZ",
  "service": "ServiceABC",
  "service_code": "ModuleXYZ-ServiceABC-svc-2026-01-22-...",
  "unique_id": "...",
  "status": "created"
}
```

### `output/application_response.json`
```json
{
  "module": "ModuleXYZ",
  "service": "ServiceABC",
  "application_id": "uuid-...",
  "application_number": "ModuleXYZ-ServiceABC-app-2026-01-22-...",
  "workflow_status": "PENDING_FOR_ASSIGNMENT",
  "mobile_number": "9876543210"
}
```

### `output/checklist_response.json`
```json
{
  "module": "ModuleXYZ",
  "service": "ServiceABC",
  "state": "PENDING_FOR_ASSIGNMENT",
  "checklist_code": "ServiceABC.PENDING_FOR_ASSIGNMENT.complaint details",
  "service_id": "uuid-...",
  "status": "submitted"
}
```

## 📈 HTML Reports

Reports are generated in `reports/` directory:

```bash
# View report
open reports/e2e_report.html
# or
xdg-open reports/e2e_report.html
```

Report includes:
- Test name and description
- Pass/Fail status
- Execution time
- Custom result details (Module, Service, IDs, etc.)

## ⚙️ Customization

### Modify Service Configuration

Edit `payloads/mdms/mdms_service_create.json`:

```json
{
  "Mdms": {
    "data": {
      "workflow": [...],
      "checklist": [...],
      "roleactions": [...],
      "idgen": [...],
      "localization": [...]
    }
  }
}
```

### Change Wait Time

Edit `conftest.py`:

```python
WAIT_MINUTES = 15  # Change to desired minutes
```

### Add New Roles

Edit `payloads/mdms/mdms_service_create.json` → `roleactions` section.

## 🐛 Troubleshooting

### Checklist not showing in UI
- Ensure `clientId` in request matches logged-in user's UUID
- Verify `accountId` is the application's ID
- Check `dataType` uses lowercase `"text"` for Text fields

### Service initialization failed
- Wait full 15 minutes after `public_service_init`
- Check if service already exists (unique constraint)

### Authentication errors
- Verify credentials in `utils/auth.py`
- Check token expiration
- Ensure user has required roles (STUDIO_ADMIN, MDMS_ADMIN)

### Test order issues
- Always run tests in sequence (use `test_e2e_flow.py`)
- Tests depend on output files from previous tests

## 📝 Available Tests Summary

| Test File | Tests | Description |
|-----------|-------|-------------|
| `test_studio_services.py` | 4 | MDMS draft, create, public service init |
| `test_application.py` | 4 | Create, assign, resolve, complete flow |
| `test_checklist_create.py` | 2 | Submit checklist for current/all states |
| `test_checklist_search.py` | 2 | Search and validate checklists |
| `test_actions_roleactions_search.py` | 2 | Verify actions and roleactions |
| `test_roles_search.py` | 1 | Verify roles |
| `test_workflow_search.py` | 1 | Validate workflow states |
| `test_idgen_search.py` | 1 | Verify ID generation formats |
| `test_localization_search.py` | 1 | Verify localizations |
| `test_individual_search.py` | 1 | Search individual/applicant |
| `test_process_instance_search.py` | 3 | Verify process at each stage |
| `test_application_search.py` | 2 | Search applications |
| `test_inbox_search.py` | 1 | Verify inbox |
| `test_e2e_flow.py` | 21 | Complete E2E orchestrator |

## 📄 License

Internal use only - eGovernments Foundation / DIGIT