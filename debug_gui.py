"""
调试版本的MT5GUI
使用调试版本的控制器
"""

import logging
from app.gui import MT5GUI
from debug_trading_buttons_controller import DebugTradingButtonsController

logger = logging.getLogger(__name__)

class DebugMT5GUI(MT5GUI):
    def __init__(self):
        logger.info("初始化调试版MT5GUI")
        super().__init__()

    def enable_trading_buttons(self):
        """启用交易按钮并设置调试控制器"""
        logger.info("启用交易按钮并设置调试控制器")

        # 先调用父类方法启用按钮
        super().enable_trading_buttons()

        # 然后设置调试版控制器
        self.setup_debug_controller()

    def setup_debug_controller(self):
        """设置调试版交易按钮控制器"""
        logger.info("设置调试版交易按钮控制器")

        if self.trader is None:
            logger.warning("trader为None，无法设置调试控制器")
            return

        # 使用调试版控制器替换原控制器
        debug_controller = DebugTradingButtonsController(self.trader, self)

        # 设置到交易按钮组件
        self.components["trading_buttons"].controller = debug_controller

        logger.info("调试版交易按钮控制器设置完成")
