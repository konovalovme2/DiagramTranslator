from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import cv2
import numpy as np
import time
import io
import csv
from ocr_service import preprocess_image, recognize_text

app = FastAPI(title="Flow2Code API")

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
    output_format: str = Form("json")  # ← Новый параметр: "json" или "csv"
):
    """
    Анализ блок-схемы
    
    Параметры:
    - file: изображение
    - mode: "up-down" или "left-right"
    - output_format: "json" или "csv" (по умолчанию "json")
    
    Возвращает: 
    - JSON с данными ИЛИ
    - файл .csv для скачивания
    """
    start_time = time.time()
    
    try:
        # Валидация
        if not file.content_type.startswith('image/'):
            raise HTTPException(400, "Файл должен быть изображением")
        
        if mode not in ["up-down", "left-right"]:
            raise HTTPException(400, "Режим должен быть 'up-down' или 'left-right'")
        
        if output_format not in ["json", "csv"]:
            raise HTTPException(400, "Формат должен быть 'json' или 'csv'")
        
        # Обработка изображения
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise HTTPException(400, "Невозможно прочитать изображение")
        
        processed_img = preprocess_image(img)
        blocks = recognize_text(processed_img)
        
        # Сортировка по режиму
        if mode == "left-right":
            blocks.sort(key=lambda b: b["bbox"][0][0])
        else:
            blocks.sort(key=lambda b: b["bbox"][0][1])
        
        processing_time = int((time.time() - start_time) * 1000)
        
        # ===== ВОЗВРАТ В ЗАВИСИМОСТИ ОТ ФОРМАТА =====
        
        if output_format == "csv":
            # Создаём CSV в памяти
            csv_buffer = io.StringIO()
            writer = csv.writer(csv_buffer)
            
            # Заголовок
            writer.writerow(["ID", "Текст", "Уверенность", "X1", "Y1", "X2", "Y2", "Режим"])
            
            # Данные
            for block in blocks:
                bbox = block["bbox"]
                writer.writerow([
                    block["id"],
                    block["text"],
                    round(block["confidence"], 4),
                    bbox[0][0],  # X1
                    bbox[0][1],  # Y1
                    bbox[2][0],  # X2
                    bbox[2][1],  # Y2
                    mode
                ])
            
            # Сохраняем в файл
            csv_filename = f"flowchart_{int(time.time())}.csv"
            with open(csv_filename, "w", encoding="utf-8") as f:
                f.write(csv_buffer.getvalue())
            
            # Возвращаем файл для скачивания
            return FileResponse(
                path=csv_filename,
                filename=csv_filename,
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename={csv_filename}"}
            )
        
        else:
            # Возвращаем JSON (по умолчанию)
            return {
                "status": "success",
                "data": {
                    "blocks": blocks,
                    "blocks_count": len(blocks),
                    "mode": mode,
                    "processing_time_ms": processing_time
                }
            }
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(500, f"Ошибка обработки: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)