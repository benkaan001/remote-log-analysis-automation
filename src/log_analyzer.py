import os
import sys
import pandas as pd
import paramiko
from datetime import date
import logging
from dotenv import load_dotenv

# ==============================================================================
# Configuration Constants
# ==============================================================================

# --- File Paths ---
PROJECT_ROOT = os.getcwd()
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
LOGS_DIR = os.path.join(PROJECT_ROOT, 'logs') # For application logs
ANALYSIS_TRACKER_FILENAME = 'log_analysis_tracker.xlsx'
ANALYSIS_TRACKER_PATH = os.path.join(DATA_DIR, ANALYSIS_TRACKER_FILENAME)
LOCAL_LOG_STORAGE_BASE = os.path.join(DATA_DIR, 'downloaded_logs') # Base dir for downloaded logs

# --- SFTP Connection ---
SFTP_PORT = 2222 # Port for the Docker SFTP server

# --- Analysis ---
LOG_PATH_COLUMN = 'remote_log_directory' # Excel column with remote paths
RESULTS_COLUMN_PREFIX = 'analysis_results_' # Prefix for results columns in Excel
SUCCESS_KEYWORD = 'Execution Return Code: 0'
FAILURE_KEYWORD = '*** Failure'
ERROR_KEYWORD = '*** Error:'

# ==============================================================================
# Logging Setup
# ==============================================================================

# Ensure the application log directory exists
os.makedirs(LOGS_DIR, exist_ok=True)
APP_LOG_FILE = os.path.join(LOGS_DIR, 'log_analyzer.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(funcName)s] - %(message)s',
    handlers=[
        logging.FileHandler(APP_LOG_FILE), # Log to a file
        logging.StreamHandler(sys.stdout) # Also log to console
    ]
)

# ==============================================================================
# Helper Functions
# ==============================================================================

def load_environment_variables() -> dict:
    """
    Loads required SSH environment variables directly from the environment
    (e.g., set by GitHub Actions secrets).

    Returns:
        dict: A dictionary containing SSH credentials and hostname.

    Raises:
        ValueError: If any required environment variable is missing.
    """
    load_dotenv()
    logging.info("Loading environment variables using os.getenv()...")
    # Relies on the variables being present in the execution environment.

    required_vars = ["SSH_HOSTNAME", "SSH_USERNAME", "SSH_PASSWORD"]
    env_vars = {var: os.getenv(var) for var in required_vars}

    missing_vars = [var for var, value in env_vars.items() if value is None]
    if missing_vars:
        # Log the specific missing variables for easier debugging in Actions
        error_msg = f"Missing required environment variables: {', '.join(missing_vars)}. Check Actions secrets or local environment."
        logging.error(error_msg)
        raise ValueError(error_msg)

    logging.info("Environment variables loaded successfully via os.getenv().")
    logging.info(f"SSH_HOSTNAME found: {env_vars.get('SSH_HOSTNAME')}")
    logging.info(f"SSH_USERNAME found: {'Yes' if env_vars.get('SSH_USERNAME') else 'No'}")
    logging.info(f"SSH_PASSWORD found: {'Yes' if env_vars.get('SSH_PASSWORD') else 'No'}")

    return env_vars

def get_analysis_tracker(filename: str, required_col: str) -> pd.DataFrame | None:
    """
    Loads the analysis tracker Excel file into a pandas DataFrame.

    Args:
        filename (str): The path to the Excel tracker file.
        required_col (str): The name of the column that must exist.

    Returns:
        pd.DataFrame or None: The loaded DataFrame, or None if loading fails.
    """
    if not os.path.exists(filename):
        logging.error(f"Tracker file not found: '{filename}'. Please create it.")
        return None

    logging.info(f"Loading tracker file: '{filename}'")
    try:
        df = pd.read_excel(filename, header=0, engine='openpyxl')
        logging.info(f"Successfully loaded tracker with shape: {df.shape}")
        if required_col not in df.columns:
            logging.error(f"Tracker file '{filename}' is missing the required column: '{required_col}'")
            return None
        logging.info(f"Required column '{required_col}' found in tracker.")
        return df
    except Exception as e:
        logging.error(f"Failed to read tracker file '{filename}': {e}")
        return None # Return None on failure

def get_current_date_string() -> str:
    """Returns today's date as a string in 'YYYYMMDD' format."""
    return date.today().strftime('%Y%m%d')

def create_log_download_directory(base_dir: str, date_string: str) -> str:
    """
    Creates the directory for storing logs downloaded on a specific date.

    Args:
        base_dir (str): The base directory for storing logs.
        date_string (str): The date string (YYYYMMDD).

    Returns:
        str: The full path to the created directory.

    Raises:
        OSError: If directory creation fails.
    """
    log_dir = os.path.join(base_dir, f"{date_string}_logs")
    if not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir)
            logging.info(f"Created local log directory: {log_dir}")
        except OSError as e:
            logging.error(f"Failed to create directory {log_dir}: {e}")
            raise # Re-raise the error
    return log_dir

def download_latest_logs(df: pd.DataFrame, ssh_config: dict, local_log_dir: str) -> list:
    """
    Connects via SFTP and downloads the latest log file from each directory
    specified in the DataFrame to the local log directory.

    Args:
        df (pd.DataFrame): DataFrame containing log paths.
        ssh_config (dict): Dictionary with SSH connection details.
        local_log_dir (str): Local directory to save downloaded logs.

    Returns:
        list: A list of remote paths that could not be accessed or processed.

    Raises:
        paramiko exceptions on connection/authentication failure.
        Other exceptions on unexpected errors.
    """
    problematic_remote_paths = []
    downloaded_log_filenames = set()

    logging.info(f"Starting log download process...")

    # Create SSH connection and SFTP session
    with paramiko.SSHClient() as ssh_client:
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        logging.info(
            f"Attempting SSH connection to: "
            f"{ssh_config.get('SSH_HOSTNAME')}:{SFTP_PORT} "
            f"as user '{ssh_config.get('SSH_USERNAME')}'..."
        )
        ssh_client.connect(
            hostname=ssh_config.get('SSH_HOSTNAME'),
            port=SFTP_PORT,
            username=ssh_config.get('SSH_USERNAME'),
            password=ssh_config.get('SSH_PASSWORD'),
            timeout=15 # Slightly longer timeout
        )
        logging.info("SSH connection established successfully.")

        with ssh_client.open_sftp() as sftp_client:
            logging.info("SFTP session opened successfully.")

            for index, row in df.iterrows():
                remote_path = str(row[LOG_PATH_COLUMN]) if pd.notna(row[LOG_PATH_COLUMN]) else None
                if not remote_path:
                    logging.warning(f"Skipping row {index}: Missing or invalid log path.")
                    continue

                logging.info(f"Processing remote path: {remote_path}")
                latest_log_filename = None # Reset for each path
                try:
                    remote_files = sftp_client.listdir(remote_path)
                    if not remote_files:
                        logging.warning(f"No log files found in: {remote_path}")
                        if remote_path not in problematic_remote_paths:
                             problematic_remote_paths.append(remote_path)
                        continue

                    latest_log_filename = max(remote_files)
                    logging.info(f"Latest log file identified: {latest_log_filename}")

                    if latest_log_filename in downloaded_log_filenames:
                        logging.info(f"Skipping duplicate download for: {latest_log_filename}")
                        continue

                    full_remote_log_path = f"{remote_path.rstrip('/')}/{latest_log_filename}"
                    local_log_path = os.path.join(local_log_dir, latest_log_filename)

                    logging.info(f"Attempting download: '{full_remote_log_path}' -> '{local_log_path}'")
                    sftp_client.get(full_remote_log_path, local_log_path)
                    downloaded_log_filenames.add(latest_log_filename)
                    logging.info(f"Successfully downloaded.")

                except FileNotFoundError:
                     logging.error(f"Remote path not found: {remote_path}")
                     if remote_path not in problematic_remote_paths:
                         problematic_remote_paths.append(remote_path)
                except IOError as io_err:
                    logging.error(f"SFTP Error accessing {remote_path}: {io_err}")
                    if remote_path not in problematic_remote_paths:
                         problematic_remote_paths.append(remote_path)
                except Exception as e:
                    log_file_ref = latest_log_filename if latest_log_filename else 'unknown file'
                    logging.error(f"Unexpected error processing {remote_path} or downloading {log_file_ref}: {e}")
                    if remote_path not in problematic_remote_paths:
                         problematic_remote_paths.append(remote_path)

    logging.info("Log download process finished.")
    if problematic_remote_paths:
         unique_problems = sorted(list(set(problematic_remote_paths)))
         logging.warning(f"Could not access or process the following {len(unique_problems)} unique remote paths: {unique_problems}")
    return problematic_remote_paths

def analyze_downloaded_logs(local_log_dir: str) -> dict:
    """
    Analyzes the downloaded log files found in the specified local directory.

    Args:
        local_log_dir (str): The local directory containing downloaded logs.

    Returns:
        dict: A dictionary mapping log filenames to their determined status.
              Returns {'error': 'directory_not_found'} if directory is missing.
              Returns empty dict if directory is empty.
    """
    log_analysis_results = {}
    logging.info(f"Starting analysis of logs in directory: {local_log_dir}")

    if not os.path.isdir(local_log_dir):
        logging.error(f"Local log directory not found: {local_log_dir}. Cannot analyze.")
        return {'error': 'directory_not_found'}

    try:
        local_log_files = os.listdir(local_log_dir)
    except Exception as e:
        logging.error(f"Error listing local directory {local_log_dir}: {e}")
        return {'error': 'directory_list_error'}


    if not local_log_files:
        logging.warning(f"No log files found in local directory: {local_log_dir}")
        return {}

    logging.info(f"Found {len(local_log_files)} log files to analyze.")

    for log_filename in local_log_files:
        local_log_path = os.path.join(local_log_dir, log_filename)
        analysis_status = 'unknown'
        try:
            logging.debug(f"Analyzing file: {log_filename}")
            with open(local_log_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.readlines()
                log_found_keyword = False
                for line in reversed(content):
                    if SUCCESS_KEYWORD in line:
                        analysis_status = 'success'; log_found_keyword = True; break
                    elif FAILURE_KEYWORD in line:
                        analysis_status = 'failure'; log_found_keyword = True
                        logging.warning(f"Found failure keyword in {log_filename}: {line.strip()}")
                        break
                    elif ERROR_KEYWORD in line:
                        analysis_status = 'error'; log_found_keyword = True
                        logging.warning(f"Found error keyword in {log_filename}: {line.strip()}")
                        break
                if not log_found_keyword:
                     logging.info(f"No specific keywords found in {log_filename}, status set to 'unknown'.")
        except FileNotFoundError:
             logging.error(f"Log file vanished during analysis?: {local_log_path}")
             analysis_status = 'not_found'
        except Exception as e:
            logging.error(f"Error reading or parsing log file {log_filename}: {e}")
            analysis_status = 'parse_error'
        log_analysis_results[log_filename] = analysis_status
        logging.info(f"Analysis result for '{log_filename}': {analysis_status}")

    logging.info("Log analysis finished.")
    return log_analysis_results

def update_tracker_with_results(
    df: pd.DataFrame,
    analysis_results: dict,
    date_string: str,
    problematic_remote_paths: list
) -> pd.DataFrame:
    """
    Updates the DataFrame with log analysis results for the given date.

    Args:
        df (pd.DataFrame): The DataFrame to update.
        analysis_results (dict): Dictionary mapping log filenames to statuses.
        date_string (str): The current date string (YYYYMMDD) for the results column.
        problematic_remote_paths (list): List of remote paths that had download/access issues.

    Returns:
        pd.DataFrame: The updated DataFrame.
    """
    results_col = f"{RESULTS_COLUMN_PREFIX}{date_string}"
    logging.info(f"Updating tracker DataFrame with results in column: {results_col}")

    if results_col not in df.columns:
        try:
            insert_pos = df.columns.get_loc(LOG_PATH_COLUMN) + 1
        except KeyError:
            insert_pos = len(df.columns)
        df.insert(insert_pos, results_col, 'not_analyzed')
        logging.info(f"Added new results column: {results_col}")
    else:
        logging.info(f"Resetting existing results column: {results_col}")
        df[results_col] = 'not_analyzed'

    analyzed_rows = set()
    for log_filename, status in analysis_results.items():
        if status in ['directory_not_found', 'directory_list_error']: continue # Skip internal error markers

        try:
            base_job_name = log_filename.split('-')[0] if '-' in log_filename else os.path.splitext(log_filename)[0]
        except Exception:
            logging.warning(f"Could not extract base job name from log filename: {log_filename}")
            continue

        matched_indices = []
        for index, row in df.iterrows():
             remote_path = str(row[LOG_PATH_COLUMN]) if pd.notna(row[LOG_PATH_COLUMN]) else None
             if remote_path:
                 path_identifier = os.path.basename(remote_path.rstrip('/'))
                 if base_job_name == path_identifier:
                     matched_indices.append(index)

        if matched_indices:
             for idx in matched_indices:
                 df.loc[idx, results_col] = status
                 analyzed_rows.add(idx)
             logging.info(f"Matched '{log_filename}' (status: {status}) to {len(matched_indices)} tracker rows (Indices: {matched_indices}).")
        else:
             logging.warning(f"Could not match log file '{log_filename}' to any row in the tracker based on path identifier '{base_job_name}'.")

    logging.info("Performing final status updates for rows without direct log matches...")
    for index, row in df.iterrows():
        current_status = df.loc[index, results_col]
        remote_path = str(row[LOG_PATH_COLUMN]) if pd.notna(row[LOG_PATH_COLUMN]) else None

        if remote_path in problematic_remote_paths:
            if current_status == 'not_analyzed':
                 df.loc[index, results_col] = 'access_error'
                 logging.debug(f"Row {index}: Marked as 'access_error' due to problematic path '{remote_path}'.")
        elif index not in analyzed_rows and current_status == 'not_analyzed':
            if not remote_path:
                df.loc[index, results_col] = 'missing_path'
                logging.debug(f"Row {index}: Marked as 'missing_path'.")
            else:
                df.loc[index, results_col] = 'log_not_found_or_analyzed'
                logging.debug(f"Row {index}: Marked as 'log_not_found_or_analyzed' for path '{remote_path}'.")

    logging.info("Tracker update process finished.")
    return df

def save_analysis_results(df: pd.DataFrame, filename: str):
    """
    Saves the updated DataFrame back to the Excel tracker file.

    Args:
        df (pd.DataFrame): The DataFrame with analysis results.
        filename (str): The path to the Excel tracker file.

    Raises:
        PermissionError: If the file cannot be written due to permissions.
        Exception: For other file saving errors.
    """
    logging.info(f"Attempting to save updated tracker to: {filename}")
    try:
        df.to_excel(filename, index=False, engine='openpyxl')
        logging.info(f"Analysis results saved successfully to: {filename}")
    except PermissionError as pe:
         logging.error(f"Permission denied saving analysis results to '{filename}'. Is the file open?")
         raise pe # Re-raise permission error
    except Exception as e:
        logging.error(f"Failed to save analysis results to '{filename}': {e}")
        raise e # Re-raise other errors

# ==============================================================================
# Main Execution Logic
# ==============================================================================

def main():
    """
    Main function to orchestrate the log analysis process.
    """
    logging.info("--- Starting Remote Log Analysis Script ---")
    exit_code = 0 # Default to success

    try:
        # 1. Load Config
        logging.info("Step 1: Loading configuration...")
        # Directly reads from environment variables set by Actions secrets or local env
        ssh_config = load_environment_variables()
        analysis_df = get_analysis_tracker(ANALYSIS_TRACKER_PATH, LOG_PATH_COLUMN)
        if analysis_df is None:
            raise ValueError("Failed to load or validate the analysis tracker Excel file.")
        logging.info("Configuration loaded successfully.")

        # 2. Prepare Directories
        logging.info("Step 2: Preparing local directories...")
        date_string = get_current_date_string()
        local_log_dir = create_log_download_directory(LOCAL_LOG_STORAGE_BASE, date_string)
        logging.info(f"Local directory for today's logs: {local_log_dir}")

        # 3. Download Logs
        logging.info("Step 3: Downloading logs...")
        problematic_paths = download_latest_logs(analysis_df, ssh_config, local_log_dir)
        logging.info("Log download completed.")
        if problematic_paths:
             logging.warning(f"Issues encountered downloading logs for {len(problematic_paths)} paths.")

        # 4. Analyze Logs
        logging.info("Step 4: Analyzing downloaded logs...")
        analysis_results_dict = analyze_downloaded_logs(local_log_dir)
        if 'error' in analysis_results_dict:
             # Handle cases where analysis couldn't run (e.g., dir missing)
             raise RuntimeError(f"Log analysis failed: {analysis_results_dict['error']}")
        logging.info("Log analysis completed.")

        # 5. Update Tracker
        logging.info("Step 5: Updating analysis tracker...")
        updated_df = update_tracker_with_results(
            analysis_df.copy(), # Work on a copy
            analysis_results_dict,
            date_string,
            problematic_paths
        )
        logging.info("Tracker update completed.")

        # 6. Save Results
        logging.info("Step 6: Saving updated tracker...")
        save_analysis_results(updated_df, ANALYSIS_TRACKER_PATH)
        logging.info("Updated tracker saved successfully.")

        logging.info("--- Remote Log Analysis Script Finished Successfully ---")

    # Specific exceptions first
    except FileNotFoundError as fnf_err:
        logging.error(f"Configuration Error: Required file not found: {fnf_err}")
        exit_code = 1
    except ValueError as val_err:
        logging.error(f"Configuration or Data Error: {val_err}")
        exit_code = 1
    except paramiko.AuthenticationException:
        logging.error("Critical Error: SSH Authentication failed. Verify credentials (secrets in Actions).")
        exit_code = 2
    except paramiko.SSHException as ssh_ex:
        logging.error(f"Critical Error: SSH connection problem: {ssh_ex}")
        exit_code = 2
    except TimeoutError:
        logging.error("Critical Error: Connection timed out.")
        exit_code = 2
    except EOFError as eof_err:
         logging.error(f"Critical Error: SFTP negotiation failed (EOFError): {eof_err}. Check Dockerfile SSH config.")
         exit_code = 2
    except PermissionError as pe:
         logging.error(f"File System Error: Could not save tracker file due to permissions: {pe}")
         exit_code = 3
    except RuntimeError as rt_err:
         logging.error(f"Runtime Error during processing: {rt_err}")
         exit_code = 4
    # Catch-all for any other unexpected errors
    except Exception as e:
        logging.exception("An unexpected critical error occurred during script execution.") # Logs full traceback
        exit_code = 5
    finally:
        logging.info(f"--- Script finished with exit code {exit_code} ---")
        sys.exit(exit_code) # Exit with appropriate code

# ==============================================================================
# Script Entry Point
# ==============================================================================

if __name__ == "__main__":
    main()
