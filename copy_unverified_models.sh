#!/bin/bash

# 脚本用于将robotwin_suitable_grasp中不在verified目录中的模型复制到prepared_rigid目录

SOURCE_DIR="/home/hcy/work/robotwin_suitable_grasp"
TARGET_DIR="/home/hcy/work/TeleIllusion/teleillusion_tests/skill_oriented_tasks/drawer_close_pick_place_cube_pm/prepared_rigid"
VERIFIED_DIR="/home/hcy/work/TeleIllusion/teleillusion_tests/skill_oriented_tasks/drawer_close_pick_place_cube_pm/verified"

# 创建目标目录如果不存在
mkdir -p "$TARGET_DIR"

# 遍历source目录中的所有子目录
for model_dir in "$SOURCE_DIR"/*/; do
    if [ -d "$model_dir" ]; then
        model_name=$(basename "$model_dir")
        
        # 检查该模型是否在verified目录中
        if [ ! -d "$VERIFIED_DIR/$model_name" ]; then
            echo "复制模型: $model_name (未在verified中)"
            
            # 复制整个目录到目标位置
            cp -r "$model_dir" "$TARGET_DIR/"
            
            if [ $? -eq 0 ]; then
                echo "  成功复制: $model_name"
            else
                echo "  复制失败: $model_name"
            fi
        else
            echo "跳过模型: $model_name (已在verified中)"
        fi
    fi
done

echo "完成复制操作"