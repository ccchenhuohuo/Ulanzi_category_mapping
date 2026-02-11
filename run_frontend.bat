@echo off
REM 快速启动 Ulanzi 分类可视化前端
REM 用法: run_frontend.bat

echo ============================================
echo   Ulanzi 灯光类目分类可视化前端
echo ============================================
echo.

REM 检查是否安装了依赖
pip show streamlit >nul 2>&1
if %errorlevel% neq 0 (
    echo 正在安装依赖...
    pip install streamlit pandas plotly
    echo.
)

REM 设置工作目录
cd /d "%~dp0"

echo 正在启动 Streamlit 前端...
echo 访问地址: http://localhost:8501
echo.
echo 按 Ctrl+C 停止服务器
echo.

REM 启动 Streamlit
streamlit run frontend/app.py

pause
