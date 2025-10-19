import unittest
from deeprehab_angles import Landmark
from deeprehab_rules.deeprehab_movements import score_deep_squat


class TestDeepRehabMovements(unittest.TestCase):
    
    def test_score_deep_squat_good_form(self):
        # Create landmarks with good squat form (knee angles > 150)
        landmarks = [Landmark(0, 0, 0, 1) for _ in range(33)]
        # Set hip, knee, and ankle positions for left leg (indices 23, 25, 27)
        landmarks[23] = Landmark(0, 0, 0, 1)    # Left hip
        landmarks[25] = Landmark(0, -1, 0, 1)   # Left knee
        landmarks[27] = Landmark(0.1, -2, 0, 1)   # Left ankle
        
        # Set hip, knee, and ankle positions for right leg (indices 24, 26, 28)
        landmarks[24] = Landmark(0.5, 0, 0, 1)  # Right hip
        landmarks[26] = Landmark(0.5, -1, 0, 1) # Right knee
        landmarks[28] = Landmark(0.6, -2, 0, 1) # Right ankle
        
        result = score_deep_squat(landmarks)
        
        self.assertEqual(result.score, 2)
        self.assertEqual(result.reason, "动作基本合格")
        self.assertGreater(result.details["left_knee"], 150)
        self.assertGreater(result.details["right_knee"], 150)
    
    def test_score_deep_squat_mild_compensation(self):
        # Create landmarks with mild compensation (knee angles between 120 and 150)
        landmarks = [Landmark(0, 0, 0, 1) for _ in range(33)]
        # Set hip, knee, and ankle positions for left leg
        landmarks[23] = Landmark(0, 0, 0, 1)    # Left hip
        landmarks[25] = Landmark(0.5, -1, 0, 1) # Left knee
        landmarks[27] = Landmark(0, -2, 0, 1)   # Left ankle
        
        # Set hip, knee, and ankle positions for right leg
        landmarks[24] = Landmark(0.5, 0, 0, 1)  # Right hip
        landmarks[26] = Landmark(1.0, -1, 0, 1) # Right knee
        landmarks[28] = Landmark(0.5, -2, 0, 1) # Right ankle
        
        result = score_deep_squat(landmarks)
        
        self.assertEqual(result.score, 1)
        self.assertEqual(result.reason, "存在轻微代偿（如膝角不足）")
        self.assertGreater(result.details["left_knee"], 120)
        self.assertLess(result.details["left_knee"], 150)
        self.assertGreater(result.details["right_knee"], 120)
        self.assertLess(result.details["right_knee"], 150)
    
    def test_score_deep_squat_poor_form(self):
        # Create landmarks with poor form (knee angles < 120)
        landmarks = [Landmark(0, 0, 0, 1) for _ in range(33)]
        # Set hip, knee, and ankle positions for left leg
        landmarks[23] = Landmark(0, 0, 0, 1)    # Left hip
        landmarks[25] = Landmark(1.0, -1, 0, 1) # Left knee
        landmarks[27] = Landmark(0, -2, 0, 1)   # Left ankle
        
        # Set hip, knee, and ankle positions for right leg
        landmarks[24] = Landmark(0.5, 0, 0, 1)  # Right hip
        landmarks[26] = Landmark(1.5, -1, 0, 1) # Right knee
        landmarks[28] = Landmark(0.5, -2, 0, 1) # Right ankle
        
        result = score_deep_squat(landmarks)
        
        self.assertEqual(result.score, 0)
        self.assertEqual(result.reason, "明显代偿或无法完成动作")
        self.assertLess(result.details["left_knee"], 120)
        self.assertLess(result.details["right_knee"], 120)


if __name__ == "__main__":
    unittest.main()