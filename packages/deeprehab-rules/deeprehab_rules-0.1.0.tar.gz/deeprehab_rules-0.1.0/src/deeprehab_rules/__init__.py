"""DeepRehab Rules Package."""

# Version of the deeprehab-rules package
__version__ = "0.1.0"

# Export main classes and functions
from .deeprehab_rules import DeepRehabRules, load_rules, ScoreResult, MovementScorer

__all__ = ["DeepRehabRules", "load_rules", "ScoreResult", "MovementScorer"]