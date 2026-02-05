from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import time
import io
import csv
from modes import Up_Down, Left_Right, snake_like

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
        
        if mode not in ["up-down", "left-right", "snake-like"]:
            raise HTTPException(400, "Режим должен быть 'up-down' или 'left-right'")
        
        file_bytes = await file.read()
        
        if mode == "up-down":
            blocks = Up_Down(file_bytes)
        elif mode == "left-right":
            blocks = Left_Right(file_bytes)
        else:
            blocks = snake_like(file_bytes)
        
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

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)