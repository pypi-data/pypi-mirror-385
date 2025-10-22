# Excel MCP Server with Supabase Storage - 详细开发计划

**项目名称：** Excel MCP Server with Supabase Storage  
**版本：** 1.0.0  
**创建时间：** 2025-10-17  
**最后更新：** 2025-10-20

---

## 📊 项目概述

### 项目目标
开发一个基于 Model Context Protocol (MCP) 的 Excel 操作服务器，集成 Supabase Storage 云存储功能，实现无需 Microsoft Office/WPS 的 Excel 文件处理能力。

### 核心功能（8个）
1. **F1 - Excel 解析为 JSON**（P0）：将 xlsx 文件转换为包含完整格式信息的 JSON
2. **F2 - JSON 生成 Excel**（P0）：从 JSON 创建格式化的 Excel 文件
3. **F3 - 单元格格式编辑**（P1）：修改字体、颜色、尺寸、合并单元格
4. **F4 - Excel 公式执行**（P1）：支持 20+ 常用公式的计算
5. **F5 - 多 Sheet 操作**（P0）：支持多工作表管理和文件合并
6. **F6 - Supabase Storage 集成**（P0）：云存储读写操作
7. **F7 - 独立运行**（P0）：无需 Microsoft Office/WPS
8. **F8 - UVX 安装方式**（P0）：支持 uvx 一键安装

### MCP 工具（12个）
1. `parse_excel_to_json` - 解析 Excel 为 JSON
2. `create_excel_from_json` - 从 JSON 创建 Excel
3. `modify_cell_format` - 修改单元格格式
4. `merge_cells` - 合并单元格
5. `unmerge_cells` - 取消合并
6. `set_row_heights` - 设置行高
7. `set_column_widths` - 设置列宽
8. `set_formula` - 设置公式
9. `recalculate_formulas` - 重新计算公式
10. `merge_excel_files` - 合并 Excel 文件
11. `manage_sheets` - 管理工作表
12. `manage_storage` - 管理云存储

### 技术栈
- **语言：** Python >= 3.9
- **核心库：** openpyxl, supabase-py, mcp, formulas, pydantic
- **测试：** pytest, pytest-asyncio, pytest-cov
- **代码质量：** black, ruff, mypy
- **部署：** uvx, PyPI

---

## 🗓️ 开发阶段规划

### ✅ 阶段 0：项目初始化（已完成）
**目标：** 搭建项目基础框架

**任务清单：**
- ✅ 从 GitHub 同步文档（README, PRD, LICENSE 等）
- ✅ 创建完整目录结构（src, tests, docs, .github）
- ✅ 创建配置文件（pyproject.toml, requirements.txt, .env）
- ✅ 创建 Python 虚拟环境
- ✅ 安装所有依赖（58 个包）
- ✅ 创建包初始化文件（__init__.py × 5）
- ✅ 验证环境配置

**交付物：**
- ✅ 完整的项目结构
- ✅ 可用的开发环境
- ✅ 配置文件齐全
- ✅ 阶段完成报告

**验收标准：**
- ✅ 所有依赖安装成功
- ✅ 包可正常导入
- ✅ 环境变量配置正确

---

### ✅ 阶段 1：基础设施（已完成）
**目标：** 创建核心工具类和基础框架

**任务清单：**
- ✅ 创建自定义异常类（`utils/errors.py`）
  - ✅ 定义错误代码体系（E001-E502）
  - ✅ 实现异常类层次结构
  - ✅ 添加错误消息模板
- ✅ 创建日志工具（`utils/logger.py`）
  - ✅ 配置日志格式和级别
  - ✅ 实现文件和控制台输出
  - ✅ 添加日志轮转功能
- ✅ 创建输入验证工具（`utils/validator.py`）
  - ✅ 实现文件路径验证
  - ✅ 实现参数类型验证
  - ✅ 实现数据范围验证
- ✅ 创建测试框架（`tests/conftest.py`）
  - ✅ 配置 pytest fixtures
  - ✅ 创建测试数据生成器
  - ✅ 配置测试环境
- ✅ 配置 CI/CD（`.github/workflows/ci.yml`）
  - ✅ 配置自动化测试
  - ✅ 配置代码质量检查
  - ✅ 配置安全审计

**交付物：**
- ✅ `src/mcp_excel_supabase/utils/errors.py`
- ✅ `src/mcp_excel_supabase/utils/logger.py`
- ✅ `src/mcp_excel_supabase/utils/validator.py`
- ✅ `tests/conftest.py`
- ✅ `.github/workflows/ci.yml`
- ✅ 单元测试（覆盖率 96% ≥ 80%）

**验收标准：**
- ✅ 所有工具类功能正常
- ✅ 测试框架可用
- ✅ CI/CD 流程运行成功

---

### ✅ 阶段 2：Supabase 集成（已完成）
**目标：** 实现云存储功能（F6）

**任务清单：**
- ✅ 创建 Supabase 客户端（`storage/client.py`）
  - ✅ 初始化 Supabase 连接
  - ✅ 实现连接池管理
  - ✅ 添加重试机制
- ✅ 实现文件上传功能（`storage/uploader.py`）
  - ✅ 单文件上传
  - ✅ 批量文件上传
  - ✅ 上传进度跟踪
- ✅ 实现文件下载功能（`storage/downloader.py`）
  - ✅ 单文件下载
  - ✅ 批量文件下载
  - ✅ 断点续传支持
- ✅ 实现文件管理功能（`storage/manager.py`）
  - ✅ 列出文件
  - ✅ 删除文件
  - ✅ 搜索文件
  - ✅ 获取文件元数据

**交付物：**
- ✅ `src/mcp_excel_supabase/storage/client.py`
- ✅ `src/mcp_excel_supabase/storage/uploader.py`
- ✅ `src/mcp_excel_supabase/storage/downloader.py`
- ✅ `src/mcp_excel_supabase/storage/manager.py`
- ✅ 单元测试（56个测试，覆盖率 95%）
- ✅ 性能测试和报告

**验收标准：**
- ✅ 上传/下载功能正常
- ✅ 错误处理完善
- ✅ 性能符合要求（单文件 < 2s）

---

### ✅ 阶段 3：Excel 解析功能（已完成）
**目标：** 实现 Excel 到 JSON 的转换（F1）

**任务清单：**
- ✅ 创建 Excel 解析器（`excel/parser.py`）
  - ✅ 解析工作表结构
  - ✅ 解析单元格数据
  - ✅ 解析单元格格式
  - ✅ 解析合并单元格
  - ✅ 解析行高列宽
- ✅ 创建 JSON 模式定义（`excel/schemas.py`）
  - ✅ 定义 Cell 模型
  - ✅ 定义 Row 模型
  - ✅ 定义 Sheet 模型
  - ✅ 定义 Workbook 模型
- ✅ 实现格式提取（`excel/format_extractor.py`）
  - ✅ 提取字体信息
  - ✅ 提取颜色信息
  - ✅ 提取边框信息
  - ✅ 提取对齐方式

**交付物：**
- ✅ `src/mcp_excel_supabase/excel/parser.py`
- ✅ `src/mcp_excel_supabase/excel/schemas.py`
- ✅ `src/mcp_excel_supabase/excel/format_extractor.py`
- ✅ 单元测试（覆盖率 ≥ 80%）
- ✅ 测试用例（至少 10 个不同格式的 Excel 文件）

**验收标准：**
- ✅ 解析准确率 100%
- ✅ 格式信息完整
- ✅ 性能：1MB 文件 < 2s

---

### ✅ 阶段 4：Excel 生成功能（已完成）
**目标：** 实现 JSON 到 Excel 的转换（F2）

**任务清单：**
- ✅ 创建 Excel 生成器（`excel/generator.py`）
  - ✅ 创建工作簿和工作表
  - ✅ 写入单元格数据
  - ✅ 应用单元格格式
  - ✅ 应用合并单元格
  - ✅ 设置行高列宽
- ✅ 实现格式应用（`excel/format_applier.py`）
  - ✅ 应用字体格式
  - ✅ 应用颜色格式
  - ✅ 应用边框格式
  - ✅ 应用对齐方式
- ✅ 实现数据验证（`excel/data_validator.py`）
  - ✅ 验证 JSON 结构
  - ✅ 验证数据类型
  - ✅ 验证格式参数

**交付物：**
- ✅ `src/mcp_excel_supabase/excel/generator.py`
- ✅ `src/mcp_excel_supabase/excel/format_applier.py`
- ✅ `src/mcp_excel_supabase/excel/data_validator.py`
- ✅ 单元测试（覆盖率 87% ≥ 80%）
- ✅ 往返测试（Excel → JSON → Excel）

**验收标准：**
- ✅ 生成的 Excel 格式正确
- ✅ 格式还原度 100%
- ✅ 性能：1000 行 0.08s < 3s

---

### ✅ 阶段 5：格式编辑功能（已完成）
**目标：** 实现单元格格式编辑（F3）

**任务清单：**
- ✅ 创建格式编辑器（`excel/format_editor.py`）
  - ✅ 修改字体（名称、大小、颜色、粗体、斜体）
  - ✅ 修改背景色
  - ✅ 修改边框
  - ✅ 修改对齐方式
  - ✅ 修改数字格式
- ✅ 实现单元格合并（`excel/cell_merger.py`）
  - ✅ 合并单元格
  - ✅ 取消合并
  - ✅ 验证合并范围
- ✅ 实现行列调整（`excel/dimension_adjuster.py`）
  - ✅ 设置行高
  - ✅ 设置列宽
  - ✅ 自动调整尺寸

**交付物：**
- ✅ `src/mcp_excel_supabase/excel/format_editor.py`
- ✅ `src/mcp_excel_supabase/excel/cell_merger.py`
- ✅ `src/mcp_excel_supabase/excel/dimension_adjuster.py`
- ✅ 单元测试（覆盖率 98.7% ≥ 80%）

**验收标准：**
- ✅ 所有格式编辑功能正常
- ✅ 不破坏现有数据
- ✅ 支持批量操作

---

### ✅ 阶段 6：MCP 服务器集成（已完成）
**目标：** 实现 MCP 协议集成和基础工具

**任务清单：**
- [x] 创建 MCP 服务器（`server.py`）
  - [x] 初始化 MCP 服务器
  - [x] 注册工具
  - [x] 实现请求处理
  - [x] 实现错误处理
- [x] 实现基础 MCP 工具
  - [x] `parse_excel_to_json` - 解析工具
  - [x] `create_excel_from_json` - 生成工具
  - [x] `modify_cell_format` - 格式编辑工具
  - [x] `merge_cells` - 合并工具
  - [x] `unmerge_cells` - 取消合并工具
  - [x] `set_row_heights` - 行高工具
  - [x] `set_column_widths` - 列宽工具
  - [x] `manage_storage` - 存储管理工具
- [x] 创建工具模式定义（`tools/schemas.py`）
  - [x] 定义输入参数模式
  - [x] 定义输出结果模式
  - [x] 添加参数验证

**交付物：**
- [x] `src/mcp_excel_supabase/server.py`
- [x] `src/mcp_excel_supabase/tools/` 目录
- [x] 8 个 MCP 工具实现
- [x] 集成测试（含手动冒烟与 Supabase E2E）

**验收标准：**
- [x] MCP 服务器正常启动
- [x] 所有工具可调用
- [x] 参数验证正确

---

### 阶段 7：公式引擎集成 ✅ 已完成
**目标：** 实现 Excel 公式执行（F4）

**任务清单：**
- [x] 创建公式引擎包装器（`excel/formula_engine.py`）
  - [x] 集成 formulas 库
  - [x] 实现公式解析
  - [x] 实现公式计算
  - [x] 处理循环引用
- [x] 实现公式管理（`excel/formula_manager.py`）
  - [x] 设置单元格公式
  - [x] 批量重新计算
  - [x] 公式依赖分析
- [x] 支持常用公式（20+）
  - [x] 数学函数（SUM, AVERAGE, MAX, MIN, ROUND 等）
  - [x] 逻辑函数（IF, AND, OR, NOT 等）
  - [x] 文本函数（CONCATENATE, LEFT, RIGHT, MID 等）
  - [x] 日期函数（TODAY, NOW, DATE, YEAR 等）
  - [x] 查找函数（VLOOKUP, HLOOKUP, INDEX, MATCH 等）
- [x] 实现 MCP 工具
  - [x] `set_formula` - 设置公式工具
  - [x] `recalculate_formulas` - 重新计算工具

**交付物：**
- [x] `src/mcp_excel_supabase/excel/formula_engine.py`
- [x] `src/mcp_excel_supabase/excel/formula_manager.py`
- [x] 2 个 MCP 工具实现
- [x] 公式测试用例（覆盖 20+ 函数）

**验收标准：**
- [x] 支持 20+ 常用公式
- [x] 计算结果准确
- [x] 错误处理完善

---

### ✅ 阶段 8：Sheet 管理功能（已完成）
**目标：** 实现多工作表操作和文件合并（F5）

**任务清单：**
- [x] 创建 Sheet 管理器（`excel/sheet_manager.py`）
  - [x] 创建工作表
  - [x] 删除工作表
  - [x] 重命名工作表
  - [x] 复制工作表
  - [x] 移动工作表
- [x] 实现文件合并（`excel/file_merger.py`）
  - [x] 合并多个 Excel 文件
  - [x] 保留格式信息
  - [x] 处理重名工作表
  - [x] 支持选择性合并
- [x] 实现 MCP 工具
  - [x] `manage_sheets` - 工作表管理工具
  - [x] `merge_excel_files` - 文件合并工具

**交付物：**
- [x] `src/mcp_excel_supabase/excel/sheet_manager.py`
- [x] `src/mcp_excel_supabase/excel/file_merger.py`
- [x] 2 个 MCP 工具实现
- [x] 单元测试（覆盖率 98-100% ≥ 80%）

**验收标准：**
- [x] 所有 Sheet 操作正常
- [x] 合并功能正确
- [x] 性能：合并 10 个文件 0.69s < 8s（快11.6倍）

---

### ✅ 阶段 9：性能优化（已完成）
**目标：** 优化性能以满足需求

**任务清单：**
- [x] 实现流式处理（`excel/stream_processor.py`）
  - [x] 大文件分块读取
  - [x] 流式写入
  - [x] 内存使用优化
- [x] 实现并发处理（`utils/concurrency.py`）
  - [x] 批量操作并发化
  - [x] 线程池管理
  - [x] 异步 I/O 优化
- [x] 实现缓存机制（`utils/cache.py`）
  - [x] 解析结果缓存
  - [x] 格式信息缓存
  - [x] LRU 缓存策略
- [x] 性能测试和调优
  - [x] 基准测试
  - [x] 性能分析
  - [x] 瓶颈优化

**交付物：**
- [x] `src/mcp_excel_supabase/excel/stream_processor.py`
- [x] `src/mcp_excel_supabase/utils/concurrency.py`
- [x] `src/mcp_excel_supabase/utils/cache.py`
- [x] 性能测试报告

**验收标准：**
- [x] 单文件（1MB）解析 0.598s < 2s（快3.3倍）
- [x] 批量（20 个）解析 0.192s < 10s（快52倍）
- [x] 生成 1000 行 0.026s < 3s（快115倍）
- [x] 合并 10 个文件 0.117s < 8s（快68倍）
- [x] 内存峰值 0.04MB增长 < 500MB（低12500倍）

---

### ✅ 阶段 10：错误处理完善（已完成）
**目标：** 完善错误处理和日志记录

**任务清单：**
- [x] 完善异常处理
  - [x] 统一错误码体系
  - [x] 添加错误上下文
  - [x] 实现错误恢复
- [x] 完善日志记录
  - [x] 添加操作审计日志
  - [x] 添加性能日志
  - [x] 添加错误追踪
- [x] 实现监控和告警
  - [x] 性能监控
  - [x] 错误率监控
  - [x] 资源使用监控
- [x] 编写故障排查文档

**交付物：**
- [x] 完善的错误处理系统
- [x] 完整的日志记录
- [x] 监控仪表板
- [x] 故障排查文档

**验收标准：**
- [x] 所有错误有明确错误码
- [x] 日志信息完整
- [x] 监控指标准确

---

### 阶段 11：文档完善 ✅ 已完成
**目标：** 完善项目文档

**任务清单：**
- [x] 编写 API 文档（`docs/api.md`）
  - [x] 所有 MCP 工具文档
  - [x] 参数说明
  - [x] 返回值说明
  - [x] 错误码说明
- [x] 编写使用示例（`docs/examples/`）
  - [x] 基础用法示例
  - [x] 高级用法示例
  - [x] 端到端示例（至少 5 个）
- [x] 编写架构文档（`docs/architecture.md`）
  - [x] 系统架构图
  - [x] 模块关系图
  - [x] 数据流图
- [x] 编写开发文档（`docs/development.md`）
  - [x] 开发环境搭建
  - [x] 代码规范
  - [x] 测试指南
  - [x] 贡献指南
- [x] 编写故障排查文档（`docs/troubleshooting.md`）
  - [x] 常见问题
  - [x] 错误码对照表
  - [x] 解决方案

**交付物：**
- [x] `docs/api.md`
- [x] `docs/examples/` 目录（6 个示例）
- [x] `docs/architecture.md`
- [x] `docs/development.md`
- [x] `docs/troubleshooting.md`（阶段10已完成）
- [x] 更新 README.md

**验收标准：**
- [x] API 文档覆盖所有工具
- [x] 至少 5 个端到端示例（实际6个）
- [x] 架构图清晰（4个Mermaid图表）
- [x] 文档无错误

---

### 阶段 12：发布准备 ✅ 已完成
**目标：** 准备正式发布 v1.0.0

**任务清单：**
- [x] 创建 PyPI 包
  - [x] 配置 pyproject.toml
  - [x] 配置 MANIFEST.in
  - [x] 构建分发包
  - [ ] 上传到 PyPI（待用户确认）
- [x] 配置 UVX 支持
  - [x] 验证 uvx 配置
  - [x] 测试 uvx 安装
  - [x] 编写 uvx 使用文档
- [x] 跨平台测试
  - [x] Windows 测试
  - [x] Linux 测试（GitHub Actions）
  - [x] macOS 测试（GitHub Actions）
- [x] 安全审计
  - [x] 依赖安全扫描
  - [x] 代码安全审查
  - [x] 创建 SECURITY.md
- [x] 发布准备
  - [x] 创建 CHANGELOG.md
  - [x] 准备 GitHub Release
  - [x] 编写发布说明

**交付物：**
- [x] PyPI 包（已构建，待发布）
- [x] UVX 配置和文档
- [x] 跨平台测试报告
- [x] 安全审计报告
- [x] CHANGELOG.md
- [x] GitHub Release v1.0.0（待创建）

**验收标准：**
- [x] PyPI 包构建成功
- [x] UVX 配置完成
- [x] Windows 测试通过
- [x] 无高危安全漏洞
- [x] 文档完整

---

## 🎯 里程碑

### M1：MVP 完成（阶段 0-4）
**目标：** 基础功能可用
- ✅ 阶段 0：项目初始化
- [ ] 阶段 1：基础设施
- [ ] 阶段 2：Supabase 集成
- [ ] 阶段 3：Excel 解析
- [ ] 阶段 4：Excel 生成

**交付物：**
- [ ] 可解析和生成 Excel 文件
- [ ] 可上传下载到 Supabase
- [ ] 基础测试通过

### M2：功能完整（阶段 5-8）
**目标：** 所有核心功能实现
- [ ] 阶段 5：格式编辑
- [ ] 阶段 6：MCP 集成
- [ ] 阶段 7：公式引擎
- [ ] 阶段 8：Sheet 管理

**交付物：**
- [ ] 12 个 MCP 工具全部实现
- [ ] 8 个核心功能全部可用
- [ ] 集成测试通过

### M3：生产就绪（阶段 9-12）
**目标：** 可正式发布
- [ ] 阶段 9：性能优化
- [ ] 阶段 10：错误处理
- [ ] 阶段 11：文档完善
- [ ] 阶段 12：发布准备

**交付物：**
- [ ] 性能达标
- [ ] 文档完整
- [ ] PyPI 发布
- [ ] v1.0.0 Release

---

## 📊 验收标准总览

### 功能验收
- [ ] 8 个核心功能 100% 实现
- [ ] 12 个 MCP 工具正常工作

### 性能验收
- [ ] 单文件（1MB）解析 < 2 秒
- [ ] 批量（20 个）解析 < 10 秒
- [ ] 生成 1000 行 < 3 秒
- [ ] 合并 10 个文件 < 8 秒
- [ ] 内存峰值 < 500MB

### 质量验收
- [ ] 单元测试覆盖率 ≥ 80%
- [ ] 集成测试通过率 100%
- [ ] Ruff lint 评分 A 级
- [ ] mypy 类型检查无错误

### 文档验收
- [ ] README 完整
- [ ] API 文档覆盖所有工具
- [ ] 至少 5 个端到端示例
- [ ] 架构图清晰

---

## 📝 备注

### 优先级调整
根据用户要求，阶段 5（格式编辑）和阶段 6（MCP 集成）已调换顺序，确保格式编辑功能开发完成后再进行 MCP 服务器集成。

### 开发模式
- 按阶段逐步开发
- 每阶段完成后进行测试
- 等待用户确认后继续下一阶段
- 所有依赖安装在项目本地环境

### Supabase 配置
- URL: `https://aimilmguliansaycjecy.supabase.co`
- 测试 Bucket: `WeeklyReport_on_Zero-CarbonParkConstruction`
- Service Role Key: 已配置

### 测试数据
- 用户提供测试 Excel 文件在 `test-excel/` 目录
- 每个阶段使用实际测试数据验证

---

**计划创建时间：** 2025-10-17  
**计划版本：** 1.0  
**最后更新：** 2025-10-20

