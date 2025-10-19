import unittest
from deeprehab_angles import Landmark
from deeprehab_movements import DeepSquatScorer, get_scorer


class TestDeepSquatScorer(unittest.TestCase):
    """Test cases for the DeepSquatScorer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.scorer = DeepSquatScorer()
    
    def test_good_form(self):
        """Test scoring with good form (knee angles > 150)."""
        landmarks = [Landmark(0, 0, 0, 1) for _ in range(33)]
        # Set positions for a good squat
        landmarks[23] = Landmark(0, 0, 0, 1)     # Left hip
        landmarks[25] = Landmark(0, -1, 0, 1)    # Left knee
        landmarks[27] = Landmark(0, -2, 0, 1)    # Left ankle
        landmarks[24] = Landmark(0.5, 0, 0, 1)   # Right hip
        landmarks[26] = Landmark(0.5, -1, 0, 1)  # Right knee
        landmarks[28] = Landmark(0.5, -2, 0, 1)  # Right ankle
        
        result = self.scorer.score(landmarks)
        
        self.assertEqual(result.score, 2)
        self.assertEqual(result.reason, "动作基本合格")
        self.assertGreater(result.details["left_knee"], 150)
        self.assertGreater(result.details["right_knee"], 150)
    
    def test_mild_compensation(self):
        """Test scoring with mild compensation (knee angles between 120 and 150)."""
        landmarks = [Landmark(0, 0, 0, 1) for _ in range(33)]
        # Set positions for a squat with mild compensation
        landmarks[23] = Landmark(0, 0, 0, 1)     # Left hip
        landmarks[25] = Landmark(0.3, -1, 0, 1)  # Left knee
        landmarks[27] = Landmark(0, -2, 0, 1)    # Left ankle
        landmarks[24] = Landmark(0.5, 0, 0, 1)   # Right hip
        landmarks[26] = Landmark(0.8, -1, 0, 1)  # Right knee
        landmarks[28] = Landmark(0.5, -2, 0, 1)  # Right ankle
        
        result = self.scorer.score(landmarks)
        
        self.assertEqual(result.score, 1)
        self.assertEqual(result.reason, "存在轻微代偿")
        self.assertGreater(result.details["left_knee"], 120)
        self.assertLess(result.details["left_knee"], 150)
        self.assertGreater(result.details["right_knee"], 120)
        self.assertLess(result.details["right_knee"], 150)
    
    def test_significant_compensation(self):
        """Test scoring with significant compensation (knee angles < 120)."""
        landmarks = [Landmark(0, 0, 0, 1) for _ in range(33)]
        # Set positions for a squat with significant compensation
        landmarks[23] = Landmark(0, 0, 0, 1)     # Left hip
        landmarks[25] = Landmark(0.8, -1, 0, 1)  # Left knee
        landmarks[27] = Landmark(0, -2, 0, 1)    # Left ankle
        landmarks[24] = Landmark(0.5, 0, 0, 1)   # Right hip
        landmarks[26] = Landmark(1.3, -1, 0, 1)  # Right knee
        landmarks[28] = Landmark(0.5, -2, 0, 1)  # Right ankle
        
        result = self.scorer.score(landmarks)
        
        self.assertEqual(result.score, 0)
        self.assertEqual(result.reason, "明显代偿")
        self.assertLess(result.details["left_knee"], 120)
        self.assertLess(result.details["right_knee"], 120)
    
    def test_get_scorer_deep_squat(self):
        """Test get_scorer function with 'deep_squat'."""
        scorer = get_scorer("deep_squat")
        self.assertIsInstance(scorer, DeepSquatScorer)
    
    def test_get_scorer_invalid_movement(self):
        """Test get_scorer function with invalid movement name."""
        with self.assertRaises(ValueError):
            get_scorer("invalid_movement")


if __name__ == "__main__":
    unittest.main()