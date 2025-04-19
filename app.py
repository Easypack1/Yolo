from fastapi import FastAPI, UploadFile, File, Header
from fastapi.responses import JSONResponse
from ultralytics import YOLO
import shutil
import os
import mysql.connector
import uuid  # ✅ 랜덤 파일명 생성을 위한 모듈

app = FastAPI()

# YOLO 모델 로드
model = YOLO("yolov8n.pt")

# MySQL 연결
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="020712",  # 비밀번호 정확히 입력
        database="travel"
    )

# 규정 불러오기
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
    x_country: str = Header(...),
    x_airline: str = Header(...)
):
    # 규정 불러오기
    try:
        regulations = get_regulations(x_country, x_airline)
        print("✅ 불러온 규정 목록:", regulations)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"규정 불러오기 실패: {e}"})

    # 고유한 파일명 생성 (빈 파일명 대비)
    extension = os.path.splitext(file.filename)[-1] or ".jpg"
    filename = f"{uuid.uuid4().hex}{extension}"
    image_path = f"temp_{filename}"

    # 이미지 저장
    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # YOLO 감지
    try:
        results = model(image_path)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"YOLO 감지 실패: {e}"})

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

    # 임시 파일 삭제
    os.remove(image_path)

    return JSONResponse(content={"detections": detections})
