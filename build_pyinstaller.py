#!/usr/bin/env python3
"""
PyInstaller快速打包脚本
"""

import os
import subprocess
import sys
import shutil

def install_pyinstaller():
    """安装PyInstaller"""
    try:
        import PyInstaller
        print("✓ PyInstaller已安装")
        return True
    except ImportError:
        print("安装PyInstaller...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ PyInstaller安装成功")
            return True
        else:
            print("❌ PyInstaller安装失败")
            return False

def copy_files_to_dist():
    """复制必要的文件到dist目录"""
    dist_dir = "dist"

    # 要复制的目录列表（排除data目录，避免数据库文件冲突）
    dirs_to_copy = ["config", "resources"]

    for dir_name in dirs_to_copy:
        if os.path.exists(dir_name):
            dest_path = os.path.join(dist_dir, dir_name)
            try:
                if os.path.exists(dest_path):
                    shutil.rmtree(dest_path)  # 删除已存在的目录
                shutil.copytree(dir_name, dest_path)
                print(f"  ✓ 复制 {dir_name}/ -> {dest_path}/")
            except Exception as e:
                print(f"  ❌ 复制 {dir_name} 失败: {e}")
        else:
            print(f"  ⚠ 目录不存在: {dir_name}")

    # 创建空的data目录（让程序自己创建数据库）
    data_dir = os.path.join(dist_dir, "data")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"  ✓ 创建空目录: data/")

    print("✅ 文件复制完成！")

def check_exe_running():
    """检查exe是否正在运行"""
    exe_path = "dist/MT5Trading.exe"
    if os.path.exists(exe_path):
        try:
            # 尝试重命名文件来检查是否被占用
            temp_name = exe_path + ".tmp"
            os.rename(exe_path, temp_name)
            os.rename(temp_name, exe_path)
            return False  # 没有被占用
        except OSError:
            return True  # 被占用
    return False

def build():
    """PyInstaller打包"""
    print("开始PyInstaller打包...")

    if not os.path.exists("main.py"):
        print("错误: 找不到 main.py")
        return False

    # 检查exe是否正在运行
    if check_exe_running():
        print("⚠️ MT5Trading.exe 正在运行，请先关闭程序再打包")
        return False
    
    # PyInstaller命令
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=MT5Trading",
        "--add-data=config;config",
        "--add-data=resources;resources",
        "--add-data=data;data",
        "--add-data=app;app",
        "main.py"
    ]
    
    print("命令:", " ".join(cmd))
    
    try:
        result = subprocess.run(cmd, check=False)
        
        exe_path = "dist/MT5Trading.exe"
        if os.path.exists(exe_path):
            size = os.path.getsize(exe_path) / (1024*1024)
            print(f"✅ 打包成功！文件: {exe_path} ({size:.1f} MB)")

            # 复制配置文件和资源文件到dist目录
            print("复制配置文件和资源文件...")
            copy_files_to_dist()

            return True
        else:
            print("❌ 打包失败")
            return False
            
    except Exception as e:
        print(f"❌ 编译出错: {e}")
        return False

if __name__ == "__main__":
    if install_pyinstaller():
        build()
