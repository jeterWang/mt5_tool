#!/usr/bin/env python3
"""
调试日志控制脚本

这个脚本可以快速开启/关闭系统中的调试日志输出
"""

import os
import re
from pathlib import Path

def toggle_debug_prints(enable_debug=False):
    """
    切换系统中的调试print语句
    
    Args:
        enable_debug: True开启调试, False关闭调试
    """
    
    # 需要处理的文件列表
    files_to_process = [
        "config/loader.py",
        "app/database.py", 
        "app/gui/account_info.py",
        "app/gui/config_manager.py",
        "app/gui/batch_order.py"
    ]
    
    print(f"{'开启' if enable_debug else '关闭'}调试日志...")
    
    for file_path in files_to_process:
        if not os.path.exists(file_path):
            print(f"警告: 文件不存在: {file_path}")
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            modified = False
            lines = content.split('\n')
            
            for i, line in enumerate(lines):
                # 检查是否包含调试print语句
                if 'print(f"' in line and any(keyword in line for keyword in [
                    'save_config:', '保存前', '数据库路径', '数据库中', '正在获取', '尝试保存', '配置中的'
                ]):
                    if enable_debug:
                        # 开启调试：移除注释
                        if line.strip().startswith('# '):
                            lines[i] = line.replace('# ', '', 1)
                            modified = True
                    else:
                        # 关闭调试：添加注释
                        if not line.strip().startswith('#'):
                            lines[i] = f"        # {line.strip()}"  # 保持缩进
                            modified = True
            
            if modified:
                new_content = '\n'.join(lines)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"已更新: {file_path}")
            else:
                print(f"无需更新: {file_path}")
                
        except Exception as e:
            print(f"错误: 处理文件失败 {file_path}: {e}")

def add_debug_config():
    """
    在配置文件中添加调试控制选项
    """
    config_file = "config/config.json"
    
    try:
        import json
        
        # 读取现有配置
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 添加调试配置（如果不存在）
        if "DEBUG" not in config:
            config["DEBUG"] = {
                "ENABLE_VERBOSE_LOGGING": False,
                "SHOW_CONFIG_SAVES": False,
                "SHOW_DATABASE_OPERATIONS": False
            }
            
            # 保存配置
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            
            print("已添加调试配置到 config.json")
        else:
            print("调试配置已存在")
            
    except Exception as e:
        print(f"错误: 添加调试配置失败: {e}")

if __name__ == "__main__":
    import sys
    
    print("MT5交易系统调试日志控制工具")
    print("=" * 40)
    
    if len(sys.argv) > 1:
        if sys.argv[1].lower() in ['on', 'enable', 'true', '1']:
            toggle_debug_prints(True)
        else:
            toggle_debug_prints(False)
    else:
        print("使用方法:")
        print("  python debug_control.py on   # 开启调试日志")
        print("  python debug_control.py off  # 关闭调试日志")
        print()
        
        choice = input("请选择操作 (on/off): ").lower()
        if choice in ['on', 'enable', 'true']:
            toggle_debug_prints(True)
        else:
            toggle_debug_prints(False)
    
    # 同时添加调试配置选项
    add_debug_config()
    
    print("\n操作完成! 重启应用生效.")