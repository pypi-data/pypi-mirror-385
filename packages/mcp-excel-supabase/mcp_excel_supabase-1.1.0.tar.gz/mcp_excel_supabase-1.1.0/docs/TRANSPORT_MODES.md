# MCP 传输模式配置指南

Excel MCP Server 支持三种传输模式，适用于不同的使用场景。

## 📋 传输模式对比

| 传输模式 | 适用场景 | 优点 | 缺点 |
|---------|---------|------|------|
| **STDIO** | Claude Desktop、命令行工具 | 简单、默认配置 | 仅限本地进程通信 |
| **HTTP** | Web 客户端、Cherry Studio | 网络访问、多客户端 | 需要配置端口 |
| **SSE** | 旧版 SSE 客户端 | 兼容性 | 已过时，推荐使用 HTTP |

## 🚀 配置方式

### 方式 1：STDIO（默认）

**适用于**：Claude Desktop、本地命令行工具

**配置示例**：

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

**特点**：
- ✅ 无需额外配置
- ✅ 自动启动和停止
- ✅ 进程隔离
- ❌ 仅限单客户端

---

### 方式 2：HTTP（推荐用于 Web 客户端）

**适用于**：Cherry Studio、Web 应用、多客户端场景

**配置示例**：

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

**连接地址**：`http://127.0.0.1:8000/mcp/`

**特点**：
- ✅ 支持网络访问
- ✅ 支持多客户端同时连接
- ✅ 完整的双向通信
- ✅ 推荐用于生产环境
- ⚠️ 需要手动管理服务器进程

**启动服务器**：

```bash
# 方式 1：通过环境变量
export MCP_TRANSPORT=http
export MCP_HOST=127.0.0.1
export MCP_PORT=8000
uvx mcp-excel-supabase

# 方式 2：在配置文件中设置（如上所示）
```

---

### 方式 3：SSE（兼容旧版客户端）

**适用于**：需要兼容旧版 SSE 客户端的场景

**配置示例**：

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

**连接地址**：`http://127.0.0.1:8000/sse`

**特点**：
- ✅ 兼容旧版客户端
- ❌ 仅支持服务器到客户端的流式传输
- ❌ 效率低于 HTTP
- ⚠️ 不推荐用于新项目

---

## 🔧 环境变量说明

| 环境变量 | 说明 | 默认值 | 可选值 |
|---------|------|--------|--------|
| `MCP_TRANSPORT` | 传输模式 | `stdio` | `stdio`, `http`, `sse` |
| `MCP_HOST` | HTTP/SSE 服务器地址 | `127.0.0.1` | 任何有效的 IP 地址 |
| `MCP_PORT` | HTTP/SSE 服务器端口 | `8000` | 1-65535 |
| `SUPABASE_URL` | Supabase 项目 URL | - | `https://yourproject.supabase.co` |
| `SUPABASE_KEY` | Supabase Service Role Key | - | 你的密钥 |

---

## 📱 Cherry Studio 配置示例

Cherry Studio 推荐使用 **HTTP 传输模式**。

### 步骤 1：启动 HTTP 服务器

创建一个启动脚本 `start-mcp-http.bat`（Windows）或 `start-mcp-http.sh`（Linux/macOS）：

**Windows (`start-mcp-http.bat`)**：
```batch
@echo off
set MCP_TRANSPORT=http
set MCP_HOST=127.0.0.1
set MCP_PORT=8000
set SUPABASE_URL=https://yourproject.supabase.co
set SUPABASE_KEY=your-service-role-key-here
uvx mcp-excel-supabase
```

**Linux/macOS (`start-mcp-http.sh`)**：
```bash
#!/bin/bash
export MCP_TRANSPORT=http
export MCP_HOST=127.0.0.1
export MCP_PORT=8000
export SUPABASE_URL=https://yourproject.supabase.co
export SUPABASE_KEY=your-service-role-key-here
uvx mcp-excel-supabase
```

### 步骤 2：运行启动脚本

```bash
# Windows
start-mcp-http.bat

# Linux/macOS
chmod +x start-mcp-http.sh
./start-mcp-http.sh
```

### 步骤 3：在 Cherry Studio 中配置

在 Cherry Studio 的 MCP 配置中添加：

```json
{
  "mcpServers": {
    "excel-supabase": {
      "url": "http://127.0.0.1:8000/mcp/"
    }
  }
}
```

或者使用命令启动方式（Cherry Studio 会自动管理进程）：

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

---

## 🐛 故障排查

### 问题 1：超时错误（Request timed out）

**原因**：首次安装时需要下载 60 个依赖包（包括 scipy 36.9MB），可能超过客户端超时限制。

**解决方案**：

1. **预先安装**（推荐）：
   ```bash
   uvx mcp-excel-supabase --help
   ```
   等待安装完成后，再在客户端中配置。

2. **使用 HTTP 模式**：
   HTTP 模式下服务器持续运行，不会每次都重新启动。

### 问题 2：端口被占用

**错误信息**：`Address already in use`

**解决方案**：

1. 更改端口：
   ```bash
   export MCP_PORT=8001  # 使用其他端口
   ```

2. 或者停止占用端口的进程：
   ```bash
   # Windows
   netstat -ano | findstr :8000
   taskkill /PID <进程ID> /F

   # Linux/macOS
   lsof -i :8000
   kill -9 <进程ID>
   ```

### 问题 3：无法连接到服务器

**检查清单**：

1. ✅ 服务器是否正在运行？
   ```bash
   # 检查进程
   ps aux | grep mcp-excel-supabase  # Linux/macOS
   tasklist | findstr python         # Windows
   ```

2. ✅ 端口是否正确？
   ```bash
   # 测试连接
   curl http://127.0.0.1:8000/mcp/
   ```

3. ✅ 防火墙是否阻止？
   - 检查防火墙设置
   - 尝试使用 `127.0.0.1` 而不是 `localhost`

---

## 💡 最佳实践

1. **开发环境**：使用 STDIO 模式，简单快速
2. **生产环境**：使用 HTTP 模式，支持多客户端
3. **Cherry Studio**：使用 HTTP 模式，避免超时问题
4. **预先安装**：首次使用前运行 `uvx mcp-excel-supabase --help` 缓存依赖
5. **日志记录**：查看服务器日志以诊断问题

---

## 📚 相关文档

- [快速开始指南](../QUICK_START.md)
- [API 参考](api.md)
- [发布指南](PUBLISHING_GUIDE.md)
- [FastMCP 官方文档](https://gofastmcp.com/deployment/running-server)

