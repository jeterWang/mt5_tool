@echo off
chcp 65001
setlocal enabledelayedexpansion

:: 设置程序根目录（使用脚本所在目录的绝对路径）
set "PROGRAM_ROOT=%~dp0"
cd /d "%PROGRAM_ROOT%"

echo ======================================
echo MT5一键交易系统启动器
echo 程序目录: %PROGRAM_ROOT%
echo ======================================

:: 设置Python解释器路径
set "PYTHON_PATH=%PROGRAM_ROOT%.venv\Scripts\python.exe"

:: 检查程序文件是否存在
if not exist "%PROGRAM_ROOT%mt5_gui.py" (
    echo 错误：找不到主程序文件！
    echo 请确保以下文件在同一目录：
    echo - mt5_gui.py
    echo - config.py
    echo - mt5_trader.py
    echo - database.py
    echo - requirements.txt
    pause
    exit /b 1
)

:: 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到Python环境！
    echo 请按照以下步骤操作：
    echo 1. 访问 https://www.python.org/downloads/
    echo 2. 下载并安装 Python 3.11
    echo 3. 安装时勾选"Add Python to PATH"
    echo 4. 安装完成后重启电脑
    echo 5. 再次运行此程序
    pause
    exit /b 1
)

:: 检查虚拟环境
if not exist "%PROGRAM_ROOT%.venv" (
    echo 正在创建虚拟环境...
    python -m venv "%PROGRAM_ROOT%.venv"
    if errorlevel 1 (
        echo 错误：创建虚拟环境失败！
        echo 请检查Python安装是否完整
        pause
        exit /b 1
    )
    echo 虚拟环境创建成功！
)

:: 检查虚拟环境Python
if not exist "%PYTHON_PATH%" (
    echo 正在创建虚拟环境...
    python -m venv "%PROGRAM_ROOT%.venv"
    if errorlevel 1 (
        echo 错误：创建虚拟环境失败！
        echo 请检查Python安装是否完整
        pause
        exit /b 1
    )
    echo 虚拟环境创建成功！
)

:: 激活虚拟环境
call "%PROGRAM_ROOT%.venv\Scripts\activate.bat"
if errorlevel 1 (
    echo 错误：激活虚拟环境失败！
    pause
    exit /b 1
)

:: 安装/更新依赖
echo 正在检查依赖...
uv pip install -r "%PROGRAM_ROOT%requirements.txt"
if errorlevel 1 (
    echo 错误：安装依赖失败！
    echo 请检查网络连接或手动安装依赖
    pause
    exit /b 1
)

:: 启动程序
echo ======================================
echo 正在启动MT5一键交易系统...
echo ======================================
uv run mt5_gui.py

:: 如果程序异常退出，显示错误信息
if errorlevel 1 (
    echo ======================================
    echo 程序异常退出！
    echo 请检查以下可能的原因：
    echo 1. MT5客户端是否已启动
    echo 2. MT5客户端是否已登录
    echo 3. 是否已启用自动交易
    echo ======================================
    pause
)

:: 退出虚拟环境
call "%PROGRAM_ROOT%.venv\Scripts\deactivate.bat"

:: 如果是从桌面运行，等待用户按键后退出
if not "%~dp0" == "%cd%\" (
    echo 按任意键退出...
    pause >nul
) 