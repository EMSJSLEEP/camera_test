import cv2

control_dict = {
    "exposure": cv2.CAP_PROP_EXPOSURE,
    "focus": cv2.CAP_PROP_FOCUS,
    "gain": cv2.CAP_PROP_GAIN,
    "exposure_auto": cv2.CAP_PROP_AUTO_EXPOSURE,
    "focus_auto": cv2.CAP_PROP_AUTOFOCUS
}

class Windows_Tools(object):
    def __init__(self, camera_dev, camera_num=None):
        if camera_dev.isOpened():
            self.cap = camera_dev
            self.set_ex_auto_mode(False)
            self.set_fo_auto_mode(False)

    def set(self, type, value):
        assert type in ["exposure", "focus", "gain", "exposure_auto", "focus_auto"]
        self.cap.set(control_dict[type], value)

    def set_ex_auto_mode(self, auto):
        assert auto in [True, False]
        auto = 1 if auto else 0
        self.set("exposure_auto", auto)

    def set_fo_auto_mode(self, auto):
        assert auto in [True, False]
        auto = 1 if auto else 0
        self.set("focus_auto", auto)

