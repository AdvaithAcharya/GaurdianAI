"""
MediaPipe Face Landmarker-based simple facial distress detector.
- Uses mouth opening ratio and eyebrow raise heuristics as a proxy for distress
- Posts to backend /api/alert with type="facial_distress" when threshold crossed

Note: requires models/face_landmarker.task (download and place it in models/)
"""
from __future__ import annotations

import asyncio
import time
from typing import List

import cv2
import httpx
import numpy as np

import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision

FACE_TASK_PATH = "models/face_landmarker.task"  # Download appropriate face landmarker model
CAMERA_INDEX = 0
BACKEND_ALERT_URL = "http://localhost:8000/api/alert"

# Landmark indices for mouth and brows (MediaPipe canonical indices)
# Using Face Landmarker (468 landmarks similar to FaceMesh); indices may vary by model version.
MOUTH_TOP = 13
MOUTH_BOTTOM = 14
BROW_LEFT_INNER = 70
BROW_RIGHT_INNER = 300
NOSE_TIP = 1

MOUTH_OPEN_THRESH = 0.055  # Relative to face size
BROW_RAISE_THRESH = 0.06   # Relative to face size

async def notify_backend(patient_id: str):
    payload = {"patient_id": patient_id, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "type": "facial_distress"}
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            await client.post(BACKEND_ALERT_URL, json=payload)
        except Exception:
            pass


def create_face_landmarker() -> mp_vision.FaceLandmarker:
    options = mp_vision.FaceLandmarkerOptions(
        base_options=mp_python.BaseOptions(model_asset_path=FACE_TASK_PATH),
        running_mode=mp_vision.RunningMode.IMAGE,
        num_faces=5,
        output_face_blendshapes=False,
        min_face_detection_confidence=0.5,
        min_face_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    )
    return mp_vision.FaceLandmarker.create_from_options(options)


def facial_distress_score(landmarks: List[mp.NormalizedLandmark]) -> float:
    lm = landmarks
    if len(lm) <= max(MOUTH_TOP, MOUTH_BOTTOM, BROW_LEFT_INNER, BROW_RIGHT_INNER, NOSE_TIP):
        return 0.0
    # Approximate face size as distance from nose tip to chin-like region (use mouth bottom as proxy)
    face_size = abs(lm[MOUTH_BOTTOM].y - lm[NOSE_TIP].y)
    if face_size <= 1e-6:
        face_size = 1.0
    mouth_open = abs(lm[MOUTH_BOTTOM].y - lm[MOUTH_TOP].y) / face_size
    brow_raise = abs(lm[BROW_LEFT_INNER].y - lm[NOSE_TIP].y) / face_size
    score = 0.0
    if mouth_open > MOUTH_OPEN_THRESH:
        score += 0.6
    if brow_raise < (1.0 - BROW_RAISE_THRESH):  # smaller y means raised (in normalized coords)
        score += 0.4
    return min(score, 1.0)


async def run_live():
    landmarker = create_face_landmarker()
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print("[facial_detector] Cannot open camera")
        return
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                await asyncio.sleep(0)
                continue
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
            result = landmarker.detect(mp_image)
            faces = getattr(result, "face_landmarks", []) or []
            for flm in faces:
                score = facial_distress_score(flm)
                if score >= 0.8:
                    # Default to P-01 if you want to map via zones; adapt as needed
                    await notify_backend("P-01")
            await asyncio.sleep(0)
    finally:
        cap.release()


if __name__ == "__main__":
    try:
        asyncio.run(run_live())
    except KeyboardInterrupt:
        pass
