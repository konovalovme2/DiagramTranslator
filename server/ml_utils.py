from ultralytics import YOLO
import easyocr
import cv2
import numpy as np

reader = easyocr.Reader(['ru', 'en'], gpu=False)
yolo_rects = YOLO(r'C:\Users\user\PycharmProjects\DiagramTranlator\server\yolo-models\rects.onnx')
yolo_arrows = YOLO(r'C:\Users\user\PycharmProjects\DiagramTranlator\server\yolo-models\arrows.onnx')
yolo_circs = YOLO(r'C:\Users\user\PycharmProjects\DiagramTranlator\server\yolo-models\circs.onnx')

def bytes_to_image(file_bytes):
    """Конвертирует байты в изображение"""
    nparr = np.frombuffer(file_bytes, np.uint8)
    return cv2.imdecode(nparr, cv2.IMREAD_COLOR)

def recognize_text_from_block(cropped_thresh):
    """Распознавание текста из блока схемы"""
    try:
        result = reader.readtext(
            cropped_thresh,
            detail=0,
            paragraph=True, 
            text_threshold=0.7  
        )
        return result[0].strip() if result else "???"
    except Exception as e:
        return f"??? (ошибка: {str(e)})"

def detect_rect(image):
    """Детекция блоков на изображении через YOLO"""
    if yolo_rects is None:
        raise RuntimeError("Модель YOLO не загружена")
    
    results = yolo_rects.predict(
        source=image,
        conf=0.5,
        device='cpu',
        verbose=False
    )


    
    blocks = []
    for r in results:
        if r.boxes is not None and len(r.boxes.xyxy) > 0:
            boxes = r.boxes.xyxy.cpu().numpy()
            for box in boxes:
                x1, y1, x2, y2 = map(int, box)
                
                padding_x = max(3, min(8, int((x2 - x1) * 0.1)))
                padding_y = max(3, min(8, int((y2 - y1) * 0.1)))
                
                x1 = max(0, x1 + padding_x)
                y1 = max(0, y1 + padding_y)
                x2 = min(image.shape[1], x2 - padding_x)
                y2 = min(image.shape[0], y2 - padding_y)
                
                if x2 <= x1 or y2 <= y1:
                    continue
                
                cropped = image[y1:y2, x1:x2]
                
                gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
                _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                
                cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
                
                blocks.append({
                    "bbox": (x1, y1, x2, y2),
                    "center": (cx, cy),
                    "cropped": thresh
                })
    
    return blocks


def detect_circs(image):
    """Детекция блоков на изображении через YOLO"""
    if yolo_rects is None:
        raise RuntimeError("Модель YOLO не загружена")

    results = yolo_circs.predict(
        source=image,
        conf=0.5,
        device='cpu',
        verbose=False
    )

    blocks = []
    for r in results:
        if r.boxes is not None and len(r.boxes.xyxy) > 0:
            boxes = r.boxes.xyxy.cpu().numpy()
            for box in boxes:
                x1, y1, x2, y2 = map(int, box)

                padding_x = max(3, min(8, int((x2 - x1) * 0.1)))
                padding_y = max(3, min(8, int((y2 - y1) * 0.1)))

                x1 = max(0, x1 + padding_x)
                y1 = max(0, y1 + padding_y)
                x2 = min(image.shape[1], x2 - padding_x)
                y2 = min(image.shape[0], y2 - padding_y)

                if x2 <= x1 or y2 <= y1:
                    continue

                cropped = image[y1:y2, x1:x2]

                gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
                _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

                cx, cy = (x1 + x2) / 2, (y1 + y2) / 2

                blocks.append({
                    "bbox": (x1, y1, x2, y2),
                    "center": (cx, cy),
                    "cropped": thresh
                })

    return blocks



def detect_arrow(image):
    """Детекция стрелок на изображении через YOLO"""
    if yolo_arrows is None:
        raise RuntimeError("Модель YOLO не загружена")
    
    results = yolo_arrows.predict(
        source=image,
        conf=0.5,
        device='cpu',
        verbose=False
    )
    
    arrows = []
    for r in results:
        if r.boxes is not None and len(r.boxes.xyxy) > 0:
            for box in r.boxes.xyxy.cpu().numpy():

                x1, y1, x2, y2 = map(int, box)
                cx, cy = (x1 + x2) / 2, (y1 + y2) / 2

                arrows.append({
                    "bbox": (x1, y1, x2, y2),
                    "center": (cx, cy)
                })
    
    return arrows