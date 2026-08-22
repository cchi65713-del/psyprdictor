import unittest

from prediction_fusion import PredictionFusion


class PredictionFusionTests(unittest.TestCase):

    def test_fusion_uses_pattern_weighted_and_context_scores(self):
        fusion = PredictionFusion()

        pattern_scores = {
            "B1": 60.0,
            "B4": 40.0,
        }
        weighted_scores = {
            "B1": 0.63,
            "B4": 0.09,
        }
        context_scores = {
            "B1": 1.0,
            "B4": 0.0,
        }

        result = fusion.fuse(
            pattern_scores,
            weighted_scores,
            context_scores,
        )

        self.assertEqual(result[0], "B1")
        self.assertGreater(result[1], 0)
        self.assertIn("B1", result[2])
        self.assertIn("B4", result[2])


if __name__ == "__main__":
    unittest.main()
