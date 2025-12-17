#!/bin/bash

# 脚本用于遍历prepared_rigid目录下所有子目录中的USD文件
# 并逐一调用drawer_close_pick_place_cube_pm_debug.py进行处理

BASE_DIR="teleillusion_tests/skill_oriented_tasks/drawer_close_pick_place_cube_pm"
PREPARED_RIGID_DIR="$BASE_DIR/prepared_rigid"
PYTHON_SCRIPT="$BASE_DIR/drawer_close_pick_place_cube_pm_debug.py"

# 检查Python脚本是否存在
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "错误: Python脚本不存在: $PYTHON_SCRIPT"
    exit 1
fi

# 遍历prepared_rigid目录下的所有子目录
for model_dir in "$PREPARED_RIGID_DIR"/*/; do
    if [ -d "$model_dir" ]; then
        model_name=$(basename "$model_dir")
        echo "正在处理模型: $model_name"
        
        # 查找visual目录下的所有USD文件
        visual_dir="$model_dir/visual"
        if [ -d "$visual_dir" ]; then
            for usd_file in "$visual_dir"/base*.usd; do
                if [ -f "$usd_file" ]; then
                    echo "  处理USD文件: $usd_file"
                    
                    # 调用Python脚本处理USD文件
                    python3 "$PYTHON_SCRIPT" --usd_path "$usd_file" --headless --livestream 2
                    
                    # 检查命令执行结果
                    if [ $? -eq 0 ]; then
                        echo "  成功处理: $usd_file"
                    else
                        echo "  处理失败: $usd_file"
                    fi
                fi
                fuser -v /dev/nvidia0 | awk '{for(i=1;i<=NF;i++)print "kill -9 " $i;}' |  sh
                echo "显存清理完成"
            done
        else
            echo "  警告: 未找到visual目录: $visual_dir"
        fi
    fi
done

echo "所有模型处理完成"