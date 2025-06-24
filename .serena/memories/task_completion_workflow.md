# 任务完成后的工作流程

## 代码提交前检查
1. **功能测试**: 启动程序确保基本功能正常
   ```bash
   uv run python main.py
   ```

2. **配置文件验证**: 确保 `config/config.json` 格式正确
   - 验证JSON语法
   - 确认必要字段存在
   - 检查数值范围合理性

3. **依赖管理**: 更新requirements.txt (如有新依赖)
   ```bash
   uv pip freeze > requirements.txt
   ```

## 构建测试
```bash
# 测试可执行文件构建
uv run python build.py

# 检查dist目录中的可执行文件
ls dist/MT5交易系统/
```

## 文件完整性检查
- 确保资源文件存在: `resources/icons/`, `resources/fonts/`
- 确保配置文件有效: `config/config.json`
- 确保数据目录存在: `data/`

## Git提交规范
```bash
# 添加修改的文件
git add .

# 提交时使用清晰的中文提交信息
git commit -m "功能: 添加新的交易功能"
git commit -m "修复: 解决连接MT5的问题"
git commit -m "优化: 改进界面响应速度"

# 推送到远程仓库
git push origin master
```

## 发布检查
- 确保README.md文档是最新的
- 测试在干净环境中的安装和运行
- 验证Windows可执行文件在目标系统上运行正常