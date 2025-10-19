from deeprehab_rules import ScoreResult, MovementScorer
from deeprehab_angles import knee_angle


class DeepSquatScorer(MovementScorer):
    """Deep Squat movement scorer based on FMS rules."""
    
    def score(self, landmarks):
        """
        Score a deep squat movement based on FMS rules.
        
        Args:
            landmarks: List of landmark positions
            
        Returns:
            ScoreResult: The scoring result
        """
        left_knee = knee_angle(landmarks, "left")
        right_knee = knee_angle(landmarks, "right")
        
        if left_knee is None or right_knee is None:
            return ScoreResult(0, "无法计算膝关节角度", {"left_knee": left_knee, "right_knee": right_knee})
        
        if left_knee > 150 and right_knee > 150:
            score = 2
            reason = "动作基本合格"
        elif left_knee > 120 and right_knee > 120:
            score = 1
            reason = "存在轻微代偿"
        else:
            score = 0
            reason = "明显代偿"
            
        return ScoreResult(score, reason, {"left_knee": left_knee, "right_knee": right_knee})


def score_deep_squat(landmarks):
    """
    Score a deep squat movement based on FMS rules.
    
    Args:
        landmarks: List of landmark positions
        
    Returns:
        ScoreResult: The scoring result
    """
    scorer = DeepSquatScorer()
    return scorer.score(landmarks)


def get_scorer(movement_name):
    """
    Get a movement scorer by name.
    
    Args:
        movement_name: Name of the movement
        
    Returns:
        MovementScorer: The movement scorer
        
    Raises:
        ValueError: If movement_name is not recognized
    """
    if movement_name == "deep_squat":
        return DeepSquatScorer()
    else:
        raise ValueError(f"Unknown movement: {movement_name}")