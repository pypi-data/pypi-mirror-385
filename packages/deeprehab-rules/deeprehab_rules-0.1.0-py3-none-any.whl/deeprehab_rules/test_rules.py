"""Tests for the deeprehab_rules package."""

import unittest
from deeprehab_rules import __version__
from deeprehab_rules.deeprehab_rules import DeepRehabRules, load_rules


class TestDeepRehabRules(unittest.TestCase):
    """Test cases for the DeepRehabRules class."""

    def test_version(self):
        """Test that the version is correctly set."""
        self.assertEqual(__version__, "0.1.0")

    def test_rules_initialization(self):
        """Test that the rules engine can be initialized."""
        rules_engine = DeepRehabRules()
        self.assertIsInstance(rules_engine, DeepRehabRules)

    def test_load_default_rules(self):
        """Test loading default rules."""
        rules = load_rules()
        self.assertIn("knee_exercise", rules)
        self.assertIn("shoulder_exercise", rules)


if __name__ == "__main__":
    unittest.main()