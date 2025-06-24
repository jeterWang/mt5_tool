# MT5交易系统项目概览

## 项目目的
这是一个基于MetaTrader 5的专业自动化交易系统，主要功能包括：
- **批量下单设置** - 支持最多10个订单的批量设置，每个订单可独立配置手数、止损止盈点数
- **智能仓位计算** - 支持手动设置手数和固定亏损计算仓位两种模式
- **止损模式** - 固定点数止损和K线关键位止损
- **突破交易** - 基于高点/低点突破的自动下单
- **风控管理** - 日亏损限额控制、日交易次数限制、自动平仓功能
- **数据同步** - 自动同步交易记录到Excel

## 技术栈
- **核心语言**: Python 3.8+
- **GUI框架**: PyQt6 (桌面应用程序)
- **交易接口**: MetaTrader5 Python API
- **数据处理**: pandas (数据分析和处理)
- **数据存储**: SQLite (本地数据库), Excel (openpyxl)
- **配置管理**: JSON配置文件
- **包管理**: uv (Python包管理器)

## 主要模块架构
- `app/gui/` - 图形界面组件 (PyQt6)
- `app/trader/` - 交易核心逻辑 (MT5 API封装)
- `app/database.py` - 数据库操作类
- `config/` - 配置管理系统
- `resources/` - 资源文件 (字体、图标、音效)
- `utils/` - 通用工具函数

## 核心类
- `MT5GUI`: 主窗口类，管理所有UI组件和定时器
- `MT5Trader`: 交易核心类，封装MT5 API操作
- `TradeDatabase`: 数据库操作类
- `BatchOrderSection`: 批量下单设置组件
- `TradingButtonsSection`: 交易按钮组件