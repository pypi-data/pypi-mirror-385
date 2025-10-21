# 🎉 Excel MCP Server v1.0.0 - Initial Release

**发布日期**: 2025-10-21

---

## ✨ 主要功能

Excel MCP Server 是一个强大的 MCP (Model Context Protocol) 服务器，提供 Excel 文件操作和 Supabase Storage 集成功能。

### 核心特性

- ✅ **Excel 解析**: 将 Excel 文件转换为 JSON，保留完整格式信息
- ✅ **Excel 生成**: 从 JSON 数据创建格式化的 Excel 文件
- ✅ **高级格式化**: 修改单元格样式、合并单元格、调整行高列宽
- ✅ **公式支持**: 执行和计算 20+ 常用 Excel 公式
  - 数学函数: SUM, AVERAGE, MAX, MIN, ROUND, ABS, POWER 等
  - 逻辑函数: IF, AND, OR, NOT 等
  - 文本函数: CONCATENATE, LEFT, RIGHT, MID, LEN 等
  - 日期函数: TODAY, NOW, DATE, YEAR, MONTH, DAY 等
  - 查找函数: VLOOKUP, HLOOKUP, INDEX, MATCH 等
- ✅ **多工作表操作**: 创建、删除、重命名、复制、移动工作表
- ✅ **文件合并**: 合并多个 Excel 文件到单个工作簿
- ✅ **Supabase 集成**: 直接读写 Supabase Storage
- ✅ **零依赖**: 无需 Microsoft Office 或 WPS
- ✅ **跨平台**: 支持 Windows、Linux、macOS

---

## 🚀 快速安装

### 方式 1: 通过 uvx（推荐）

```bash
uvx --from git+https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage mcp-excel-supabase
```

### 方式 2: 通过 pip

```bash
pip install git+https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage
```

### 方式 3: 克隆仓库

```bash
git clone https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage
cd Excel-MCP-Server-with-Supabase-Storage
pip install -e .
```

---

## 🔧 Claude Desktop 配置

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

重启 Claude Desktop 即可使用。

---

## 📦 包含的 MCP 工具

本版本提供 **12 个 MCP 工具**：

| 工具 | 功能描述 |
|------|----------|
| `parse_excel_to_json` | 解析 Excel 文件为 JSON 格式 |
| `create_excel_from_json` | 从 JSON 数据生成 Excel 文件 |
| `modify_cell_format` | 修改单元格格式（字体、颜色、边框等） |
| `merge_cells` | 合并单元格范围 |
| `unmerge_cells` | 取消合并单元格 |
| `set_row_heights` | 设置行高 |
| `set_column_widths` | 设置列宽 |
| `manage_storage` | 管理 Supabase Storage（上传/下载/列表/删除） |
| `set_formula` | 设置单元格公式 |
| `recalculate_formulas` | 重新计算工作簿中的所有公式 |
| `manage_sheets` | 管理工作表（创建/删除/重命名/复制/移动） |
| `merge_excel_files` | 合并多个 Excel 文件 |

详细 API 文档: [docs/api.md](https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage/blob/main/docs/api.md)

---

## 📊 性能指标

在标准开发机器上的性能测试结果（Intel i5, 8GB RAM）：

| 操作 | 目标性能 | 实际性能 | 状态 |
|------|----------|----------|------|
| 解析 1MB Excel 文件 | < 2 秒 | **0.598 秒** | ✅ **3.3x 更快** |
| 生成 1000 行数据 | < 3 秒 | **0.026 秒** | ✅ **115x 更快** |
| 合并 10 个文件 | < 8 秒 | **0.117 秒** | ✅ **68x 更快** |
| 批量处理 20 个文件 | < 10 秒 | **0.192 秒** | ✅ **52x 更快** |
| 格式化 1000 个单元格 | < 0.5 秒 | **0.089 秒** | ✅ **5.6x 更快** |

### 性能优化特性

- ✅ LRU 缓存（128 条目）
- ✅ 线程池并发（8 个工作线程）
- ✅ 流式 I/O 处理大文件
- ✅ 内存高效（5000 行仅增加 0.04MB）

---

## 📚 文档资源

- **[README](https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage/blob/main/README.md)** - 项目概述和快速开始
- **[API 文档](https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage/blob/main/docs/api.md)** - 完整的 API 参考
- **[使用示例](https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage/tree/main/docs/examples)** - 6 个端到端示例
  - 基础解析
  - Excel 生成
  - 单元格格式化
  - 公式操作
  - 文件合并
  - Supabase 集成
- **[架构设计](https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage/blob/main/docs/architecture.md)** - 系统架构和设计模式
- **[开发指南](https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage/blob/main/docs/development.md)** - 贡献和开发流程
- **[故障排查](https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage/blob/main/docs/troubleshooting.md)** - 常见问题和解决方案
- **[发布指南](https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage/blob/main/docs/PUBLISHING_GUIDE.md)** - 发布和部署指南

---

## 🧪 测试覆盖率

- **单元测试**: 100+ 测试用例
- **代码覆盖率**: 平均 90%+
  - Excel 模块: 87-100%
  - Storage 模块: 95%
  - Utils 模块: 96-100%
- **代码质量**: 
  - Ruff lint: A 级
  - Black 格式化: 100% 通过
  - mypy 类型检查: 无错误

---

## 🔒 安全性

- ✅ 依赖安全扫描（pip-audit）
- ✅ 无已知高危漏洞
- ✅ 环境变量隔离（`.env` 文件）
- ✅ 安全策略文档（[SECURITY.md](https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage/blob/main/SECURITY.md)）

---

## 🐛 已知问题

无已知严重问题。

如发现问题，请提交 [Issue](https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage/issues)。

---

## 🗺️ 未来计划

### v1.1 (计划中)

- 📋 图表生成支持
- 📋 条件格式化
- 📋 数据验证规则
- 📋 更多高级公式函数
- 📋 WebUI 控制面板

---

## 🙏 致谢

感谢以下开源项目：

- [openpyxl](https://openpyxl.readthedocs.io/) - Excel 文件操作
- [Supabase](https://supabase.com/) - 云存储后端
- [MCP Protocol](https://modelcontextprotocol.io/) - Model Context Protocol
- [formulas](https://github.com/vinci1it2000/formulas) - Excel 公式引擎

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage/blob/main/LICENSE) 文件。

---

## 📞 支持

- **问题反馈**: [GitHub Issues](https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage/issues)
- **讨论交流**: [GitHub Discussions](https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage/discussions)
- **邮箱**: hikaru_lamperouge@163.com

---

**完整变更日志**: [CHANGELOG.md](https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage/blob/main/CHANGELOG.md)

---

**感谢使用 Excel MCP Server！** 🎉

如果觉得这个项目有帮助，请给我们一个 ⭐ Star！

