2024-06-09 [EXECUTE]
- 工具调用: edit_file
- 操作对象: app/config/config_manager.py, app/gui/settings.py
- 更改内容: 
  1. 在ConfigManager初始化时注册DEFAULT_TIMEFRAME、DAILY_LOSS_LIMIT、SYMBOLS等核心配置项，指定默认值和类型。
  2. settings.py中相关配置项的读取和保存全部改为通过config_manager.get/set接口访问，演示新用法，便于后续全局迁移。
- 执行结果: 成功
- 下一步: 继续迁移其它配置项，逐步替换全局变量访问，完善配置中心功能。