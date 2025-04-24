@echo off
chcp 65001
setlocal enabledelayedexpansion

:: 设置程序根目录
set "PROGRAM_ROOT=%~dp0"
echo 程序目录: %PROGRAM_ROOT%

:: 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到Python环境，请先安装Python 3.11
    pause
    exit /b 1
)

:: 检查虚拟环境
if not exist "%PROGRAM_ROOT%venv" (
    echo 正在创建虚拟环境...
    python -m venv "%PROGRAM_ROOT%venv"
    if errorlevel 1 (
        echo 错误：创建虚拟环境失败
        pause
        exit /b 1
    )
)

:: 激活虚拟环境
call "%PROGRAM_ROOT%venv\Scripts\activate.bat"

:: 安装依赖
echo 正在检查依赖...
uv pip install -r "%PROGRAM_ROOT%requirements.txt"

:: 启动程序
echo 正在启动程序...
python "%PROGRAM_ROOT%mt5_gui.py"

:: 如果程序异常退出，暂停显示错误信息
if errorlevel 1 (
    echo 程序异常退出，请检查错误信息
    pause
)

:: 退出虚拟环境
deactivate 