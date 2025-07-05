"""
打包调试版本的MT5交易系统
"""

import os
import subprocess
import sys
import shutil

def check_exe_running():
    """检查exe是否正在运行"""
    exe_path = "dist/MT5Trading_Debug_Console.exe"
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
    
    # 创建空的data目录和logs目录
    for dir_name in ["data", "logs"]:
        dir_path = os.path.join(dist_dir, dir_name)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(f"  ✓ 创建空目录: {dir_name}/")
    
    print("✅ 文件复制完成！")

def clean_cache():
    """清理PyInstaller缓存"""
    print("清理PyInstaller缓存...")

    # 删除缓存目录
    cache_dirs = ["build", "__pycache__", "dist"]
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            try:
                shutil.rmtree(cache_dir)
                print(f"  ✓ 删除缓存目录: {cache_dir}")
            except Exception as e:
                print(f"  ⚠ 删除 {cache_dir} 失败: {e}")

    # 删除spec文件
    spec_files = ["MT5Trading_Debug.spec", "MT5Trading.spec"]
    for spec_file in spec_files:
        if os.path.exists(spec_file):
            try:
                os.remove(spec_file)
                print(f"  ✓ 删除spec文件: {spec_file}")
            except Exception as e:
                print(f"  ⚠ 删除 {spec_file} 失败: {e}")

def build_debug():
    """打包调试版本"""
    print("开始打包调试版本...")

    if not os.path.exists("debug_main.py"):
        print("错误: 找不到 debug_main.py")
        return False

    # 检查exe是否正在运行
    if check_exe_running():
        print("⚠️ MT5Trading_Debug_Console.exe 正在运行，请先关闭程序再打包")
        return False

    # 清理缓存
    clean_cache()
    
    # PyInstaller命令 - 显示控制台窗口
    cmd = [
        "pyinstaller",
        "--onefile",
        "--console",  # 显示控制台窗口，替换 --windowed
        "--clean",  # 清理临时文件
        "--noconfirm",  # 不询问覆盖
        "--name=MT5Trading_Debug_Console",
        "--add-data=config;config",
        "--add-data=resources;resources",
        "--add-data=data;data",
        "--add-data=app;app",
        "--add-data=debug_place_batch_order.py;.",
        "--add-data=debug_batch_order.py;.",
        "--add-data=debug_trading_buttons_controller.py;.",
        "--add-data=debug_gui.py;.",
        "debug_main.py"
    ]
    
    try:
        print("执行PyInstaller命令...")
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            exe_path = "dist/MT5Trading_Debug_Console.exe"
            if os.path.exists(exe_path):
                size = os.path.getsize(exe_path) / (1024*1024)
                print(f"✅ 调试版本打包成功！文件: {exe_path} ({size:.1f} MB)")
                
                # 复制配置文件和资源文件到dist目录
                print("复制配置文件和资源文件...")
                copy_files_to_dist()
                
                print("\n🔍 调试版本特性:")
                print("- 详细的日志输出")
                print("- 日志文件保存在 dist/logs/ 目录")
                print("- 控制台实时显示日志")
                print("- 下单过程完整记录")
                
                return True
            else:
                print("❌ 打包失败")
                return False
        else:
            print(f"❌ 编译出错: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 打包异常: {str(e)}")
        return False

if __name__ == "__main__":
    if build_debug():
        print("\n🎉 控制台调试版本打包完成！")
        print("运行 dist/MT5Trading_Debug_Console.exe 来启动调试版本")
        print("🖥️ 控制台窗口会显示实时日志")
        print("📁 日志文件也会保存在 dist/logs/ 目录中")
    else:
        print("\n❌ 调试版本打包失败")
