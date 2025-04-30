# Remote Log Analysis Automation

## Overview

Remote Log Analysis Automation is a Python-based solution for automating the retrieval and analysis of log files from remote servers. This project demonstrates professional-grade automation for DevOps and system administration tasks by securely connecting via SSH/SFTP, downloading the latest log files from specified directories, parsing them for success, failure, or error patterns, and updating a tracking spreadsheet with the analysis results.

**Key Features:**

* Secure remote log retrieval using SSH/SFTP (`paramiko`)
* Intelligent log parsing with customizable success/error pattern detection
* Results tracking and visualization in Excel (`pandas`, `openpyxl`)
* Secure credential management with environment variables (`python-dotenv`)
* Docker-based test environment for development and demonstration
* Interactive Jupyter notebook support for step-by-step exploration

## Project Structure

```text
remote-log-analysis-automation/
├── .env
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
├── notebooks/
│   └── 01_setup_config.ipynb
├── src/
│   └── log_analyzer.py
├── sample_logs_generated/
│   ├── finance/
│   └── marketing/
├── data/
│   ├── log_analysis_tracker.xlsx
│   └── downloaded_logs/
└── logs/
    └── log_analyzer.log
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

* **No logs found** : Verify the paths in `log_analysis_tracker.xlsx` are correct
* **Pattern matching failures** : Review the success/error patterns in your `.env` file

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

*This project was created to demonstrate automation capabilities for system administration and DevOps tasks. It showcases skills in Python development, secure remote connections, data analysis, and Docker containerization.*
