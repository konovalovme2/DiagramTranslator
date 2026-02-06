from ml_utils import bytes_to_image, detect_rect, detect_arrow, recognize_text_from_block, detect_circs, detect_gates
from graph_utils import match_arrows_to_blocks, distance, translate_graph




def Up_Down(file_bytes):
    """Обработка схемы сверху вниз"""
    image = bytes_to_image(file_bytes)
    if image is None:
        raise ValueError("Невозможно прочитать изображение")
    
    blocks = detect_rect(image)
    blocks_circs = detect_circs(image)
    gates = detect_gates(image)
    if len(blocks_circs) > 0:
        blocks.extend(blocks_circs)
    if len(blocks) == 0:
        return [{"id": 1, "text": "Блоки не обнаружены"}]
    
    blocks_sorted = sorted(blocks, key=lambda b: b["center"][1])
    gates_sorted = sorted(gates, key=lambda b: b["center"][1])
    
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
                    text_res[j] = f"Вариант 2 - {text_blocks[i]}"
                    text_res[i] = f"Вариант 1 - {text_blocks[j]}"

    # for i in range(0, len(text_res)) :
    #     if "Вариант" in text_res[i] and i > 0:
    #         ids.append(step)
    #         step += 1
    #         formatted.append(f"{step}. {text_res[i]}")
    #     else:
    #         if "Вариант" in text_res[i]:
    #             ids.append(step)
    #             formatted.append(text_res[i])
    #             step += 1
    ids = list(range(1, len(text_res)+1))

    # j = 0
    # for i in range(len(text_res)):
    #     j += 1
    #     if 'Вариант' in text_res[i]:
    #         ids.append(j)
    #         text_res[i] = str(j) + '. ' + text_res[i]
    #         j -= 1
    #     else:
    #         if ('Вариант' in text_res[i - 1]) and (i > 0):
    #             ids.append(j)
    #             j += 1
    #             text_res[i] = str(j) + '. ' + text_res[i]
    #         else:
    #             ids.append(j)
    #             text_res[i] = str(j) + '. ' + text_res[i]

    # for i in range(len(ids)):
        # if 'Вариант' in text_res[i]:
        #     ids[i] = text_res[i].split()[1][0:9] + ' ' + text_res[i].split()[2][0]
    counter = 0

    for i in range(len(ids)):
        if  'Вариант 1' in text_res[i]  and counter == 0:
            ids[i] = str(i) + '.Вариант 1'
            counter = i
        if 'Вариант 1' in text_res[i] and counter != 0:
            counter += 1
            ids[i] = str(counter) + '.Вариант 1'

    counter = 0
    for i in range(len(ids)):
        if 'Вариант 2' in text_res[i] and counter == 0:
            ids[i] = str(i-1) + '.Вариант 2'
            counter = i
        if 'Вариант 2' in text_res[i] and counter != 0:
            counter += 1
            ids[i] = str(counter-1) + '.Вариант 2'

    for i in range(len(ids)):
        if ('Вариант' in text_res[i - 1]) and (i > 0) and ('Вариант' not in text_res[i]):
            ids[i] = str(int(ids[i-1][0])+1)
    formatted = []
    for i in range(len(text_res)):
        if 'Вариант' not in text_res[i]:
            formatted.append(text_res[i])
        else:
            formatted.append(text_res[i].split('-')[1][1:])
    print(gates_sorted)
    text_gates = [recognize_text_from_block(g["cropped"]) for g in gates_sorted]
    if len(gates) > 0:
        for i in range(len(text_gates)):
            centers.append((gates[i]['center']))
        centers_sorted = sorted(centers, key=lambda x: x[1])

        # text_gates = [recognize_text_from_block(g["cropped"] for g in gates_sorted)]
        #
        for i in range(len(text_gates)):
            # print(centers_sorted)
            # print(gates[i]['center'])
            index = centers_sorted.index(gates_sorted[i]['center'])
            print(index, gates_sorted[i]['center'])
            if text_gates[i] != '???':
                formatted.insert(index, 'УСЛОВИЕ: ' + text_gates[i])
                ids.insert(index, '')
            else:
                formatted.insert(index, 'УСЛОВИЕ')
                ids.insert(index, '')

    return [{"id": i, "text": text} for i, text in zip(ids, formatted)]
def Left_Right(file_bytes):
    """Обработка схемы слева направо"""
    image = bytes_to_image(file_bytes)
    if image is None:
        raise ValueError("Невозможно прочитать изображение")
    
    blocks = detect_rect(image)
    blocks_circs = detect_circs(image)
    gates = detect_gates(image)
    if len(blocks_circs) > 0:
        blocks.extend(blocks_circs)
    
    if len(blocks) == 0:
        return [{"id": 1, "text": "Блоки не обнаружены"}]
    
    blocks_sorted = sorted(blocks, key=lambda b: b["center"][0])
    gates_sorted = sorted(gates, key=lambda b: b["center"][0])
    print(blocks_sorted)
    
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
                    text_res[j] = f"Вариант 2 - {text_blocks[i]}"
                    text_res[i] = f"Вариант 1 - {text_blocks[j]}"
    ids = list(range(1, len(text_res) + 1))
    counter = 0

    for i in range(len(ids)):
        if 'Вариант 1' in text_res[i] and counter == 0:
            ids[i] = str(i) + '.Вариант 1'
            counter = i
        if 'Вариант 1' in text_res[i] and counter != 0:
            counter += 1
            ids[i] = str(counter) + '.Вариант 1'

    counter = 0
    for i in range(len(ids)):
        if 'Вариант 2' in text_res[i] and counter == 0:
            ids[i] = str(i - 1) + '.Вариант 2'
            counter = i
        if 'Вариант 2' in text_res[i] and counter != 0:
            counter += 1
            ids[i] = str(counter - 1) + '.Вариант 2'

    for i in range(len(ids)):
        if ('Вариант' in text_res[i - 1]) and (i > 0) and ('Вариант' not in text_res[i]):
            ids[i] = str(int(str(ids[i - 1]).split('.')[0]) + 1)
        if ('Вариант' not in text_res[i - 1]) and (i > 0) and ('Вариант' not in text_res[i]):
            ids[i] = str(int(str(ids[i - 1]).split('.')[0]) + 1)

    formatted = []
    for i in range(len(text_res)):
        if 'Вариант' not in text_res[i]:
            formatted.append(text_res[i])
        else:
            formatted.append(text_res[i].split('-')[1][1:])

    print(len(gates))
    text_gates = [recognize_text_from_block(g["cropped"]) for g in gates_sorted]
    if len(gates) > 0:
        for i in range(len(text_gates)):
            centers.append((gates_sorted[i]['center']))
        centers_sorted = sorted(centers, key=lambda x: x[0])


        # text_gates = [recognize_text_from_block(g["cropped"] for g in gates_sorted)]
        #
        for i in range(len(text_gates)):
            print(centers_sorted)
            print(gates[i]['center'])
            index = centers_sorted.index(gates[i]['center'])
            if text_gates[i] != '???':
                formatted.insert(index, 'УСЛОВИЕ: '+  text_gates[i])
                ids.insert(index, '')
            else:
                formatted.insert(index, 'УСЛОВИЕ')
                ids.insert(index, '')
    if formatted[-1] == 'УСЛОВИЕ':
        formatted = formatted[0:len(formatted)-1]
        ids = ids[0:len(ids)-1]

    return [{"id": i, "text": text} for i, text in zip(ids, formatted)]

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