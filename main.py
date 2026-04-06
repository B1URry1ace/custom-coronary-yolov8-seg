import json
import io
import base64
import numpy as np
from ultralytics import YOLO
from PIL import Image

def init_context(context):
    context.logger.info("Инициализация модели YOLOv8-seg...")
    model = YOLO("/opt/nuclio/best.pt")
    context.user_data.model = model
    context.logger.info("✅ Модель загружена успешно")

def handler(context, event):
    context.logger.info("Получен запрос на инференс")
    
    data = event.body
    
    try:
        if isinstance(data, dict):
            # Nuclio уже распарсил JSON в словарь
            img_b64 = data.get("image")
            img_bytes = base64.b64decode(img_b64)
            
        elif isinstance(data, (bytes, bytearray)):
            try:
                # Пытаемся прочитать как сырую JSON-строку
                payload = json.loads(data.decode("utf-8"))
                img_bytes = base64.b64decode(payload["image"])
            except Exception:
                img_bytes = data
                
        elif isinstance(data, str):
            # Пришла строка с JSON
            payload = json.loads(data)
            img_bytes = base64.b64decode(payload["image"])
            
        else:
            raise ValueError(f"Неизвестный формат данных: {type(data)}")

        image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        
    except Exception as e:
        context.logger.error(f"Ошибка декодирования картинки: {str(e)}")
        return context.Response(body=f"Image error: {e}", status_code=500)

    # Инференс
    results = context.user_data.model.predict(
        image,
        conf=0.30,
        iou=0.45,
        retina_masks=True,
        verbose=False
    )

    annotations = []
    result = results[0]
    names = context.user_data.model.names 

    # Обработка результатов
    if result.masks is not None:
        for mask, cls_id, conf in zip(result.masks.xy, result.boxes.cls, result.boxes.conf):
            points = mask.flatten().tolist()
            class_name = names[int(cls_id)]
            
            annotations.append({
                "confidence": str(float(conf)),
                "label": class_name,
                "points": points,
                "type": "polygon"
            })

    # Явно возвращаем правильный JSON-ответ
    return context.Response(
        body=json.dumps(annotations),
        headers={},
        content_type='application/json',
        status_code=200
    )