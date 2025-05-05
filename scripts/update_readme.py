#!/usr/bin/env python3
"""
Script to update the README.md with the latest tracker data.
"""
import sys
import os
import re
import pandas as pd
from tabulate import tabulate
import logging

sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))
from src.utils.date_helpers import get_readme_date_string

# Configure logging
LOG_FILE = 'logs/log_analyzer.log'
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)

def update_readme_with_tracker() -> bool:
    """Update the README.md file with the latest tracker data."""
    tracker_path = 'data/log_analysis_tracker.xlsx'
    readme_path = 'README.md'

    logging.info(f'Reading tracker: {tracker_path}')

    if not os.path.exists(tracker_path):
        logging.warning(f'Tracker file {tracker_path} not found. Skipping README update.')
        return False

    # Read the Excel file
    try:
        df = pd.read_excel(tracker_path)
    except Exception as e:
        logging.error(f'Error reading tracker file: {e}')
        return False

    # Generate the markdown table
    summary = tabulate(df.head(50), headers='keys', tablefmt='github', showindex=False)

    logging.info(f'Reading README: {readme_path}')

    # Read the current README content
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            content= f.read()
    except Exception as e:
        logging.error(f'Error reading README file: {e}')
        return False

    # Create the new section
    current_date = get_readme_date_string()
    new_section = f'\n## Latest Tracker Preview Updated on {current_date}\n\n' + summary + '\n'

    # Remove existing tracker section if it exists
    pattern = r'(## Latest Tracker Preview.*?)(?=\n## |\Z)'
    content = re.sub(pattern, '', content, flags=re.DOTALL | re.MULTILINE)

    # Add the new section
    if '## Latest Tracker Preview' not in content:
        content += new_section
    else:
        content = re.sub(r'## Latest Tracker Preview.*', new_section.strip(), content, flags=re.MULTILINE)

    logging.info(f'Writing updated README: {readme_path}')

    # Write the updated content back to the README
    try:
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        logging.error(f'Error writing README file: {e}')
        return False

if __name__ == '__main__':
    success = update_readme_with_tracker()
    if success:
        logging.info("README successfully updated with tracker data.")
    else:
        logging.error("Failed to update README.")
        exit(1)