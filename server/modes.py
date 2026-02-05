from ml_utils import bytes_to_image, detect_rect, detect_arrow, recognize_text_from_block
from graph_utils import match_arrows_to_blocks, distance, translate_graph

def Up_Down(file_bytes):
    """Обработка схемы сверху вниз"""
    image = bytes_to_image(file_bytes)
    if image is None:
        raise ValueError("Невозможно прочитать изображение")
    
    blocks = detect_rect(image)
    
    if len(blocks) == 0:
        return [{"id": 1, "text": "Блоки не обнаружены"}]
    
    blocks_sorted = sorted(blocks, key=lambda b: b["center"][1])
    
    text_blocks = [recognize_text_from_block(b["cropped"]) for b in blocks_sorted]
    centers = [b["center"] for b in blocks_sorted]
    
    text_res = text_blocks.copy()
    for i in range(len(centers)):
        for j in range(i + 1, len(centers)):
            if abs(centers[i][1] - centers[j][1]) < 20:
                if centers[i][0] < centers[j][0]:
                    text_res[i] = f"Вариант 1 - {text_blocks[i]}"
                    text_res[j] = f"Вариант 2 - {text_blocks[j]}"
                else:
                    text_res[i] = f"Вариант 2 - {text_blocks[i]}"
                    text_res[j] = f"Вариант 1 - {text_blocks[j]}"
    
    formatted = []
    step = 0
    for text in text_res:
        if "Вариант" in text:
            formatted.append(text)
        else:
            step += 1
            formatted.append([step, text])
    
    return [{"id": i+1, "text": text} for i, text in enumerate(formatted)]

def Left_Right(file_bytes):
    """Обработка схемы слева направо"""
    image = bytes_to_image(file_bytes)
    if image is None:
        raise ValueError("Невозможно прочитать изображение")
    
    blocks = detect_rect(image)
    
    if len(blocks) == 0:
        return [{"id": 1, "text": "Блоки не обнаружены"}]
    
    blocks_sorted = sorted(blocks, key=lambda b: b["center"][0])
    
    text_blocks = [recognize_text_from_block(b["cropped"]) for b in blocks_sorted]
    centers = [b["center"] for b in blocks_sorted]
    
    text_res = text_blocks.copy()
    for i in range(len(centers)):
        for j in range(i + 1, len(centers)):
            if abs(centers[i][0] - centers[j][0]) < 20:
                if centers[i][1] < centers[j][1]:
                    text_res[i] = f"Вариант 1 - {text_blocks[i]}"
                    text_res[j] = f"Вариант 2 - {text_blocks[j]}"
                else:
                    text_res[i] = f"Вариант 2 - {text_blocks[i]}"
                    text_res[j] = f"Вариант 1 - {text_blocks[j]}"
    
    formatted = []
    step = 0
    for text in text_res:
        if "Вариант" in text:
            formatted.append(text)
        else:
            step += 1
            formatted.append(f"{step}. {text}")
    
    return [{"id": i+1, "text": text} for i, text in enumerate(formatted)]

def snake_like(file_bytes):
    """Обход схемы и построение графа"""
    image = bytes_to_image(file_bytes)
    if image is None:
        raise ValueError("Невозможно прочитать изображение")
    
    blocks = detect_rect(image)
    arrows = detect_arrow(image)
    if len(blocks) == 0:
        return [{"id": -1, "text": "Блоки не обнаружены"}]
    elif len(arrows) == 0:
        return [{"id": -1, "text": "Стрелки не обнаружены"}]
    
    graph = match_arrows_to_blocks(blocks, arrows)
    start_idx = min(
        range(len(blocks)),
        key=lambda i: (blocks[i]["center"][1], blocks[i]["center"][0])
    )

    result = translate_graph(graph, blocks, start_idx)
    
    return [{"id": i+1, "text": line} for i, line in enumerate(result)]