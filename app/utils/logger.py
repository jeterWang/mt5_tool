"""
统一日志管理系统

这个模块提供统一的日志接口，但不影响现有的print语句
原有代码可以继续使用print，新代码逐步使用logger
"""

import logging
import os
from pathlib import Path
from typing import Optional


class AppLogger:
    """应用程序日志管理器"""
    
    _loggers = {}
    _initialized = False
    
    @classmethod
    def setup_logging(cls, log_level: str = "INFO", log_file: Optional[str] = None):
        """
        初始化日志系统
        
        Args:
            log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            log_file: 日志文件路径，None则只输出到控制台
        """
        if cls._initialized:
            return
            
        # 创建根日志配置
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        date_format = '%Y-%m-%d %H:%M:%S'
        
        # 设置基本配置
        level = getattr(logging, log_level.upper(), logging.INFO)
        
        if log_file:
            # 确保日志目录存在
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            logging.basicConfig(
                level=level,
                format=log_format,
                datefmt=date_format,
                handlers=[
                    logging.FileHandler(log_file, encoding='utf-8'),
                    logging.StreamHandler()  # 同时输出到控制台
                ]
            )
        else:
            logging.basicConfig(
                level=level,
                format=log_format,
                datefmt=date_format,
                handlers=[logging.StreamHandler()]
            )
        
        cls._initialized = True
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        获取指定名称的日志器
        
        Args:
            name: 日志器名称，通常使用模块名
            
        Returns:
            Logger实例
        """
        if not cls._initialized:
            cls.setup_logging()
            
        if name not in cls._loggers:
            cls._loggers[name] = logging.getLogger(name)
            
        return cls._loggers[name]


# 便捷函数，供其他模块使用
def get_logger(name: str) -> logging.Logger:
    """获取日志器的便捷函数"""
    return AppLogger.get_logger(name)


# 为了向后兼容，提供一个print的替代函数
# def debug_print(*args, **kwargs):
    """
    兼容性打印函数，可以逐步替换原有的print语句
    
    这个函数现在就是print，但未来可以改为使用日志系统
    """
    # print(*args, **kwargs)