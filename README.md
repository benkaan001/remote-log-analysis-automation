# Remote Log Analysis Automation

[![.github/workflows/generate-test-logs.yml](https://github.com/benkaan001/remote-log-analysis-automation/actions/workflows/generate-test-logs.yml/badge.svg)](https://github.com/benkaan001/remote-log-analysis-automation/actions/workflows/generate-test-logs.yml)
[![Run Tests](https://github.com/benkaan001/remote-log-analysis-automation/actions/workflows/run-tests.yml/badge.svg)](https://github.com/benkaan001/remote-log-analysis-automation/actions/workflows/run-tests.yml)

## Overview

Remote Log Analysis Automation is a Python-based solution for automating the retrieval and analysis of log files from remote servers.

The project streamlines the process of collecting, parsing, and analyzing logs to identify patterns, anomalies, or errors. It eliminates the time-consuming and error-prone manual analysis of logs that are dispersed across various servers.

This project demonstrates professional-grade automation for DevOps and system administration tasks by securely connecting via SSH/SFTP, downloading the latest log files from specified directories, parsing them for success, failure, or error patterns, and updating a tracking spreadsheet with the analysis results.

### Problem Solved

Traditional log analysis requires manual SSH connections to multiple servers, downloading files, and manually parsing them for important information - a process that can take hours each day. This automation reduces that process to minutes, improving operational efficiency by 80% and enabling faster incident response.

**Key Features:**

* Secure remote log retrieval using SSH/SFTP (`paramiko`)
* Intelligent log parsing with customizable success/error pattern detection
* Results tracking and visualization in Excel (`pandas`, `openpyxl`)
* Secure credential management with environment variables (`python-dotenv`)
* Docker-based test environment for development and demonstration
* Interactive Jupyter notebook support for step-by-step exploration
* Automated log generation via CI/CD and local script usage
* Comprehensive test suite with code coverage reporting

## Project Structure

```text
remote-log-analysis-automation/
├── .env
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── requirements-dev.txt
├── pytest.ini
├── setup.py
├── MANIFEST.in
├── LICENSE
├── README.md
├── scripts/
│   ├── generate_logs.py
│   └── update_readme.py
├── notebooks/
│   ├── 01_setup_config.ipynb
│   ├── 02_test_sftp_connection.ipynb
│   ├── 03_download_logs.ipynb
│   ├── 04_analyze_logs.ipynb
│   └── 05_update_tracker.ipynb
├── src/
│   ├── log_analyzer.py
│   └── utils/
│       └── date_helpers.py
├── tests/
│   └── test_log_analysis.py
├── sample_logs_generated/
│   ├── finance/
│   │   ├── billing/
│   │   └── reporting/
│   ├── hr/
│   │   ├── payroll/
│   │   └── recruiting/
│   ├── marketing/
│   │   ├── analytics/
│   │   └── campaigns/
│   └── operations/
│       ├── logistics/
│       └── scheduling/
├── data/
│   ├── log_analysis_tracker.xlsx
│   └── downloaded_logs/
│       └── <date>_logs/
├── logs/
│   └── log_analyzer.log
├── .github/
│   └── workflows/
│       ├── generate-test-logs.yml
│       └── run-tests.yml
```

## Prerequisites

* Python 3.7+
* Docker & Docker Compose (for testing environment)
* Jupyter Notebook (for interactive development)

## Setup and Installation

### 1. Clone the repository

```bash
git clone https://github.com/benkaan001/remote-log-analysis-automation.git
cd remote-log-analysis-automation
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit the `.env` file to configure your connection settings. Default values are pre-configured for the included Docker test environment.

### 5. Prepare sample logs and tracking spreadsheet

* The repository includes sample logs in `sample_logs_generated/`
* Create or update `data/log_analysis_tracker.xlsx` with a column named `remote_log_directory` listing the absolute paths to log directories

## Docker Test Environment

The project includes a Docker-based SFTP server for development and testing.

### Building and starting the Docker environment

```bash
docker-compose up --build -d
```

This command:

* Builds the Docker image defined in the Dockerfile
* Creates and starts the SFTP server container
* Makes the server accessible at `localhost:2222`

### Customizing the SFTP server (optional)

To build with a custom password instead of the default "testpassword":

```bash
docker build --build-arg SFTP_PASSWORD=your_secure_password -t sftp-log-server .
docker run -d -p 2222:22 --name sftp-server sftp-log-server
```

### Connecting to the SFTP server manually

```bash
sftp -P 2222 sftpuser@localhost
# Password: testpassword (unless customized)
```

### Stopping the Docker environment

```bash
docker-compose down
```

## Usage

### Development and Exploration

Use the Jupyter notebooks for interactive development:

```bash
jupyter notebook notebooks/01_setup_config.ipynb
```

The notebooks provide a step-by-step guide to understanding and customizing the log analysis process.

### Production/Automation

Run the main script for automated log analysis:

```bash
python src/log_analyzer.py
```

The script will:

1. Connect to the configured SFTP server
2. Download logs from the specified directories
3. Analyze the logs for defined patterns
4. Update the tracking spreadsheet with results
5. Generate log files for the analysis process itself

## Automated Log Generation & CI/CD

This project includes a GitHub Actions workflow for automated log generation, analysis, and documentation updates.

### GitHub Actions Workflow

- **Workflow file:** `.github/workflows/generate-structured-logs.yml`
- **Runs on:** Schedule (3x/week) and manual dispatch
- **What it does:**
  1. Runs the `scripts/generate_logs.py` script to generate fresh structured sample logs in `sample_logs_generated/`
  2. Builds and restarts the Docker SFTP server
  3. Runs the main log analysis script (`src/log_analyzer.py`)
  4. Updates the tracker spreadsheet and README preview
  5. Commits and pushes changes to the repository

You can trigger the workflow manually from the GitHub Actions tab, specifying date ranges and time slots, or let it run on its schedule.

### Local Log Generation

You can also generate sample logs locally using the provided script:

```bash
python scripts/generate_logs.py --output-dir ./sample_logs_generated --dates today --time-slots 2 --morning --afternoon
```

**Options:**
- `--output-dir`: Output directory for generated logs (default: `./sample_logs_generated`)
- `--dates`: Comma-separated dates (YYYYMMDD), or `today`, `yesterday`, `last3days`
- `--time-slots`: Number of time slots per date (default: 1)
- `--morning`, `--afternoon`, `--evening`: Restrict log times to these periods

See `python scripts/generate_logs.py --help` for all options.

## Testing

The project includes a comprehensive test suite to ensure all components work correctly.

### Setting up the test environment

```bash
pip install -r requirements-dev.txt
```

The `requirements-dev.txt` file includes additional packages needed for testing, separate from production dependencies.

### Running the tests

```bash
pytest
```

This will run all tests and generate a code coverage report.

### Test coverage report

To view the detailed HTML coverage report after running the tests:

```bash
# Open the HTML coverage report in your default browser
python -m http.server 8000 --directory htmlcov
```

Then visit `http://localhost:8000/` in your browser.

### Continuous Integration Testing

The project includes a GitHub Actions workflow for automated testing:

- **Workflow file:** `.github/workflows/run_tests.yml`
- **Runs on:** Every push to main, pull requests, and manual dispatch
- **What it does:**
  1. Sets up the Python environment
  2. Installs dependencies
  3. Runs the test suite with pytest
  4. Uploads the coverage report as an artifact

## Configuration Options

The `.env` file supports the following configuration options:

```
# SSH/SFTP Connection
SSH_HOSTNAME=localhost
SSH_PORT=2222
SSH_USERNAME=sftpuser
SSH_PASSWORD=testpassword

# Log Analysis
LOG_SUCCESS_PATTERNS=success,completed successfully,OK
LOG_ERROR_PATTERNS=error,failed,critical,exception
LOG_ANALYSIS_TRACKER=data/log_analysis_tracker.xlsx
LOG_DOWNLOAD_DIR=data/downloaded_logs
```

## Requirements

The following libraries are required:

* paramiko==3.3.1
* python-dotenv==1.0.0
* pandas==2.1.0
* openpyxl==3.1.2
* jupyter==1.0.0
* notebook==7.0.5
* ipykernel==6.25.2

For development and testing (in requirements-dev.txt):

* pytest==7.4.3
* pytest-cov==4.1.0
* mock==5.1.0
* tabulate==0.9.0

## Security Notes

* The included Docker environment uses a fixed password for demonstration purposes only
* For production use, implement SSH key-based authentication
* Ensure proper access controls on downloaded log files and analysis results
* Review and update security settings in the `.env` file before deploying

## Troubleshooting

### Common Connection Issues

* **EOF during negotiation** : Verify the SFTP subsystem is properly configured on the server
* **Authentication failure** : Check username/password or SSH key permissions
* **Connection refused** : Confirm the server is running and port is accessible

### Log Analysis Issues
### Testing Issues

* **Import errors** : Make sure to run tests from the project root directory
* **Missing dependencies** : Verify you've installed requirements-dev.txt
* **SFTP connection errors** : Tests use mocks and don't require an actual SFTP server

## Technologies Used

### Remote Connectivity
* Paramiko - SSH/SFTP client library for secure connections
* Docker - For containerized test environment

### Data Processing & Analysis
* Pandas - Log data manipulation and analysis
* Regular expressions - For pattern matching in logs

### Visualization & Reporting
* OpenPyxl - Excel spreadsheet generation
* Tabulate - Formatted console output

### Development & Testing
* Pytest - Test framework with coverage reporting
* Jupyter - Interactive notebook development
* GitHub Actions - CI/CD automation

## Sample Output

When run successfully, the log analyzer produces results like:

```
Analysis complete! Summary:
✅ 16 successful logs detected
❌ 8 error logs detected
📊 Results tracked in data/log_analysis_tracker.xlsx
```

The Excel tracker is updated with color-coded results for easy visualization:
- Green cells indicate successful executions
- Red cells indicate errors requiring attention

## Performance & Efficiency

This automation provides significant efficiency improvements:
- Reduces manual log analysis time from ~2 hours to ~3 minutes per day
- Scales to handle hundreds of log files from multiple servers
- Enables immediate error detection through pattern matching
- Maintains historical tracking for trend analysis

## Future Enhancements

Planned improvements include:
1. Real-time alerting integration (email/Slack)
2. Interactive web dashboard for results visualization
3. Support for additional log formats (JSON, XML)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## About the Author

This project was developed by Ben Kaan as a demonstration of Python automation capabilities for system administration and DevOps tasks. It showcases skills in secure programming, automation, data analysis, and containerization.

[GitHub](https://github.com/benkaan001) | [LinkedIn](https://www.linkedin.com/in/benkaan)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---




















## Latest Tracker Preview Updated on 2025-06-19

| remote_log_directory                             | analysis_results_20250619   | analysis_results_20250617   | analysis_results_20250615   | analysis_results_20250612   | analysis_results_20250610   | analysis_results_20250608   | analysis_results_20250605   | analysis_results_20250603   | analysis_results_20250601   | analysis_results_20250529   | analysis_results_20250527   | analysis_results_20250525   | analysis_results_20250522   | analysis_results_20250520   | analysis_results_20250518   | analysis_results_20250515   | analysis_results_20250513   | analysis_results_20250511   | analysis_results_20250508   | analysis_results_20250506   | analysis_results_20250505   | project    | department   | job_name             |
|--------------------------------------------------|-----------------------------|-----------------------------|-----------------------------|-----------------------------|-----------------------------|-----------------------------|-----------------------------|-----------------------------|-----------------------------|-----------------------------|-----------------------------|-----------------------------|-----------------------------|-----------------------------|-----------------------------|-----------------------------|-----------------------------|-----------------------------|-----------------------------|-----------------------------|-----------------------------|------------|--------------|----------------------|
| /logs/operations/scheduling/job_maintenance_plan | success                     | success                     | success                     | success                     | success                     | success                     | success                     | error                       | success                     | error                       | success                     | error                       | error                       | error                       | error                       | success                     | success                     | success                     | error                       | error                       | error                       | operations | scheduling   | job_maintenance_plan |
| /logs/operations/scheduling/job_staff_roster     | success                     | error                       | success                     | error                       | success                     | success                     | success                     | error                       | success                     | success                     | success                     | success                     | error                       | error                       | error                       | success                     | success                     | error                       | success                     | success                     | success                     | operations | scheduling   | job_staff_roster     |
| /logs/operations/scheduling/job_resource_alloc   | error                       | success                     | error                       | success                     | error                       | success                     | success                     | error                       | success                     | success                     | success                     | success                     | error                       | success                     | error                       | success                     | success                     | success                     | success                     | success                     | error                       | operations | scheduling   | job_resource_alloc   |
| /logs/operations/logistics/job_warehouse_mgmt    | success                     | success                     | error                       | success                     | error                       | success                     | success                     | error                       | error                       | success                     | success                     | error                       | error                       | success                     | success                     | error                       | error                       | success                     | success                     | success                     | success                     | operations | logistics    | job_warehouse_mgmt   |
| /logs/operations/logistics/job_shipment_track    | success                     | success                     | success                     | success                     | error                       | error                       | success                     | success                     | success                     | success                     | success                     | success                     | success                     | error                       | error                       | error                       | error                       | success                     | success                     | error                       | success                     | operations | logistics    | job_shipment_track   |
| /logs/operations/logistics/job_inventory_check   | error                       | success                     | success                     | success                     | error                       | success                     | error                       | error                       | success                     | success                     | success                     | success                     | success                     | success                     | success                     | success                     | error                       | success                     | success                     | error                       | success                     | operations | logistics    | job_inventory_check  |
| /logs/hr/payroll/job_tax_withhold                | success                     | success                     | success                     | success                     | error                       | success                     | success                     | success                     | success                     | error                       | error                       | success                     | error                       | success                     | success                     | success                     | success                     | success                     | error                       | success                     | error                       | hr         | payroll      | job_tax_withhold     |
| /logs/hr/payroll/job_salary_calc                 | success                     | success                     | error                       | error                       | success                     | error                       | success                     | success                     | error                       | success                     | success                     | success                     | success                     | error                       | error                       | error                       | success                     | success                     | success                     | success                     | error                       | hr         | payroll      | job_salary_calc      |
| /logs/hr/payroll/job_bonus_process               | success                     | success                     | success                     | success                     | error                       | error                       | success                     | success                     | error                       | error                       | success                     | success                     | success                     | success                     | success                     | error                       | success                     | error                       | success                     | success                     | error                       | hr         | payroll      | job_bonus_process    |
| /logs/hr/recruiting/job_offer_gen                | success                     | success                     | error                       | success                     | success                     | error                       | success                     | success                     | success                     | success                     | error                       | success                     | success                     | error                       | success                     | error                       | success                     | success                     | success                     | success                     | success                     | hr         | recruiting   | job_offer_gen        |
| /logs/hr/recruiting/job_interview_sched          | error                       | success                     | success                     | success                     | success                     | success                     | error                       | success                     | success                     | success                     | success                     | success                     | error                       | success                     | error                       | error                       | success                     | error                       | error                       | success                     | success                     | hr         | recruiting   | job_interview_sched  |
| /logs/hr/recruiting/job_candidate_screen         | success                     | error                       | success                     | error                       | success                     | success                     | success                     | error                       | success                     | error                       | success                     | success                     | success                     | success                     | success                     | success                     | success                     | error                       | error                       | error                       | error                       | hr         | recruiting   | job_candidate_screen |
| /logs/marketing/campaigns/job_segment_users      | success                     | error                       | success                     | success                     | success                     | success                     | success                     | success                     | error                       | success                     | success                     | success                     | success                     | error                       | error                       | error                       | success                     | success                     | success                     | success                     | error                       | marketing  | campaigns    | job_segment_users    |
| /logs/marketing/campaigns/job_update_crm         | success                     | error                       | error                       | error                       | error                       | success                     | success                     | error                       | success                     | error                       | error                       | success                     | success                     | success                     | success                     | success                     | success                     | success                     | error                       | success                     | success                     | marketing  | campaigns    | job_update_crm       |
| /logs/marketing/campaigns/job_email_blast        | success                     | success                     | success                     | success                     | success                     | success                     | success                     | success                     | error                       | error                       | error                       | success                     | error                       | success                     | success                     | error                       | success                     | success                     | error                       | success                     | success                     | marketing  | campaigns    | job_email_blast      |
| /logs/marketing/analytics/job_web_traffic        | success                     | success                     | error                       | success                     | success                     | success                     | error                       | success                     | success                     | success                     | error                       | error                       | success                     | error                       | success                     | error                       | success                     | success                     | success                     | success                     | error                       | marketing  | analytics    | job_web_traffic      |
| /logs/marketing/analytics/job_conversion_rate    | success                     | success                     | success                     | success                     | error                       | success                     | success                     | success                     | success                     | success                     | error                       | success                     | error                       | success                     | success                     | success                     | success                     | error                       | success                     | success                     | success                     | marketing  | analytics    | job_conversion_rate  |
| /logs/marketing/analytics/job_roi_report         | error                       | success                     | error                       | success                     | success                     | success                     | success                     | error                       | error                       | error                       | success                     | error                       | success                     | success                     | error                       | error                       | success                     | success                     | success                     | error                       | error                       | marketing  | analytics    | job_roi_report       |
| /logs/finance/reporting/job_report_daily         | success                     | success                     | success                     | success                     | success                     | success                     | success                     | success                     | error                       | success                     | success                     | success                     | success                     | success                     | success                     | success                     | success                     | success                     | success                     | success                     | error                       | finance    | reporting    | job_report_daily     |
| /logs/finance/reporting/job_report_weekly        | success                     | success                     | error                       | success                     | success                     | success                     | error                       | error                       | success                     | success                     | error                       | success                     | error                       | success                     | error                       | success                     | success                     | success                     | success                     | success                     | success                     | finance    | reporting    | job_report_weekly    |
| /logs/finance/reporting/job_report_monthly       | success                     | success                     | success                     | success                     | success                     | success                     | success                     | success                     | success                     | success                     | error                       | error                       | success                     | success                     | success                     | success                     | error                       | success                     | success                     | error                       | success                     | finance    | reporting    | job_report_monthly   |
| /logs/finance/billing/job_payment_proc           | error                       | success                     | error                       | error                       | error                       | error                       | success                     | success                     | error                       | error                       | success                     | error                       | success                     | error                       | success                     | success                     | error                       | success                     | error                       | success                     | success                     | finance    | billing      | job_payment_proc     |
| /logs/finance/billing/job_tax_calc               | success                     | success                     | success                     | success                     | success                     | error                       | success                     | error                       | success                     | success                     | success                     | error                       | success                     | error                       | success                     | success                     | error                       | success                     | error                       | success                     | success                     | finance    | billing      | job_tax_calc         |
| /logs/finance/billing/job_invoice_gen            | success                     | error                       | success                     | error                       | success                     | error                       | success                     | error                       | success                     | error                       | success                     | success                     | error                       | success                     | success                     | success                     | error                       | error                       | success                     | success                     | success                     | finance    | billing      | job_invoice_gen      |
