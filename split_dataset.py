import os
import shutil
import random
from pathlib import Path

# Пути (поменяй, если нужно)
dataset_root = Path(r"C:\LABS\AutoAnnotationProj\coronary_dataset")
images_dir = dataset_root / "images"
labels_dir = dataset_root / "labels"

# Создаём папки train/val
for split in ["train", "val"]:
    (images_dir / split).mkdir(exist_ok=True)
    (labels_dir / split).mkdir(exist_ok=True)

# Получаем все изображения
image_files = list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.png"))
print(f"Всего изображений: {len(image_files)}")

# === ВАРИАНТ 1: Простой случайный сплит (если пациенты не важны) ===
random.seed(42)  # для воспроизводимости
random.shuffle(image_files)

val_size = int(len(image_files) * 0.15)   # 15% на val
val_images = image_files[:val_size]
train_images = image_files[val_size:]

print(f"Train: {len(train_images)} | Val: {len(val_images)}")

# Копируем файлы
for img_path in train_images:
    label_path = labels_dir / (img_path.stem + ".txt")
    shutil.copy(img_path, images_dir / "train" / img_path.name)
    if label_path.exists():
        shutil.copy(label_path, labels_dir / "train" / label_path.name)

for img_path in val_images:
    label_path = labels_dir / (img_path.stem + ".txt")
    shutil.copy(img_path, images_dir / "val" / img_path.name)
    if label_path.exists():
        shutil.copy(label_path, labels_dir / "val" / label_path.name)

print("Разделение завершено!")