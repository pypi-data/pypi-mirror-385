# 📦 发布指南 - Publishing Guide

本文档详细说明如何将 Excel MCP Server 发布到 GitHub 和 PyPI，以支持 uvx 一键安装。

## 📋 目录

- [前置准备](#前置准备)
- [方案选择](#方案选择)
- [发布到 GitHub](#发布到-github)
- [发布到 PyPI](#发布到-pypi)
- [验证安装](#验证安装)
- [常见问题](#常见问题)

---

## 🔧 前置准备

### 1. 检查项目状态

确认以下文件已准备就绪：

```bash
# 必需文件清单
✅ pyproject.toml          # 包配置文件
✅ README.md               # 项目说明
✅ LICENSE                 # 开源许可证
✅ .gitignore              # Git 忽略规则
✅ .env.example            # 环境变量模板
✅ CHANGELOG.md            # 变更日志
✅ SECURITY.md             # 安全政策
✅ src/mcp_excel_supabase/ # 源代码
✅ tests/                  # 测试代码
✅ docs/                   # 文档
```

### 2. 清理项目

在发布前，清理不必要的文件：

```bash
# 删除临时文件和缓存
Remove-Item -Recurse -Force __pycache__, .pytest_cache, .mypy_cache, .ruff_cache, htmlcov, .coverage -ErrorAction SilentlyContinue

# 删除构建产物（稍后重新构建）
Remove-Item -Recurse -Force dist, build, *.egg-info -ErrorAction SilentlyContinue

# 删除日志文件
Remove-Item -Recurse -Force logs -ErrorAction SilentlyContinue

# 删除测试产物
Remove-Item -Recurse -Force Formal-unit-testing -ErrorAction SilentlyContinue
```

### 3. 运行完整测试

```bash
# 激活虚拟环境
.\venv\Scripts\Activate.ps1

# 运行所有测试
pytest

# 代码质量检查
ruff check .
black --check .
mypy src/mcp_excel_supabase
```

---

## 🎯 方案选择

### 方案 A：发布到 PyPI（推荐）⭐

**优点：**
- ✅ 用户体验最佳：`uvx mcp-excel-supabase`
- ✅ 自动版本管理
- ✅ 官方包索引，可信度高
- ✅ 支持版本锁定：`uvx mcp-excel-supabase==1.0.0`

**缺点：**
- ⚠️ 需要 PyPI 账号
- ⚠️ 包名可能被占用
- ⚠️ 发布后难以撤回

**适用场景：**
- 正式发布的稳定版本
- 希望被广泛使用的项目
- 需要版本管理的项目

### 方案 B：仅 GitHub

**优点：**
- ✅ 无需 PyPI 账号
- ✅ 完全控制代码
- ✅ 可以随时修改

**缺点：**
- ⚠️ 安装命令较长：`uvx --from git+https://github.com/用户名/仓库名 mcp-excel-supabase`
- ⚠️ 需要 Git 访问权限
- ⚠️ 版本管理需要使用 Git 标签

**适用场景：**
- 内部项目或私有项目
- 开发测试阶段
- 不希望公开到 PyPI

---

## 📤 发布到 GitHub

### 步骤 1：初始化 Git 仓库（如果尚未初始化）

```bash
# 检查是否已初始化
git status

# 如果未初始化，执行：
git init
git add .
git commit -m "Initial commit: Excel MCP Server v1.0.0"
```

### 步骤 2：创建 GitHub 仓库

1. 访问 https://github.com/new
2. 填写仓库信息：
   - **Repository name**: `Excel-MCP-Server-with-Supabase-Storage`
   - **Description**: `MCP server for Excel operations with Supabase Storage integration`
   - **Visibility**: Public（公开）或 Private（私有）
   - **不要**勾选 "Initialize this repository with a README"（我们已有 README）

### 步骤 3：推送代码到 GitHub

```bash
# 添加远程仓库（替换为你的 GitHub 用户名）
git remote add origin https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage.git

# 推送代码
git branch -M main
git push -u origin main
```

### 步骤 4：创建 GitHub Release

1. 访问仓库页面：`https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage`
2. 点击右侧 "Releases" → "Create a new release"
3. 填写 Release 信息：
   - **Tag version**: `v1.0.0`
   - **Release title**: `v1.0.0 - Initial Release`
   - **Description**: 复制下面的模板

```markdown
# 🎉 Excel MCP Server v1.0.0 - Initial Release

## ✨ 主要功能

- ✅ **Excel 解析**: 将 Excel 文件转换为 JSON，保留完整格式信息
- ✅ **Excel 生成**: 从 JSON 数据创建格式化的 Excel 文件
- ✅ **高级格式化**: 修改单元格样式、合并单元格、调整行高列宽
- ✅ **公式支持**: 执行和计算 20+ 常用 Excel 公式
- ✅ **多工作表操作**: 合并多个 Excel 文件到单个工作簿
- ✅ **Supabase 集成**: 直接读写 Supabase Storage
- ✅ **零依赖**: 无需 Microsoft Office 或 WPS
- ✅ **跨平台**: 支持 Windows、Linux、macOS

## 🚀 快速安装

### 方式 1：通过 uvx（推荐）

```bash
uvx --from git+https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage mcp-excel-supabase
```

### 方式 2：通过 pip

```bash
pip install git+https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage
```

## 📦 包含的工具

提供 12 个 MCP 工具：
1. `parse_excel_to_json` - 解析 Excel 为 JSON
2. `create_excel_from_json` - 从 JSON 创建 Excel
3. `modify_cell_format` - 修改单元格格式
4. `merge_cells` - 合并单元格
5. `unmerge_cells` - 取消合并
6. `set_row_heights` - 设置行高
7. `set_column_widths` - 设置列宽
8. `manage_storage` - 管理云存储
9. `set_formula` - 设置公式
10. `recalculate_formulas` - 重新计算公式
11. `manage_sheets` - 管理工作表
12. `merge_excel_files` - 合并 Excel 文件

## 📊 性能指标

| 操作 | 目标 | 实际 | 状态 |
|------|------|------|------|
| 解析 1MB 文件 | <2s | 0.598s | ✅ **3.3x 更快** |
| 生成 1000 行 | <3s | 0.026s | ✅ **115x 更快** |
| 合并 10 个文件 | <8s | 0.117s | ✅ **68x 更快** |
| 批量 20 个文件 | <10s | 0.192s | ✅ **52x 更快** |

## 📚 文档

- [README](https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage/blob/main/README.md)
- [API 文档](https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage/blob/main/docs/api.md)
- [使用示例](https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage/tree/main/docs/examples)
- [架构设计](https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage/blob/main/docs/architecture.md)

## 🐛 已知问题

无

## 🙏 致谢

感谢所有贡献者和测试人员！

---

**完整变更日志**: [CHANGELOG.md](https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage/blob/main/CHANGELOG.md)
```

4. 点击 "Publish release"

### 步骤 5：验证 GitHub 安装

```bash
# 测试从 GitHub 安装
uvx --from git+https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage mcp-excel-supabase --help
```

---

## 🚀 发布到 PyPI

### 步骤 1：注册 PyPI 账号

1. 访问 https://pypi.org/account/register/
2. 注册账号并验证邮箱
3. 启用两步验证（推荐）

### 步骤 2：创建 API Token

1. 登录 PyPI
2. 访问 https://pypi.org/manage/account/token/
3. 点击 "Add API token"
4. 填写信息：
   - **Token name**: `excel-mcp-upload`
   - **Scope**: "Entire account"（首次上传）或选择特定项目
5. 复制生成的 token（格式：`pypi-...`）

### 步骤 3：配置 PyPI 凭证

创建 `~/.pypirc` 文件（Windows: `%USERPROFILE%\.pypirc`）：

```ini
[distutils]
index-servers =
    pypi

[pypi]
username = __token__
password = pypi-你的token
```

### 步骤 4：构建分发包

```bash
# 激活虚拟环境
.\venv\Scripts\Activate.ps1

# 安装构建工具
pip install --upgrade build twine

# 清理旧的构建产物
Remove-Item -Recurse -Force dist, build, *.egg-info -ErrorAction SilentlyContinue

# 构建包
python -m build

# 验证构建结果
ls dist/
# 应该看到：
# mcp_excel_supabase-1.0.0-py3-none-any.whl
# mcp_excel_supabase-1.0.0.tar.gz
```

### 步骤 5：检查包

```bash
# 检查包的完整性
twine check dist/*

# 应该看到：
# Checking dist/mcp_excel_supabase-1.0.0-py3-none-any.whl: PASSED
# Checking dist/mcp_excel_supabase-1.0.0.tar.gz: PASSED
```

### 步骤 6：上传到 TestPyPI（可选，推荐）

先上传到测试环境验证：

```bash
# 上传到 TestPyPI
twine upload --repository testpypi dist/*

# 测试安装
uvx --index-url https://test.pypi.org/simple/ mcp-excel-supabase
```

### 步骤 7：上传到 PyPI

```bash
# 上传到正式 PyPI
twine upload dist/*

# 输入用户名：__token__
# 输入密码：你的 API token
```

### 步骤 8：验证 PyPI 安装

```bash
# 等待 1-2 分钟让 PyPI 索引更新

# 测试安装
uvx mcp-excel-supabase --help

# 应该看到帮助信息
```

---

## ✅ 验证安装

### 1. 验证 uvx 安装

```bash
# 方式 1：从 PyPI 安装（如果已发布）
uvx mcp-excel-supabase --help

# 方式 2：从 GitHub 安装
uvx --from git+https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage mcp-excel-supabase --help
```

### 2. 验证 Claude Desktop 集成

编辑 Claude Desktop 配置文件：

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "excel-supabase": {
      "command": "uvx",
      "args": ["mcp-excel-supabase"],
      "env": {
        "SUPABASE_URL": "https://yourproject.supabase.co",
        "SUPABASE_KEY": "your-service-role-key-here"
      }
    }
  }
}
```

重启 Claude Desktop，检查 MCP 工具是否可用。

---

## ❓ 常见问题

### Q1: 包名已被占用怎么办？

**解决方案：**
1. 修改 `pyproject.toml` 中的 `name` 字段
2. 例如：`mcp-excel-supabase-storage` 或 `excel-mcp-supabase`
3. 重新构建并上传

### Q2: uvx 安装失败

**可能原因：**
- Python 版本不兼容（需要 ≥3.9）
- 网络问题
- 包名错误

**解决方案：**
```bash
# 检查 Python 版本
python --version

# 使用详细输出查看错误
uvx --verbose mcp-excel-supabase
```

### Q3: 如何更新已发布的包？

**步骤：**
1. 修改 `pyproject.toml` 中的 `version`（例如：`1.0.1`）
2. 更新 `CHANGELOG.md`
3. 重新构建：`python -m build`
4. 上传新版本：`twine upload dist/*`
5. 创建新的 GitHub Release（tag: `v1.0.1`）

### Q4: 如何撤回已发布的包？

**PyPI 政策：**
- 无法删除已发布的版本
- 可以"yank"（标记为不推荐）：访问 PyPI 项目页面 → Manage → Yank release

**建议：**
- 发布前在 TestPyPI 充分测试
- 使用语义化版本号
- 维护详细的 CHANGELOG

---

## 📝 发布检查清单

发布前请确认：

- [ ] 所有测试通过（`pytest`）
- [ ] 代码质量检查通过（`ruff`, `black`, `mypy`）
- [ ] 文档完整且准确
- [ ] `CHANGELOG.md` 已更新
- [ ] 版本号正确（`pyproject.toml`）
- [ ] `.gitignore` 配置正确
- [ ] 敏感信息已移除（`.env` 文件）
- [ ] LICENSE 文件存在
- [ ] README 包含安装和使用说明
- [ ] 构建包检查通过（`twine check`）
- [ ] 在 TestPyPI 测试成功（可选）

---

## 🎯 推荐发布流程

1. **开发阶段**: 仅推送到 GitHub
2. **测试阶段**: 上传到 TestPyPI
3. **正式发布**: 上传到 PyPI + 创建 GitHub Release
4. **后续更新**: 同时更新 PyPI 和 GitHub

---

**祝发布顺利！** 🎉

如有问题，请查阅：
- [Python Packaging Guide](https://packaging.python.org/)
- [PyPI Help](https://pypi.org/help/)
- [GitHub Docs](https://docs.github.com/)

