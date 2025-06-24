# MT5交易系统开发命令

## 包管理命令 (使用uv)
```bash
# 创建虚拟环境
uv venv

# 安装项目依赖
uv pip install -r requirements.txt

# 同步依赖 (推荐)
uv sync

# 添加新依赖
uv add package_name

# 移除依赖
uv remove package_name

# 显示已安装包
uv pip list

# 冻结依赖到requirements.txt
uv pip freeze > requirements.txt
```

## 运行命令
```bash
# 启动主程序
uv run python main.py

# 或者直接运行
python main.py

# 构建可执行文件
uv run python build.py
```

## 项目文件操作
```bash
# Windows系统常用命令
dir                 # 列出目录内容
cd directory        # 切换目录
copy file1 file2    # 复制文件
del filename        # 删除文件
type filename       # 查看文件内容
```

## 开发环境设置
```bash
# 克隆项目后初始化
git clone <repository>
cd mt5-trading-system
uv venv
uv sync

# 运行开发版本
uv run python main.py
```

## 调试和日志
- 程序日志会在控制台输出
- MT5连接状态会在状态栏显示
- 配置文件位于 `config/config.json`
- 数据库文件位于 `data/trade_history.db`