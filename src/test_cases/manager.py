"""
Test Case Manager
Loads, validates, and manages test cases from JSON configuration
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Iterator
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class TestCase:
    """Represents a single test case."""

    id: str
    name: str
    description: str
    preconditions: List[str]
    steps: List[Dict]
    fail_conditions: List[Dict]
    category: Optional[str] = None


class TestCaseManager:
    """
    Load and manage test cases from JSON configuration.

    Supports:
    - Loading test cases from JSON file
    - Validation against schema
    - Filtering by name, category, tag
    - Iteration over test cases
    """

    def __init__(self, config_path: str = "config/test_cases.json"):
        """
        Initialize Test Case Manager.

        Args:
            config_path: Path to test_cases.json configuration file

        Raises:
            FileNotFoundError: If config file doesn't exist
        """
        self.config_path = Path(config_path)
        self.test_cases: Dict[str, TestCase] = {}
        self.config: Dict = {}

        self._load_config()

    def _load_config(self) -> None:
        """Load and validate configuration file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}")

        self._validate_config()
        self._parse_test_cases()

        logger.info(f"Loaded {len(self.test_cases)} test cases from {self.config_path}")

    def _validate_config(self) -> None:
        """
        Validate configuration structure.

        Raises:
            ValueError: If configuration is invalid
        """
        if 'test_cases' not in self.config:
            raise ValueError("Config must contain 'test_cases' key")

        test_cases = self.config['test_cases']
        if not isinstance(test_cases, dict):
            raise ValueError("'test_cases' must be a dictionary")

        for test_id, test_def in test_cases.items():
            self._validate_test_case_structure(test_id, test_def)

    def _validate_test_case_structure(self, test_id: str, test_def: Dict) -> None:
        """
        Validate individual test case structure.

        Raises:
            ValueError: If test case structure is invalid
        """
        required_fields = ['name', 'steps']
        for field in required_fields:
            if field not in test_def:
                raise ValueError(
                    f"Test case '{test_id}' missing required field: {field}"
                )

        # Validate steps
        steps = test_def.get('steps', [])
        if not isinstance(steps, list) or len(steps) == 0:
            raise ValueError(f"Test case '{test_id}' must have at least one step")

        for i, step in enumerate(steps):
            self._validate_step_structure(test_id, i, step)

    def _validate_step_structure(self, test_id: str, step_index: int, step: Dict) -> None:
        """
        Validate step structure.

        Raises:
            ValueError: If step structure is invalid
        """
        required_step_fields = ['id', 'expected']
        for field in required_step_fields:
            if field not in step:
                raise ValueError(
                    f"Test case '{test_id}' step {step_index} missing field: {field}"
                )

        expected = step.get('expected')
        if not isinstance(expected, list) or len(expected) == 0:
            raise ValueError(
                f"Test case '{test_id}' step {step_index} 'expected' must be non-empty list"
            )

    def _parse_test_cases(self) -> None:
        """Parse test cases from loaded config."""
        test_cases_config = self.config.get('test_cases', {})

        for test_id, test_def in test_cases_config.items():
            test_case = TestCase(
                id=test_id,
                name=test_def.get('name', ''),
                description=test_def.get('description', ''),
                preconditions=test_def.get('preconditions', []),
                steps=test_def.get('steps', []),
                fail_conditions=test_def.get('fail_conditions', []),
                category=test_def.get('category')
            )
            self.test_cases[test_id] = test_case

    def get_test_case(self, test_id: str) -> Optional[TestCase]:
        """
        Get a specific test case by ID.

        Args:
            test_id: Test case identifier

        Returns:
            TestCase or None if not found
        """
        return self.test_cases.get(test_id)

    def list_test_cases(self) -> List[TestCase]:
        """Get all test cases."""
        return list(self.test_cases.values())

    def list_by_category(self, category: str) -> List[TestCase]:
        """
        Get test cases by category.

        Args:
            category: Category name

        Returns:
            List of matching test cases
        """
        return [
            tc for tc in self.test_cases.values()
            if tc.category == category
        ]

    def list_by_name_pattern(self, pattern: str) -> List[TestCase]:
        """
        Get test cases matching name pattern.

        Args:
            pattern: Pattern to match in test case name (case-insensitive)

        Returns:
            List of matching test cases
        """
        pattern_lower = pattern.lower()
        return [
            tc for tc in self.test_cases.values()
            if pattern_lower in tc.name.lower()
        ]

    def iterate_test_cases(self) -> Iterator[TestCase]:
        """Iterate over all test cases."""
        for test_case in self.test_cases.values():
            yield test_case

    def get_stats(self) -> Dict:
        """Get statistics about loaded test cases."""
        return {
            'total': len(self.test_cases),
            'by_category': self._count_by_category(),
            'by_steps': self._count_by_steps(),
        }

    def _count_by_category(self) -> Dict[str, int]:
        """Count test cases by category."""
        counts = {}
        for tc in self.test_cases.values():
            cat = tc.category or 'uncategorized'
            counts[cat] = counts.get(cat, 0) + 1
        return counts

    def _count_by_steps(self) -> Dict[int, int]:
        """Count test cases by number of steps."""
        counts = {}
        for tc in self.test_cases.values():
            step_count = len(tc.steps)
            counts[step_count] = counts.get(step_count, 0) + 1
        return counts

    def print_stats(self) -> None:
        """Print test case statistics."""
        stats = self.get_stats()

        print("\n=== TEST CASE STATISTICS ===")
        print(f"Total test cases: {stats['total']}")

        if stats['by_category']:
            print("\nBy category:")
            for cat, count in sorted(stats['by_category'].items()):
                print(f"  {cat}: {count}")

        if stats['by_steps']:
            print("\nBy step count:")
            for steps, count in sorted(stats['by_steps'].items()):
                print(f"  {steps} steps: {count}")

    def validate_config_file(self) -> bool:
        """
        Validate that config file is correct.

        Returns:
            True if valid, False otherwise
        """
        try:
            self._validate_config()
            return True
        except ValueError as e:
            logger.error(f"Config validation failed: {e}")
            return False
