# DIGIT Studio API Automation Framework

Automated API testing framework for DIGIT Studio Services using Python pytest.

## 📁 Project Structure

```
studio_automation_script/
├── tests/
│   ├── test_studio_services.py          # MDMS & Public Service tests
│   ├── test_application.py              # Application Create/Update tests
│   ├── test_application_search.py       # Application Search tests
│   ├── test_inbox_search.py             # Inbox Search tests
│   ├── test_roles_search.py             # Roles validation tests
│   ├── test_workflow_search.py          # Workflow validation tests
│   ├── test_actions_roleactions_search.py # Actions & Roleactions tests
│   ├── test_idgen_search.py             # ID Generation format tests
│   └── test_process_instance_search.py  # Process Instance/Workflow history tests
├── payloads/
│   ├── mdms/
│   │   └── mdms_service_create.json     # MDMS service configuration payload
│   └── public_service/
│       ├── public_service_init.json     # Public service init payload
│       ├── create_application.json      # Application create payload
│       └── update_application.json      # Application update payload
├── utils/
│   ├── api_client.py                    # API client with auth
│   ├── auth.py                          # Authentication helper
│   ├── config.py                        # Configuration (BASE_URL, tenantId)
│   ├── data_loader.py                   # JSON payload loader
│   └── request_info.py                  # RequestInfo builder
├── output/                              # Test output files (auto-generated)
│   ├── mdms_response.json
│   ├── public_service_response.json
│   └── application_response.json
├── .env                                 # Environment variables
├── pytest.ini                           # Pytest configuration
└── README.md                            # This file
```

## 🔧 Setup

### 1. Install Dependencies

```bash
pip install pytest requests python-dotenv --break-system-packages
```

### 2. Configure Environment

Create `.env` file:

```env
BASE_URL=https://unified-uat.digit.org
TENANTID=st
USERNAME=your_username
PASSWORD=your_password
USERTYPE=EMPLOYEE
CLIENT_AUTH_HEADER=Basic ZWdvdi11c2VyLWNsaWVudDo=
```

### 3. Copy Test Files

```bash
# Copy all test files to tests/ directory
cp ~/Downloads/test_*.py tests/

# Copy payload files
cp ~/Downloads/create_application.json payloads/public_service/
cp ~/Downloads/update_application.json payloads/public_service/
```

## 🚀 Running Tests

### Complete End-to-End Flow

Run tests in this order for complete service setup and application flow:

```bash
# Step 1: Create MDMS Service Configuration
pytest tests/test_studio_services.py::test_mdms_service_create -v

# Step 2: Initialize Public Service
pytest tests/test_studio_services.py::test_public_service_init -v

# Step 3: Verify Service Setup
pytest tests/test_roles_search.py::test_roles_search -v
pytest tests/test_workflow_search.py::test_workflow_search -v
pytest tests/test_idgen_search.py::test_idgen_search -v
pytest tests/test_actions_roleactions_search.py::test_actions_search -v
pytest tests/test_actions_roleactions_search.py::test_roleactions_search -v

# Step 4: Create Application
pytest tests/test_application.py::test_application_create -v

# Step 5: Verify Application Created
pytest tests/test_application_search.py::test_application_search -v
pytest tests/test_inbox_search.py::test_inbox_search -v
pytest tests/test_process_instance_search.py::test_process_instance_after_create -v

# Step 6: Assign Application
pytest tests/test_application.py::test_application_assign -v
pytest tests/test_process_instance_search.py::test_process_instance_after_assign -v

# Step 7: Resolve Application
pytest tests/test_application.py::test_application_resolve -v
pytest tests/test_process_instance_search.py::test_process_instance_after_resolve -v

# Step 8: Validate Complete Flow
pytest tests/test_process_instance_search.py::test_process_instance_validate_flow -v
```

### Quick Test Commands

```bash
# Complete Studio Setup (MDMS + Public Service)
pytest tests/test_studio_services.py::test_complete_studio_setup -v

# Complete Application Flow (Create + Assign + Resolve)
pytest tests/test_application.py::test_complete_application_flow -v

# Run All Tests in a File
pytest tests/test_studio_services.py -v
pytest tests/test_application.py -v
```

## 📋 Test Files Reference

### 1. test_studio_services.py

| Test | Description |
|------|-------------|
| `test_mdms_service_create` | Creates MDMS service configuration with random module/service names |
| `test_public_service_init` | Initializes public service |
| `test_complete_studio_setup` | Runs both in sequence |

### 2. test_application.py

| Test | Description |
|------|-------------|
| `test_application_create` | Creates new application |
| `test_application_assign` | ASSIGN workflow action |
| `test_application_resolve` | RESOLVE workflow action |
| `test_complete_application_flow` | Runs Create → Assign → Resolve |

### 3. test_application_search.py

| Test | Description |
|------|-------------|
| `test_application_search` | Search & validate application by number |
| `test_application_search_by_service_code` | Search all apps by service code |

### 4. test_inbox_search.py

| Test | Description |
|------|-------------|
| `test_inbox_search` | Search inbox for application |
| `test_inbox_search_validate_application` | Validate application details in inbox |

### 5. test_roles_search.py

| Test | Description |
|------|-------------|
| `test_roles_search` | Search roles for service |
| `test_roles_validate` | Assert expected roles exist |
| `test_search_specific_role` | Search specific role by code |

### 6. test_workflow_search.py

| Test | Description |
|------|-------------|
| `test_workflow_search` | Search workflow for service |
| `test_workflow_validate` | Validate workflow states/actions |
| `test_workflow_states_and_actions` | Assert all states/actions exist |

### 7. test_actions_roleactions_search.py

| Test | Description |
|------|-------------|
| `test_actions_search` | Search actions-test for service |
| `test_roleactions_search` | Search roleactions for service roles |
| `test_actions_validate` | Validate actions exist |
| `test_roleactions_validate` | Validate roleactions exist |
| `test_service_access_config` | Complete validation of both |

### 8. test_idgen_search.py

| Test | Description |
|------|-------------|
| `test_idgen_search` | Search idgen formats for service |
| `test_idgen_validate` | Assert expected idgens exist |
| `test_idgen_format_details` | Get detailed format info |

### 9. test_process_instance_search.py

| Test | Description |
|------|-------------|
| `test_process_instance_search` | Search process instance history |
| `test_process_instance_after_create` | Verify after APPLIED action |
| `test_process_instance_after_assign` | Verify after ASSIGN action |
| `test_process_instance_after_resolve` | Verify after RESOLVE action |
| `test_process_instance_validate_flow` | Validate complete workflow flow |

## 🔄 Workflow Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                        SERVICE SETUP                                 │
├─────────────────────────────────────────────────────────────────────┤
│  MDMS Create ──► Public Service Init ──► Roles/Workflow/Idgen       │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      APPLICATION FLOW                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐       │
│  │  CREATE  │───►│  ASSIGN  │───►│  RESOLVE │───►│ COMPLETE │       │
│  │ (APPLIED)│    │          │    │          │    │          │       │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘       │
│       │               │               │               │              │
│       ▼               ▼               ▼               ▼              │
│  PENDING_FOR    PENDING_AT_LME    RESOLVED       RESOLVED           │
│  ASSIGNMENT                                                          │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## 📝 Output Files

Tests save responses to `output/` directory:

| File | Description |
|------|-------------|
| `mdms_response.json` | Module, service, id from MDMS create |
| `public_service_response.json` | Service code, id, status |
| `application_response.json` | Application details for updates |

## ⚠️ Important Notes

1. **Run in Order**: Tests depend on previous test outputs. Run MDMS → Public Service → Application in sequence.

2. **Fresh Data**: Each `test_mdms_service_create` generates new random module/service names to avoid duplicates.

3. **Server Availability**: If you get `503 Service Unavailable`, wait and retry.

4. **Auth Token**: Uses `auth-token` header for search APIs, `Authorization: Bearer` for create/update APIs.

## 🐛 Troubleshooting

### Service Already Exists Error
```bash
# Generate fresh module/service names
pytest tests/test_studio_services.py::test_mdms_service_create -v
```

### File Not Found Error
```bash
# Ensure payload files exist
ls payloads/public_service/
# Should show: create_application.json, update_application.json, public_service_init.json
```

### 401 Unauthorized Error
- Check `.env` credentials
- Search APIs need `auth-token` header

### 500 Server Error
- Check payload structure
- Verify placeholders are replaced
- Check server logs

## 📊 Expected Validations

### Roles Created
- `{Module}_{Service}_COMPLAINT_EVALUATOR`
- `{Module}_{Service}_EMPLOYEE_VIEW`

### Workflow States
- `PENDING_FOR_ASSIGNMENT`
- `PENDING_AT_LME`
- `REJECTED`
- `RESOLVED`

### Workflow Actions
- `APPLIED`, `ASSIGN`, `REJECT`, `REASSIGN`, `RESOLVE`, `REOPEN`

### Idgen Formats
- Application: `{module}-{service}-app-[cy:yyyy-MM-dd]-[SEQ_PUBLIC_APPLICATION]`
- Service: `{module}-{service}-svc-[cy:yyyy-MM-dd]-[SEQ_PUBLIC_APPLICATION]`

## 📄 License

pytest tests/test_application.py::test_application_create -v
pytest tests/test_application.py::test_application_assign -v
pytest tests/test_application.py::test_application_resolve -v
pytest tests/test_application.py::test_complete_application_flow -v

pytest tests/test_studio_services.py::test_mdms_service_create -v
pytest tests/test_studio_services.py::test_public_service_init -v
pytest tests/test_studio_services.py::test_complete_studio_setup -v

pytest tests/test_application_search.py::test_application_search -v
pytest tests/test_inbox_search.py::test_inbox_search -v
pytest tests/test_workflow_search.py::test_workflow_search -v
pytest tests/test_actions_roleactions_search.py -v
pytest tests/test_process_instance_search.py -v

pytest tests/test_e2e_flow.py::test_e2e_complete_flow -v -s
pytest tests/test_application.py -v --html=reports/app_report.html
pytest tests/test_studio_services.py -v --html=reports/studio_report.html
google-chrome reports/app_report.html
google-chrome reports/studio_report.html


pytest tests/test_studio_services.py::test_mdms_service_create \
       tests/test_studio_services.py::test_public_service_init \
       tests/test_application.py::test_application_create \
       tests/test_application.py::test_application_assign \
       tests/test_application.py::test_application_resolve \
       -v --html=reports/flow_report.html --self-contained-html