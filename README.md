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

### 2. Individual Test Modules

Run specific test phases:

```bash
# Service setup only
pytest tests/test_studio_services.py -v -s

# Application tests only
pytest tests/test_application.py -v -s

# All verification tests
pytest tests/test_*_search.py -v -s

# Specific test
pytest tests/test_workflow_search.py::test_workflow_validate -v -s
```

### 3. Negative/Security Tests (Data-Driven)

Run negative scenarios using `test_data_driven.py`:

```bash
# All negative tests
pytest tests/test_data_driven.py -v -s

# Specific negative test suites
pytest tests/test_data_driven.py::TestMDMSDraftNegative -v -s
pytest tests/test_data_driven.py::TestApplicationNegative -v -s
pytest tests/test_data_driven.py::TestSecurityScenarios -v -s
```

**Note:** Negative tests require `test_scenarios_config.json` file with test scenarios.

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
| `TestApplicationNegative` | Application creation failures |
| `TestWorkflowNegative` | Invalid workflow transitions |
| `TestChecklistNegative` | Checklist submission failures |
| `TestAuthenticationNegative` | Authentication failures |
| `TestSecurityScenarios` | XSS, SQL injection, script injection |
| `TestSearchNegative` | Invalid search parameters |

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
