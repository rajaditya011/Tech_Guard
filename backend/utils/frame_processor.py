"""
HomeGuardian AI — Frame Processor
Frame preprocessing pipeline: resize, normalize, format conversion.
"""

import base64
import logging
from typing import Optional, Tuple

import numpy as np

logger = logging.getLogger("homeguardian.frame_processor")

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    logger.warning("OpenCV not available. Frame processing will use fallback mode.")


class FrameProcessor:
    """Processes raw video frames for YOLO inference and storage."""

    YOLO_INPUT_SIZE = (640, 640)
    STORAGE_SIZE = (640, 480)

    @staticmethod
    def decode_base64_frame(base64_data: str) -> Optional[np.ndarray]:
        if not CV2_AVAILABLE:
            return None
        try:
            img_bytes = base64.b64decode(base64_data)
            nparr = np.frombuffer(img_bytes, np.uint8)
            return cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        except Exception as e:
            logger.error(f"Failed to decode frame: {e}")
            return None

    @staticmethod
    def encode_frame_base64(frame: np.ndarray, quality: int = 85) -> str:
        if not CV2_AVAILABLE:
            return ""
        try:
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, quality])
            return base64.b64encode(buffer).decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to encode frame: {e}")
            return ""

    @staticmethod
    def resize_for_yolo(frame: np.ndarray) -> np.ndarray:
        if not CV2_AVAILABLE:
            return frame
        return cv2.resize(frame, FrameProcessor.YOLO_INPUT_SIZE)

    @staticmethod
    def resize_for_storage(frame: np.ndarray) -> np.ndarray:
        if not CV2_AVAILABLE:
            return frame
        return cv2.resize(frame, FrameProcessor.STORAGE_SIZE)

    @staticmethod
    def normalize(frame: np.ndarray) -> np.ndarray:
        return frame.astype(np.float32) / 255.0

    @staticmethod
    def preprocess_for_yolo(frame: np.ndarray) -> np.ndarray:
        resized = FrameProcessor.resize_for_yolo(frame)
        if CV2_AVAILABLE:
            rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        else:
            rgb = resized
        return FrameProcessor.normalize(rgb)

    @staticmethod
    def add_timestamp_overlay(frame: np.ndarray, timestamp: str) -> np.ndarray:
        if not CV2_AVAILABLE:
            return frame
        overlay = frame.copy()
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size = cv2.getTextSize(timestamp, font, 0.5, 1)[0]
        x, y = 10, frame.shape[0] - 10
        cv2.rectangle(overlay, (x - 2, y - text_size[1] - 4), (x + text_size[0] + 2, y + 4), (0, 0, 0), -1)
        cv2.putText(overlay, timestamp, (x, y), font, 0.5, (255, 255, 255), 1)
        return overlay

    @staticmethod
    def compute_motion_diff(frame1: np.ndarray, frame2: np.ndarray, threshold: int = 25) -> Tuple[float, np.ndarray]:
        if not CV2_AVAILABLE:
            return 0.0, np.zeros((1,))
        gray1 = cv2.GaussianBlur(cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY), (21, 21), 0)
        gray2 = cv2.GaussianBlur(cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY), (21, 21), 0)
        diff = cv2.absdiff(gray1, gray2)
        _, thresh = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)
        return np.sum(thresh > 0) / thresh.size, thresh
