# MT5交易系统代码规范

## 代码风格
- **Python版本**: 3.8+
- **编码格式**: UTF-8
- **缩进**: 4个空格
- **行长度**: 一般不超过88字符

## 命名规范
- **类名**: PascalCase (如 `MT5GUI`, `TradeDatabase`)
- **函数名**: snake_case (如 `connect_mt5`, `update_positions`)
- **变量名**: snake_case (如 `trade_count`, `account_info`)
- **常量**: UPPER_SNAKE_CASE (如 `DAILY_LOSS_LIMIT`, `DEFAULT_TIMEFRAME`)
- **私有方法**: 以下划线开头 (如 `_get_account_id`)

## 文档字符串
- 使用简洁的中文注释
- 模块级别有模块说明
- 重要函数有简短的功能说明

```python
"""
MT5交易系统启动入口

运行此模块可启动MT5交易系统GUI界面
"""

def main():
    """启动应用程序"""
    pass
```

## 导入顺序
1. 标准库导入
2. 第三方库导入 (如 PyQt6, pandas, MetaTrader5)
3. 本地模块导入 (从 app, config, utils)

## 异常处理
- 使用具体的异常类型
- 包含有意义的错误消息
- 在GUI应用中适当显示用户友好的错误信息

## 配置管理
- 所有配置参数集中在 `config/config.json`
- 使用 `config/loader.py` 统一加载配置
- 支持运行时配置修改和保存