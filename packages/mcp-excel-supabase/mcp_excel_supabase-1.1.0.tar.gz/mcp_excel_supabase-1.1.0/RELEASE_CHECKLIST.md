# 📋 发布检查清单 - Release Checklist

使用此清单确保发布流程顺利完成。

---

## 🔍 发布前检查

### 代码质量

- [ ] 所有测试通过
  ```powershell
  pytest
  ```

- [ ] 代码质量检查通过
  ```powershell
  ruff check .
  black --check .
  mypy src/mcp_excel_supabase
  ```

- [ ] 无安全漏洞
  ```powershell
  pip-audit
  ```

### 文档完整性

- [ ] README.md 准确且完整
- [ ] CHANGELOG.md 已更新
- [ ] API 文档完整（docs/api.md）
- [ ] 使用示例可用（docs/examples/）
- [ ] .env.example 包含所有必需变量

### 配置文件

- [ ] pyproject.toml 版本号正确
- [ ] LICENSE 文件存在
- [ ] .gitignore 配置正确
- [ ] SECURITY.md 存在

### 敏感信息

- [ ] .env 文件未被提交
- [ ] 无硬编码的密钥或密码
- [ ] 测试数据不包含真实凭证

---

## 📦 构建和验证

### 清理项目

- [ ] 删除所有缓存文件
  ```powershell
  Get-ChildItem -Path . -Include __pycache__,.pytest_cache,.mypy_cache,.ruff_cache -Recurse -Force | Remove-Item -Recurse -Force
  ```

- [ ] 删除测试产物
  ```powershell
  Remove-Item -Path htmlcov,.coverage,logs,Formal-unit-testing -Recurse -Force -ErrorAction SilentlyContinue
  ```

- [ ] 删除旧的构建产物
  ```powershell
  Remove-Item -Path dist,build -Recurse -Force -ErrorAction SilentlyContinue
  Get-ChildItem -Path . -Filter "*.egg-info" -Recurse -Force | Remove-Item -Recurse -Force
  ```

### 构建包

- [ ] 安装构建工具
  ```powershell
  pip install --upgrade build twine
  ```

- [ ] 构建分发包
  ```powershell
  python -m build
  ```

- [ ] 验证构建结果
  ```powershell
  twine check dist/*
  ```
  应该看到：
  ```
  Checking dist/mcp_excel_supabase-1.0.0-py3-none-any.whl: PASSED
  Checking dist/mcp_excel_supabase-1.0.0.tar.gz: PASSED
  ```

---

## 🌐 发布到 GitHub

### Git 准备

- [ ] 所有更改已提交
  ```powershell
  git status
  ```

- [ ] 提交信息清晰
  ```powershell
  git log --oneline -5
  ```

- [ ] 创建版本标签
  ```powershell
  git tag -a v1.0.0 -m "Release v1.0.0"
  ```

### 推送到 GitHub

- [ ] 推送代码
  ```powershell
  git push origin main
  ```

- [ ] 推送标签
  ```powershell
  git push origin v1.0.0
  ```

### 创建 GitHub Release

- [ ] 访问 GitHub 仓库页面
- [ ] 点击 "Releases" → "Create a new release"
- [ ] 选择标签: `v1.0.0`
- [ ] 填写标题: `v1.0.0 - Initial Release`
- [ ] 复制 `.github/RELEASE_TEMPLATE.md` 内容到描述
- [ ] 上传构建产物（可选）:
  - `dist/mcp_excel_supabase-1.0.0-py3-none-any.whl`
  - `dist/mcp_excel_supabase-1.0.0.tar.gz`
- [ ] 点击 "Publish release"

---

## 🚀 发布到 PyPI（可选）

### PyPI 准备

- [ ] 已注册 PyPI 账号
- [ ] 已创建 API Token
- [ ] 已配置 `~/.pypirc` 文件

### 测试发布（推荐）

- [ ] 上传到 TestPyPI
  ```powershell
  twine upload --repository testpypi dist/*
  ```

- [ ] 测试安装
  ```powershell
  uvx --index-url https://test.pypi.org/simple/ mcp-excel-supabase
  ```

- [ ] 验证功能正常

### 正式发布

- [ ] 上传到 PyPI
  ```powershell
  twine upload dist/*
  ```

- [ ] 等待 1-2 分钟让索引更新

- [ ] 测试安装
  ```powershell
  uvx mcp-excel-supabase
  ```

---

## ✅ 发布后验证

### 安装测试

- [ ] GitHub 安装成功
  ```powershell
  uvx --from git+https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage mcp-excel-supabase --help
  ```

- [ ] PyPI 安装成功（如果已发布）
  ```powershell
  uvx mcp-excel-supabase --help
  ```

### Claude Desktop 集成

- [ ] 配置文件已更新
- [ ] Claude Desktop 已重启
- [ ] MCP 工具可见
- [ ] 工具功能正常

### 文档链接

- [ ] README 中的链接可访问
- [ ] 文档链接正确
- [ ] 示例代码可运行

### 社区通知

- [ ] 更新项目主页
- [ ] 发布公告（如适用）
- [ ] 通知相关用户

---

## 📝 发布后任务

### 更新文档

- [ ] 更新 README 中的版本号
- [ ] 更新安装说明
- [ ] 添加发布公告

### 监控

- [ ] 检查 GitHub Issues
- [ ] 监控下载量
- [ ] 收集用户反馈

### 规划下一版本

- [ ] 创建 v1.1 里程碑
- [ ] 整理待实现功能
- [ ] 更新 Roadmap

---

## 🔄 版本更新流程

当需要发布新版本时：

1. **更新版本号**
   - [ ] 修改 `pyproject.toml` 中的 `version`
   - [ ] 更新 `CHANGELOG.md`

2. **重复上述检查清单**

3. **创建新的 Release**
   - [ ] 新标签: `v1.0.1`, `v1.1.0` 等
   - [ ] 更新 Release 说明

---

## ❓ 问题排查

### 构建失败

- 检查 `pyproject.toml` 配置
- 确认所有依赖已安装
- 查看构建日志

### 上传失败

- 验证 PyPI 凭证
- 检查包名是否已被占用
- 确认网络连接

### 安装失败

- 检查 Python 版本 (≥3.9)
- 验证包名拼写
- 查看详细错误信息

---

## 📚 参考资源

- [详细发布指南](docs/PUBLISHING_GUIDE.md)
- [快速开始指南](QUICK_START.md)
- [Python Packaging Guide](https://packaging.python.org/)
- [PyPI Help](https://pypi.org/help/)

---

**祝发布顺利！** 🎉

完成后请在此清单上打勾，确保没有遗漏任何步骤。

