# MT5一键交易工具

这是一个基于MetaTrader 5 (MT5) API的自动化交易工具，提供了简单易用的图形界面，支持多种交易功能。

## 主要功能

- 🚀 一键下单功能
  - 支持市价单和挂单
  - 可同时下多个订单
  - 每个订单可独立设置止盈止损
  - 支持批量设置交易量

- 📊 K线周期监控
  - 支持多个时间周期（M1, M5, M15, M30, H1, H4）
  - 自动计算收盘倒计时
  - 收盘提醒功能

- 💼 订单管理
  - 一键平仓功能
  - 一键撤销挂单
  - 突破单功能（支持高点和低点突破）

- ⚙️ 配置灵活
  - 支持多个交易品种（默认 XAUUSDm, XAGUSDm）
  - 可自定义默认参数
  - 支持环境变量配置

## 安装说明

1. 确保已安装Python 3.11或更低版本（MetaTrader5包目前不支持Python 3.13）

2. 克隆仓库：
```bash
git clone https://github.com/jeterWang/mt5_tool.git
cd mt5_tool
```

3. 创建并激活虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

4. 安装依赖：
```bash
uv pip install -r requirements.txt
```

5. 配置环境变量：
   - 复制`.env.example`为`.env`
   - 在`.env`中填入您的MT5账号信息：
```
MT5_USERNAME=您的账号
MT5_PASSWORD=您的密码
MT5_SERVER=您的服务器
```

## 使用说明

1. 确保MT5客户端已登录并启用了自动交易

2. 运行程序：
```bash
python mt5_gui.py
```

3. 主要功能说明：
   - 选择交易品种和K线周期
   - 设置交易量、止盈止损点数
   - 使用一键下单功能进行交易
   - 使用突破单功能设置自动突破订单
   - 使用一键平仓功能快速关闭所有持仓
   - 使用撤单功能取消所有挂单

## 注意事项

- 使用前请确保了解交易风险
- 建议在模拟账户中充分测试
- 确保网络连接稳定
- 定期检查MT5客户端状态

## 许可证

MIT License

## 作者

jeterWang

## 贡献

欢迎提交Issue和Pull Request！ 