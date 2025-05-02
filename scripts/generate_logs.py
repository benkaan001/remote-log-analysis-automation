#!/usr/bin/env python3
"""
Script to generate fake log data for the remote-log-analysis-automation project.
This is mostly for testing and demo purposes.

TODO: Maybe add more randomness to error messages or log structure later.
"""

import os
import random
import datetime
import argparse
from pathlib import Path

# --- Domain/job structure ---
LOG_STRUCTURE = {
    # Finance jobs
    "finance": {
        "billing": [
            "job_invoice_gen",
            "job_payment_proc",
            "job_tax_calc"
        ],
        "reporting": [
            "job_report_daily",
            "job_report_monthly",
            "job_report_weekly"
        ]
    },
    # Marketing jobs
    "marketing": {
        "analytics": [
            "job_conversion_rate",
            "job_roi_report",
            "job_web_traffic"
        ],
        "campaigns": [
            "job_email_blast",
            "job_segment_users",
            "job_update_crm"
        ]
    }
}

# Add more domains (could be loaded from config in future)
ADDITIONAL_DOMAINS = {
    "operations": {
        "logistics": [
            "job_inventory_check",
            "job_shipment_track",
            "job_warehouse_mgmt"
        ],
        "scheduling": [
            "job_staff_roster",
            "job_resource_alloc",
            "job_maintenance_plan"
        ]
    },
    "hr": {
        "recruiting": [
            "job_candidate_screen",
            "job_interview_sched",
            "job_offer_gen"
        ],
        "payroll": [
            "job_salary_calc",
            "job_bonus_process",
            "job_tax_withhold"
        ]
    }
}
LOG_STRUCTURE.update(ADDITIONAL_DOMAINS)

USER_NAMES = {
    "finance": ["finance_user1", "accountant1", "finance_admin"],
    "marketing": ["marketing_user1", "analyst1", "campaign_manager"],
    "operations": ["ops_user1", "logistics_manager", "scheduler"],
    "hr": ["hr_user1", "recruiter1", "payroll_admin"]
}
DEFAULT_USERS = ["system_user", "admin_user", "batch_user"]

EXEC_SCOPES = ["PROD", "DEV", "TEST", "UAT"]

# --- Error scenarios ---
ERROR_SCENARIOS = {
    0: [
        "Script executed successfully.",
        "All data processed without errors.",
        "Report generated successfully.",
        "Analysis completed with no issues.",
        "Data extraction and transformation successful."
    ],
    1: [
        "Script completed with warnings: Missing optional parameters.",
        "Non-critical data quality issue detected: Null values in optional fields.",
        "Performance warning: Query execution exceeded threshold.",
        "Warning: Some metrics might be incomplete due to data latency."
    ],
    2: [
        "Configuration warning: Using default settings due to missing config.",
        "Environment variable not set, using fallback configuration.",
        "Configuration file contains deprecated parameters.",
        "Resource allocation sub-optimal, consider adjusting configuration."
    ],
    4: [
        "Division by zero encountered in calculation.",
        "Failed to connect to dependent data source.",
        "Invalid data format in source table.",
        "Query timeout after 60 seconds.",
        "Memory allocation error during data processing.",
        "Unexpected NULL values in required columns."
    ],
    8: [
        "Critical error: Database connection failed after 3 retries.",
        "Fatal error in data processing pipeline.",
        "Script terminated due to insufficient permissions.",
        "Severe data integrity issue detected.",
        "Required table not found in database."
    ]
}

DOMAIN_ERRORS = {
    "finance": {
        "billing": [
            "Invoice generation failed: Invalid customer account.",
            "Payment processing error: Gateway timeout.",
            "Tax calculation failed: Missing tax rate for region."
        ],
        "reporting": [
            "Report generation failed: Data source unavailable.",
            "Monthly aggregation error: Inconsistent daily data.",
            "Weekly report failed: Missing required metrics."
        ]
    },
    "marketing": {
        "analytics": [
            "Conversion calculation error: Missing funnel stage data.",
            "ROI calculation failed: Revenue data unavailable.",
            "Traffic analysis error: Invalid source attribution."
        ],
        "campaigns": [
            "Email blast failed: SMTP server connection error.",
            "User segmentation failed: Invalid criteria specified.",
            "CRM update failed: API authentication error."
        ]
    },
    "operations": {
        "logistics": [
            "Logistics generation failed: Invalid customer account.",
            "Logistics processing error: Gateway timeout.",
            "Logistics calculation failed: Missing tax rate for region."
        ],
        "scheduling": [
            "Scheduling generation failed: Data source unavailable.",
            "Scheduling aggregation error: Inconsistent daily data.",
            "Scheduling report failed: Missing required metrics."
        ]
    },
    "hr": {
        "recruiting": [
            "Recruiting generation failed: Data source unavailable.",
            "Recruiting aggregation error: Inconsistent daily data.",
            "Recruiting report failed: Missing required metrics."
        ],
        "payroll": [
            "Payroll generation failed: Data source unavailable.",
            "Payroll aggregation error: Inconsistent daily data.",
            "Payroll report failed: Missing required metrics."
        ]
    }
}


def get_domain_specific_error(domain, subdomain, return_code):
    # If success, just return a generic success message
    if return_code <= 0:
        return random.choice(ERROR_SCENARIOS[0])
    # Try to get a domain-specific error (70% chance)
    if domain in DOMAIN_ERRORS and subdomain in DOMAIN_ERRORS[domain] and random.random() < 0.7:
        return random.choice(DOMAIN_ERRORS[domain][subdomain])
    # Otherwise, fallback to generic error
    return random.choice(ERROR_SCENARIOS[return_code])


def generate_time(date_str, time_range=None):
    # Returns a random time string in HHMMSS format
    if time_range:
        start_hour, end_hour = time_range
    else:
        start_hour, end_hour = 0, 23
    hour = random.randint(start_hour, end_hour)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return f"{hour:02d}{minute:02d}{second:02d}"


def generate_log_content(date_str, start_time, domain, sub_domain, job_name, user_name=None, exec_scope=None):
    # Pick user and exec scope if not given
    if user_name is None:
        user_name = random.choice(USER_NAMES.get(domain, DEFAULT_USERS))
    if exec_scope is None:
        exec_scope = random.choice(EXEC_SCOPES)
    # Simulate execution time
    execution_seconds = random.randint(5, 60)
    end_time_dt = datetime.datetime.strptime(start_time, "%H%M%S") + datetime.timedelta(seconds=execution_seconds)
    end_time = end_time_dt.strftime("%H%M%S")
    # Weighted random for return code
    return_code = random.choices([0, 1, 2, 4, 8], weights=[70, 10, 5, 10, 5], k=1)[0]
    result_message = get_domain_specific_error(domain, sub_domain, return_code)
    display_job_name = job_name.replace("job_", "").replace("_", " ").upper()
    # Build log lines
    log_lines = []
    log_lines.append(f"{domain.upper()} {sub_domain.upper()} JOB LOG {date_str}_{start_time}")
    log_lines.append(f"----------------------")
    log_lines.append(f"{date_str}_{start_time} ## Passed Parameter Values:")
    log_lines.append(f"{date_str}_{start_time} DOMAIN: {domain}")
    log_lines.append(f"{date_str}_{start_time} SUB_DOMAIN: {sub_domain}")
    log_lines.append(f"{date_str}_{start_time} USER_NAME: {user_name}")
    log_lines.append(f"{date_str}_{start_time} TABLE_NAME: {job_name}")
    log_lines.append(f"{date_str}_{start_time} EXEC_SCOPE: {exec_scope}")
    log_lines.append("")
    log_lines.append(f"{date_str}_{start_time} ## Derived Variable Values:")
    log_lines.append(f"{date_str}_{start_time} STARTTIME: {start_time}")
    log_lines.append(f"{date_str}_{start_time} LOGDATE: {date_str}_{start_time}")
    log_lines.append(f"{date_str}_{start_time} JOB={job_name}")
    log_lines.append("")
    log_lines.append(f"{date_str}_{start_time} ###############################################################")
    log_lines.append(f"{date_str}_{start_time} ### RUNNING {display_job_name} SCRIPT")
    log_lines.append(f"{date_str}_{start_time} ###############################################################")
    log_lines.append("")
    script_path = f"/scripts/{domain}/{sub_domain}/{job_name}/{job_name}.sql"
    log_lines.append(f"{date_str}_{start_time} ## Checking if script exists")
    log_lines.append(f"{date_str}_{start_time} Script File: {script_path}")
    log_lines.append(f"{date_str}_{start_time} File exists...")
    log_lines.append("")
    log_lines.append(f"{date_str}_{start_time} ## Running script")
    log_lines.append(f"{date_str}_{start_time}  *** Logon successfully completed.")
    # Not the most elegant, but works
    elapsed = random.randint(1, 5)
    log_lines.append(f"  *** Total elapsed time was {elapsed} second{'s' if elapsed > 1 else ''}.")
    if return_code > 0:
        log_lines.append(f"  *** Error: {result_message}")
        log_lines.append(f"  *** Script execution failed.")
    else:
        log_lines.append(f"  *** {result_message}")
        log_lines.append(f"  *** Script execution successful.")
    log_lines.append(f"  *** RC (return code) = {return_code}")
    log_lines.append(f"{date_str}_{end_time}")
    log_lines.append(f"{date_str}_{end_time}")
    log_lines.append(f"Execution Return Code: {return_code}")
    log_lines.append(f"{date_str}_{end_time}")
    if return_code > 0:
        log_lines.append(f"---------")
        log_lines.append(f"JOB ERROR")
        log_lines.append(f"---------")
    else:
        log_lines.append(f"-----------")
        log_lines.append(f"JOB SUCCESS")
        log_lines.append(f"-----------")
    log_lines.append(f"Start Time: {start_time}, End Time: {end_time}")
    return "\n".join(log_lines)


def generate_logs_for_date(output_dir, date_str, time_ranges=None):
    # This function generates logs for all jobs for a given date
    files_generated = 0
    if not time_ranges:
        time_ranges = [None]
    for domain, subdomains in LOG_STRUCTURE.items():
        domain_dir = os.path.join(output_dir, domain)
        for subdomain, jobs in subdomains.items():
            subdomain_dir = os.path.join(domain_dir, subdomain)
            for job in jobs:
                job_dir = os.path.join(subdomain_dir, job)
                os.makedirs(job_dir, exist_ok=True)
                for time_range in time_ranges:
                    if time_range is None:
                        start_time = generate_time(date_str)
                    else:
                        start_time = generate_time(date_str, time_range)
                    log_content = generate_log_content(date_str, start_time, domain, subdomain, job)
                    filename = f"{job}-{date_str}_{start_time}.log"
                    file_path = os.path.join(job_dir, filename)
                    with open(file_path, "w") as f:
                        f.write(log_content)
                    files_generated += 1
    return files_generated


def main():
    parser = argparse.ArgumentParser(description="Generate structured log files matching existing format")
    parser.add_argument("--output-dir", type=str, default="./sample_logs_generated",
                        help="Base directory for generated logs")
    parser.add_argument("--dates", type=str, default="today",
                        help="Comma-separated dates in YYYYMMDD format, or 'today', 'yesterday', 'last3days'")
    parser.add_argument("--time-slots", type=int, default=1,
                        help="Number of time slots to generate logs for each date (1-5)")
    parser.add_argument("--morning", action="store_true",
                        help="Generate logs for morning time slot (08:00-11:59)")
    parser.add_argument("--afternoon", action="store_true",
                        help="Generate logs for afternoon time slot (12:00-17:59)")
    parser.add_argument("--evening", action="store_true",
                        help="Generate logs for evening time slot (18:00-23:59)")
    args = parser.parse_args()

    # Figure out which dates to use
    if args.dates.lower() == "today":
        dates = [datetime.datetime.now().strftime("%Y%m%d")]
    elif args.dates.lower() == "yesterday":
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        dates = [yesterday.strftime("%Y%m%d")]
    elif args.dates.lower() == "last3days":
        dates = []
        for i in range(3):
            day = datetime.datetime.now() - datetime.timedelta(days=i)
            dates.append(day.strftime("%Y%m%d"))
    else:
        dates = args.dates.split(",")

    # Set up time ranges
    time_ranges = []
    if args.morning:
        time_ranges.append((8, 11))
    if args.afternoon:
        time_ranges.append((12, 17))
    if args.evening:
        time_ranges.append((18, 23))
    # If no time range, just use random times
    if not time_ranges:
        time_ranges = [None] * args.time_slots

    total_files = 0
    for date_str in dates:
        print(f"Generating logs for {date_str}...")  # Debug print
        files_generated = generate_logs_for_date(args.output_dir, date_str, time_ranges)
        total_files += files_generated
        print(f"Generated {files_generated} log files for date {date_str}")
    print(f"Total: {total_files} log files generated in {args.output_dir}")

if __name__ == "__main__":
    main()