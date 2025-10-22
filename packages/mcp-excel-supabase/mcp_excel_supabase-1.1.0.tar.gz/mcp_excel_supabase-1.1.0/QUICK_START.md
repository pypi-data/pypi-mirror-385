# 🚀 快速开始 - Quick Start Guide

本指南帮助你快速安装和配置 Excel MCP Server。

## 📦 安装

### 从 PyPI 安装（推荐）

```bash
uvx mcp-excel-supabase
```

### 从 GitHub 安装

```bash
uvx --from git+https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage mcp-excel-supabase
```

---

## 🌐 传输模式配置

Excel MCP Server 支持三种传输模式：

### 1. STDIO（默认）- 适用于 Claude Desktop

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

### 2. HTTP - 适用于 Cherry Studio 等 Web 客户端

```json
{
  "mcpServers": {
    "excel-supabase": {
      "command": "uvx",
      "args": ["mcp-excel-supabase"],
      "env": {
        "SUPABASE_URL": "https://yourproject.supabase.co",
        "SUPABASE_KEY": "your-service-role-key-here",
        "MCP_TRANSPORT": "http",
        "MCP_HOST": "127.0.0.1",
        "MCP_PORT": "8000"
      }
    }
  }
}
```

连接地址：`http://127.0.0.1:8000/mcp/`

### 3. SSE - 兼容旧版客户端

```json
{
  "mcpServers": {
    "excel-supabase": {
      "command": "uvx",
      "args": ["mcp-excel-supabase"],
      "env": {
        "SUPABASE_URL": "https://yourproject.supabase.co",
        "SUPABASE_KEY": "your-service-role-key-here",
        "MCP_TRANSPORT": "sse",
        "MCP_HOST": "127.0.0.1",
        "MCP_PORT": "8000"
      }
    }
  }
}
```

连接地址：`http://127.0.0.1:8000/sse`

**详细配置说明**：请参阅 [传输模式配置指南](docs/TRANSPORT_MODES.md)

---

## 🐛 常见问题

### 超时错误（Request timed out）

**解决方案**：首次使用前预先安装依赖

```bash
uvx mcp-excel-supabase --help
```

等待安装完成后，再在客户端中配置。

### Cherry Studio 配置

推荐使用 HTTP 传输模式，详见 [传输模式配置指南](docs/TRANSPORT_MODES.md#-cherry-studio-配置示例)。

---

## 📋 发布前检查清单（开发者）

在开始之前，请确认：

- ✅ 所有代码已提交到本地 Git 仓库
- ✅ 所有测试通过（`pytest`）
- ✅ 代码质量检查通过（`ruff`, `black`）
- ✅ 文档完整且准确
- ✅ `.env` 文件未被提交（已在 `.gitignore` 中）
- ✅ 版本号正确（`pyproject.toml` 中的 `version = "1.0.0"`）

---

## 🎯 方案选择

### 方案 A：仅发布到 GitHub（推荐新手）⭐

**优点：**
- ✅ 简单快速，无需 PyPI 账号
- ✅ 完全免费
- ✅ 可以随时修改

**安装命令：**
```bash
uvx --from git+https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage mcp-excel-supabase
```

**适合：** 个人项目、内部使用、测试阶段

### 方案 B：发布到 PyPI（推荐正式发布）

**优点：**
- ✅ 用户体验最佳
- ✅ 官方包索引，可信度高
- ✅ 支持版本管理

**安装命令：**
```bash
uvx mcp-excel-supabase
```

**适合：** 正式发布、公开项目、希望被广泛使用

---

## 📤 方案 A：发布到 GitHub（5 分钟）

### 步骤 1：创建 GitHub 仓库

1. 访问 https://github.com/new
2. 填写信息：
   - **Repository name**: `Excel-MCP-Server-with-Supabase-Storage`
   - **Description**: `MCP server for Excel operations with Supabase Storage integration`
   - **Visibility**: Public（公开）
   - **不要**勾选任何初始化选项
3. 点击 "Create repository"

### 步骤 2：推送代码

在项目目录中运行：

```powershell
# 检查 Git 状态
git status

# 如果有未提交的更改，先提交
git add .
git commit -m "Release v1.0.0"

# 添加远程仓库（替换为你的仓库地址）
git remote add origin https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage.git

# 推送代码
git branch -M main
git push -u origin main
```

### 步骤 3：创建 GitHub Release

1. 访问你的仓库页面
2. 点击右侧 "Releases" → "Create a new release"
3. 填写：
   - **Tag**: `v1.0.0`
   - **Title**: `v1.0.0 - Initial Release`
   - **Description**: 复制下面的内容

```markdown
# 🎉 Excel MCP Server v1.0.0

## ✨ 主要功能

- ✅ Excel 解析与生成
- ✅ 高级格式化
- ✅ 公式支持（20+ 函数）
- ✅ Supabase 集成
- ✅ 跨平台支持

## 🚀 安装

```bash
uvx --from git+https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage mcp-excel-supabase
```

## 📚 文档

- [README](README.md)
- [API 文档](docs/api.md)
- [使用示例](docs/examples/)

完整变更日志: [CHANGELOG.md](CHANGELOG.md)
```

4. 点击 "Publish release"

### 步骤 4：测试安装

```powershell
# 测试从 GitHub 安装
uvx --from git+https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage mcp-excel-supabase --help
```

### 步骤 5：配置 Claude Desktop

编辑配置文件（Windows: `%APPDATA%\Claude\claude_desktop_config.json`）：

```json
{
  "mcpServers": {
    "excel-supabase": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage",
        "mcp-excel-supabase"
      ],
      "env": {
        "SUPABASE_URL": "https://yourproject.supabase.co",
        "SUPABASE_KEY": "your-service-role-key-here"
      }
    }
  }
}
```

**完成！** 🎉 你的项目已经可以通过 uvx 安装了。

---

## 🚀 方案 B：发布到 PyPI（15 分钟）

### 前置准备

1. **注册 PyPI 账号**
   - 访问 https://pypi.org/account/register/
   - 验证邮箱

2. **创建 API Token**
   - 登录后访问 https://pypi.org/manage/account/token/
   - 点击 "Add API token"
   - Token name: `excel-mcp-upload`
   - Scope: "Entire account"
   - 复制生成的 token（格式：`pypi-...`）

3. **配置凭证**
   
   创建文件 `~/.pypirc`（Windows: `%USERPROFILE%\.pypirc`）：
   
   ```ini
   [distutils]
   index-servers =
       pypi
       testpypi
   
   [pypi]
   username = __token__
   password = pypi-你的token
   
   [testpypi]
   username = __token__
   password = pypi-你的testpypi-token
   ```

### 步骤 1：使用发布脚本（推荐）

```powershell
# 运行发布脚本（仅构建，不上传）
.\scripts\publish.ps1 -Target github

# 或者跳过测试（如果已经测试过）
.\scripts\publish.ps1 -Target github -SkipTests
```

### 步骤 2：上传到 TestPyPI（可选，推荐）

先在测试环境验证：

```powershell
# 上传到 TestPyPI
twine upload --repository testpypi dist/*

# 测试安装
uvx --index-url https://test.pypi.org/simple/ mcp-excel-supabase
```

### 步骤 3：上传到 PyPI

```powershell
# 上传到正式 PyPI
twine upload dist/*

# 输入用户名：__token__
# 输入密码：你的 API token
```

### 步骤 4：验证安装

```powershell
# 等待 1-2 分钟让 PyPI 索引更新

# 测试安装
uvx mcp-excel-supabase --help
```

### 步骤 5：配置 Claude Desktop

编辑配置文件：

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

**完成！** 🎉 你的项目已经发布到 PyPI 了。

---

## 🔧 手动构建（如果不使用脚本）

```powershell
# 1. 激活虚拟环境
.\venv\Scripts\Activate.ps1

# 2. 安装构建工具
pip install --upgrade build twine

# 3. 清理旧构建
Remove-Item -Recurse -Force dist, build, *.egg-info -ErrorAction SilentlyContinue

# 4. 构建包
python -m build

# 5. 检查包
twine check dist/*

# 6. 上传（选择一个）
twine upload --repository testpypi dist/*  # TestPyPI
twine upload dist/*                         # PyPI
```

---

## ✅ 验证清单

发布后请验证：

- [ ] GitHub 仓库可访问
- [ ] GitHub Release 已创建
- [ ] uvx 安装成功
- [ ] Claude Desktop 配置正确
- [ ] MCP 工具可用
- [ ] 文档链接正常

---

## 📝 更新版本

当需要发布新版本时：

1. **更新版本号**
   ```toml
   # pyproject.toml
   version = "1.0.1"  # 修改这里
   ```

2. **更新 CHANGELOG**
   ```markdown
   # CHANGELOG.md
   ## [1.0.1] - 2025-10-21
   ### Fixed
   - 修复了某个 bug
   ```

3. **重新构建和发布**
   ```powershell
   # 重新构建
   python -m build
   
   # 上传新版本
   twine upload dist/*
   
   # 创建新的 GitHub Release (tag: v1.0.1)
   ```

---

## ❓ 常见问题

### Q: 包名已被占用怎么办？

修改 `pyproject.toml` 中的 `name` 字段：
```toml
name = "mcp-excel-supabase-storage"  # 或其他名称
```

### Q: uvx 安装失败？

检查：
1. Python 版本 ≥ 3.9：`python --version`
2. 网络连接
3. 包名是否正确

### Q: 如何撤回已发布的版本？

PyPI 不允许删除版本，但可以"yank"（标记为不推荐）：
- 访问 PyPI 项目页面 → Manage → Yank release

---

## 📚 更多资源

- **详细发布指南**: [docs/PUBLISHING_GUIDE.md](docs/PUBLISHING_GUIDE.md)
- **API 文档**: [docs/api.md](docs/api.md)
- **开发指南**: [docs/development.md](docs/development.md)
- **故障排查**: [docs/troubleshooting.md](docs/troubleshooting.md)

---

**祝发布顺利！** 🎉

如有问题，请查看 [详细发布指南](docs/PUBLISHING_GUIDE.md) 或提交 [Issue](https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage/issues)。

