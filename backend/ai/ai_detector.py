"""
MediaPipe-based multi-person pose estimator with a temporal wave-gesture detector.
When a distress wave is detected for a mapped patient ID, it notifies the FastAPI backend.

This module is intentionally written to be self-contained and easy to integrate:
- Uses MediaPipe Tasks Pose Landmarker (LIVE_STREAM, num_poses=10)
- Maps poses to patient zones (ward layout) using normalized coordinates
- Implements temporal reversal-count logic on wrist movement relative to shoulder
- Posts alerts asynchronously to http://localhost:8000/api/alert using httpx

Note: This is a runnable reference. Model path and camera index may need adjustment.
"""
from __future__ import annotations

import asyncio
import time
from typing import Dict, Optional, Tuple, List

import numpy as np
import cv2
import httpx
import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# MediaPipe Tasks API
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
# Allow overriding the model path via env var POSE_LANDMARKER_TASK
POSE_TASK_PATH = os.getenv("POSE_LANDMARKER_TASK", "models/pose_landmarker_full.task")  # Ensure the file exists
CAMERA_INDEX = 0
MAX_PERSONS = 10  # Multi-person detection

# Example ward zones (normalized [0,1] coordinates): xmin, ymin, xmax, ymax
PATIENT_ZONES: Dict[str, Tuple[float, float, float, float]] = {
    "P-01": (0.00, 0.00, 0.33, 0.50),
    "P-02": (0.33, 0.00, 0.66, 0.50),
    "P-03": (0.66, 0.00, 1.00, 0.50),
    "P-04": (0.00, 0.50, 0.33, 1.00),
    "P-05": (0.33, 0.50, 0.66, 1.00),
    "P-06": (0.66, 0.50, 1.00, 1.00),
}

# Temporal wave detection state per patient
# Fields: count (# of reversals), last_direction (-1/0/+1), last_time (sec)
WAVE_STATE: Dict[str, Dict[str, float]] = {}

# Thresholds
DELTA_X_THRESH = 0.08   # Horizontal wrist movement relative to shoulder (normalized)
COUNT_TARGET = 3        # Reversal count target
TIMEOUT_SEC = 3.0       # Time window to reach COUNT_TARGET

BACKEND_ALERT_URL = "http://localhost:8000/api/alert"

# -----------------------------------------------------------------------------
# Utility functions
# -----------------------------------------------------------------------------

def get_patient_id(center_x: float, center_y: float) -> Optional[str]:
    """Map a body center to a patient zone ID using PATIENT_ZONES.
    center_x/center_y are normalized [0,1].
    """
    for pid, (xmin, ymin, xmax, ymax) in PATIENT_ZONES.items():
        if xmin <= center_x <= xmax and ymin <= center_y <= ymax:
            return pid
    return None


def check_for_distress_wave(patient_id: str, shoulder: Tuple[float, float], wrist: Tuple[float, float]) -> bool:
    """Temporal gesture detector: count direction reversals of wrist vs. shoulder.

    Logic:
    - Compute dx = wrist_x - shoulder_x (normalized)
    - If |dx| > DELTA_X_THRESH, determine direction sign(dx)
    - Increment count only on direction reversal
    - Reset state if TIMEOUT_SEC exceeded since last event
    - Return True when count reaches COUNT_TARGET within TIMEOUT_SEC
    """
    global WAVE_STATE

    now = time.monotonic()
    dx = wrist[0] - shoulder[0]
    direction = 1 if dx > DELTA_X_THRESH else (-1 if dx < -DELTA_X_THRESH else 0)

    state = WAVE_STATE.get(patient_id, {"count": 0, "last_direction": 0, "last_time": 0.0})

    # Timeout reset
    if state["last_time"] and (now - state["last_time"]) > TIMEOUT_SEC:
        state = {"count": 0, "last_direction": 0, "last_time": 0.0}

    if direction != 0:
        if state["last_direction"] != 0 and direction != state["last_direction"]:
            state["count"] += 1
        state["last_direction"] = direction
        state["last_time"] = now

    WAVE_STATE[patient_id] = state
    return state["count"] >= COUNT_TARGET


# -----------------------------------------------------------------------------
# Core processing
# -----------------------------------------------------------------------------

async def notify_backend(patient_id: str):
    """Send alert to backend asynchronously using httpx."""
    payload = {"patient_id": patient_id, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            await client.post(BACKEND_ALERT_URL, json=payload)
        except Exception:
            # Best-effort notify
            pass


def create_pose_landmarker() -> mp_vision.PoseLandmarker:
    base_options = mp_python.BaseOptions(model_asset_path=POSE_TASK_PATH)
    options = mp_vision.PoseLandmarkerOptions(
        base_options=base_options,
        running_mode=mp_vision.RunningMode.IMAGE,  # Use synchronous IMAGE mode (no callback required)
        num_poses=MAX_PERSONS,
        min_pose_detection_confidence=0.5,
        min_pose_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    )
    return mp_vision.PoseLandmarker.create_from_options(options)


async def run_live():
    """Run live camera processing loop.
    This function demonstrates how to plug the detector into the backend.
    """
    landmarker = create_pose_landmarker()
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print("[ai_detector] Cannot open camera")
        return

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                await asyncio.sleep(0)
                continue

            # Convert to MediaPipe Image
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)

            # Synchronous detection in IMAGE mode (no callback required)
            result = landmarker.detect(mp_image)

            poses = getattr(result, "pose_landmarks", []) or []
            for pose in poses:
                # Each pose is a list of landmarks with .x/.y/.z
                lm = pose  # List of landmarks
                if len(lm) <= 16:
                    continue
                shoulder = (float(lm[11].x), float(lm[11].y))
                wrist = (float(lm[16].x), float(lm[16].y))

                # Estimate body center from hips/shoulders (simplified)
                center_x = np.clip(np.mean([lm[11].x, lm[12].x, lm[23].x, lm[24].x]), 0.0, 1.0)
                center_y = np.clip(np.mean([lm[11].y, lm[12].y, lm[23].y, lm[24].y]), 0.0, 1.0)
                pid = get_patient_id(center_x, center_y)
                if not pid:
                    continue

                if check_for_distress_wave(pid, shoulder, wrist):
                    await notify_backend(pid)

            await asyncio.sleep(0)  # yield
    finally:
        cap.release()


if __name__ == "__main__":
    # Run a short demo loop (press Ctrl+C to stop). Adjust CAMERA_INDEX and POSE_TASK_PATH.
    try:
        asyncio.run(run_live())
    except KeyboardInterrupt:
        pass
