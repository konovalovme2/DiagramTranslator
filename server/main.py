from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import cv2
import numpy as np
import time
import io
import csv

app = FastAPI(title="DiagramTranslator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)

@app.post("/api/v1/analyze")
async def analyze_flowchart(
    file: UploadFile = File(...),
    mode: str = Form("up-down"),
):
    """
    Анализ блок-схемы
    
    Параметры:
    - file: изображение
    - mode: "up-down", "left-right" или "snake-style"
    
    Возвращает: 
    - файл .csv для скачивания
    """
    
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(400, "Файл должен быть изображением")
        
        if mode not in ["up-down", "left-right"]:
            raise HTTPException(400, "Режим должен быть 'up-down' или 'left-right'")
        
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        #ВОТ ТУТ ИСПОЛЬЗУЕМ НАШИ МОДЕЛИ

        # (пока заглушка)
        blocks = [
            {"id": 1, "text": "Начало"},
            {"id": 2, "text": "i = 0"},
            {"id": 3, "text": "i < 10?"},
            {"id": 4, "text": "i = i + 1"},
            {"id": 5, "text": "Конец"}
        ]
        
        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer)
        writer.writerow(["Шаг", "Действие"])
        
        for block in blocks:
            writer.writerow([f"Шаг {block['id']}", block['text']])
        
        timestamp = int(time.time())
        return {
            "status": "success",
            "data": {
                "blocks": blocks,
                "blocks_count": len(blocks),
                "mode": mode
            }
        }
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(500, f"Ошибка обработки: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)