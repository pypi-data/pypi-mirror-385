from dataset_toolkit import load_yolo_from_local, merge_datasets, export_to_coco, export_to_txt

# 1. 加载 YOLO 格式数据集
dataset1 = load_yolo_from_local(
    "/opt/dlami/nvme/workspace_wenxiang/parcel/test_FPPI",
    categories={0: 'parcel', 1: 'person'}
)

dataset2 = load_yolo_from_local(
    "/opt/dlami/nvme/workspace_wenxiang/parcel/test_val",
    categories={0: 'parcel', 1: 'person'}
)

# 2. 合并数据集（带类别重映射）
final_categories = {0: 'parcel', 1: 'person'}
category_mapping = {
    'parcel': 'parcel',
    'person': 'person'
}

merged = merge_datasets(
    datasets=[dataset1, dataset2],
    category_mapping=category_mapping,
    final_categories=final_categories,
    new_dataset_name="merged_dataset"
)

# 3. 导出为 COCO 格式
export_to_txt(merged, "output/merged.txt")
