"""
Test Result Reporter - US-4
Generates detailed test reports in JSON and console formats
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class TestResultReporter:
    """
    Generate and format test results.

    Features:
    - JSON report generation
    - Statistics calculation
    - Human-readable console output
    - Detailed step-by-step tracking
    """

    def __init__(self, test_name: str = "Test Run"):
        """
        Initialize reporter.

        Args:
            test_name: Name of the test run
        """
        self.test_name = test_name
        self.start_time = datetime.now()
        self.end_time = None
        self.test_results: List[Dict] = []
        self.summary = {}

    def add_test_result(self, result: Dict) -> None:
        """
        Add a test result.

        Args:
            result: Test result dictionary
        """
        self.test_results.append(result)

    def generate_report(self) -> Dict:
        """
        Generate complete test report.

        Returns:
            Report dictionary with all metrics
        """
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()

        # Calculate statistics
        total_tests = len(self.test_results)
        passed_tests = sum(
            1 for r in self.test_results
            if r.get('status') == 'passed'
        )
        failed_tests = sum(
            1 for r in self.test_results
            if r.get('status') == 'failed'
        )
        timeout_tests = sum(
            1 for r in self.test_results
            if r.get('status') == 'timeout'
        )

        # Calculate step statistics
        total_steps = sum(
            len(r.get('step_results', []))
            for r in self.test_results
        )
        passed_steps = sum(
            sum(1 for s in r.get('step_results', []) if s.get('status') == 'passed')
            for r in self.test_results
        )

        self.summary = {
            'test_run': {
                'name': self.test_name,
                'start_time': self.start_time.isoformat(),
                'end_time': self.end_time.isoformat(),
                'duration_seconds': duration,
                'total_tests': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'timeout': timeout_tests,
                'success_rate': passed_tests / total_tests if total_tests > 0 else 0
            },
            'step_statistics': {
                'total_steps': total_steps,
                'passed_steps': passed_steps,
                'failed_steps': total_steps - passed_steps
            },
            'test_results': self.test_results
        }

        return self.summary

    def to_json(self, pretty: bool = True) -> str:
        """
        Serialize report to JSON.

        Args:
            pretty: Whether to pretty-print JSON

        Returns:
            JSON string
        """
        report = self.generate_report()
        if pretty:
            return json.dumps(report, indent=2, default=str)
        return json.dumps(report, default=str)

    def save_to_file(self, filepath: str) -> None:
        """
        Save report to JSON file.

        Args:
            filepath: Path to save report
        """
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w') as f:
            f.write(self.to_json(pretty=True))

        logger.info(f"Report saved to {filepath}")

    def print_summary(self) -> None:
        """Print human-readable summary."""
        if not self.summary:
            self.generate_report()

        summary = self.summary['test_run']
        steps = self.summary['step_statistics']

        print("\n" + "=" * 60)
        print(f"TEST REPORT: {summary['name']}")
        print("=" * 60)

        # Overall result
        if summary['success_rate'] == 1.0:
            status = "✓ ALL TESTS PASSED"
        elif summary['failed'] == 0 and summary['timeout'] == 0:
            status = "✓ ALL TESTS PASSED"
        else:
            status = "✗ TESTS FAILED"

        print(f"\nStatus: {status}")
        print(f"Duration: {summary['duration_seconds']:.1f}s")

        # Test statistics
        print(f"\nTests: {summary['total_tests']}")
        print(f"  ✓ Passed: {summary['passed']}")
        print(f"  ✗ Failed: {summary['failed']}")
        print(f"  ⏱ Timeout: {summary['timeout']}")
        print(f"  Success rate: {summary['success_rate']:.1%}")

        # Step statistics
        print(f"\nSteps: {steps['total_steps']}")
        print(f"  ✓ Passed: {steps['passed_steps']}")
        print(f"  ✗ Failed: {steps['failed_steps']}")

        # Test details
        if self.test_results:
            print(f"\nTest Details:")
            for result in self.test_results:
                status_symbol = "✓" if result.get('status') == 'passed' else "✗"
                print(f"  {status_symbol} {result.get('name', 'Unknown')}")
                if result.get('failure_reason'):
                    print(f"     {result['failure_reason']}")

        print("=" * 60 + "\n")
