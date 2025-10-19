from deeprehab_angles import knee_angle
from deeprehab_rules import ScoreResult


def score_deep_squat(landmarks) -> ScoreResult:
    left_angle = knee_angle(landmarks, "left")
    right_angle = knee_angle(landmarks, "right")
    
    if left_angle is None or right_angle is None:
        return ScoreResult(0, "无法计算膝关节角度", {"left_knee": left_angle, "right_knee": right_angle})
    
    if left_angle > 150 and right_angle > 150:
        score = 2
        reason = "动作基本合格"
    elif left_angle > 120 and right_angle > 120:
        score = 1
        reason = "存在轻微代偿（如膝角不足）"
    else:
        score = 0
        reason = "明显代偿或无法完成动作"
        
    return ScoreResult(score, reason, {"left_knee": left_angle, "right_knee": right_angle})