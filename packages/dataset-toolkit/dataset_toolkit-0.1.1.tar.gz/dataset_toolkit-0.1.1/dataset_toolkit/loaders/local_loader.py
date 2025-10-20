# dataset_toolkit/loaders/local_loader.py
from pathlib import Path
from typing import Dict
from PIL import Image
import csv
import json

# 从我们自己的包中导入模块
from dataset_toolkit.models import Dataset, ImageAnnotation, Annotation
from dataset_toolkit.utils.coords import yolo_to_absolute_bbox

def load_yolo_from_local(dataset_path: str, categories: Dict[int, str]) -> Dataset:
    """
    从本地文件系统加载YOLO格式的数据集。
    """
    root_path = Path(dataset_path)
    image_dir = root_path / 'images'
    label_dir = root_path / 'labels'
    
    if not image_dir.is_dir():
        raise FileNotFoundError(f"图片目录不存在: {image_dir}")
    if not label_dir.is_dir():
        raise FileNotFoundError(f"标注目录不存在: {label_dir}")

    dataset = Dataset(name=root_path.name, categories=categories)
    supported_extensions = ['.jpg', '.jpeg', '.png']
    
    print(f"开始加载数据集: {root_path.name}...")
    
    for image_path in image_dir.iterdir():
        if image_path.suffix.lower() not in supported_extensions:
            continue

        try:
            with Image.open(image_path) as img:
                img_width, img_height = img.size
        except IOError:
            print(f"警告: 无法打开图片，已跳过: {image_path}")
            continue
        image_annotation = ImageAnnotation(
            image_id=image_path.name,
            path=str(image_path.resolve()),
            width=img_width,
            height=img_height
        )
        
        label_path = label_dir / (image_path.stem + '.txt')
        if label_path.exists():
            with open(label_path, 'r') as f:
                for line in f:
                    try:
                        parts = [float(p) for p in line.strip().split()]
                        if len(parts) != 5: continue
                        
                        cls_id, yolo_box = int(parts[0]), parts[1:]
                        abs_bbox = yolo_to_absolute_bbox(tuple(yolo_box), img_width, img_height)
                        
                        annotation = Annotation(category_id=cls_id, bbox=abs_bbox)
                        image_annotation.annotations.append(annotation)
                    except (ValueError, IndexError):
                        print(f"警告: 无法解析行，已跳过: {label_path} -> '{line.strip()}'")

        dataset.images.append(image_annotation)

    print(f"加载完成. 共找到 {len(dataset.images)} 张图片.")
    return dataset


def load_csv_result_from_local(dataset_path: str, categories: Dict[int, str] = None) -> Dataset:
    """
    从本地文件系统加载包含 result.csv 的数据集。
    
    数据集结构：
    - 根目录下包含 jpg 图片文件
    - result.csv 文件，格式为：file_id,result_json
    - result_json 是 JSON 数组，包含检测结果
      格式: [{"box": [x1, y1, x2, y2], "conf": 0.xx, "class_id": 0, "class_name": "parcel"}]
    
    参数:
        dataset_path: 数据集根目录路径
        categories: 类别映射字典 {class_id: class_name}，如果为 None 则从数据自动提取
    """
    root_path = Path(dataset_path)
    csv_path = root_path / 'result.csv'
    
    if not csv_path.exists():
        raise FileNotFoundError(f"result.csv 文件不存在: {csv_path}")
    
    # 如果没有提供 categories，则使用空字典，稍后从数据中提取
    if categories is None:
        categories = {}
    
    dataset = Dataset(name=root_path.name, categories=categories)
    supported_extensions = ['.jpg', '.jpeg', '.png']
    
    print(f"开始加载数据集: {root_path.name}...")
    
    # 读取 CSV 文件，建立 file_id 到 result_json 的映射
    # 手动解析以处理 JSON 中的逗号
    results_dict = {}
    with open(csv_path, 'r', encoding='utf-8') as f:
        # 跳过表头
        header = f.readline().strip()
        if header != 'file_id,result_json':
            print(f"警告: CSV 表头格式不匹配，期望 'file_id,result_json'，实际为 '{header}'")
        
        # 逐行解析
        for line_num, line in enumerate(f, start=2):
            line = line.strip()
            if not line:
                continue
            
            # 查找第一个逗号作为分隔符，之后的所有内容都是 result_json
            comma_idx = line.find(',')
            if comma_idx == -1:
                print(f"警告: 第 {line_num} 行格式错误，已跳过: {line}")
                continue
            
            file_id = line[:comma_idx].strip()
            result_json = line[comma_idx + 1:].strip()
            results_dict[file_id] = result_json
    
    print(f"从 result.csv 读取了 {len(results_dict)} 条标注记录.")
    
    # 遍历根目录下的所有图片文件
    image_count = 0
    for image_path in root_path.iterdir():
        if not image_path.is_file() or image_path.suffix.lower() not in supported_extensions:
            continue
        
        try:
            with Image.open(image_path) as img:
                img_width, img_height = img.size
        except IOError:
            print(f"警告: 无法打开图片，已跳过: {image_path}")
            continue
        
        image_annotation = ImageAnnotation(
            image_id=image_path.name,
            path=str(image_path.resolve()),
            width=img_width,
            height=img_height
        )
        
        # 查找对应的标注结果（文件名不含后缀）
        file_id = image_path.stem
        if file_id in results_dict:
            result_json = results_dict[file_id]
            
            # 解析 JSON 格式的检测结果
            try:
                detections = json.loads(result_json)
                
                # 遍历每个检测框
                for det in detections:
                    box = det.get('box', [])
                    conf = det.get('conf', 1.0)
                    class_id = det.get('class_id', 0)
                    class_name = det.get('class_name', 'unknown')
                    
                    # 如果 categories 中没有这个类别，自动添加
                    if class_id not in dataset.categories:
                        dataset.categories[class_id] = class_name
                    
                    # box 格式为 [x1, y1, x2, y2]，需要转换为 [x_min, y_min, width, height]
                    if len(box) == 4:
                        x1, y1, x2, y2 = box
                        x_min = x1
                        y_min = y1
                        width = x2 - x1
                        height = y2 - y1
                        
                        annotation = Annotation(
                            category_id=class_id,
                            bbox=[x_min, y_min, width, height]
                        )
                        image_annotation.annotations.append(annotation)
                    else:
                        print(f"警告: 无效的边界框格式，已跳过: {file_id} -> {box}")
                        
            except json.JSONDecodeError as e:
                print(f"警告: 无法解析 JSON，已跳过: {file_id} -> {e}")
        
        dataset.images.append(image_annotation)
        image_count += 1
    
    print(f"加载完成. 共找到 {image_count} 张图片, {len(dataset.categories)} 个类别.")
    print(f"类别映射: {dataset.categories}")
    return dataset