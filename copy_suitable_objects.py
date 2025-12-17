import os
import json
import shutil

def copy_suitable_objects():
    # 定义路径
    source_dir = "/home/hcy/work/robotwin_converted"
    dest_dir = "/home/hcy/work/robotwin_suitable_grasp"
    labels_file = "/home/hcy/work/grasp_labels.json"
    
    # 检查源目录和标签文件是否存在
    if not os.path.exists(source_dir):
        print(f"源目录 {source_dir} 不存在")
        return
        
    if not os.path.exists(labels_file):
        print(f"标签文件 {labels_file} 不存在")
        return
    
    # 创建目标目录（如果不存在）
    os.makedirs(dest_dir, exist_ok=True)
    
    # 读取grasp_labels.json文件
    with open(labels_file, 'r', encoding='utf-8') as f:
        grasp_labels = json.load(f)
    
    # 统计信息
    total_suitable = 0
    copied_count = 0
    failed_count = 0
    
    # 遍历所有标记为适合抓握的对象
    for folder_name, is_suitable in grasp_labels.items():
        if is_suitable:
            total_suitable += 1
            source_folder = os.path.join(source_dir, folder_name)
            dest_folder = os.path.join(dest_dir, folder_name)
            
            # 检查源文件夹是否存在
            if os.path.exists(source_folder):
                try:
                    # 复制整个文件夹
                    shutil.copytree(source_folder, dest_folder)
                    print(f"已复制: {folder_name}")
                    copied_count += 1
                except Exception as e:
                    print(f"复制 {folder_name} 失败: {str(e)}")
                    failed_count += 1
            else:
                print(f"源文件夹不存在: {source_folder}")
                failed_count += 1
    
    # 输出统计信息
    print(f"\n处理完成!")
    print(f"总共适合抓握的对象数量: {total_suitable}")
    print(f"成功复制: {copied_count}")
    print(f"复制失败: {failed_count}")

if __name__ == "__main__":
    copy_suitable_objects()