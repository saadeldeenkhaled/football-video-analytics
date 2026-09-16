import unittest

from analytics.tracking import CentroidTracker
from calibration.pitch import estimate_pixels_per_meter, image_to_pitch
from team.assignment import assign_team


class CoreAnalyticsTests(unittest.TestCase):
    def test_tracker_preserves_id_and_accumulates_distance(self):
        tracker = CentroidTracker(max_distance=10)
        first = tracker.update([((0, 0), "red")], fps=25, pixels_per_meter=40)
        second = tracker.update([((4, 0), "red")], fps=25, pixels_per_meter=40)
        self.assertEqual(first[0].track_id, second[0].track_id)
        self.assertAlmostEqual(second[0].distance_m, 0.1)
        self.assertAlmostEqual(second[0].speed_mps, 2.5)

    def test_calibration_helpers(self):
        self.assertEqual(estimate_pixels_per_meter(680), 10)
        self.assertEqual(image_to_pitch((2, 3)), (2, 3))
        self.assertEqual(image_to_pitch((2, 3), [[1, 0, 1], [0, 1, 2], [0, 0, 1]]), (3, 5))

    def test_team_assignment(self):
        self.assertEqual(assign_team((220, 20, 20)), "red")
        self.assertEqual(assign_team((20, 20, 220)), "blue")
        self.assertEqual(assign_team(()), "unknown")


if __name__ == "__main__":
    unittest.main()