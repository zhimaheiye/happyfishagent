"""Reuse MaaFramework recognition on explicit frames, without a gameplay Pipeline.

The recognition controller never sends game input. Real screenshots/clicks remain
in the Recorder's selected transport; recognition receives an explicit frame.
"""
import dataclasses
import json
from datetime import datetime
from pathlib import Path

import numpy as np


class MaaVision:
    def __init__(self, session_dir, model_dir, adb):
        from maa.controller import AdbController
        from maa.define import MaaAdbScreencapMethodEnum, MaaAdbInputMethodEnum
        from maa.resource import Resource
        from maa.tasker import Tasker
        from maa.toolkit import Toolkit

        self.root = Path(session_dir) / "vision"
        self.root.mkdir(exist_ok=True)
        self.frame_path = self.root / "frame.png"
        self.last_ocr_image = None
        Toolkit.init_option(str(self.root), {"stdout_level": 0})
        self.resource = Resource()
        self.resource.use_cpu()
        if not self.resource.post_ocr_model(Path(model_dir)).wait().succeeded:
            raise RuntimeError("Maa OCR model failed to load: %s" % model_dir)
        # post_recognition receives the image explicitly. This controller is only
        # an initialized API holder: never submit game input or screenshot jobs.
        self.controller = AdbController(adb.adb_path, adb.serial,
                                       MaaAdbScreencapMethodEnum.Encode,
                                       MaaAdbInputMethodEnum.AdbShell)
        if not self.controller.post_connection().wait().succeeded:
            raise RuntimeError("Maa recognition controller initialization failed")
        self.tasker = Tasker()
        if not self.tasker.bind(self.resource, self.controller):
            raise RuntimeError("Maa vision resource binding failed")

    def ocr(self, picture, roi=None):
        from maa.pipeline import JRecognitionType, JOCR
        image = np.array(picture.convert("RGB"))[:, :, ::-1].copy()
        picture.save(self.frame_path)
        # Keep the exact recognition source, including guard/module reads. The
        # Recorder's earlier after-frame can still be a transition animation.
        self.last_ocr_image = self.root / (datetime.now().strftime("%Y%m%d-%H%M%S-%f") + ".png")
        picture.save(self.last_ocr_image)
        params = JOCR(roi=tuple(roi)) if roi else JOCR()
        job = self.tasker.post_recognition(JRecognitionType.OCR, params, image).wait()
        detail = job.get()
        if not detail or not detail.nodes or not detail.nodes[0].recognition:
            raise RuntimeError("Maa OCR did not return a recognition result")
        rows = detail.nodes[0].recognition.all_results
        def encode(value):
            if dataclasses.is_dataclass(value):
                return dataclasses.asdict(value)
            if hasattr(value, "tolist"):
                return value.tolist()
            raise TypeError(type(value).__name__)
        result = json.loads(json.dumps(rows, default=encode))
        self.last_ocr_image.with_suffix(".json").write_text(
            json.dumps({"image": self.last_ocr_image.name, "roi": roi, "rows": result},
                       ensure_ascii=False, indent=2), encoding="utf-8")
        return result


class AdbMaaDevice:
    def __init__(self, adb, vision):
        self.adb = adb
        self.vision = vision
        self.serial = adb.serial
        self.source = "adb+maa-vision"

    def screencap(self):
        return self.adb.screencap()

    def coordinate_space(self, size):
        return self.adb.coordinate_space(size)

    def tap(self, x, y):
        return self.adb.tap(x, y)

    def swipe(self, x1, y1, x2, y2, duration):
        return self.adb.swipe(x1, y1, x2, y2, duration)

    def ocr(self, roi=None):
        return self.vision.ocr(self.screencap(), roi)
