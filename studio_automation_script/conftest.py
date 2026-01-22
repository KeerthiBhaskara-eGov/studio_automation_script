import pytest
import json
import os
import time

# ========== Wait Control ==========
_studio_setup_completed = False

# ========== HTML Report Customization ==========

def pytest_configure(config):
    """Add metadata to report"""
    if hasattr(config, '_metadata'):
        config._metadata['Project'] = 'DIGIT Studio API Automation'
        config._metadata['Tenant'] = 'st'


def pytest_html_report_title(report):
    """Set report title"""
    report.title = "DIGIT Studio API Test Report"


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Add extra details to each test in report + track studio setup completion"""
    global _studio_setup_completed
    
    outcome = yield
    report = outcome.get_result()
    
    if report.when == "call":
        # Track studio setup completion for wait logic
        if report.passed and ("test_public_service_init" in item.name or "test_03_public_service_init" in item.name):
            _studio_setup_completed = True
        
        extra = getattr(report, "extra", [])
        
        # Check if test has stored result
        if hasattr(item, "_test_result") and item._test_result:
            result = item._test_result
            
            # Create HTML table for details
            html = '<div style="margin:10px 0;"><h4>📋 Test Details</h4>'
            html += '<table style="border-collapse:collapse;width:100%;max-width:600px;">'
            
            for key, value in result.items():
                bg_color = "#e8f5e9" if "Status" in key or "Complete" in key else "#f5f5f5"
                if isinstance(value, (dict, list)):
                    value = f"<pre>{json.dumps(value, indent=2)}</pre>"
                html += f'''
                <tr style="background:{bg_color};">
                    <td style="border:1px solid #ddd;padding:8px;font-weight:bold;">{key}</td>
                    <td style="border:1px solid #ddd;padding:8px;">{value}</td>
                </tr>'''
            
            html += '</table></div>'
            
            # Add to extras
            try:
                from pytest_html import extras
                extra.append(extras.html(html))
            except ImportError:
                pass
        
        report.extra = extra


def pytest_runtest_setup(item):
    """Wait 15 minutes before search tests if studio setup just completed"""
    global _studio_setup_completed
    
    # List of tests that should trigger the wait (first test after studio setup)
    wait_trigger_tests = ["test_actions_search", "test_04_actions_search"]
    
    if any(test_name in item.name for test_name in wait_trigger_tests) and _studio_setup_completed:
        wait_minutes = 15
        print(f"\n\n{'='*60}")
        print(f"⏳ Waiting {wait_minutes} minutes for service initialization...")
        print(f"{'='*60}")
        
        for i in range(wait_minutes, 0, -1):
            print(f"   ⏱️  {i} minute(s) remaining...")
            time.sleep(60)
        
        print(f"{'='*60}")
        print("✅ Wait complete. Proceeding with search tests...")
        print(f"{'='*60}\n")
        
        # Reset flag
        _studio_setup_completed = False


@pytest.hookimpl(optionalhook=True)
def pytest_html_results_summary(prefix, summary, postfix):
    """Add summary with output file data"""
    
    summary_html = '<h2>📊 Execution Summary</h2>'
    
    # Load output files if exist
    files = {
        "MDMS Draft": "output/mdms_draft_response.json",
        "MDMS Response": "output/mdms_response.json",
        "Public Service": "output/public_service_response.json", 
        "Application": "output/application_response.json"
    }
    
    summary_html += '<table style="border-collapse:collapse;margin:10px 0;">'
    
    for name, path in files.items():
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                
                summary_html += f'<tr><td colspan="2" style="background:#2196F3;color:white;padding:8px;font-weight:bold;">{name}</td></tr>'
                
                for key, value in data.items():
                    if value and not key.endswith("_by") and not key.endswith("_time"):
                        summary_html += f'''
                        <tr>
                            <td style="border:1px solid #ddd;padding:6px;background:#f5f5f5;">{key}</td>
                            <td style="border:1px solid #ddd;padding:6px;">{value}</td>
                        </tr>'''
            except:
                pass
    
    summary_html += '</table>'
    prefix.extend([summary_html])