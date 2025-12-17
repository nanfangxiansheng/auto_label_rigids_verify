#!/bin/bash

# 批量处理robotwin_test目录下所有USD文件的脚本

BASE_DIR="/home/hcy/work/robotwin_suitable_grasp_spe"
PYTHON_SCRIPT="/home/hcy/work/auto_label_rigid_spe.py"

# 检查基础目录是否存在
if [ ! -d "$BASE_DIR" ]; then
    echo "错误: 基础目录 $BASE_DIR 不存在"
    exit 1
fi

# 检查Python脚本是否存在
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "错误: Python脚本 $PYTHON_SCRIPT 不存在"
    exit 1
fi

# 初始化计数器
total_processed=0
total_success=0
total_failed=0

echo "开始批量处理USD文件..."
echo "基础目录: $BASE_DIR"
echo "----------------------------------------"

# 遍历所有子目录
for subdir in "$BASE_DIR"/*/; do
    if [ -d "$subdir" ]; then
        folder_name=$(basename "$subdir")
        visual_dir="$subdir/visual"
        
        echo "处理目录: $folder_name"
        
        # 检查visual目录是否存在
        if [ ! -d "$visual_dir" ]; then
            echo "  跳过: visual目录不存在"
            continue
        fi
        
        # 查找所有USD文件
        usd_files=$(find "$visual_dir" -name "*.usd" -type f)
        
        if [ -z "$usd_files" ]; then
            echo "  跳过: 未找到USD文件"
            continue
        fi
        
        # 计算USD文件数量
        file_count=$(echo "$usd_files" | wc -l)
        echo "  找到 $file_count 个USD文件"
        
        # 处理每个USD文件
        while IFS= read -r usd_file; do
            if [ -n "$usd_file" ]; then
                ((total_processed++))
                echo "  处理: $(basename "$usd_file")"
                
                # 调用Python脚本处理USD文件
                python3 "$PYTHON_SCRIPT" --usd_path "$usd_file"  
                
                if [ $? -eq 0 ]; then
                    ((total_success++))
                    echo "    成功"
                else
                    ((total_failed++))
                    echo "    失败"
                fi
            fi
        done <<< "$usd_files"
        
        echo ""
    fi
done

echo "========================================"
echo "批量处理完成!"
echo "总计处理文件数: $total_processed"
echo "成功处理数: $total_success"
echo "失败处理数: $total_failed"
echo "========================================"