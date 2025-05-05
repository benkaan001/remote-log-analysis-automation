import tempfile
import os
from src.utils import date_helpers
from src import log_analyzer
import pandas as pd
import pytest
from unittest import mock


def test_get_current_date_string():
    result = date_helpers.get_current_date_string()
    assert len(result) == 8 and result.isdigit()


def test_get_readme_date_string():
    result = date_helpers.get_readme_date_string()
    assert len(result) == 10 and result[4] == '-' and result[7] == '-'


def test_create_log_download_directory():
    with tempfile.TemporaryDirectory() as tmpdir:
        date_str = '20250101'
        log_dir = log_analyzer.create_log_download_directory(tmpdir, date_str)
        assert os.path.exists(log_dir)
        assert log_dir.endswith(f"{date_str}_logs")


def test_create_log_download_directory_idempotent():
    with tempfile.TemporaryDirectory() as tmpdir:
        date_str = '20250101'
        log_dir1 = log_analyzer.create_log_download_directory(tmpdir, date_str)
        log_dir2 = log_analyzer.create_log_download_directory(tmpdir, date_str)
        assert log_dir1 == log_dir2
        assert os.path.exists(log_dir1)


def test_analyze_downloaded_logs_empty():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Directory exists but is empty
        result = log_analyzer.analyze_downloaded_logs(tmpdir)
        assert result == {}


def test_analyze_downloaded_logs_success():
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = os.path.join(tmpdir, 'test_success.log')
        with open(log_path, 'w') as f:
            f.write('Some log line\nExecution Return Code: 0\n')
        result = log_analyzer.analyze_downloaded_logs(tmpdir)
        assert 'test_success.log' in result
        assert result['test_success.log'] == 'success'


def test_analyze_downloaded_logs_error():
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = os.path.join(tmpdir, 'test_error.log')
        with open(log_path, 'w') as f:
            f.write('Something happened\n  *** Error: Something bad\n')
        result = log_analyzer.analyze_downloaded_logs(tmpdir)
        assert 'test_error.log' in result
        assert result['test_error.log'] == 'error'


def test_analyze_downloaded_logs_failure():
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = os.path.join(tmpdir, 'test_failure.log')
        with open(log_path, 'w') as f:
            f.write('Oops\n*** Failure\n')
        result = log_analyzer.analyze_downloaded_logs(tmpdir)
        assert 'test_failure.log' in result
        assert result['test_failure.log'] == 'failure'


def test_update_tracker_with_results_adds_column():
    df = pd.DataFrame({
        'remote_log_directory': ['/logs/finance/billing/job_invoice_gen'],
        'project': ['finance'],
        'department': ['billing'],
        'job_name': ['job_invoice_gen']
    })
    analysis_results = {'job_invoice_gen-20250505_120000.log': 'success'}
    date_string = '20250505'
    problematic_paths = []
    updated = log_analyzer.update_tracker_with_results(df, analysis_results, date_string, problematic_paths)
    col = f"analysis_results_{date_string}"
    assert col in updated.columns
    assert updated[col].iloc[0] == 'success'


def test_get_analysis_tracker_missing_file():
    result = log_analyzer.get_analysis_tracker('nonexistent_file.xlsx', 'remote_log_directory')
    assert result is None


def test_load_environment_variables_all_present(monkeypatch):
    monkeypatch.setenv('SSH_HOSTNAME', 'localhost')
    monkeypatch.setenv('SSH_USERNAME', 'user')
    monkeypatch.setenv('SSH_PASSWORD', 'pass')
    env = log_analyzer.load_environment_variables()
    assert env['SSH_HOSTNAME'] == 'localhost'
    assert env['SSH_USERNAME'] == 'user'
    assert env['SSH_PASSWORD'] == 'pass'


def test_load_environment_variables_missing(monkeypatch):
    monkeypatch.delenv('SSH_HOSTNAME', raising=False)
    monkeypatch.delenv('SSH_USERNAME', raising=False)
    monkeypatch.delenv('SSH_PASSWORD', raising=False)
    with mock.patch('src.log_analyzer.load_dotenv', lambda *a, **kw: None):
        with pytest.raises(ValueError) as exc:
            log_analyzer.load_environment_variables()
    assert 'Missing required environment variables' in str(exc.value)


def test_update_tracker_with_results_access_error():
    df = pd.DataFrame({
        'remote_log_directory': ['/logs/finance/billing/job_invoice_gen'],
        'project': ['finance'],
        'department': ['billing'],
        'job_name': ['job_invoice_gen']
    })
    analysis_results = {}
    date_string = '20250505'
    problematic_paths = ['/logs/finance/billing/job_invoice_gen']
    updated = log_analyzer.update_tracker_with_results(df, analysis_results, date_string, problematic_paths)
    col = f"analysis_results_{date_string}"
    assert col in updated.columns
    assert updated[col].iloc[0] == 'access_error'


def test_update_tracker_with_results_missing_path():
    df = pd.DataFrame({
        'remote_log_directory': [None],
        'project': ['finance'],
        'department': ['billing'],
        'job_name': ['job_invoice_gen']
    })
    analysis_results = {}
    date_string = '20250505'
    problematic_paths = []
    updated = log_analyzer.update_tracker_with_results(df, analysis_results, date_string, problematic_paths)
    col = f"analysis_results_{date_string}"
    assert col in updated.columns
    assert updated[col].iloc[0] == 'missing_path'


def test_get_analysis_tracker_valid_file():
    # Use the real tracker file if it exists and has the required column
    tracker_path = os.path.join('data', 'log_analysis_tracker.xlsx')
    if not os.path.exists(tracker_path):
        pytest.skip('Tracker file not present')
    df = log_analyzer.get_analysis_tracker(tracker_path, 'remote_log_directory')
    assert df is not None
    assert 'remote_log_directory' in df.columns


def test_analyze_downloaded_logs_multiple_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        files = {
            'success.log': 'Execution Return Code: 0\n',
            'error.log': '*** Error: Something bad\n',
            'failure.log': '*** Failure\n',
            'other.log': 'No pattern here\n'
        }
        for fname, content in files.items():
            with open(os.path.join(tmpdir, fname), 'w') as f:
                f.write(content)
        result = log_analyzer.analyze_downloaded_logs(tmpdir)
        assert result['success.log'] == 'success'
        assert result['error.log'] == 'error'
        assert result['failure.log'] == 'failure'
        assert result['other.log'] == 'unknown'