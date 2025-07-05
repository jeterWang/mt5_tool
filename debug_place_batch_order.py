"""
调试版本的批量下单命令
添加详细日志来找出下单失败的原因
"""

import logging
import MetaTrader5 as mt5
from app.commands.base_command import BaseCommand
from app.utils.trade_helpers import (
    check_daily_loss_limit_and_notify,
    check_trade_limit_and_notify,
    check_mt5_connection_and_notify,
    get_valid_rates,
    play_trade_beep,
    show_status_message,
    get_timeframe,
    calculate_breakeven_position_size,
)
from app.config.config_manager import config_manager

logger = logging.getLogger(__name__)

class DebugPlaceBatchOrderCommand(BaseCommand):
    def __init__(self, trader, gui_window, order_type):
        self.trader = trader
        self.gui_window = gui_window
        self.order_type = order_type
        logger.info(f"创建批量{order_type}订单命令")

    def execute(self):
        logger.info("=" * 60)
        logger.info(f"开始执行批量{self.order_type}订单")
        logger.info("=" * 60)
        
        try:
            # 1. 检查日损失限制
            logger.info("1. 检查日损失限制...")
            if not check_daily_loss_limit_and_notify(self.gui_window):
                logger.warning("日损失限制检查失败")
                return
            logger.info("✓ 日损失限制检查通过")
            
            # 2. 检查交易限制
            logger.info("2. 检查交易限制...")
            if not check_trade_limit_and_notify(self.gui_window.db, self.gui_window):
                logger.warning("交易限制检查失败")
                return
            logger.info("✓ 交易限制检查通过")
            
            # 3. 检查MT5连接
            logger.info("3. 检查MT5连接...")
            if not check_mt5_connection_and_notify(self.trader, self.gui_window):
                logger.error("MT5连接检查失败")
                return
            logger.info("✓ MT5连接检查通过")
            
            # 4. 获取交易设置
            logger.info("4. 获取交易设置...")
            trading_settings = self.gui_window.components["trading_settings"]
            symbol = trading_settings.symbol_input.currentText()
            logger.info(f"交易品种: {symbol}")
            
            # 5. 获取批量订单设置
            logger.info("5. 获取批量订单设置...")
            batch_order = self.gui_window.components["batch_order"]
            batch_order.sync_checked_from_ui()
            checked_orders = [order for order in batch_order.orders if order["checked"]]
            batch_count = len(checked_orders)
            logger.info(f"勾选的订单数量: {batch_count}")
            
            if batch_count == 0:
                logger.warning("未勾选任何批量下单订单")
                show_status_message(self.gui_window, "未勾选任何批量下单订单！")
                return
            
            # 6. 获取止损模式
            logger.info("6. 获取止损模式...")
            sl_mode = (
                "FIXED_POINTS"
                if trading_settings.sl_mode_combo.currentIndex() == 0
                else "CANDLE_KEY_LEVEL"
            )
            logger.info(f"止损模式: {sl_mode}")
            
            # 7. 检查现有持仓
            logger.info("7. 检查现有持仓...")
            positions = self.trader.get_positions_by_symbol_and_type(symbol, self.order_type)
            has_positions = bool(positions)
            logger.info(f"现有{self.order_type}持仓数量: {len(positions) if positions else 0}")
            
            # 8. 获取市场信息
            logger.info("8. 获取市场信息...")
            tick = mt5.symbol_info_tick(symbol)
            if not tick:
                logger.error(f"无法获取{symbol}当前价格")
                show_status_message(self.gui_window, f"无法获取{symbol}当前价格！")
                return
            
            symbol_info = mt5.symbol_info(symbol)
            if not symbol_info:
                logger.error(f"无法获取{symbol}品种信息")
                show_status_message(self.gui_window, f"无法获取{symbol}品种信息！")
                return
                
            point = symbol_info.point
            spread = tick.ask - tick.bid
            batch_entry_price = tick.ask if self.order_type == "buy" else tick.bid
            
            logger.info(f"当前价格 - Ask: {tick.ask}, Bid: {tick.bid}")
            logger.info(f"点值: {point}")
            logger.info(f"点差: {spread}")
            logger.info(f"入场价格: {batch_entry_price}")
            
            # 9. 计算止损价格
            logger.info("9. 计算止损价格...")
            if sl_mode == "FIXED_POINTS":
                sl_points = checked_orders[0]["sl_points"]
                logger.info(f"固定点数止损: {sl_points}点")
                
                if self.order_type == "buy":
                    sl_price = batch_entry_price - sl_points * point
                else:
                    sl_price = batch_entry_price + sl_points * point + spread
                    
                logger.info(f"计算的止损价格: {sl_price}")
            else:
                # K线关键位止损
                logger.info("使用K线关键位止损")
                countdown = self.gui_window.components["countdown"]
                timeframe = countdown.timeframe_combo.currentText()
                lookback = checked_orders[0]["sl_candle"]
                
                logger.info(f"时间框架: {timeframe}")
                logger.info(f"回看K线数: {lookback}")
                
                rates = get_valid_rates(symbol, get_timeframe(timeframe), lookback + 2, self.gui_window)
                if rates is None:
                    logger.error("无法获取K线数据")
                    return
                    
                lowest_point = min([rate["low"] for rate in rates[2:]])
                highest_point = max([rate["high"] for rate in rates[2:]])
                
                logger.info(f"关键位 - 最低点: {lowest_point}, 最高点: {highest_point}")
                
                # 获取止损偏移
                sl_offset_points = config_manager.get("BREAKOUT_SETTINGS", {}).get("SL_OFFSET_POINTS", 0)
                sl_offset = sl_offset_points * point
                logger.info(f"止损偏移: {sl_offset_points}点 = {sl_offset}")
                
                if self.order_type == "buy":
                    sl_price = lowest_point - sl_offset
                else:
                    sl_price = highest_point + sl_offset + spread
                    
                logger.info(f"计算的止损价格: {sl_price}")
            
            # 10. 开始下单
            logger.info("10. 开始批量下单...")
            orders = []
            
            for i, order in enumerate(checked_orders):
                logger.info(f"处理第{i+1}个订单...")
                logger.info(f"订单参数: {order}")
                
                # 计算交易量
                volume = order["volume"]
                logger.info(f"原始交易量: {volume}")
                
                # 检查仓位计算模式
                position_sizing_mode = config_manager.get("POSITION_SIZING", {}).get("DEFAULT_MODE", "FIXED_LOSS")
                logger.info(f"仓位计算模式: {position_sizing_mode}")

                # 检查仓位计算模式
                position_sizing_mode = config_manager.get("POSITION_SIZING", {}).get("DEFAULT_MODE", "FIXED_LOSS")
                logger.info(f"仓位计算模式: {position_sizing_mode}")

                # 如果是保本模式，重新计算交易量
                if has_positions and order.get("fixed_loss", 0) > 0:
                    logger.info("使用保本模式计算交易量...")
                    calculated_volume = calculate_breakeven_position_size(
                        self.trader, symbol, self.order_type, order["fixed_loss"]
                    )
                    if calculated_volume <= 0:
                        logger.error(f"订单{i+1}：保本仓位计算失败，跳过")
                        continue
                    volume = calculated_volume
                    logger.info(f"保本模式计算的交易量: {volume}")

                # 如果没有持仓且使用固定损失模式
                elif not has_positions and position_sizing_mode == "FIXED_LOSS":
                    fixed_loss = order.get("fixed_loss", 0)
                    logger.info(f"使用固定损失模式，固定损失金额: {fixed_loss}")

                    if fixed_loss <= 0:
                        logger.warning(f"订单{i+1}：固定损失金额为0或负数，跳过")
                        continue

                    # 获取当前价格
                    tick = mt5.symbol_info_tick(symbol)
                    if not tick:
                        logger.error(f"订单{i+1}：无法获取{symbol}当前价格，跳过")
                        continue

                    entry_price = tick.ask if self.order_type == "buy" else tick.bid
                    logger.info(f"入场价格: {entry_price}")

                    # 调用调试版本的仓位计算函数
                    logger.info("调用调试版本的仓位计算函数...")
                    batch_order = self.gui_window.components["batch_order"]

                    # 使用调试版本的计算函数
                    from debug_batch_order import debug_calculate_position_size_for_order
                    calculated_volume = debug_calculate_position_size_for_order(
                        i, self.order_type, entry_price, symbol, batch_order.orders
                    )
                    logger.info(f"调试计算结果: {calculated_volume}")

                    if calculated_volume <= 0:
                        logger.error(f"订单{i+1}：固定损失仓位计算失败，跳过")
                        continue

                    volume = calculated_volume
                    logger.info(f"固定损失模式计算的交易量: {volume}")

                # 如果没有持仓且使用固定损失模式
                elif not has_positions and position_sizing_mode == "FIXED_LOSS":
                    fixed_loss = order.get("fixed_loss", 0)
                    logger.info(f"使用固定损失模式，固定损失金额: {fixed_loss}")

                    if fixed_loss <= 0:
                        logger.warning(f"订单{i+1}：固定损失金额为0或负数，跳过")
                        continue

                    # 获取当前价格
                    tick = mt5.symbol_info_tick(symbol)
                    if not tick:
                        logger.error(f"订单{i+1}：无法获取{symbol}当前价格，跳过")
                        continue

                    entry_price = tick.ask if self.order_type == "buy" else tick.bid
                    logger.info(f"入场价格: {entry_price}")

                    # 调用仓位计算函数
                    logger.info("调用 calculate_position_size_for_order...")
                    batch_order = self.gui_window.components["batch_order"]
                    calculated_volume = batch_order.calculate_position_size_for_order(
                        i, self.order_type, entry_price, symbol
                    )
                    logger.info(f"计算结果: {calculated_volume}")

                    if calculated_volume <= 0:
                        logger.error(f"订单{i+1}：固定损失仓位计算失败，跳过")
                        continue

                    volume = calculated_volume
                    logger.info(f"固定损失模式计算的交易量: {volume}")
                
                if volume <= 0:
                    logger.warning(f"订单{i+1}：交易量为0，跳过")
                    continue
                
                # 执行下单
                logger.info(f"执行下单 - 品种:{symbol}, 类型:{self.order_type}, 量:{volume}")
                
                try:
                    if sl_mode == "FIXED_POINTS":
                        logger.info("使用固定点数止损下单...")
                        mt5_order = self.trader.place_order_with_tp_sl(
                            symbol=symbol,
                            order_type=self.order_type,
                            volume=volume,
                            sl_points=order["sl_points"],
                            tp_points=order["tp_points"],
                            comment=f"批量下单{i+1}",
                        )
                    else:
                        logger.info("使用关键位止损下单...")
                        mt5_order = self.trader.place_order_with_key_level_sl(
                            symbol=symbol,
                            order_type=self.order_type,
                            volume=volume,
                            sl_price=sl_price,
                            tp_points=order["tp_points"],
                            comment=f"批量下单{i+1}",
                        )
                    
                    if mt5_order:
                        logger.info(f"✓ 订单{i+1}下单成功，订单号: {mt5_order}")
                        orders.append(mt5_order)
                    else:
                        logger.error(f"✗ 订单{i+1}下单失败")
                        
                        # 获取MT5错误信息
                        last_error = mt5.last_error()
                        logger.error(f"MT5错误信息: {last_error}")
                        
                except Exception as e:
                    logger.error(f"订单{i+1}下单异常: {str(e)}")
                    import traceback
                    logger.error(traceback.format_exc())
            
            # 11. 处理结果
            logger.info("11. 处理下单结果...")
            if orders:
                logger.info(f"✅ 成功下单数量: {len(orders)}")
                
                # 更新界面
                self.gui_window.components["pnl_info"].update_daily_pnl_info(self.trader)
                self.gui_window.components["account_info"].update_account_info(self.trader)
                
                show_status_message(self.gui_window, f"批量{self.order_type}订单已成功下单")
                play_trade_beep(config_manager)
            else:
                logger.error("❌ 所有订单下单失败")
                show_status_message(self.gui_window, f"批量{self.order_type}单失败！")
                
        except Exception as e:
            logger.error(f"批量下单执行异常: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            show_status_message(self.gui_window, f"批量下单出错：{str(e)}")
        
        logger.info("=" * 60)
        logger.info(f"批量{self.order_type}订单执行完成")
        logger.info("=" * 60)
