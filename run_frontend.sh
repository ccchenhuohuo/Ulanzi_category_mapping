#!/bin/bash
# 快速启动 Ulanzi 分类可视化前端 (Linux/Mac)
# 用法: bash run_frontend.sh

echo "============================================"
echo "  Ulanzi 灯光类目分类可视化前端"
echo "============================================"

# 检查是否安装了依赖
pip show streamlit >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "正在安装依赖..."
    pip install streamlit pandas plotly
    echo
fi

# 设置工作目录
cd "$(dirname "$0")"

echo "正在启动 Streamlit 前端..."
echo "访问地址: http://localhost:8501"
echo
echo "按 Ctrl+C 停止服务器"
echo

# 启动 Streamlit
streamlit run frontend/app.py
