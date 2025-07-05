"""
MT5交易系统启动入口 - 调试版本
添加详细日志来调试下单问题
"""

import sys
import os
import logging
from datetime import datetime

# 设置详细的日志配置
log_filename = f"mt5_debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

# 创建日志目录
if not os.path.exists("logs"):
    os.makedirs("logs")

log_filepath = os.path.join("logs", log_filename)

# 配置日志 - 同时输出到文件和控制台
logging.basicConfig(
    level=logging.DEBUG,  # 最详细的日志级别
    format='[%(asctime)s] [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler(log_filepath, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# 确保控制台立即显示输出
sys.stdout.flush()

print("=" * 80)
print("🔍 MT5交易系统 - 控制台调试版本")
print("=" * 80)
print(f"📁 日志文件: {log_filepath}")
print(f"🖥️ 控制台实时显示所有日志")
print("=" * 80)

logger = logging.getLogger(__name__)

def log_system_info():
    """记录系统信息"""
    logger.info("=" * 60)
    logger.info("MT5交易系统启动 - 调试模式")
    logger.info("=" * 60)
    
    # Python环境信息
    logger.info(f"Python版本: {sys.version}")
    logger.info(f"Python路径: {sys.executable}")
    logger.info(f"工作目录: {os.getcwd()}")
    
    # 检查关键文件
    critical_files = [
        "config/config.json",
        "app/gui/__init__.py",
        "app/config/config_manager.py"
    ]
    
    for file_path in critical_files:
        if os.path.exists(file_path):
            logger.info(f"✓ 文件存在: {file_path}")
        else:
            logger.error(f"✗ 文件缺失: {file_path}")
    
    # 检查MT5模块
    try:
        import MetaTrader5 as mt5
        logger.info(f"✓ MetaTrader5模块导入成功")
        
        # 尝试初始化MT5
        if mt5.initialize():
            logger.info("✓ MT5初始化成功")
            account_info = mt5.account_info()
            if account_info:
                logger.info(f"MT5账户: {account_info.login}")
                logger.info(f"账户余额: {account_info.balance}")
                logger.info(f"账户权益: {account_info.equity}")
            else:
                logger.warning("无法获取MT5账户信息")
            mt5.shutdown()
        else:
            logger.error("MT5初始化失败")
            
    except ImportError as e:
        logger.error(f"✗ MetaTrader5模块导入失败: {e}")
    except Exception as e:
        logger.error(f"✗ MT5检查出错: {e}")
    
    # 检查PyQt6
    try:
        from PyQt6.QtWidgets import QApplication
        logger.info("✓ PyQt6模块导入成功")
    except ImportError as e:
        logger.error(f"✗ PyQt6模块导入失败: {e}")

def log_config_info():
    """记录配置信息"""
    logger.info("检查配置文件...")
    
    try:
        from app.config.config_manager import config_manager
        
        # 检查配置文件路径
        config_path = config_manager._config_path if hasattr(config_manager, '_config_path') else "未知"
        logger.info(f"配置文件路径: {config_path}")
        
        # 检查关键配置
        symbols = config_manager.get("SYMBOLS", [])
        logger.info(f"交易品种: {symbols}")
        
        breakout_settings = config_manager.get("BREAKOUT_SETTINGS", {})
        logger.info(f"突破设置: {breakout_settings}")
        
        gui_settings = config_manager.get("GUI_SETTINGS", {})
        logger.info(f"GUI设置: {gui_settings}")
        
    except Exception as e:
        logger.error(f"配置检查失败: {e}")
        import traceback
        logger.error(traceback.format_exc())

def main():
    """主函数 - 调试版本"""
    try:
        # 记录系统信息
        log_system_info()
        
        # 记录配置信息
        log_config_info()
        
        # 启动GUI
        logger.info("启动GUI应用...")
        from PyQt6.QtWidgets import QApplication
        from app.gui import MT5GUI
        
        app = QApplication(sys.argv)
        
        # 创建主窗口
        logger.info("创建主窗口...")
        from debug_gui import DebugMT5GUI
        window = DebugMT5GUI()
        
        # 显示窗口
        logger.info("显示主窗口...")
        window.show()
        
        logger.info("进入事件循环...")
        logger.info(f"日志文件: {log_filepath}")
        
        # 运行应用
        sys.exit(app.exec())
        
    except Exception as e:
        logger.error(f"应用启动失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        # 显示错误对话框
        try:
            from PyQt6.QtWidgets import QApplication, QMessageBox
            if not QApplication.instance():
                app = QApplication(sys.argv)
            
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("启动错误")
            msg.setText(f"应用启动失败:\n{str(e)}\n\n详细日志请查看: {log_filepath}")
            msg.exec()
            
        except:
            print(f"严重错误: {e}")
            print(f"详细日志: {log_filepath}")

if __name__ == "__main__":
    main()
