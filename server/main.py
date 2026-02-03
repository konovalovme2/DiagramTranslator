from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
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
    allow_methods=["*"],
    allow_headers=["*"],
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
    - mode: "up-down" или "left-right"
    
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
        
        
        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer)
        writer.writerow(["Шаг", "Действие"])
        
        #ВОТ ТУТ ЗАПИСЫВАЕМ В ТАБЛИЦУ

        csv_filename = f"Description_{int(time.time())}.csv"
        with open(csv_filename, "w", encoding="utf-8") as f:
            f.write(csv_buffer.getvalue())
        
        return FileResponse(
            path=csv_filename,
            filename=csv_filename,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={csv_filename}"}
        )
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(500, f"Ошибка обработки: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)