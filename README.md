# MT5交易系统

## 功能简介
MT5交易系统是一款基于MetaTrader 5的多功能量化交易管理工具，支持一键批量下单、风控、交易记录自动同步、日内盈亏统计等实用功能。

### 主要功能
- **批量下单**：支持一键批量买入/卖出、挂高低点突破单。
- **一键平仓/撤销挂单**：支持一键平掉所有持仓或撤销所有挂单。
- **日内风控**：可自定义每日最大亏损，自动平仓并禁止当日交易，风控事件自动记录。
- **交易记录自动同步**：自动从MT5同步近3天平仓单，按账号分Sheet保存到Excel。
- **盈亏统计**：实时显示今日已实现盈亏、当前浮动盈亏、日内总盈亏。
- **多时区支持**：可自定义MT5服务器时区和本地时区，成交时间自动转换为本地时间。
- **自定义参数**：所有风控、下单、品种参数均可在config.json中灵活配置。
- **美观易用的图形界面**：支持窗口置顶、K线周期选择、声音提醒等。

## 项目结构
```
mt5/
├── app/                 # 应用核心代码（主程序、界面、交易逻辑等）
│   ├── __init__.py      # 初始化文件
│   ├── database.py      # 数据库操作类
│   ├── trader/          # 交易相关模块
│   ├── gui/             # 图形界面相关模块
│   └── ...
├── config/              # 配置文件目录
│   ├── __init__.py      # 初始化文件
│   ├── config.json      # 配置JSON文件（所有参数、批量下单等）
│   └── loader.py        # 配置加载器
├── resources/           # 资源文件目录
│   ├── fonts/           # 字体文件
│   ├── icons/           # 图标文件
│   └── sounds/          # 音效文件
├── data/                # 数据存储目录
├── utils/               # 工具类和函数
│   ├── __init__.py      # 初始化文件
│   └── paths.py         # 路径处理工具
├── main.py              # 主程序入口
├── requirements.txt     # 依赖包列表
└── README.md            # 项目说明文件
```

> **使用说明：**
>
> - **推荐方式1：** 直接到 [Releases](https://github.com/yourrepo/mt5-trading-system/releases) 页面下载最新的 `.7z` 压缩包，解压后双击运行，无需源码和环境配置。
> - **方式2：** 如需自定义开发或二次开发，可克隆源码并按下方开发环境设置操作。

## 开发环境设置
1. **克隆仓库**
   ```bash
   git clone https://github.com/yourrepo/mt5-trading-system.git
   cd mt5-trading-system
   ```

2. **安装依赖**
   ```bash
   # 使用uv包管理器
   uv venv
   uv pip install -r requirements.txt
   ```

3. **运行程序**
   ```bash
   python main.py
   ```

## 配置说明
- 所有配置项均存储在`config/config.json`文件中
- 可以直接编辑此文件，也可以通过程序界面进行修改
- 配置项说明：
  - `SYMBOLS`: 交易品种列表
  - `DEFAULT_TIMEFRAME`: 默认K线周期
  - `DAILY_TRADE_LIMIT`: 每日最大交易次数
  - `DAILY_LOSS_LIMIT`: 每日最大亏损限额
  - `TRADING_DAY_RESET_HOUR`: 交易日重置时间
  - `GUI_SETTINGS`: GUI界面相关设置
  - `BATCH_ORDER_DEFAULTS`: 批量下单默认参数
  - `DEFAULT_PARAMS`: 各交易品种的默认参数
  - `Delta_TIMEZONE`: 时区差值

## 常见问题
- **启动无命令行窗口**：本程序为纯GUI应用，启动时不会弹出黑色命令行。
- **MT5未连接/未登录**：请先在本地MT5终端登录账号并保持运行。
- **成交时间不对**：请在 `config.json` 设置正确的 `Delta_TIMEZONE`。
- **交易记录缺失**：同步逻辑每分钟自动拉取近3天平仓单，若有遗漏可手动调整同步范围。
- **风控触发后无法交易**：当天日内亏损达到上限后，所有下单按钮会自动禁用，次日自动恢复。

## 反馈与支持
如有功能建议、BUG反馈或定制需求，请在项目Issue区留言，或联系开发者。

---

**MT5TradeManager —— 让量化交易更高效、更安全、更智能！** 