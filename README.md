# DIGIT Studio Automation Test Suite

Comprehensive automated testing framework for DIGIT Studio Services - validates end-to-end service creation, configuration, application workflows, and checklist management.

## Overview

This test suite automates the complete DIGIT Studio workflow from MDMS (Master Data Management Service) configuration to application processing through various workflow states. It includes both positive E2E tests and negative/security test scenarios.

**Key Features:**
- **21 E2E Tests**: Complete workflow automation from service creation to application resolution
- **Data-Driven Negative Tests**: Security, boundary, and validation testing using configurable scenarios
- **Automated Wait Handling**: Smart 15-minute wait after service initialization
- **HTML Reporting**: Detailed test reports with execution summaries
- **CI/CD Ready**: Easily integrated into Jenkins, GitHub Actions, GitLab CI

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment (create/edit .env file)
BASE_URL=https://unified-uat.digit.org
USERNAME=your_username
PASSWORD=your_password
TENANTID=st
USERTYPE=EMPLOYEE
CLIENT_AUTH_HEADER=Basic ZWdvdi11c2VyLWNsaWVudDo=

# 3. Run E2E tests
pytest test_e2e_flow.py -v -s --html=reports/e2e_report.html --self-contained-html

# 4. View results
# - Terminal: Console output
# - HTML Report: reports/e2e_report.html
# - Output Data: output/*.json
```

**Duration:** ~20-25 minutes (includes 15-minute wait for service initialization)

---

## Prerequisites

- **Python**: 3.10 or higher
- **DIGIT Access**: Valid credentials with roles: `STUDIO_ADMIN`, `MDMS_ADMIN`, `LME`
- **Network**: Access to DIGIT API endpoints
- **Environment**: UAT/QA only (NOT production)

⚠️ **Important:**
- This suite **creates real data** in DIGIT (services, applications, configurations)
- Tests take **20-25 minutes** to complete
- Run only in **UAT/QA environments**

---

## Project Structure

```
studio_automation_script/
├── test_e2e_flow.py              # Main E2E orchestrator (21 tests)
├── conftest.py                   # Pytest configuration & wait logic
├── pytest.ini                    # Pytest settings
├── .env                          # Environment variables (credentials)
├── requirements.txt              # Python dependencies
│
├── tests/                        # Test modules
│   ├── test_studio_services.py           # Service setup (draft, create, init)
│   ├── test_application.py               # Application lifecycle
│   ├── test_checklist_create.py          # Checklist submission
│   ├── test_data_driven.py               # Negative/security tests
│   ├── test_*_search.py                  # Verification tests
│   └── ...                               # Other test modules
│
├── utils/                        # Utility modules
│   ├── api_client.py             # API client with auth
│   ├── config.py                 # Configuration loader
│   ├── data_loader.py            # JSON payload loader
│   └── ...
│
├── payloads/                     # JSON request templates
│   ├── mdms/                     # MDMS payloads
│   ├── Application/              # Application payloads
│   ├── public_service/           # Public service payloads
│   └── checklist/                # Checklist payloads
│
├── output/                       # Runtime generated files
│   ├── mdms_response.json
│   ├── application_response.json
│   └── ...
│
└── reports/                      # HTML test reports
    └── e2e_report.html
```

---

## Running Tests

### 1. Full E2E Test Suite (Recommended)

Runs all 21 tests sequentially with automatic 15-minute wait:

```bash
pytest test_e2e_flow.py -v -s --html=reports/e2e_report.html --self-contained-html
```

**What happens:**
- Phase 1: Service Setup (3 tests)
- [15-minute automatic wait]
- Phase 2: Verification (7 tests)
- Phase 3: Application Flow (8 tests)
- Phase 4: Final Verification (3 tests)

### 2. Test Modules (By Category)

Run entire test modules by category:

```bash
# Service Setup
pytest tests/test_studio_services.py -v -s                    # MDMS draft, service create, public service init

# Application Lifecycle
pytest tests/test_application.py -v -s                        # Create, assign, resolve application

# Checklist Tests
pytest tests/test_checklist_create.py -v -s                   # Checklist submission
pytest tests/test_checklist_search.py -v -s                   # Checklist verification

# Verification/Search Tests (run after 15-min wait)
pytest tests/test_actions_roleactions_search.py -v -s         # Actions & role-actions
pytest tests/test_roles_search.py -v -s                       # Roles verification
pytest tests/test_workflow_search.py -v -s                    # Workflow validation
pytest tests/test_idgen_search.py -v -s                       # ID generation formats
pytest tests/test_localization_search.py -v -s                # Localization keys

# Data Search Tests
pytest tests/test_individual_search.py -v -s                  # Individual/applicant search
pytest tests/test_process_instance_search.py -v -s            # Process instance tracking
pytest tests/test_application_search.py -v -s                 # Application search
pytest tests/test_inbox_search.py -v -s                       # Inbox verification

# All verification tests at once
pytest tests/test_*_search.py -v -s
```

### 3. Negative/Security Tests (Data-Driven)

Run negative scenarios using `test_data_driven.py`:

```bash
# All negative tests
pytest tests/test_data_driven.py -v -s

# Run specific negative test suites individually
pytest tests/test_data_driven.py::TestMDMSDraftNegative -v -s                  # MDMS draft negative tests
pytest tests/test_data_driven.py::TestMDMSServiceCreateNegative -v -s          # MDMS service create negative tests
pytest tests/test_data_driven.py::TestPublicServiceInitNegative -v -s          # Public service init negative tests
pytest tests/test_data_driven.py::TestAuthenticationNegative -v -s             # Authentication negative tests
pytest tests/test_data_driven.py::TestApplicationNegative -v -s                # Application negative tests
pytest tests/test_data_driven.py::TestWorkflowNegative -v -s                   # Workflow negative tests
pytest tests/test_data_driven.py::TestChecklistNegative -v -s                  # Checklist negative tests
pytest tests/test_data_driven.py::TestSearchNegative -v -s                     # Search negative tests
pytest tests/test_data_driven.py::TestSecurityScenarios -v -s                  # Security scenarios (XSS, SQL injection)
pytest tests/test_data_driven.py::TestAllNegativeScenarios -v -s               # Summary of all scenarios
```

**Note:** Negative tests require `test_scenarios_config.json` file with test scenarios.

### 4. Individual E2E Tests

Run specific E2E tests from the main flow:

```bash
# Phase 1: Service Setup
pytest test_e2e_flow.py::test_01_mdms_draft_create -v -s
pytest test_e2e_flow.py::test_02_mdms_service_create -v -s
pytest test_e2e_flow.py::test_03_public_service_init -v -s

# Phase 2: Verification Tests
pytest test_e2e_flow.py::test_04_actions_search -v -s
pytest test_e2e_flow.py::test_05_roleactions_search -v -s
pytest test_e2e_flow.py::test_06_checklist_search -v -s
pytest test_e2e_flow.py::test_07_idgen_search -v -s
pytest test_e2e_flow.py::test_08_localization_search -v -s
pytest test_e2e_flow.py::test_09_roles_search -v -s
pytest test_e2e_flow.py::test_10_workflow_validate -v -s

# Phase 3: Application Flow
pytest test_e2e_flow.py::test_11_application_create -v -s
pytest test_e2e_flow.py::test_12_checklist_create_all_and_submit -v -s
pytest test_e2e_flow.py::test_13_individual_search -v -s
pytest test_e2e_flow.py::test_14_process_instance_after_create -v -s
pytest test_e2e_flow.py::test_15_application_assign -v -s
pytest test_e2e_flow.py::test_16_process_instance_after_assign -v -s
pytest test_e2e_flow.py::test_17_application_resolve -v -s
pytest test_e2e_flow.py::test_18_process_instance_after_resolve -v -s

# Phase 4: Final Verification
pytest test_e2e_flow.py::test_19_application_search -v -s
pytest test_e2e_flow.py::test_20_application_search_by_service_code -v -s
pytest test_e2e_flow.py::test_21_inbox_search -v -s
```

**Note:** Individual E2E tests may fail if prerequisites haven't run. Always run the full E2E flow first.

### 5. Service Tests Module

Run tests from `test_studio_services.py`:

```bash
# All service tests
pytest tests/test_studio_services.py -v -s

# Individual service tests
pytest tests/test_studio_services.py::test_mdms_draft_create -v -s
pytest tests/test_studio_services.py::test_mdms_service_create -v -s
pytest tests/test_studio_services.py::test_public_service_init -v -s
pytest tests/test_studio_services.py::test_complete_studio_setup -v -s        # Runs all 3 in sequence
```

### 6. Application Tests Module

Run tests from `test_application.py`:

```bash
# All application tests
pytest tests/test_application.py -v -s

# Individual application tests
pytest tests/test_application.py::test_application_create -v -s
pytest tests/test_application.py::test_application_assign -v -s
pytest tests/test_application.py::test_application_resolve -v -s
pytest tests/test_application.py::test_complete_application_flow -v -s        # Runs all 3 in sequence
```

### 7. Verification/Search Tests

Run individual search/verification tests:

```bash
# Actions & Role-Actions
pytest tests/test_actions_roleactions_search.py::test_actions_search -v -s
pytest tests/test_actions_roleactions_search.py::test_roleactions_search -v -s

# Checklist
pytest tests/test_checklist_search.py::test_checklist_search -v -s
pytest tests/test_checklist_create.py::test_checklist_for_current_state -v -s
pytest tests/test_checklist_create.py::test_checklist_create_all_and_submit -v -s

# Roles & Workflow
pytest tests/test_roles_search.py::test_roles_search -v -s
pytest tests/test_workflow_search.py::test_workflow_validate -v -s

# ID Generation & Localization
pytest tests/test_idgen_search.py::test_idgen_search -v -s
pytest tests/test_localization_search.py::test_localization_search -v -s

# Individual & Process Instance
pytest tests/test_individual_search.py::test_individual_search -v -s
pytest tests/test_process_instance_search.py::test_process_instance_after_create -v -s
pytest tests/test_process_instance_search.py::test_process_instance_after_assign -v -s
pytest tests/test_process_instance_search.py::test_process_instance_after_resolve -v -s

# Application Search & Inbox
pytest tests/test_application_search.py::test_application_search -v -s
pytest tests/test_application_search.py::test_application_search_by_service_code -v -s
pytest tests/test_inbox_search.py::test_inbox_search -v -s
```

### 8. Run Tests by Pattern

Use pytest patterns to run multiple related tests:

```bash
# Run all search tests
pytest tests/test_*_search.py -v -s

# Run tests matching keyword
pytest -k "search" -v -s                    # All tests with "search" in name
pytest -k "application" -v -s               # All tests with "application" in name
pytest -k "checklist" -v -s                 # All tests with "checklist" in name
pytest -k "negative" -v -s                  # All negative tests

# Run tests from specific directory
pytest tests/ -v -s                         # All tests in tests directory
```

---

## Test Flow

### E2E Test Flow (21 Tests)

```
PHASE 1: SERVICE SETUP
├── test_01: Create MDMS draft
├── test_02: Publish service configuration
└── test_03: Initialize public service
     │
     ▼
  [15-MINUTE WAIT]
     │
     ▼
PHASE 2: VERIFY SERVICE SETUP
├── test_04: Verify actions
├── test_05: Verify role-actions
├── test_06: Verify checklists
├── test_07: Verify ID generation
├── test_08: Verify localization
├── test_09: Verify roles
└── test_10: Validate workflow
     │
     ▼
PHASE 3: APPLICATION FLOW
├── test_11: Create application [APPLIED → PENDING_FOR_ASSIGNMENT]
├── test_12: Submit checklists
├── test_13: Verify individual
├── test_14: Verify process instance (create)
├── test_15: Assign application [PENDING_FOR_ASSIGNMENT → PENDING_AT_LME]
├── test_16: Verify process instance (assign)
├── test_17: Resolve application [PENDING_AT_LME → RESOLVED]
└── test_18: Verify process instance (resolve)
     │
     ▼
PHASE 4: FINAL VERIFICATION
├── test_19: Search by application number
├── test_20: Search by service code
└── test_21: Verify inbox
```

### Negative Test Categories

Using `test_data_driven.py`:

- **MDMS Draft**: Invalid payloads, missing fields, XSS attempts
- **Service Create**: Duplicate services, malformed configurations
- **Public Service Init**: Missing data, invalid tenant
- **Application**: Invalid mobile, missing name, wrong service code
- **Workflow**: Invalid state transitions, unauthorized actions
- **Checklist**: Missing required fields, invalid data types
- **Security**: XSS, SQL injection, script injection attempts
- **Authentication**: Invalid tokens, missing auth headers

---

## Configuration

### Environment Variables (.env)

```bash
# DIGIT Platform
BASE_URL=https://unified-uat.digit.org
TENANTID=st

# Authentication
USERNAME=SUPERUSER
PASSWORD=eGov@123
USERTYPE=EMPLOYEE
CLIENT_AUTH_HEADER=Basic ZWdvdi11c2VyLWNsaWVudDo=

# Search Parameters
SEARCH_LIMIT=200
SEARCH_OFFSET=0
```

### Modifying Service Configuration

Edit `payloads/mdms/mdms_service_create.json` to customize:
- Workflow states and transitions
- Checklist definitions
- Role-action mappings
- ID generation formats
- Localization keys

---

## Output Files

Test execution generates the following files:

**`output/mdms_response.json`**
```json
{
  "module": "ModuleXYZ",
  "service": "ServiceABC",
  "service_code": "ModuleXYZ-ServiceABC-svc-2026-01-22-001",
  "unique_id": "abc-123-def-456",
  "status": "created"
}
```

**`output/application_response.json`**
```json
{
  "application_id": "app-uuid-123",
  "application_number": "ModuleXYZ-ServiceABC-app-2026-01-22-001",
  "workflow_status": "RESOLVED",
  "mobile_number": "9876543210"
}
```

**`reports/e2e_report.html`**
- Comprehensive HTML report with test results
- Pass/fail status with color coding
- Execution time and detailed outputs
- Summary of output data

---

## Troubleshooting

### Common Issues

**Authentication Errors (401)**
```bash
# Verify credentials
cat .env | grep USERNAME
cat .env | grep PASSWORD

# Ensure user has required roles: STUDIO_ADMIN, MDMS_ADMIN, LME
```

**Service Initialization Failed**
- Wait full 15 minutes after service initialization
- Check if service already exists (unique constraint)
- Verify tenant ID matches

**Tests Fail When Run Individually**
- Always use E2E flow: `pytest test_e2e_flow.py`
- Tests depend on output from previous tests
- Check `output/*.json` files exist

**MDMS Duplicate Service Error**
```bash
# Use unique service names in payloads/mdms/mdms_draft_create.json
# Change "service": "ServiceABC" to "service": "ServiceABC_v2"
```

**Application State Transition Failed**
- Verify workflow configuration
- Ensure user has required role for action
- Check current application state matches expected

### Debug Mode

```bash
# Maximum verbosity
pytest test_e2e_flow.py -vv -s --tb=long

# Specific test with debugging
pytest tests/test_application.py::test_application_create -vv -s --tb=long
```

---

## FAQ

**Q: How long does the full E2E test take?**
A: ~20-25 minutes, including the mandatory 15-minute wait.

**Q: Can I run tests in parallel?**
A: No for E2E flow. Tests must run sequentially due to dependencies.

**Q: Why the 15-minute wait?**
A: Backend needs time to process MDMS configuration, create workflows, set up actions, and propagate changes.

**Q: Can I test against production?**
A: **No.** This suite creates data. Use only in UAT/QA environments.

**Q: What data gets created?**
A: MDMS service configuration, applications, checklists, individuals, process instances, and localization keys. Data persists after tests.

**Q: How do I customize the service?**
A: Edit `payloads/mdms/mdms_draft_create.json` and `payloads/mdms/mdms_service_create.json`.

**Q: What if a test fails midway?**
A: Check HTML report for error details, review output files, manually clean up created services, and re-run from the beginning.

---

## Test Summary

### E2E Tests (test_e2e_flow.py)

| Test Count | Category | Description |
|------------|----------|-------------|
| 3 | Service Setup | MDMS draft, service create, public service init |
| 7 | Verification | Actions, roles, workflow, checklists, localization, ID gen |
| 8 | Application | Create, assign, resolve + process instance tracking |
| 3 | Search | Application search, inbox verification |
| **21** | **Total** | **Complete E2E Flow** |

### Negative Tests (test_data_driven.py)

| Test Suite | Purpose |
|------------|---------|
| `TestMDMSDraftNegative` | MDMS draft validation failures |
| `TestMDMSServiceCreateNegative` | Service create validation failures |
| `TestPublicServiceInitNegative` | Public service init failures |
| `TestAuthenticationNegative` | Authentication failures |
| `TestApplicationNegative` | Application creation failures |
| `TestWorkflowNegative` | Invalid workflow transitions |
| `TestChecklistNegative` | Checklist submission failures |
| `TestSearchNegative` | Invalid search parameters |
| `TestSecurityScenarios` | XSS, SQL injection, script injection |
| `TestAllNegativeScenarios` | Summary of all scenarios |

**Run commands:** See [Section 3: Negative/Security Tests](#3-negativesecurity-tests-data-driven) above for detailed commands.

### Test Modules Coverage

| Module | Test Count | Description |
|--------|------------|-------------|
| `test_studio_services.py` | 4 | MDMS draft, service create, public service init, complete setup |
| `test_application.py` | 4 | Application create, assign, resolve, complete flow |
| `test_checklist_create.py` | 2 | Checklist submission for current/all states |
| `test_checklist_search.py` | 2 | Checklist search and validation |
| `test_actions_roleactions_search.py` | 2 | Actions and roleactions verification |
| `test_roles_search.py` | 1 | Roles verification |
| `test_workflow_search.py` | 1 | Workflow validation |
| `test_idgen_search.py` | 1 | ID generation format verification |
| `test_localization_search.py` | 1 | Localization verification |
| `test_individual_search.py` | 1 | Individual search |
| `test_process_instance_search.py` | 3 | Process instance tracking (create/assign/resolve) |
| `test_application_search.py` | 2 | Application search (by number, by service code) |
| `test_inbox_search.py` | 1 | Inbox verification |

**Run commands:** See [Section 2: Test Modules](#2-test-modules-by-category), [Section 5: Service Tests](#5-service-tests-module), [Section 6: Application Tests](#6-application-tests-module), and [Section 7: Verification Tests](#7-verificationsearch-tests) for detailed commands.

---

## CI/CD Integration

### GitHub Actions

```yaml
name: DIGIT Studio E2E Tests

on:
  push:
    branches: [ main, develop ]
  schedule:
    - cron: '0 2 * * *'

jobs:
  e2e-tests:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    - run: pip install -r requirements.txt
    - run: |
        cat > .env << EOF
        BASE_URL=${{ secrets.BASE_URL }}
        USERNAME=${{ secrets.USERNAME }}
        PASSWORD=${{ secrets.PASSWORD }}
        TENANTID=st
        USERTYPE=EMPLOYEE
        EOF
    - run: pytest test_e2e_flow.py -v -s --html=reports/e2e_report.html --self-contained-html
    - uses: actions/upload-artifact@v3
      if: always()
      with:
        name: test-results
        path: |
          reports/
          output/
```

### Docker

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["pytest", "test_e2e_flow.py", "-v", "-s", "--html=reports/e2e_report.html", "--self-contained-html"]
```

```bash
# Build and run
docker build -t digit-studio-tests .
docker run --env-file .env -v $(pwd)/reports:/app/reports digit-studio-tests
```

---

## Best Practices

1. **Always use E2E flow for complete testing**
   ```bash
   pytest test_e2e_flow.py -v -s --html=reports/e2e_report.html --self-contained-html
   ```

2. **Clean output directory before new runs**
   ```bash
   rm -f output/*.json output/*.txt
   ```

3. **Use unique service names to avoid conflicts**
   - Modify `payloads/mdms/mdms_draft_create.json`
   - Change service name for each test run

4. **Respect the 15-minute wait**
   - Don't skip or reduce wait time
   - Backend needs time to process

5. **Review output files after each phase**
   ```bash
   cat output/mdms_response.json | jq .
   cat output/application_response.json | jq .
   ```

---

## Quick Reference - Common Commands

```bash
# ========== RECOMMENDED: Full E2E Test ==========
pytest test_e2e_flow.py -v -s --html=reports/e2e_report.html --self-contained-html

# ========== Run by Phase ==========
# Phase 1: Service Setup
pytest tests/test_studio_services.py -v -s

# Phase 2: Verification (after 15-min wait)
pytest tests/test_*_search.py -v -s

# Phase 3: Application Flow
pytest tests/test_application.py -v -s
pytest tests/test_checklist_create.py -v -s

# ========== Negative Tests ==========
# All negative tests
pytest tests/test_data_driven.py -v -s

# Specific negative test suite
pytest tests/test_data_driven.py::TestApplicationNegative -v -s
pytest tests/test_data_driven.py::TestSecurityScenarios -v -s

# ========== Individual E2E Tests ==========
pytest test_e2e_flow.py::test_01_mdms_draft_create -v -s
pytest test_e2e_flow.py::test_11_application_create -v -s
pytest test_e2e_flow.py::test_21_inbox_search -v -s

# ========== Clean & Rerun ==========
rm -f output/*.json output/*.txt
pytest test_e2e_flow.py -v -s --html=reports/e2e_report.html --self-contained-html

# ========== Debug Mode ==========
pytest test_e2e_flow.py -vv -s --tb=long
pytest tests/test_application.py::test_application_create -vv -s --tb=long

# ========== View Results ==========
cat output/mdms_response.json | jq .
cat output/application_response.json | jq .
open reports/e2e_report.html  # macOS
xdg-open reports/e2e_report.html  # Linux
```

---

## Resources

- [DIGIT Platform Documentation](https://core.digit.org/)
- [DIGIT Studio Guide](https://core.digit.org/guides/developer-guide/digit-studio)
- [Pytest Documentation](https://docs.pytest.org/)
- [Python Requests Library](https://requests.readthedocs.io/)

---

## Contributing

To contribute:
1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes (follow PEP 8 style guide)
3. Test: `pytest test_e2e_flow.py -v -s`
4. Commit: `git commit -m "Add: description"`
5. Create pull request with test results

---

## License

**Internal use only - eGovernments Foundation / DIGIT**

This automation suite is for internal use by eGovernments Foundation and authorized DIGIT platform partners. Provided "as is" without warranty.

---

**Version:** 1.0.0
**Last Updated:** 2026-01-27
**Maintained By:** eGovernments Foundation QA Team

For support, contact the DIGIT Studio team or refer to internal documentation.
