# SSE/HTTP 传输支持说明

## ✅ 已实现功能

Excel MCP Server 现已支持三种传输模式：

1. **STDIO**（默认）- 标准输入/输出
2. **HTTP** - HTTP 传输（推荐用于 Web 客户端）
3. **SSE** - Server-Sent Events（兼容旧版客户端）

## 🔧 实现细节

### 代码修改

修改了 `src/mcp_excel_supabase/server.py` 的 `main()` 函数：

```python
def main() -> None:
    """MCP 服务器主入口函数
    
    支持通过环境变量配置传输方式：
    - MCP_TRANSPORT: 传输方式 (stdio|http|sse)，默认 stdio
    - MCP_HOST: HTTP/SSE 服务器地址，默认 127.0.0.1
    - MCP_PORT: HTTP/SSE 服务器端口，默认 8000
    """
    import os
    
    # 读取传输配置
    transport = os.getenv("MCP_TRANSPORT", "stdio").lower()
    host = os.getenv("MCP_HOST", "127.0.0.1")
    port = int(os.getenv("MCP_PORT", "8000"))
    
    logger.info(f"启动 Excel-Supabase MCP 服务器 (传输方式: {transport})")
    
    # 根据传输方式启动服务器
    if transport == "stdio":
        mcp.run()
    elif transport == "http":
        logger.info(f"HTTP 服务器地址: http://{host}:{port}/mcp/")
        mcp.run(transport="http", host=host, port=port)
    elif transport == "sse":
        logger.info(f"SSE 服务器地址: http://{host}:{port}/sse")
        mcp.run(transport="sse", host=host, port=port)
    else:
        logger.error(f"不支持的传输方式: {transport}")
        logger.error("支持的传输方式: stdio, http, sse")
        raise ValueError(f"不支持的传输方式: {transport}")
```

### 环境变量

| 变量名 | 说明 | 默认值 | 示例 |
|--------|------|--------|------|
| `MCP_TRANSPORT` | 传输模式 | `stdio` | `http`, `sse`, `stdio` |
| `MCP_HOST` | 服务器地址 | `127.0.0.1` | `0.0.0.0`, `localhost` |
| `MCP_PORT` | 服务器端口 | `8000` | `8080`, `3000` |

## 📚 使用示例

### 1. STDIO 模式（默认）

```bash
# 不需要设置环境变量
uvx mcp-excel-supabase
```

或在配置文件中：

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

### 2. HTTP 模式

```bash
# 通过环境变量
export MCP_TRANSPORT=http
export MCP_HOST=127.0.0.1
export MCP_PORT=8000
uvx mcp-excel-supabase
```

或在配置文件中：

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

### 3. SSE 模式

```bash
# 通过环境变量
export MCP_TRANSPORT=sse
export MCP_HOST=127.0.0.1
export MCP_PORT=8000
uvx mcp-excel-supabase
```

或在配置文件中：

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

## 🎯 Cherry Studio 配置

Cherry Studio 推荐使用 **HTTP 传输模式**。

### 方式 1：自动启动（推荐）

Cherry Studio 会自动管理服务器进程：

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

### 方式 2：手动启动

1. 使用提供的启动脚本：
   - Windows: `examples/start-http-server.bat`
   - Linux/macOS: `examples/start-http-server.sh`

2. 在 Cherry Studio 中配置 URL：
   ```json
   {
     "mcpServers": {
       "excel-supabase": {
         "url": "http://127.0.0.1:8000/mcp/"
       }
     }
   }
   ```

## 🐛 故障排查

### 问题 1：超时错误

**症状**：
```
Error invoking remote method 'mcp:list-tools': Error: [MCP] Error activating server MCP 服务器: MCP error -32001: Request timed out
```

**原因**：首次安装需要下载依赖包（约 60 个，包括 scipy 36.9MB）

**解决方案**：

1. **预先安装**（推荐）：
   ```bash
   uvx mcp-excel-supabase --help
   ```
   等待安装完成后再配置客户端。

2. **使用 HTTP 模式**：
   HTTP 模式下服务器持续运行，避免每次启动都重新安装。

### 问题 2：端口被占用

**症状**：
```
Address already in use
```

**解决方案**：

1. 更改端口：
   ```bash
   export MCP_PORT=8001
   ```

2. 或停止占用端口的进程：
   ```bash
   # Windows
   netstat -ano | findstr :8000
   taskkill /PID <进程ID> /F

   # Linux/macOS
   lsof -i :8000
   kill -9 <进程ID>
   ```

### 问题 3：无法连接

**检查清单**：

1. ✅ 服务器是否运行？
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

## 📝 更新日志

### v1.0.1（计划中）

- ✅ 添加 HTTP 传输支持
- ✅ 添加 SSE 传输支持
- ✅ 通过环境变量配置传输模式
- ✅ 创建启动脚本示例
- ✅ 更新文档

## 🔗 相关资源

- [传输模式配置指南](TRANSPORT_MODES.md)
- [快速开始指南](../QUICK_START.md)
- [FastMCP 官方文档](https://gofastmcp.com/deployment/running-server)
- [MCP 协议规范](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports)

## 💡 最佳实践

1. **开发环境**：使用 STDIO 模式（默认）
2. **生产环境**：使用 HTTP 模式
3. **Cherry Studio**：使用 HTTP 模式，避免超时
4. **预先安装**：首次使用前运行 `uvx mcp-excel-supabase --help`
5. **日志记录**：查看服务器日志诊断问题

## 🤝 贡献

如果你发现问题或有改进建议，欢迎：

1. 提交 Issue
2. 创建 Pull Request
3. 在 Discord 社区讨论

---

**注意**：此功能基于 FastMCP 框架实现，感谢 FastMCP 团队的出色工作！

