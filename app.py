from fastapi import FastAPI, UploadFile, File, Header, HTTPException
from fastapi.responses import JSONResponse
from ultralytics import YOLO
import shutil
import os
import mysql.connector

app = FastAPI()

# YOLO 모델 로드
model = YOLO('yolov8n.pt')

# DB 연결 함수
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="비밀번호",  # 🔄 여기에 본인 비밀번호
        database="travel"
    )

# 규정 불러오기
def get_regulations(country: str, airline: str) -> dict:
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT item, category FROM regulations
        WHERE country=%s AND airline=%s
    """, (country, airline))

    results = cursor.fetchall()
    cursor.close()
    conn.close()

    # {'knife': '반입 불가', 'bottle': '기내 반입 가능' ...}
    return {row['item'].lower(): row['category'] for row in results}


@app.post("/predict")
async def predict(
    file: UploadFile = File(...),
    x_country: str = Header(...),
    x_airline: str = Header(...)
):
    # 규정 불러오기
    try:
        regulations = get_regulations(x_country, x_airline)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"규정 불러오기 실패: {e}")

    # 이미지 저장
    image_path = f"temp_{file.filename}"
    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # YOLO 예측
    results = model(image_path)

    detections = []
    for result in results:
        boxes = result.boxes
        for box in boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            name = result.names[cls_id]

            category = regulations.get(name.lower(), "분류 불가")
            detections.append({
                "label": name,
                "confidence": round(conf, 2),
                "category": category
            })

    os.remove(image_path)

    return JSONResponse(content={"detections": detections})
