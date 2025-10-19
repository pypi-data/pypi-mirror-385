"""DeepRehab Movements Package."""

# Version of the deeprehab-movements package
__version__ = "0.1.0"

# Export main classes and functions
from .deeprehab_movements import DeepSquatScorer, get_scorer, score_deep_squat

__all__ = ["DeepSquatScorer", "get_scorer", "score_deep_squat"]