# MT5交易系统代码库结构

## 目录结构
```
mt5/
├── app/                 # 应用核心代码
│   ├── __init__.py      # 版本信息
│   ├── database.py      # SQLite数据库操作
│   ├── gui/             # GUI界面组件
│   │   ├── main_window.py       # 主窗口 (MT5GUI类)
│   │   ├── batch_order.py       # 批量下单设置
│   │   ├── trading_buttons.py   # 交易按钮组件
│   │   ├── account_info.py      # 账户信息显示
│   │   ├── positions_table.py   # 持仓表格
│   │   ├── countdown.py         # 倒计时组件
│   │   ├── pnl_info.py         # 盈亏信息
│   │   ├── trading_settings.py  # 交易设置
│   │   ├── risk_control.py      # 风控检查
│   │   ├── settings.py          # 设置对话框
│   │   └── config_manager.py    # GUI配置管理
│   └── trader/          # 交易核心模块
│       ├── core.py      # MT5Trader主类
│       ├── orders.py    # 下单相关函数
│       ├── data_sync.py # 数据同步功能
│       └── symbol_info.py # 交易品种信息
├── config/              # 配置管理
│   ├── config.json      # 主配置文件
│   ├── config.json.example # 配置示例
│   └── loader.py        # 配置加载器
├── resources/           # 资源文件
│   ├── fonts/           # 字体文件
│   ├── icons/           # 图标文件
│   └── sounds/          # 音效文件
├── data/                # 数据存储
│   └── trade_history.db # SQLite数据库
├── utils/               # 工具函数
│   └── paths.py         # 路径处理
├── main.py              # 程序入口点
├── build.py             # 构建脚本
└── requirements.txt     # 依赖清单
```

## 核心组件关系
- `main.py` → `MT5GUI` (主窗口)
- `MT5GUI` → `MT5Trader` (交易核心)
- `MT5GUI` → 各种GUI组件 (batch_order, trading_buttons等)
- `MT5Trader` → MT5 API (MetaTrader5库)
- 所有组件 → `config/loader.py` (配置管理)

## 关键文件说明
- **main.py**: 应用程序启动入口
- **app/gui/main_window.py**: 主窗口类，包含所有UI逻辑和定时器
- **app/trader/core.py**: MT5交易核心，封装所有交易操作
- **config/loader.py**: 配置系统，管理所有应用设置
- **build.py**: PyInstaller构建脚本，生成Windows可执行文件