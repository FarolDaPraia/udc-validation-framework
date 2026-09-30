"""
Step Validator - US-2
Sequential test step validation with state machine
"""

import time
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class StepStatus(Enum):
    """Status of a test step."""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class StepResult:
    """Result of step validation."""
    step_id: int
    status: StepStatus
    duration_seconds: float
    expected_results: List[Dict] = field(default_factory=list)
    failure_reason: Optional[str] = None
    matched_entries: List[Dict] = field(default_factory=list)


class StepValidator:
    """
    Validate test steps sequentially using state machine.

    Features:
    - Sequential step execution
    - Timeout handling per step
    - Fail condition detection
    - State tracking
    - Clear status reporting
    """

    def __init__(self, fail_conditions: List[Dict] = None):
        """
        Initialize Step Validator.

        Args:
            fail_conditions: List of fail conditions to monitor
        """
        self.fail_conditions = fail_conditions or []
        self.current_step = None
        self.current_step_index = 0
        self.results: List[StepResult] = []
        self.state = StepStatus.PENDING
        self.start_time = None

    def start_test(self) -> None:
        """Start test execution."""
        self.start_time = time.time()
        self.state = StepStatus.RUNNING
        self.current_step_index = 0
        self.results = []
        logger.info("Test started")

    def validate_step(
        self,
        step: Dict,
        expected_results: List[Dict],
        timeout: float = 10.0
    ) -> StepResult:
        """
        Validate a single step.

        Args:
            step: Step definition
            expected_results: Expected results to match
            timeout: Timeout in seconds

        Returns:
            StepResult with status and details
        """
        step_id = step.get('id', self.current_step_index + 1)
        step_name = step.get('name', f'Step {step_id}')

        logger.info(f"Validating step {step_id}: {step_name}")

        step_start = time.time()
        result = StepResult(
            step_id=step_id,
            status=StepStatus.PENDING,
            duration_seconds=0.0,
            expected_results=expected_results
        )

        # Check fail conditions BEFORE validating step
        for fail_cond in self.fail_conditions:
            if self._check_fail_condition(fail_cond):
                result.status = StepStatus.FAILED
                result.failure_reason = f"Fail condition triggered: {fail_cond.get('description', 'unknown')}"
                result.duration_seconds = time.time() - step_start
                logger.error(f"Fail condition detected: {result.failure_reason}")
                self.results.append(result)
                return result

        # Validate expected results
        if not expected_results:
            result.status = StepStatus.PASSED
            result.duration_seconds = time.time() - step_start
            logger.info(f"Step {step_id} passed (no expected results)")
            self.results.append(result)
            return result

        # Check if all expected results are satisfied
        all_matched = True
        matched_count = 0

        for expected in expected_results:
            source = expected.get('source', 'serial2')
            timeout_val = expected.get('timeout', timeout)

            # For now, we're simulating - in real implementation,
            # this would be called by adapter (Serial2Adapter, BackendAPIAdapter)
            matched = self._simulate_expected_match(expected)

            if matched:
                matched_count += 1
                matched_entry = {
                    'source': source,
                    'status': 'matched',
                    'timestamp': time.time()
                }
                result.matched_entries.append(matched_entry)
            else:
                all_matched = False
                result.matched_entries.append({
                    'source': source,
                    'status': 'not_matched',
                    'expected': expected
                })

        # Determine step status
        if all_matched:
            result.status = StepStatus.PASSED
            logger.info(f"Step {step_id} passed: all expected results matched")
        elif time.time() - step_start > timeout:
            result.status = StepStatus.TIMEOUT
            result.failure_reason = f"Timeout after {timeout}s"
            logger.error(f"Step {step_id} timeout")
        else:
            result.status = StepStatus.FAILED
            result.failure_reason = f"Expected results not matched ({matched_count}/{len(expected_results)})"
            logger.error(f"Step {step_id} failed: {result.failure_reason}")

        result.duration_seconds = time.time() - step_start
        self.results.append(result)
        self.current_step_index += 1

        return result

    def _check_fail_condition(self, fail_cond: Dict) -> bool:
        """
        Check if a fail condition is triggered.

        Args:
            fail_cond: Fail condition definition

        Returns:
            True if fail condition is triggered
        """
        fail_type = fail_cond.get('type', 'unknown')

        # In real implementation, this would check actual logs
        # For now, simulate based on configuration
        if fail_type == 'error_log':
            # Simulate: return False (no error found)
            return False
        elif fail_type == 'timeout':
            # Simulate: return False (no timeout)
            return False
        elif fail_type == 'keyword':
            # Simulate: return False (keyword not found)
            return False

        return False

    def _simulate_expected_match(self, expected: Dict) -> bool:
        """
        Simulate matching of expected result.

        In real implementation, this would be called by adapters.

        Args:
            expected: Expected result definition

        Returns:
            True if would match
        """
        # For testing: return True if all conditions are present
        source = expected.get('source')
        if source == 'serial2':
            message = expected.get('message')
            level = expected.get('level')
            timeout = expected.get('timeout')
            return message is not None and timeout is not None
        elif source == 'backend_api':
            endpoint = expected.get('endpoint')
            field = expected.get('field')
            value = expected.get('value')
            return endpoint is not None and field is not None
        return False

    def get_test_result(self) -> Dict:
        """
        Get final test result.

        Returns:
            Test result summary
        """
        duration = (time.time() - self.start_time) if self.start_time else 0

        passed_count = sum(1 for r in self.results if r.status == StepStatus.PASSED)
        failed_count = sum(1 for r in self.results if r.status == StepStatus.FAILED)
        timeout_count = sum(1 for r in self.results if r.status == StepStatus.TIMEOUT)

        test_status = (
            "passed" if failed_count == 0 and timeout_count == 0
            else "failed"
        )

        return {
            'status': test_status,
            'total_steps': len(self.results),
            'passed': passed_count,
            'failed': failed_count,
            'timeout': timeout_count,
            'duration_seconds': duration,
            'step_results': [
                {
                    'step_id': r.step_id,
                    'status': r.status.value,
                    'duration': r.duration_seconds,
                    'failure_reason': r.failure_reason,
                    'matched_count': len([m for m in r.matched_entries if m.get('status') == 'matched'])
                }
                for r in self.results
            ]
        }

    def print_results(self) -> None:
        """Print test results."""
        result = self.get_test_result()

        print("\n=== TEST RESULT ===")
        print(f"Status: {result['status'].upper()}")
        print(f"Duration: {result['duration_seconds']:.1f}s")
        print(f"Steps: {result['passed']} passed, {result['failed']} failed, {result['timeout']} timeout")
        print(f"\nStep Details:")

        for step_result in result['step_results']:
            status_symbol = {
                'passed': '✓',
                'failed': '✗',
                'timeout': '⏱'
            }.get(step_result['status'], '?')

            print(f"  {status_symbol} Step {step_result['step_id']}: {step_result['status']} ({step_result['duration']:.2f}s)")
            if step_result['failure_reason']:
                print(f"     Reason: {step_result['failure_reason']}")
