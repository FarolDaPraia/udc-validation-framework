#!/usr/bin/env python3
"""
Run Tests - US-5
CLI Interface for Test Validation Framework

Usage:
    python scripts/run_tests.py --mode full
    python scripts/run_tests.py --test udc_startup
    python scripts/run_tests.py --suite regression
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.test_cases.manager import TestCaseManager
from src.test_cases.validator import StepValidator
from src.test_cases.adapters.serial2 import Serial2Adapter
from src.test_cases.reporter import TestResultReporter


def main():
    parser = argparse.ArgumentParser(
        description='UDC Test Validation Framework - Run Tests',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --mode full                    # Run all tests
  %(prog)s --test udc_startup            # Run single test
  %(prog)s --suite regression            # Run test suite
  %(prog)s --test udc_startup --verbose  # Verbose output
  %(prog)s --test udc_startup --output report.json  # Export report
        """
    )

    parser.add_argument(
        '--mode',
        choices=['full', 'quick'],
        default='quick',
        help='Test execution mode (default: quick)'
    )

    parser.add_argument(
        '--test',
        help='Run specific test by name'
    )

    parser.add_argument(
        '--suite',
        choices=['regression', 'startup', 'runtime', 'all'],
        help='Run predefined test suite'
    )

    parser.add_argument(
        '--output',
        help='Export report to JSON file'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output'
    )

    parser.add_argument(
        '--live',
        action='store_true',
        help='Show real-time progress'
    )

    parser.add_argument(
        '--config',
        default='config/test_cases.json',
        help='Path to test configuration (default: config/test_cases.json)'
    )

    args = parser.parse_args()

    try:
        # Load test cases
        if args.verbose:
            print(f"[*] Loading test cases from {args.config}")

        manager = TestCaseManager(args.config)

        if args.verbose:
            stats = manager.get_stats()
            print(f"[*] Loaded {stats['total']} test cases")

        # Determine which tests to run
        tests_to_run = []

        if args.test:
            test = manager.get_test_case(args.test)
            if not test:
                print(f"[ERROR] Test '{args.test}' not found")
                return 1
            tests_to_run = [test]

        elif args.suite:
            if args.suite == 'all':
                tests_to_run = manager.list_test_cases()
            else:
                tests_to_run = manager.list_by_category(args.suite)

        elif args.mode == 'full':
            tests_to_run = manager.list_test_cases()

        else:
            # Quick mode - run first test only
            all_tests = manager.list_test_cases()
            tests_to_run = all_tests[:1] if all_tests else []

        if not tests_to_run:
            print("[ERROR] No tests selected to run")
            return 1

        if args.verbose:
            print(f"[*] Running {len(tests_to_run)} test(s)")

        # Create reporter
        reporter = TestResultReporter(f"Test Run ({len(tests_to_run)} tests)")

        # Run tests
        for test_case in tests_to_run:
            if args.live:
                print(f"\n[TEST] {test_case.name}")

            # Create validator
            validator = StepValidator(test_case.fail_conditions)
            validator.start_test()

            # Create adapter
            adapter = Serial2Adapter()

            # Run steps
            for step in test_case.steps:
                expected = step.get('expected', [])
                step_result = validator.validate_step(step, expected)

                if args.verbose or args.live:
                    status = "✓" if step_result.status.value == "passed" else "✗"
                    print(f"  {status} Step {step_result.step_id}: {step_result.status.value}")

            # Get test result
            test_result = validator.get_test_result()
            reporter.add_test_result({
                'test_id': test_case.id,
                'name': test_case.name,
                'status': test_result['status'],
                'duration': test_result['duration_seconds'],
                'step_results': test_result['step_results']
            })

        # Print summary
        reporter.print_summary()

        # Export if requested
        if args.output:
            if args.verbose:
                print(f"[*] Exporting report to {args.output}")
            reporter.save_to_file(args.output)

        # Exit with proper code
        report = reporter.generate_report()
        if report['test_run']['failed'] > 0 or report['test_run']['timeout'] > 0:
            return 1

        return 0

    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        return 1
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
