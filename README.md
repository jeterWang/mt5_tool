# MT5一键下单脚本

这是一个用于MetaTrader 5的一键下单脚本，支持自动止盈止损和分批止盈功能。

## 功能特点

- 一键下单（支持市价单和限价单）
- 自动设置止盈止损
- 支持分批止盈
- 支持查看持仓信息
- 支持手动平仓

## 安装依赖

使用uv安装依赖包：

```bash
uv pip install -r requirements.txt
```

## 配置

1. 在项目根目录创建`.env`文件
2. 添加以下配置信息：

```
MT5_LOGIN=你的MT5账号
MT5_PASSWORD=你的MT5密码
MT5_SERVER=你的MT5服务器
```

## 使用示例

### 1. 简单下单（带止盈止损）

```python
from mt5_trader import MT5Trader

# 创建交易实例
trader = MT5Trader(
    login=123456,
    password="your_password",
    server="your_server"
)

# 下单（0.1手EURUSD，止损50点，止盈100点）
order = trader.place_order_with_tp_sl(
    symbol="EURUSD",
    order_type="buy",
    volume=0.1,
    sl_points=50,
    tp_points=100,
    comment="测试订单"
)
```

### 2. 分批止盈下单

```python
# 设置分批止盈
tp_levels = [
    {"points": 30, "volume": 0.03},  # 30点止盈，平仓0.03手
    {"points": 60, "volume": 0.03},  # 60点止盈，平仓0.03手
    {"points": 100, "volume": 0.04}  # 100点止盈，平仓0.04手
]

# 下单（0.1手EURUSD，止损50点，分批止盈）
order = trader.place_order_with_partial_tp(
    symbol="EURUSD",
    order_type="buy",
    volume=0.1,
    sl_points=50,
    tp_levels=tp_levels,
    comment="分批止盈测试"
)
```

### 3. 查看持仓信息

```python
# 获取持仓信息
position = trader.get_position(ticket=123456)
```

### 4. 手动平仓

```python
# 平仓
trader.close_position(ticket=123456)
```

## 注意事项

1. 使用前请确保MT5平台已经登录
2. 确保账户有足够的保证金
3. 分批止盈的总量不能超过订单总量
4. 建议在实盘交易前先在模拟账户测试

## 错误处理

脚本会处理常见的错误情况，如：
- 连接失败
- 登录失败
- 下单失败
- 交易品种不存在
- 参数错误

所有错误都会通过打印信息提示用户。 