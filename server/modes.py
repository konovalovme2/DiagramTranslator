from ml_utils import bytes_to_image, detect_rect, detect_arrow, recognize_text_from_block, detect_circs
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
            formatted.append(f"{step}. {text}")
    
    return [{"id": i+1, "text": text} for i, text in enumerate(formatted)]

def Left_Right(file_bytes):
    """Обработка схемы слева направо"""
    image = bytes_to_image(file_bytes)
    if image is None:
        raise ValueError("Невозможно прочитать изображение")
    
    blocks = detect_rect(image)
    blocks_circs = detect_circs(image)
    if len(blocks_circs) > 0:
        blocks.extend(blocks_circs)
    
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
    image = bytes_to_image(file_bytes)
    blocks = detect_rect(image)
    arrows = detect_arrow(image)
    
    if not blocks:
        return [{"id": -1, "text": "Блоки не обнаружены"}]
    if not arrows:
        return [{"id": -1, "text": "Стрелки не обнаружены"}]
    
    current_idx = min(range(len(blocks)), key=lambda i: (blocks[i]["center"][1], blocks[i]["center"][0]))
    result = [recognize_text_from_block(blocks[current_idx]["cropped"])]
    visited = {current_idx}
    
    for _ in range(len(blocks) - 1):
        arrow_idx = min(
            range(len(arrows)),
            key=lambda i: distance(blocks[current_idx]["center"], arrows[i]["center"])
        )
        arrow_center = arrows[arrow_idx]["center"]

        next_idx = None
        min_dist = float('inf')
        for i, block in enumerate(blocks):
            if i in visited:
                continue
            dist = distance(arrow_center, block["center"])
            if dist < min_dist:
                min_dist = dist
                next_idx = i
        
        if next_idx is None:
            break
        
        visited.add(next_idx)
        result.append(recognize_text_from_block(blocks[next_idx]["cropped"]))
        current_idx = next_idx
    
    return [{"id": i+1, "text": text} for i, text in enumerate(result)]