"""
Configuration constants and settings for CrowdSafe AI.
"""

import os
from pydantic import BaseModel

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
PROCESSED_DIR = os.path.join(BASE_DIR, "processed")
DATA_DIR = os.path.join(BASE_DIR, "data")
SAMPLE_DIR = os.path.join(BASE_DIR, "sample_data")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(SAMPLE_DIR, exist_ok=True)

# Risk Level Definitions & Colors (BGR for OpenCV & HEX for UI)
RISK_LEVELS = {
    "normal": {
        "label": "Normal",
        "color_hex": "#10B981",  # Emerald Green
        "color_bgr": (129, 185, 16),
        "code": 0
    },
    "increasing": {
        "label": "Increasing",
        "color_hex": "#F59E0B",  # Amber / Yellow
        "color_bgr": (11, 158, 245),
        "code": 1
    },
    "high": {
        "label": "High",
        "color_hex": "#F97316",  # Orange
        "color_bgr": (22, 115, 249),
        "code": 2
    },
    "critical": {
        "label": "Critical",
        "color_hex": "#EF4444",  # Red
        "color_bgr": (68, 68, 239),
        "code": 3
    }
}

# Detection defaults
DEFAULT_CONFIDENCE_THRESHOLD = 0.35
DEFAULT_PERSON_CLASS_ID = 0  # COCO class 0 is 'person'

# Video playback/processing speed limit
MAX_PROCESSING_FPS = 25.0
