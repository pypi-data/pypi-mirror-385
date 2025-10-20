# dataset_toolkit/exporters/yolo_exporter.py
"""
导出为 YOLO 格式（完整的 images/ + labels/ 目录结构）
"""
import os
from pathlib import Path
from typing import Optional


def export_to_yolo_format(
    dataset,
    output_dir: str,
    use_symlinks: bool = True,
    overwrite: bool = False
):
    """
    导出数据集为完整的 YOLO 格式目录结构
    
    参数:
        dataset: Dataset 对象
        output_dir: 输出目录路径
        use_symlinks: 是否使用软链接（True）或复制文件（False）
        overwrite: 是否覆盖已存在的文件
    
    输出结构:
        output_dir/
        ├── images/
        │   ├── img1.jpg
        │   └── img2.jpg
        └── labels/
            ├── img1.txt
            └── img2.txt
    """
    output_path = Path(output_dir)
    images_dir = output_path / 'images'
    labels_dir = output_path / 'labels'
    
    # 创建目录
    images_dir.mkdir(parents=True, exist_ok=True)
    labels_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"导出 YOLO 格式到: {output_path}")
    print(f"  使用软链接: {use_symlinks}")
    
    success_count = 0
    error_count = 0
    
    for img in dataset.images:
        try:
            # 获取图片文件名（不含扩展名）
            img_path = Path(img.path)
            img_name = img_path.name
            stem = img_path.stem
            
            # 1. 处理图片（软链接或复制）
            target_img_path = images_dir / img_name
            
            if target_img_path.exists() and not overwrite:
                # 文件已存在，跳过
                pass
            else:
                if use_symlinks:
                    # 使用软链接
                    if target_img_path.exists():
                        target_img_path.unlink()
                    target_img_path.symlink_to(img_path.resolve())
                else:
                    # 复制文件
                    import shutil
                    shutil.copy2(img_path, target_img_path)
            
            # 2. 生成标注文件
            label_path = labels_dir / f"{stem}.txt"
            
            with open(label_path, 'w') as f:
                for ann in img.annotations:
                    # 内部格式: [x_min, y_min, width, height] (绝对像素值)
                    # YOLO 格式: class_id x_center y_center width height (归一化)
                    
                    x_min, y_min, width, height = ann.bbox
                    
                    # 转换为 YOLO 归一化格式
                    x_center = (x_min + width / 2) / img.width
                    y_center = (y_min + height / 2) / img.height
                    norm_width = width / img.width
                    norm_height = height / img.height
                    
                    # 写入：class_id x_center y_center width height
                    f.write(f"{ann.category_id} {x_center:.6f} {y_center:.6f} {norm_width:.6f} {norm_height:.6f}\n")
            
            success_count += 1
            
        except Exception as e:
            print(f"警告: 处理图片失败 {img.path}: {e}")
            error_count += 1
            continue
    
    print(f"✓ 导出完成:")
    print(f"  成功: {success_count} 张图片")
    if error_count > 0:
        print(f"  失败: {error_count} 张图片")
    print(f"  图片目录: {images_dir}")
    print(f"  标注目录: {labels_dir}")
    
    return output_path


def export_to_yolo_and_txt(
    dataset,
    yolo_dir: str,
    txt_file: str,
    use_symlinks: bool = True,
    use_relative_paths: bool = False
):
    """
    导出为 YOLO 格式并生成对应的 txt 列表文件
    
    参数:
        dataset: Dataset 对象
        yolo_dir: YOLO 格式输出目录
        txt_file: txt 列表文件路径
        use_symlinks: 是否使用软链接
        use_relative_paths: txt 中是否使用相对路径
    
    返回:
        yolo_dir_path: YOLO 目录路径
    """
    # 1. 导出为 YOLO 格式
    yolo_path = export_to_yolo_format(dataset, yolo_dir, use_symlinks=use_symlinks)
    
    # 2. 生成 txt 列表文件（指向 YOLO 目录中的 images/）
    images_dir = yolo_path / 'images'
    txt_path = Path(txt_file)
    txt_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"\n生成 txt 列表: {txt_file}")
    
    with open(txt_file, 'w') as f:
        for img in dataset.images:
            img_name = Path(img.path).name
            # 指向 YOLO 目录中的图片（可能是软链接）
            img_in_yolo = images_dir / img_name
            
            if use_relative_paths:
                # 相对于 txt 文件的路径
                rel_path = os.path.relpath(img_in_yolo, txt_path.parent)
                f.write(f"{rel_path}\n")
            else:
                # 绝对路径（指向 YOLO images 目录，不要 resolve，保持 YOLO 结构）
                f.write(f"{str(img_in_yolo.absolute())}\n")
    
    print(f"✓ txt 列表已生成: {len(dataset.images)} 行")
    
    return yolo_path

