import cv2
import numpy as np
from pathlib import Path
from threading import Lock


class ONNXDetector:

    def __init__(self, model_path):
        self.net = cv2.dnn.readNetFromONNX(str(model_path))
        self.lock = Lock()
        self.input_size = 640

        self.names = {
            0: "person",
            63: "laptop",
            67: "cell phone",
            73: "book",
        }

    def detect(self, image, conf=0.50, iou=0.45):

        if image is None or image.size == 0:
            raise ValueError("Invalid camera frame")

        height, width = image.shape[:2]

        scale = min(
            self.input_size / width,
            self.input_size / height
        )

        new_width = max(1, round(width * scale))
        new_height = max(1, round(height * scale))

        resized = cv2.resize(
            image, (new_width, new_height)
        )

        padded = np.full(
            (640, 640, 3), 114, dtype=np.uint8
        )

        x = (640 - new_width) // 2
        y = (640 - new_height) // 2

        padded[
            y:y + new_height,
            x:x + new_width
        ] = resized

        blob = cv2.dnn.blobFromImage(
            padded,
            1 / 255.0,
            (640, 640),
            swapRB=True,
            crop=False
        )

        with self.lock:
            self.net.setInput(blob)
            output = self.net.forward().copy()

        predictions = output[0].T

        boxes = []
        scores = []
        class_ids = []

        for prediction in predictions:

            class_scores = prediction[4:]
            class_id = int(np.argmax(class_scores))
            confidence = float(class_scores[class_id])

            if confidence < conf:
                continue

            if class_id not in self.names:
                continue

            cx, cy, w, h = prediction[:4]

            boxes.append([
                float(cx - w / 2),
                float(cy - h / 2),
                float(w),
                float(h)
            ])

            scores.append(confidence)
            class_ids.append(class_id)

        detections = []

        for class_id, label in self.names.items():

            indices = [
                i for i, c in enumerate(class_ids)
                if c == class_id
            ]

            if not indices:
                continue

            selected = cv2.dnn.NMSBoxes(
                [boxes[i] for i in indices],
                [scores[i] for i in indices],
                conf,
                iou
            )

            for index in np.asarray(selected).flatten():
                original_index = indices[int(index)]

                detections.append({
                    "label": label,
                    "confidence": scores[original_index]
                })

        return detections