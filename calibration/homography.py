from calibration.pitch import image_to_pitch


class PitchCalibrator:
    def __init__(self, homography=None, pixels_per_meter=None):
        self.homography = homography
        self.pixels_per_meter = pixels_per_meter

    def pixel_to_meters(self, x, y):
        if self.homography is not None:
            return image_to_pitch((x, y), self.homography)
        if self.pixels_per_meter:
            return x / self.pixels_per_meter, y / self.pixels_per_meter
        return x, y
