from ultralytics import YOLO

# YOLO 모델 로딩
model = YOLO("yolov8n.pt")

def detect_image(image_path: str):
    results = model(image_path)
    detections = []

    for result in results:
        boxes = result.boxes
        for box in boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            label = result.names[cls_id]
            detections.append({"label": label, "confidence": round(conf, 2)})

    return detections
