# Automated QA & Reporting Pipeline for CI

This repository implements a modular, production-grade continuous integration workflow for a multi-app Django environment.  
It integrates **Pytest**, **Cypress**, and **Allure Framework** to provide full-stack test coverage, result aggregation, and visual reporting.

## System Architecture

### Core Components

The pipeline orchestrates multi-layered testing across backend and frontend domains, normalizes disparate test outputs into unified data structures, and publishes interactive reports through static hosting infrastructure.

**Application Coverage:**
- `base`: Full-stack testing (Django backend + Cypress E2E)
- `notifications`: Backend testing suite

**Testing Framework Integration:**
- Backend: Pytest with coverage analysis
- Frontend: Cypress E2E automation
- Reporting: JUnit XML, Cobertura coverage, Allure visualization

**Infrastructure:**
- CI/CD: GitHub Actions with matrix parallelization
- Deployment: GitHub Pages for static report hosting
- Data Export: CSV/JSON with workflow telemetry

### Processing Pipeline


<img width="800" height="1050" alt="processing_pipeline" src="https://github.com/user-attachments/assets/c8632d40-8f26-4df2-a817-9807102939cc" />


## Development Workflow

### Environment Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Frontend testing prerequisites
npm ci
```

### Backend Test Execution

**Base Application:**
```bash
pytest -q base/tests \
  --junitxml=reports/base/backend/pytest.xml \
  --cov=base \
  --cov-report=xml:reports/base/backend/coverage.xml \
  --alluredir=reports/base/backend/allure-results
```

**Notifications Application:**
```bash
pytest -q notifications/tests \
  --junitxml=reports/notifications/backend/pytest.xml \
  --cov=notifications \
  --cov-report=xml:reports/notifications/backend/coverage.xml \
  --alluredir=reports/notifications/backend/allure-results
```

### Frontend Test Execution

```bash
python manage.py migrate --noinput
python manage.py runserver 0.0.0.0:8000 &
npx cypress run --browser chrome
```

### Data Processing

**Per-Job Conversion:**
```bash
python scripts/convert_junit_to_csv.py \
  "reports/base/backend/pytest.xml" \
  "reports/base/backend/tests_backend.csv" \
  "base" "pytest" "<run_id>" "<run_number>" "<sha>" "<branch>" "<workflow>"
```

**Cross-Suite Aggregation:**
```bash
python scripts/merge_junit_tests.py 'reports/**/*.xml' reports/out \
  "<run_id>" "<run_number>" "<sha>" "<branch>" "<workflow>"
```

### Local Report Preview

```bash
allure serve reports/base/backend/allure-results
```

## CI/CD Configuration

### Primary Pipeline (`main-CI.yml`)

**Trigger Conditions:**
- Pull requests targeting `main` and `HN_feature_GitHub_Test_Exports`
- Manual workflow dispatch

**Execution Strategy:**

Matrix-based parallelization across applications with conditional frontend execution.

**Per-Application Workflow:**

1. Dependency installation and environment configuration
2. Backend test suite execution with coverage analysis
3. JUnit XML enrichment with workflow metadata
4. Artifact upload to GitHub Actions storage
5. Conditional frontend testing for applicable applications
6. Django server initialization and Cypress execution
7. Frontend test result transformation and artifact upload

**Aggregation Phase:**

1. Multi-artifact download from all matrix jobs
2. Unified dataset generation (`all_tests.csv`, `all_tests.json`)
3. Consolidated artifact upload for downstream consumption

### Report Generation Pipeline (`allure.yml`)

**Trigger:** Completion event from `main-CI` workflow

**Execution Steps:**

1. Artifact retrieval from completed CI run
2. Allure result consolidation across all test suites
3. Static site generation with historical trending
4. GitHub Pages deployment with artifact retention

## Data Artifacts

### Generated Outputs

| Artifact Path | Description | Format |
|--------------|-------------|---------|
| `reports/<app>/backend/pytest.xml` | Backend test results | JUnit XML |
| `reports/<app>/backend/coverage.xml` | Code coverage metrics | Cobertura XML |
| `reports/<app>/backend/allure-results/` | Allure raw results | Directory |
| `reports/<app>/frontend/*.xml` | Frontend test results | JUnit XML |
| `collected/out/all_tests.csv` | Unified test dataset | CSV |
| `collected/out/all_tests.json` | Unified test dataset | JSON |
| GitHub Pages | Interactive test report | Static HTML |

### Data Schema

Exported datasets include comprehensive metadata for analytical consumption:

- `django_app`: Application identifier  
- `test_type`: Type of test (e.g., unit, integration)  
- `suite`: Test suite classification  
- `class`: Test class/module path  
- `test_name`: Individual test identifier  
- `status`: Execution outcome (passed/failed/skipped)  
- `duration_seconds`: Execution time (seconds)  
- `test_file`: Source file location  
- `error_message`: Failure diagnostics or skip reason  
- `execution_timestamp`: Execution timestamp (ISO 8601)  
- `job_uid`: GitHub Actions job unique identifier  
- `job_name`: GitHub Actions job name  
- `run_id`: GitHub Actions workflow run identifier  
- `run_number`: Sequential run number  
- `commit_sha`: Git commit hash  
- `ref_name`: Reference name (branch or tag)  
- `target_branch`: Target branch name (where PR is merged)  
- `source_branch`: Source branch name (where PR originates)  
- `pr_title`: Pull request title  
- `workflow_name`: Workflow identifier  
- `source_file`: Source file path  

## Integration Capabilities

### Visualization Platforms

- **Allure Framework**: Built-in interactive reporting with trend analysis
- **Grafana**: CSV/JSON consumption via Infinity data source
- **Apache Superset**: Direct data source integration for custom dashboards
- **Custom Analytics**: RESTful consumption of structured test data

### External Storage

Optional S3 integration for long-term artifact retention and cross-system data access.

### Notification Channels

- GitHub Checks API (native integration)
- Extensible webhook support for Slack, Microsoft Teams, or email notification systems

## Future Enhancements

- Matrix expansion for additional Django applications
- Statistical flaky test detection and regression analysis
- Role-based access control for sensitive test artifacts
- Allure historical data retention across workflow executions

