from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from ultralytics import YOLO
import shutil
import os
import mysql.connector

app = FastAPI()

model = YOLO("yolov8n.pt")

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="여기에_비밀번호",  # 너의 비밀번호로 변경!
        database="travel"
    )

def get_regulations(country: str, airline: str) -> dict:
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT item, category, explanation FROM regulations
        WHERE country = %s AND airline = %s
    """, (country.strip(), airline.strip()))

    results = cursor.fetchall()
    cursor.close()
    conn.close()

    return {
        row['item'].lower().strip(): {
            "category": row['category'],
            "explanation": row['explanation']
        } for row in results
    }

@app.post("/predict")
async def predict(
    file: UploadFile = File(...),
    country: str = Form(...),
    airline: str = Form(...)
):
    # 규정 불러오기
    try:
        regulations = get_regulations(country, airline)
        print("✅ 불러온 규정 목록:", regulations)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"규정 불러오기 실패: {e}"})

    # 이미지 저장
    image_path = f"temp_{file.filename}"
    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # YOLO 감지
    results = model(image_path)

    detections = []
    for result in results:
        boxes = result.boxes
        for box in boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            label = result.names[cls_id].lower().strip()

            reg_info = regulations.get(label, {
                "category": "분류 불가",
                "explanation": "해당 품목에 대한 규정이 없습니다."
            })

            print("▶ 감지된 label:", label)
            print("▶ 규정 매칭 결과:", reg_info)

            detections.append({
                "label": label,
                "confidence": round(conf, 2),
                "category": reg_info.get("category", "분류 불가"),
                "description": reg_info.get("explanation", "설명 없음")
            })

    os.remove(image_path)
    return JSONResponse(content={"detections": detections})
