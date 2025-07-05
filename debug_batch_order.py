"""
调试版本的批量订单组件
添加详细的仓位计算日志
"""

import logging
import MetaTrader5 as mt5
from app.config.config_manager import config_manager

logger = logging.getLogger(__name__)

def debug_calculate_position_size_for_order(order_idx, order_type, entry_price, symbol, orders):
    """
    调试版本的仓位计算函数
    添加详细日志来找出计算失败的原因
    """
    logger.info("=" * 40)
    logger.info(f"开始计算订单{order_idx+1}的仓位大小")
    logger.info("=" * 40)
    
    try:
        order = orders[order_idx]
        fixed_loss = order["fixed_loss"]
        
        logger.info(f"订单参数:")
        logger.info(f"  - 订单索引: {order_idx}")
        logger.info(f"  - 交易类型: {order_type}")
        logger.info(f"  - 入场价格: {entry_price}")
        logger.info(f"  - 交易品种: {symbol}")
        logger.info(f"  - 固定损失: {fixed_loss}")
        logger.info(f"  - 完整订单: {order}")
        
        # 1. 检查品种信息
        logger.info("1. 获取品种信息...")
        symbol_info = mt5.symbol_info(symbol)
        if not symbol_info:
            logger.error(f"无法获取{symbol}品种信息")
            return 0
        
        point = symbol_info.point
        contract_size = symbol_info.trade_contract_size
        min_volume = symbol_info.volume_min
        max_volume = symbol_info.volume_max
        volume_step = symbol_info.volume_step
        
        logger.info(f"品种信息:")
        logger.info(f"  - 点值: {point}")
        logger.info(f"  - 合约大小: {contract_size}")
        logger.info(f"  - 最小手数: {min_volume}")
        logger.info(f"  - 最大手数: {max_volume}")
        logger.info(f"  - 手数步长: {volume_step}")
        
        # 2. 获取市场价格
        logger.info("2. 获取市场价格...")
        tick = mt5.symbol_info_tick(symbol)
        if not tick:
            logger.error(f"无法获取{symbol}当前价格")
            return 0
        
        spread = tick.ask - tick.bid if tick and tick.ask and tick.bid else 0
        logger.info(f"市场价格:")
        logger.info(f"  - Ask: {tick.ask}")
        logger.info(f"  - Bid: {tick.bid}")
        logger.info(f"  - 点差: {spread}")
        
        # 3. 计算止损价格
        logger.info("3. 计算止损价格...")
        sl_mode = config_manager.get("SL_MODE", "FIXED_POINTS")
        logger.info(f"止损模式: {sl_mode}")
        
        sl_price = 0
        
        if sl_mode == "FIXED_POINTS":
            sl_points = order.get("sl_points", 0)
            logger.info(f"固定点数止损: {sl_points}点")
            
            if order_type == "buy":
                sl_price = entry_price - sl_points * point
            else:
                sl_price = entry_price + sl_points * point + spread
                
            logger.info(f"计算的止损价格: {sl_price}")
            
        else:
            # K线关键位止损
            logger.info("使用K线关键位止损")
            sl_candle = order.get("sl_candle", 3)
            logger.info(f"回看K线数: {sl_candle}")
            
            # 获取时间框架
            try:
                from app.gui.countdown import CountdownSection
                # 这里需要从GUI获取时间框架，暂时使用默认值
                timeframe = "M1"  # 默认值
                logger.info(f"时间框架: {timeframe}")
                
                # 获取K线数据
                from app.utils.trade_helpers import get_valid_rates, get_timeframe
                rates = get_valid_rates(symbol, get_timeframe(timeframe), sl_candle + 2, None)
                
                if rates is None:
                    logger.error("无法获取K线数据")
                    return 0
                
                lowest_point = min([rate["low"] for rate in rates[2:]])
                highest_point = max([rate["high"] for rate in rates[2:]])
                
                logger.info(f"关键位:")
                logger.info(f"  - 最低点: {lowest_point}")
                logger.info(f"  - 最高点: {highest_point}")
                
                # 获取止损偏移
                sl_offset_points = config_manager.get("BREAKOUT_SETTINGS", {}).get("SL_OFFSET_POINTS", 0)
                sl_offset = sl_offset_points * point
                logger.info(f"止损偏移: {sl_offset_points}点 = {sl_offset}")
                
                if order_type == "buy":
                    sl_price = lowest_point - sl_offset
                else:
                    sl_price = highest_point + sl_offset + spread
                    
                logger.info(f"计算的止损价格: {sl_price}")
                
            except Exception as e:
                logger.error(f"K线关键位止损计算失败: {e}")
                return 0
        
        # 4. 计算价格差距
        logger.info("4. 计算价格差距...")
        price_diff = abs(entry_price - sl_price)
        logger.info(f"价格差距: |{entry_price} - {sl_price}| = {price_diff}")
        
        if price_diff <= 0:
            logger.error("价格差距为0或负数，无法计算仓位")
            return 0
        
        # 5. 计算仓位大小
        logger.info("5. 计算仓位大小...")
        logger.info(f"公式: 仓位大小 = 固定损失 / (价格差距 * 合约大小)")
        logger.info(f"计算: {fixed_loss} / ({price_diff} * {contract_size})")
        
        position_size = fixed_loss / (price_diff * contract_size)
        logger.info(f"原始计算结果: {position_size}")
        
        # 6. 调整到有效手数
        logger.info("6. 调整到有效手数...")
        logger.info(f"调整前: {position_size}")
        
        # 确保在最小/最大范围内
        position_size = max(min_volume, min(max_volume, position_size))
        logger.info(f"范围调整后: {position_size}")
        
        # 调整到步长的倍数
        position_size = round(position_size / volume_step) * volume_step
        logger.info(f"步长调整后: {position_size}")
        
        # 7. 验证结果
        logger.info("7. 验证计算结果...")
        if position_size <= 0:
            logger.error("最终仓位大小为0或负数")
            return 0
        
        # 计算实际风险金额
        actual_risk = position_size * price_diff * contract_size
        logger.info(f"实际风险金额: {position_size} * {price_diff} * {contract_size} = {actual_risk}")
        logger.info(f"目标风险金额: {fixed_loss}")
        logger.info(f"风险差异: {abs(actual_risk - fixed_loss)}")
        
        logger.info("=" * 40)
        logger.info(f"✅ 订单{order_idx+1}仓位计算成功: {position_size}")
        logger.info("=" * 40)
        
        return position_size
        
    except Exception as e:
        logger.error(f"仓位计算异常: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return 0
