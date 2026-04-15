# custom-coronary-yolov8-seg

## Этап 0: Что должно быть уже готово

Установлен Docker Desktop + CVAT запущен (docker compose up -d)
Есть Task/Project в CVAT с размеченными полигонами (Shape)
Должны быть такие лейблы в CVAT:
  - Right coronary artery
  - Left coronary artery

## Этап 1: Подготовка окружения на Windows

1. Python 3.12
2. Виртуальное окружение:
```
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install ultralytics==8.3.0
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126 #Для NVIDIA
```

## Этап 2: Экспорт данных из CVAT

1. В CVAT открой Task → Actions → Export dataset. (with image)
2. Выбери формат Ultralytics YOLO Segmentation 1.0.
3. Скачай zip и распакуй в папку c твоим проектом

## Этап 3: Обучение модели

1. Скачай файл model_train.ipynb, и отредактируй его.
2. Запусти ноутбук. После обучения скопируй файл:
runs/segment/coronary_yolov8m_seg/weights/best.pt
в удобное место своего проекта

__Файлы моделей best.pt, можете скачать здесь:__ \
[YOLO_Medium_V1_NO_VALIDATION](https://drive.google.com/file/d/1NesrzecCfIKY5XpGdu8wWZWZ6A6oyv1b/view?usp=sharing) -Обучена на полной выборке 170 изображений, без валидации \
[YOLO_Large_V1.1_VALID_75/15](https://drive.google.com/file/d/18ZUi59f6Xq3d1HH0E997ToWlInn6GS4n/view?usp=sharing) -Обучена на 173 изображениях, валидация 75/15% \

## Этап 4: Подготовка serverless-функции
  ### 4.1 Запуск serverless в CVAT (один раз)
  В PowerShell (в папке CVAT):
  
    
    docker compose -f docker-compose.yml -f components/serverless/docker-compose.serverless.yml up -d
    

  ### 4.2 Установка Nuclio CLI (nuctl) в Ubuntu (WSL)
  Открой Ubuntu и выполни:
  ```
  # Добавляем права на Docker
  sudo usermod -aG docker $USER
  newgrp docker
  
  # Устанавливаем nuctl (один раз)
  curl -s https://api.github.com/repos/nuclio/nuclio/releases/latest \
    | grep "browser_download_url.*linux-amd64" \
    | cut -d : -f 2,3 | tr -d \" | wget -qi - && \
    chmod +x nuctl-* && sudo mv nuctl-* /usr/local/bin/nuctl
  
  nuctl version   # должна показать версию
  ```

  ### 4.3 Деплой
1. Ubuntu (WSL) перейди в папку:
```
cd /mnt/....../CVAT/cvat-develop/serverless
mkdir -p custom-coronary-yolov8-seg
cd custom-coronary-yolov8-seg
```
2. Скопируй или создай файл function-gpu.yaml
3. Скопируй или создай файл main.py
4. Скопируй модель в папку:
```
cp /mnt/......./best.pt ./best.pt
```
5. Создаём функцию в Nuclio
```
nuctl create project cvat
```
6. Запусти деплой:
```
nuctl deploy --project-name cvat --path . --platform local
```
7. Проверяем работу нашей функции в __Nuclio__ : http://localhost:8070/projects/cvat/functions

<img width="3822" height="683" alt="image" src="https://github.com/user-attachments/assets/b3343e62-7c42-435c-bfd0-2452d7070c4f" />


# Этап 5: Перезапуск CVAT
  Powershell:
  ```
docker compose -f docker-compose.yml -f components/serverless/docker-compose.serverless.yml restart cvat_server cvat_worker_annotation
  ```
<img width="1519" height="888" alt="image" src="https://github.com/user-attachments/assets/77176c37-a608-413f-992f-12820fae2511" />

<img width="1559" height="458" alt="image" src="https://github.com/user-attachments/assets/1b2e495c-c3da-487d-b734-2887c23bd8b5" />

И выбираем нашу модель.\
Или же другим способом:
<img width="2172" height="1344" alt="image" src="https://github.com/user-attachments/assets/c6ae4e81-1648-460f-902f-768dd3eae225" />

