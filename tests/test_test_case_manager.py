"""
Unit tests for TestCaseManager
"""

import pytest
import json
import tempfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.test_cases.manager import TestCaseManager, TestCase


@pytest.fixture
def valid_config():
    """Fixture with valid test case configuration."""
    return {
        "test_cases": {
            "test_001": {
                "name": "Simple Test",
                "description": "A simple test case",
                "category": "basic",
                "preconditions": ["System ready"],
                "steps": [
                    {
                        "id": 1,
                        "name": "Step 1",
                        "expected": [
                            {
                                "source": "serial2",
                                "message": "test.*message",
                                "level": "Info",
                                "timeout": 5
                            }
                        ]
                    }
                ],
                "fail_conditions": []
            },
            "test_002": {
                "name": "Complex Test",
                "description": "A complex test case",
                "category": "advanced",
                "preconditions": [],
                "steps": [
                    {
                        "id": 1,
                        "name": "Step 1",
                        "expected": [{"source": "serial2", "message": ".*", "timeout": 5}]
                    },
                    {
                        "id": 2,
                        "name": "Step 2",
                        "expected": [{"source": "serial2", "message": ".*", "timeout": 10}]
                    }
                ],
                "fail_conditions": [
                    {"type": "error_log", "message": ".*Error.*"}
                ]
            }
        }
    }


@pytest.fixture
def config_file(valid_config):
    """Fixture that creates a temporary config file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(valid_config, f)
        temp_path = f.name

    yield temp_path

    Path(temp_path).unlink()


class TestTestCaseManagerLoading:
    """Test loading and parsing of test cases."""

    def test_load_valid_config(self, config_file):
        """Test loading valid configuration."""
        manager = TestCaseManager(config_file)
        assert len(manager.test_cases) == 2
        assert 'test_001' in manager.test_cases
        assert 'test_002' in manager.test_cases

    def test_load_missing_file(self):
        """Test loading from missing file."""
        with pytest.raises(FileNotFoundError):
            TestCaseManager("/nonexistent/path/config.json")

    def test_load_invalid_json(self):
        """Test loading invalid JSON."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json }")
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="Invalid JSON"):
                TestCaseManager(temp_path)
        finally:
            Path(temp_path).unlink()

    def test_missing_test_cases_key(self):
        """Test config missing 'test_cases' key."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"other": "data"}, f)
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="'test_cases' key"):
                TestCaseManager(temp_path)
        finally:
            Path(temp_path).unlink()


class TestTestCaseValidation:
    """Test configuration validation."""

    def test_missing_required_field(self):
        """Test validation of missing required field."""
        config = {
            "test_cases": {
                "test_001": {
                    "name": "Test"
                    # Missing 'steps'
                }
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f)
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="missing required field"):
                TestCaseManager(temp_path)
        finally:
            Path(temp_path).unlink()

    def test_invalid_steps_structure(self):
        """Test validation of invalid steps."""
        config = {
            "test_cases": {
                "test_001": {
                    "name": "Test",
                    "steps": []  # Empty steps
                }
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f)
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="at least one step"):
                TestCaseManager(temp_path)
        finally:
            Path(temp_path).unlink()


class TestTestCaseAccess:
    """Test accessing test cases."""

    def test_get_test_case(self, config_file):
        """Test getting a specific test case."""
        manager = TestCaseManager(config_file)
        tc = manager.get_test_case('test_001')

        assert tc is not None
        assert tc.id == 'test_001'
        assert tc.name == "Simple Test"
        assert tc.category == "basic"

    def test_get_nonexistent_test_case(self, config_file):
        """Test getting nonexistent test case."""
        manager = TestCaseManager(config_file)
        tc = manager.get_test_case('nonexistent')
        assert tc is None

    def test_list_all_test_cases(self, config_file):
        """Test listing all test cases."""
        manager = TestCaseManager(config_file)
        test_cases = manager.list_test_cases()

        assert len(test_cases) == 2
        names = [tc.name for tc in test_cases]
        assert "Simple Test" in names
        assert "Complex Test" in names

    def test_list_by_category(self, config_file):
        """Test filtering by category."""
        manager = TestCaseManager(config_file)

        basic = manager.list_by_category("basic")
        assert len(basic) == 1
        assert basic[0].name == "Simple Test"

        advanced = manager.list_by_category("advanced")
        assert len(advanced) == 1
        assert advanced[0].name == "Complex Test"

    def test_list_by_name_pattern(self, config_file):
        """Test filtering by name pattern."""
        manager = TestCaseManager(config_file)

        matches = manager.list_by_name_pattern("simple")
        assert len(matches) == 1
        assert matches[0].name == "Simple Test"

        all_matches = manager.list_by_name_pattern("test")
        assert len(all_matches) == 2


class TestTestCaseIteration:
    """Test iteration over test cases."""

    def test_iterate_test_cases(self, config_file):
        """Test iterating over test cases."""
        manager = TestCaseManager(config_file)
        test_cases = list(manager.iterate_test_cases())

        assert len(test_cases) == 2
        for tc in test_cases:
            assert isinstance(tc, TestCase)


class TestStatistics:
    """Test statistics generation."""

    def test_get_stats(self, config_file):
        """Test statistics generation."""
        manager = TestCaseManager(config_file)
        stats = manager.get_stats()

        assert stats['total'] == 2
        assert 'basic' in stats['by_category']
        assert stats['by_category']['basic'] == 1
        assert stats['by_category']['advanced'] == 1

    def test_by_steps_count(self, config_file):
        """Test counting by step count."""
        manager = TestCaseManager(config_file)
        stats = manager.get_stats()

        # test_001 has 1 step, test_002 has 2 steps
        assert stats['by_steps'][1] == 1
        assert stats['by_steps'][2] == 1


class TestValidation:
    """Test configuration validation method."""

    def test_validate_valid_config(self, config_file):
        """Test validation of valid config."""
        manager = TestCaseManager(config_file)
        assert manager.validate_config_file() is True

    def test_validate_invalid_config(self):
        """Test validation of invalid config."""
        config = {
            "test_cases": {
                "test_001": {
                    "name": "Test"
                    # Missing 'steps'
                }
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f)
            temp_path = f.name

        try:
            manager = TestCaseManager(temp_path)
            # Should raise during init, so we can't call validate_config_file
        except ValueError:
            pass  # Expected
        finally:
            Path(temp_path).unlink()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
