2024-06-09 [EXECUTE]
- 工具调用: edit_file
- 操作对象: app/gui/config_manager.py
- 更改内容: 所有配置项的访问和保存方式迁移为config_manager.get/set接口，彻底消除全局变量依赖，保存时用config_manager.save()。
- 执行结果: 成功
- 下一步: 继续迁移其它直接依赖配置的GUI模块，保证全局配置一致性和可维护性。