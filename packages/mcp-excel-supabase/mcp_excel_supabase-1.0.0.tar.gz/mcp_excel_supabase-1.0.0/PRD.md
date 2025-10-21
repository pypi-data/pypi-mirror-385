# 产品需求文档 (PRD)
## Excel MCP Server - Supabase Storage Integration

**版本**: v1.0  
**日期**: 2025-10-17  
**项目经理**: Product Manager  
**状态**: 待开发

---

## 📋 目录

1. [项目概述](#1-项目概述)
2. [用户画像与场景](#2-用户画像与场景)
3. [功能需求](#3-功能需求)
4. [技术约束与建议](#4-技术约束与建议)
5. [项目计划](#5-项目计划)
6. [验收标准](#6-验收标准总结)
7. [附录](#7-附录)

---

## 1. 项目概述

### 1.1 项目名称
**Excel MCP Server with Supabase Storage**

### 1.2 项目背景
随着AI辅助开发工具（如Claude）的普及，开发者需要一个强大的Excel处理能力来自动化数据处理任务。当前市场缺少一个能够：
- ✅ 无需本地Excel/WPS软件
- ✅ 深度集成云存储(Supabase)
- ✅ 提供完整格式控制
- ✅ 支持MCP协议的Excel处理工具

### 1.3 业务目标
1. **主要目标**: 为MCP生态提供企业级Excel处理能力
2. **次要目标**: 简化云端Excel文件的读写操作流程
3. **长期愿景**: 成为MCP生态中标准的表格处理解决方案

### 1.4 成功指标
- 安装成功率 > 95%
- Excel格式保真度 > 99%
- API响应时间 < 2秒(单文件<1MB)
- GitHub Stars > 100 (6个月内)
- 文档完整度评分 > 4.5/5
- 首位用户(项目发起人)满意度 = 100%

### 1.5 项目约束（已确认）
- **文件规模**: 最多同时处理20个Excel文档，每个≤1MB
- **Supabase配置**: 用户具有Storage API访问权限，无需特殊bucket权限设置
- **错误策略**: 遇到不支持的功能或错误时，抛出明确错误并终止操作
- **开源协议**: MIT License（便于商业和个人使用）
- **第一用户**: 项目发起人将作为Alpha测试用户提供迭代反馈

---

## 2. 用户画像与场景

### 2.1 目标用户
**主要用户**: AI辅助开发工程师
- 使用Claude等AI工具进行自动化开发
- 需要处理批量Excel数据（≤20个文件/批次）
- 熟悉命令行工具和Python生态
- 使用Supabase作为云存储后端

**次要用户**: 数据分析师/自动化脚本开发者
- 需要批量处理小型Excel文件
- 使用云存储管理数据资产
- 追求无GUI的自动化解决方案

### 2.2 核心使用场景

#### 场景1: 批量数据迁移与格式转换
**角色**: 数据工程师（项目发起人）  
**目标**: 将Supabase中的多个Excel报表转换为JSON进行数据分析  
**前置条件**: 
- Supabase Storage中存储了≤20个Excel文件
- 每个文件≤1MB
- 文件包含复杂格式（颜色、字体、合并单元格）

**流程**: 
```
用户通过MCP → 指定storage bucket → 批量解析xlsx → 
输出JSON（包含完整格式信息）→ 导入数据处理流程
```

**成功标准**:
- 所有文件在10秒内完成解析
- 格式信息完整保留（字体、颜色、尺寸）
- JSON结构清晰易于后续处理

#### 场景2: 自动化报表生成
**角色**: 业务分析师  
**目标**: 根据JSON数据生成格式化的Excel报表  
**流程**:
```
数据处理系统 → 生成JSON数据 → MCP生成格式化Excel → 
上传至Supabase → 通知相关人员下载
```

**成功标准**:
- Excel格式完全符合企业规范（指定字体、颜色）
- 公式自动计算（如SUM、AVERAGE）
- 文件可在无Office软件环境下生成

#### 场景3: 多源数据合并
**角色**: 项目经理  
**目标**: 合并各部门的周报Excel为单一工作簿  
**流程**:
```
读取5-10个xlsx文件 → MCP合并为多sheet工作簿 → 
统一格式（标题字体、列宽）→ 生成汇总报表
```

**成功标准**:
- 每个文件成为独立sheet
- Sheet名称可自定义
- 原有格式保持不变

### 2.3 用户痛点（已验证）
1. ❌ 现有工具（xlwings）依赖本地Office软件
2. ❌ pandas读取Excel后格式信息丢失
3. ❌ 云存储集成需要额外编写boto3/supabase代码
4. ❌ 安装配置流程复杂（需要配置环境变量、路径）
5. ❌ 无MCP协议支持，无法与Claude等AI工具直接集成

---

## 3. 功能需求

### 3.1 核心功能

#### 【P0】F1: Excel文件解析为JSON

**功能描述**  
将单个或多个xlsx文件（最多20个，每个≤1MB）解析为结构化JSON，包含完整的格式信息。

**用户故事**
```
作为 项目发起人（第一用户）
我想要 批量解析Excel文件为JSON
以便于 在Python脚本中处理表格数据和格式信息
```

**验收标准**
- ✅ 支持.xlsx格式(Excel 2007+)
- ✅ 支持批量解析（1-20个文件）
- ✅ 单次批量操作时间 < 10秒（20个文件，每个1MB）
- ✅ 从Supabase Storage读取文件（通过文件名）
- ✅ 输出JSON包含以下完整信息:

**JSON输出格式规范**:
```json
{
  "filename": "sales_report.xlsx",
  "file_size_kb": 245,
  "parsed_at": "2025-10-17T10:30:00Z",
  "sheets": [
    {
      "name": "Q1销售",
      "index": 0,
      "dimensions": {
        "rows": 100,
        "cols": 10,
        "used_range": "A1:J100"
      },
      "column_widths": [15.5, 20.0, 12.0, ...],
      "row_heights": [25.0, 18.75, 18.75, ...],
      "merged_cells": [
        {"range": "A1:B1", "value": "销售总额"},
        {"range": "C1:D1", "value": "利润"}
      ],
      "cells": [
        {
          "address": "A1",
          "row": 1,
          "col": 1,
          "value": "销售总额",
          "type": "string",
          "formula": null,
          "font": {
            "name": "微软雅黑",
            "size": 12,
            "color": "#FF0000",
            "bold": true,
            "italic": false,
            "underline": "none"
          },
          "fill": {
            "type": "solid",
            "color": "#FFFF00"
          },
          "alignment": {
            "horizontal": "center",
            "vertical": "middle",
            "wrap_text": true,
            "indent": 0
          },
          "border": {
            "top": {"style": "thin", "color": "#000000"},
            "bottom": {"style": "thin", "color": "#000000"},
            "left": {"style": "thin", "color": "#000000"},
            "right": {"style": "thin", "color": "#000000"}
          },
          "number_format": "General"
        },
        {
          "address": "B2",
          "row": 2,
          "col": 2,
          "value": 1234.56,
          "type": "number",
          "formula": "=SUM(B3:B10)",
          "font": {...},
          "fill": {...},
          "alignment": {...},
          "border": {...},
          "number_format": "#,##0.00"
        }
      ]
    }
  ],
  "metadata": {
    "creator": "Microsoft Excel",
    "last_modified_by": "User",
    "created": "2025-10-15T14:20:00Z",
    "modified": "2025-10-17T09:15:00Z"
  }
}
```

**错误处理**:
- 文件不存在 → 抛出 `FileNotFoundError` 并列出可用文件
- 文件格式错误 → 抛出 `InvalidFileFormatError`
- 文件超过1MB → 抛出 `FileSizeExceededError(limit=1MB, actual=XXX)`
- 批量超过20个 → 抛出 `BatchLimitExceededError(limit=20, actual=XXX)`

**性能要求**:
- 单文件(1MB): < 2秒
- 批量(20个文件，共20MB): < 10秒

**优先级**: P0 (核心功能)

---

#### 【P0】F2: JSON转换为Excel文件

**功能描述**  
将符合规范的JSON数据转换为格式化的xlsx文件，并上传至Supabase Storage。

**用户故事**
```
作为 项目发起人
我想要 将JSON数据生成为格式化的Excel文件
以便于 分发给没有技术背景的业务人员
```

**验收标准**
- ✅ 接受标准化JSON输入(格式同F1)
- ✅ 完整还原所有格式信息（100%保真度）:
  - 单元格数据和类型
  - 字体样式（名称、大小、颜色、粗斜体）
  - 颜色和背景（RGB/HEX格式）
  - 单元格尺寸（列宽、行高）
  - 合并单元格（自动合并指定范围）
  - 公式（保持公式引用，可自动计算）
  - 边框样式
  - 对齐方式
  - 数字格式
  
- ✅ 输出文件直接上传至Supabase Storage指定bucket
- ✅ 支持自定义文件名和路径
- ✅ 支持覆盖已存在文件（需明确参数 `overwrite=true`）

**API设计示例**:
```python
create_excel_from_json(
    bucket="reports",
    file_path="2024/Q1/sales_summary.xlsx",
    json_data=json_string_or_dict,
    overwrite=True,  # 默认False，避免误覆盖
    calculate_formulas=True  # 是否预计算公式值
)
```

**错误处理**:
- JSON格式错误 → 抛出 `InvalidJSONFormatError` 并说明具体字段
- 文件已存在且overwrite=False → 抛出 `FileExistsError`
- Supabase上传失败 → 抛出 `SupabaseUploadError` 并显示原因

**性能要求**:
- 生成文件(1000行) + 上传: < 3秒

**优先级**: P0

---

#### 【P1】F3: 单元格格式编辑

**功能描述**  
提供细粒度的单元格格式修改能力，支持批量操作。

**用户故事**
```
作为 报表生成器
我想要 批量修改单元格的格式属性
以便于 快速调整报表外观符合企业规范
```

**验收标准**

##### 3.1 尺寸调整
- ✅ **行高设置**:
  ```python
  set_row_height(bucket, file_path, sheet, row=1, height=25.0)
  set_row_heights(bucket, file_path, sheet, rows=[1,2,3], height=25.0)
  ```
  
- ✅ **列宽设置**:
  ```python
  set_column_width(bucket, file_path, sheet, column="A", width=15.5)
  set_column_widths(bucket, file_path, sheet, columns=["A","B","C"], width=20.0)
  auto_fit_column(bucket, file_path, sheet, column="A")  # 自适应内容
  ```

##### 3.2 合并单元格操作
- ✅ **合并操作**:
  ```python
  merge_cells(bucket, file_path, sheet, range="A1:C1")
  merge_cells(bucket, file_path, sheet, range="A1:C3")  # 矩形区域
  ```
  
- ✅ **取消合并**:
  ```python
  unmerge_cells(bucket, file_path, sheet, range="A1:C1")
  ```
  
- ✅ **识别已合并区域**:
  ```python
  get_merged_cells(bucket, file_path, sheet)
  # 返回: [{"range": "A1:C1", "value": "标题"}, ...]
  ```

##### 3.3 文本换行
- ✅ **启用/禁用自动换行**:
  ```python
  set_wrap_text(bucket, file_path, sheet, cell="A1", wrap=True)
  set_wrap_text(bucket, file_path, sheet, range="A1:C10", wrap=True)  # 批量
  ```

##### 3.4 字体设置
- ✅ **支持的字体属性**:
  ```python
  set_font(
      bucket, file_path, sheet, cell="A1",
      font_name="Arial",           # 常见字体: Arial, 微软雅黑, 宋体, Calibri
      font_size=14,                # pt单位
      font_color="#FF0000",        # RGB/HEX格式
      bold=True,
      italic=False,
      underline="single"           # none/single/double
  )
  ```

##### 3.5 单元格颜色
- ✅ **背景色和前景色**:
  ```python
  set_cell_color(
      bucket, file_path, sheet, cell="A1",
      fill_color="#FFFF00",        # 背景色
      font_color="#000000"         # 字体颜色
  )
  ```

**批量操作示例**:
```python
# 批量格式化标题行
format_cells(
    bucket="reports",
    file_path="sales.xlsx",
    sheet="Sheet1",
    range="A1:J1",
    font={"name": "微软雅黑", "size": 12, "bold": True, "color": "#FFFFFF"},
    fill={"color": "#4472C4"},
    alignment={"horizontal": "center", "vertical": "middle"}
)
```

**错误处理**:
- 单元格范围无效 → 抛出 `InvalidCellRangeError`
- 不支持的字体 → 抛出 `UnsupportedFontError` 并列出可用字体
- 颜色格式错误 → 抛出 `InvalidColorFormatError(expected="#RRGGBB or rgb(r,g,b)")`

**优先级**: P1

---

#### 【P1】F4: Excel公式执行

**功能描述**  
支持常用Excel公式的解析、计算和写入。

**用户故事**
```
作为 数据分析师
我想要 在生成的Excel中使用公式
以便于 实现动态计算和数据关联
```

**验收标准**

##### 4.1 支持的公式类型（MVP阶段）

**数学和统计函数**:
- ✅ `SUM(range)` - 求和
- ✅ `AVERAGE(range)` - 平均值
- ✅ `COUNT(range)` - 计数
- ✅ `MAX(range)` - 最大值
- ✅ `MIN(range)` - 最小值
- ✅ `ROUND(number, digits)` - 四舍五入

**逻辑函数**:
- ✅ `IF(condition, true_value, false_value)` - 条件判断
- ✅ `AND(condition1, condition2, ...)` - 逻辑与
- ✅ `OR(condition1, condition2, ...)` - 逻辑或
- ✅ `NOT(condition)` - 逻辑非

**文本函数**:
- ✅ `CONCATENATE(text1, text2, ...)` - 文本拼接
- ✅ `LEFT(text, num_chars)` - 左侧字符
- ✅ `RIGHT(text, num_chars)` - 右侧字符
- ✅ `MID(text, start, num_chars)` - 中间字符
- ✅ `LEN(text)` - 文本长度
- ✅ `UPPER(text)` / `LOWER(text)` - 大小写转换

**日期函数**:
- ✅ `TODAY()` - 当前日期
- ✅ `NOW()` - 当前日期时间
- ✅ `DATE(year, month, day)` - 构造日期

**查找函数**:
- ✅ `VLOOKUP(lookup_value, table_array, col_index, [range_lookup])`
- ✅ `HLOOKUP(lookup_value, table_array, row_index, [range_lookup])`

##### 4.2 公式特性
- ✅ **单元格引用**:
  - 相对引用: `A1`, `B2`
  - 绝对引用: `$A$1`, `$B$2`
  - 混合引用: `$A1`, `A$1`
  
- ✅ **范围引用**: `A1:C10`, `B2:B100`

- ✅ **跨Sheet引用**: `Sheet2!A1`, `'Q1销售'!B5`

- ✅ **公式计算**:
  ```python
  # 写入公式并自动计算
  set_formula(
      bucket, file_path, sheet, cell="B10",
      formula="=SUM(B2:B9)",
      calculate=True  # 自动计算结果
  )
  
  # 批量重新计算
  recalculate_formulas(bucket, file_path)
  ```

- ✅ **公式错误处理**:
  - `#DIV/0!` - 除零错误
  - `#REF!` - 引用无效
  - `#VALUE!` - 值类型错误
  - `#NAME?` - 函数名错误
  - 遇到错误 → 保留错误值，不中断操作

##### 4.3 不支持的功能（P2阶段）
- ❌ 数组公式 `{=SUM(A1:A10*B1:B10)}`
- ❌ VBA宏
- ❌ 复杂嵌套公式（>5层）
- ❌ 自定义函数

**错误处理**:
- 不支持的函数 → 抛出 `UnsupportedFormulaError(function=XXX)` 并列出支持列表
- 公式语法错误 → 抛出 `FormulaSyntaxError` 并指出错误位置

**优先级**: P1

---

#### 【P0】F5: 多Sheet操作

**功能描述**  
支持在单个工作簿中管理多个工作表，包括合并操作。

**用户故事**
```
作为 项目管理者
我想要 合并多个Excel文件为一个工作簿
以便于 统一管理和分发相关数据
```

**验收标准**

##### 5.1 读取操作
- ✅ **解析多sheet文件**:
  ```python
  # 返回所有sheet的数据
  parse_excel_to_json(bucket, file_path)  # 默认解析所有sheet
  ```
  
- ✅ **指定sheet读取**:
  ```python
  parse_excel_to_json(bucket, file_path, sheets=["Sheet1", "销售数据"])
  parse_excel_to_json(bucket, file_path, sheet_indices=[0, 2])  # 按索引
  ```
  
- ✅ **获取sheet列表**:
  ```python
  list_sheets(bucket, file_path)
  # 返回: [{"name": "Sheet1", "index": 0, "visible": True}, ...]
  ```

##### 5.2 写入操作
- ✅ **创建新sheet**:
  ```python
  create_sheet(bucket, file_path, sheet_name="新数据", index=0)  # 插入位置
  ```
  
- ✅ **重命名sheet**:
  ```python
  rename_sheet(bucket, file_path, old_name="Sheet1", new_name="销售数据")
  ```
  
- ✅ **删除sheet**:
  ```python
  delete_sheet(bucket, file_path, sheet_name="临时数据")
  ```
  
- ✅ **调整sheet顺序**:
  ```python
  reorder_sheets(bucket, file_path, sheet_order=["Sheet3", "Sheet1", "Sheet2"])
  ```

##### 5.3 合并操作（核心功能）
- ✅ **多文件合并为单个工作簿**:
  ```python
  merge_excel_files(
      bucket="reports",
      input_files=["sales_q1.xlsx", "sales_q2.xlsx", "sales_q3.xlsx"],
      output_file="annual_sales.xlsx",
      sheet_names=["Q1", "Q2", "Q3"],  # 可选: 自定义sheet名称
      overwrite=True
  )
  ```

- ✅ **合并规则**:
  - 每个输入文件的第一个sheet作为合并内容
  - 如果输入文件有多个sheet，需明确指定要合并的sheet
  - 保持原有格式不变
  - 自动处理重名sheet（添加后缀 `_2`, `_3`）
  
- ✅ **高级合并**:
  ```python
  merge_excel_files(
      bucket="reports",
      input_configs=[
          {"file": "file1.xlsx", "sheet": "Data", "rename_to": "Q1数据"},
          {"file": "file2.xlsx", "sheet": "Sheet1", "rename_to": "Q2数据"}
      ],
      output_file="merged.xlsx"
  )
  ```

**性能要求**:
- 合并10个文件(每个1MB): < 8秒

**错误处理**:
- Sheet不存在 → 抛出 `SheetNotFoundError` 并列出可用sheet
- Sheet名称冲突 → 自动重命名并警告
- 输入文件超过20个 → 抛出 `BatchLimitExceededError`

**优先级**: P0

---

#### 【P0】F6: Supabase Storage集成

**功能描述**  
无缝集成Supabase Storage作为文件存储后端，支持完整的CRUD操作。

**用户故事**
```
作为 云原生应用开发者
我想要 直接从Supabase读写Excel文件
以便于 避免本地文件管理的复杂性
```

**验收标准**

##### 6.1 环境配置（已确认）
- ✅ **通过环境变量注入**:
  ```bash
  SUPABASE_URL=https://xxx.supabase.co
  SUPABASE_KEY=eyJhbGc...  # Service Key 或 Anon Key
  ```
  
- ✅ **支持.env文件**:
  ```bash
  # .env文件示例
  SUPABASE_URL=https://yourproject.supabase.co
  SUPABASE_KEY=your-service-role-key
  ```

- ✅ **权限要求**:
  - 用户已具有Storage API访问权限（已确认✓）
  - 无需特殊bucket权限设置（已确认✓）
  - 支持公开和私有bucket

##### 6.2 读取操作
- ✅ **从bucket读取文件**:
  ```python
  # 简单读取
  read_excel_from_storage(bucket="reports", file_path="sales.xlsx")
  
  # 带路径读取
  read_excel_from_storage(bucket="reports", file_path="2024/Q1/sales.xlsx")
  ```
  
- ✅ **列出bucket文件**:
  ```python
  list_storage_files(bucket="reports", path_prefix="2024/")
  # 返回: [
  #   {"name": "sales.xlsx", "size": 245760, "updated_at": "2025-10-17T10:00:00Z"},
  #   {"name": "Q1/report.xlsx", "size": 102400, "updated_at": "..."}
  # ]
  ```
  
- ✅ **搜索文件**:
  ```python
  search_storage_files(bucket="reports", pattern="*.xlsx", limit=20)
  ```

##### 6.3 写入操作
- ✅ **上传文件**:
  ```python
  upload_excel_to_storage(
      bucket="reports",
      file_path="2024/Q1/sales.xlsx",
      data=excel_binary_or_json,
      overwrite=False  # 默认不覆盖，避免误操作
  )
  ```
  
- ✅ **覆盖控制**:
  ```python
  # 明确覆盖
  upload_excel_to_storage(bucket, file_path, data, overwrite=True)
  
  # 自动重命名（如果已存在）
  upload_excel_to_storage(bucket, file_path, data, auto_rename=True)
  # 结果: sales.xlsx → sales_1.xlsx
  ```

##### 6.4 管理操作
- ✅ **删除文件**:
  ```python
  delete_storage_file(bucket="reports", file_path="old_report.xlsx")
  ```
  
- ✅ **移动文件**:
  ```python
  move_storage_file(
      bucket="reports",
      source="temp/draft.xlsx",
      destination="2024/Q1/final.xlsx"
  )
  ```
  
- ✅ **复制文件**:
  ```python
  copy_storage_file(
      bucket="reports",
      source="template.xlsx",
      destination="2024/Q1/report.xlsx"
  )
  ```
  
- ✅ **获取文件元数据**:
  ```python
  get_file_metadata(bucket="reports", file_path="sales.xlsx")
  # 返回: {
  #   "name": "sales.xlsx",
  #   "size": 245760,
  #   "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  #   "created_at": "2025-10-15T14:20:00Z",
  #   "updated_at": "2025-10-17T09:15:00Z",
  #   "url": "https://xxx.supabase.co/storage/v1/object/public/reports/sales.xlsx"
  # }
  ```

##### 6.5 批量操作（限制20个）
- ✅ **批量下载**:
  ```python
  batch_download(
      bucket="reports",
      file_paths=["file1.xlsx", "file2.xlsx", ...],  # 最多20个
      local_dir="/tmp/downloads"  # 可选: 保存到本地
  )
  ```
  
- ✅ **批量上传**:
  ```python
  batch_upload(
      bucket="reports",
      files=[
          {"path": "2024/file1.xlsx", "data": data1},
          {"path": "2024/file2.xlsx", "data": data2}
      ]  # 最多20个
  )
  ```

**性能要求**:
- 单文件上传(1MB): < 1秒
- 单文件下载(1MB): < 1秒
- 批量操作(20个文件): < 10秒

**错误处理**:
- 环境变量未设置 → 抛出 `SupabaseConfigError("SUPABASE_URL not set")`
- 认证失败 → 抛出 `SupabaseAuthError("Invalid API key")`
- Bucket不存在 → 抛出 `BucketNotFoundError` 并列出可用bucket
- 文件不存在 → 抛出 `FileNotFoundError` 并列出该路径下文件
- 网络超时 → 抛出 `SupabaseTimeoutError` 并建议重试

**优先级**: P0

---

#### 【P0】F7: 独立运行(无需Office软件)

**功能描述**  
纯Python实现，不依赖Microsoft Office、WPS或LibreOffice。

**技术选型**
- **核心库**: `openpyxl` (读写xlsx)
- **公式计算**: `formulas` 或自定义引擎
- **样式处理**: `openpyxl.styles`
- **Supabase集成**: `supabase-py`

**验收标准**
- ✅ 所有功能无需安装Office软件
- ✅ 跨平台支持(Windows/Linux/macOS)
- ✅ 依赖项≤10个（保持轻量）
- ✅ 安装包大小 < 50MB

**测试环境**:
- ✅ 在无GUI的Linux服务器上验证
- ✅ 在Windows 10/11上验证（无Office）
- ✅ 在macOS上验证（无Office）

**优先级**: P0

---

#### 【P0】F8: UVX安装方式

**功能描述**  
支持通过uvx快速安装和使用，一条命令完成部署。

**用户故事**
```
作为 MCP用户（项目发起人）
我想要 通过一条命令安装MCP服务
以便于 快速集成到我的Claude工作流
```

**验收标准**

##### 8.1 安装方式
```bash
# 方式1: 从PyPI安装（推荐）
uvx mcp-excel-supabase

# 方式2: 从GitHub直接安装
uvx --from git+https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage mcp-excel-supabase

# 方式3: 本地开发安装
git clone https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage
cd Excel-MCP-Server-with-Supabase-Storage
uvx --from . mcp-excel-supabase
```

##### 8.2 项目结构
```
Excel-MCP-Server-with-Supabase-Storage/
├── .github/
│   └── workflows/
│       ├── test.yml                    # CI测试
│       ├── lint.yml                    # 代码质量检查
│       └── publish.yml                 # 发布到PyPI
├── docs/
│   ├── README.md                       # 主文档
│   ├── API.md                          # API参考
│   ├── EXAMPLES.md                     # 使用示例
│   ├── ARCHITECTURE.md                 # 架构设计
│   └── CONTRIBUTING.md                 # 贡献指南
├── src/
│   └── mcp_excel_supabase/
│       ├── __init__.py
│       ├── __main__.py                 # CLI入口
│       ├── server.py                   # MCP服务器主入口
│       ├── tools.py                    # MCP工具注册
│       ├── excel/
│       │   ├── __init__.py
│       │   ├── parser.py               # F1: JSON解析
│       │   ├── writer.py               # F2: Excel生成
│       │   ├── formatter.py            # F3: 格式编辑
│       │   ├── formula_engine.py       # F4: 公式计算
│       │   └── sheet_manager.py        # F5: Sheet操作
│       ├── storage/
│       │   ├── __init__.py
│       │   └── supabase_client.py      # F6: Supabase集成
│       └── utils/
│           ├── __init__.py
│           ├── logger.py               # 日志工具
│           ├── validator.py            # 输入验证
│           └── errors.py               # 自定义异常
├── tests/
│   ├── __init__.py
│   ├── conftest.py                     # pytest配置
│   ├── test_parser.py
│   ├── test_writer.py
│   ├── test_formatter.py
│   ├── test_formula.py
│   ├── test_sheet_manager.py
│   ├── test_supabase.py
│   ├── test_integration.py             # 集成测试
│   └── fixtures/
│       ├── sample1.xlsx
│       ├── sample2.xlsx
│       └── expected_output.json
├── .env.example                        # 环境变量模板
├── .gitignore
├── LICENSE                             # MIT License
├── PRD.md                              # 本文档
├── README.md                           # 项目说明
├── pyproject.toml                      # 项目配置
└── requirements.txt                    # 依赖列表（兼容性）
```

##### 8.3 pyproject.toml配置
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "mcp-excel-supabase"
version = "1.0.0"
description = "MCP server for Excel operations with Supabase Storage integration"
authors = [
    {name = "1126misakp", email = "your-email@example.com"}
]
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.9"
keywords = ["mcp", "excel", "supabase", "openpyxl", "automation"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

dependencies = [
    "openpyxl>=3.1.0",
    "supabase>=2.0.0",
    "mcp>=1.0.0",
    "python-dotenv>=1.0.0",
    "formulas>=1.2.0",
    "pydantic>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=4.1.0",
    "black>=24.0.0",
    "ruff>=0.3.0",
    "mypy>=1.8.0",
]

[project.urls]
Homepage = "https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage"
Documentation = "https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage/blob/main/docs/README.md"
Repository = "https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage"
Issues = "https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage/issues"

[project.scripts]
mcp-excel-supabase = "mcp_excel_supabase.server:main"

[tool.hatch.build.targets.wheel]
packages = ["src/mcp_excel_supabase"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "--cov=mcp_excel_supabase --cov-report=html --cov-report=term"

[tool.black]
line-length = 100
target-version = ["py39", "py310", "py311"]

[tool.ruff]
line-length = 100
target-version = "py39"

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

##### 8.4 Claude Desktop配置示例
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

##### 8.5 安装测试清单
- ✅ Windows 10/11 (PowerShell)
- ✅ Ubuntu 22.04 LTS
- ✅ macOS 13+ (Ventura/Sonoma)
- ✅ Python 3.9, 3.10, 3.11, 3.12

**错误处理**:
- Python版本不符 → 抛出明确错误并提示最低版本要求
- 环境变量缺失 → 提供`.env.example`链接
- uvx安装失败 → 提供pip安装备选方案

**优先级**: P0

---

### 3.2 非功能需求

#### NFR1: 性能要求（已明确）
基于项目约束（最多20个文件，每个≤1MB）：

| 操作 | 性能指标 | 备注 |
|------|---------|------|
| 单文件解析(1MB) | < 2秒 | 包含所有格式信息 |
| 批量解析(20个文件) | < 10秒 | 并行处理 |
| 单文件生成(1000行) | < 3秒 | 包含格式和公式 |
| 文件上传/下载(1MB) | < 1秒 | Supabase网络IO |
| 合并10个文件 | < 8秒 | 保持格式 |
| 内存占用 | < 500MB | 单进程峰值 |

**性能优化策略**:
- 使用流式处理避免全文件加载
- 批量操作时启用并发（最多5个并发）
- 缓存Supabase连接
- 大文件（>500KB）显示进度条

#### NFR2: 安全要求
- ✅ **密钥管理**:
  - Supabase密钥仅通过环境变量传递
  - 不在日志中输出密钥（脱敏处理）
  - 不硬编码任何敏感信息
  
- ✅ **输入验证**:
  - 文件路径验证（防止路径遍历攻击）
  - 文件大小验证（≤1MB）
  - 批量数量验证（≤20个）
  - JSON格式验证（防止注入攻击）
  
- ✅ **依赖安全**:
  - 使用`pip-audit`扫描漏洞
  - 锁定依赖版本范围
  - 定期更新依赖（每季度）

#### NFR3: 兼容性要求
- Python版本: ≥3.9（支持3.9, 3.10, 3.11, 3.12）
- Excel格式: .xlsx (Excel 2007+)
- 操作系统: Windows 10+/Ubuntu 20.04+/macOS 12+
- MCP协议: 符合v1.0+ stable版本

#### NFR4: 可维护性
- ✅ **代码质量**:
  - 代码覆盖率: ≥80%
  - Type hints覆盖率: 100%（所有公开API）
  - 文档字符串: 100%（所有公开API）
  - Ruff lint评分: A级
  
- ✅ **日志规范**:
  - 日志级别: DEBUG/INFO/WARNING/ERROR/CRITICAL
  - 日志格式: `[时间] [级别] [模块] 消息`
  - 错误日志包含堆栈跟踪
  - 支持日志文件输出
  
- ✅ **错误处理规范**:
  - 所有错误继承自`MCPExcelError`基类
  - 错误消息包含上下文和建议操作
  - 用户友好的错误提示（避免技术术语）
  - 错误码体系（如E001, E002...）

#### NFR5: 可观测性
- ✅ **监控指标**:
  - 操作成功率
  - 平均响应时间
  - 错误率和错误类型分布
  - Supabase API调用次数
  
- ✅ **调试支持**:
  - `--debug`模式输出详细日志
  - `--dry-run`模式预览操作不执行
  - 性能分析模式（显示各阶段耗时）

---

## 4. 技术约束与建议

### 4.1 技术栈

| 组件 | 技术选型 | 版本要求 | 理由 |
|------|---------|---------|------|
| Excel处理 | `openpyxl` | >=3.1.0 | 纯Python，功能完整，活跃维护 |
| 云存储 | `supabase-py` | >=2.0.0 | 官方SDK，文档完善 |
| MCP框架 | `mcp` | >=1.0.0 | 标准协议实现 |
| 公式计算 | `formulas` | >=1.2.0 | 成熟的公式引擎 |
| 数据验证 | `pydantic` | >=2.0.0 | 类型安全，性能优秀 |
| 环境管理 | `python-dotenv` | >=1.0.0 | 简化配置管理 |
| 测试框架 | `pytest` | >=8.0.0 | 标准Python测试工具 |
| 代码质量 | `ruff` + `black` | >=0.3.0, >=24.0.0 | 现代化lint和格式化 |
| 类型检查 | `mypy` | >=1.8.0 | 静态类型检查 |

### 4.2 MCP工具定义

**工具列表（共12个核心工具）**:

#### 📄 文件解析与生成
1. **`parse_excel_to_json`**
   - 功能: 解析单个或多个Excel文件为JSON
   - 输入: `bucket`, `file_paths` (单个或数组), `sheets` (可选)
   - 输出: JSON字符串或对象
   - 示例:
     ```json
     {
       "bucket": "reports",
       "file_paths": ["sales_q1.xlsx", "sales_q2.xlsx"],
       "sheets": null
     }
     ```

2. **`create_excel_from_json`**
   - 功能: 从JSON创建Excel文件
   - 输入: `bucket`, `file_path`, `json_data`, `overwrite`, `calculate_formulas`
   - 输出: 上传成功确认和文件URL
   - 示例:
     ```json
     {
       "bucket": "reports",
       "file_path": "2024/Q1/summary.xlsx",
       "json_data": {...},
       "overwrite": true,
       "calculate_formulas": true
     }
     ```

#### 🎨 格式编辑
3. **`modify_cell_format`**
   - 功能: 修改单个或批量单元格格式
   - 输入: `bucket`, `file_path`, `sheet`, `cell_range`, `format_options`
   - 输出: 修改确认
   - 示例:
     ```json
     {
       "bucket": "reports",
       "file_path": "sales.xlsx",
       "sheet": "Sheet1",
       "cell_range": "A1:J1",
       "format_options": {
         "font": {"name": "Arial", "size": 12, "bold": true},
         "fill": {"color": "#4472C4"},
         "alignment": {"horizontal": "center"}
       }
     }
     ```

4. **`merge_cells`**
   - 功能: 合并单元格
   - 输入: `bucket`, `file_path`, `sheet`, `range`
   - 输出: 合并确认

5. **`unmerge_cells`**
   - 功能: 取消合并单元格
   - 输入: `bucket`, `file_path`, `sheet`, `range`
   - 输出: 取消合并确认

6. **`set_row_heights`**
   - 功能: 设置行高
   - 输入: `bucket`, `file_path`, `sheet`, `rows`, `height`
   - 输出: 设置确认

7. **`set_column_widths`**
   - 功能: 设置列宽
   - 输入: `bucket`, `file_path`, `sheet`, `columns`, `width`
   - 输出: 设置确认

#### 📐 公式操作
8. **`set_formula`**
   - 功能: 写入或更新公式
   - 输入: `bucket`, `file_path`, `sheet`, `cell`, `formula`, `calculate`
   - 输出: 公式和计算结果

9. **`recalculate_formulas`**
   - 功能: 重新计算所有公式
   - 输入: `bucket`, `file_path`, `sheets` (可选)
   - 输出: 计算完成确认

#### 📊 Sheet管理
10. **`merge_excel_files`**
    - 功能: 合并多个Excel文件
    - 输入: `bucket`, `input_files`, `output_file`, `sheet_names`, `overwrite`
    - 输出: 合并后文件路径
    - 示例:
      ```json
      {
        "bucket": "reports",
        "input_files": ["q1.xlsx", "q2.xlsx", "q3.xlsx"],
        "output_file": "annual.xlsx",
        "sheet_names": ["Q1", "Q2", "Q3"],
        "overwrite": true
      }
      ```

11. **`manage_sheets`**
    - 功能: 创建/重命名/删除/排序sheet
    - 输入: `bucket`, `file_path`, `action`, `params`
    - 输出: 操作确认
    - 示例:
      ```json
      {
        "bucket": "reports",
        "file_path": "sales.xlsx",
        "action": "rename",
        "params": {"old_name": "Sheet1", "new_name": "销售数据"}
      }
      ```

#### 💾 存储管理
12. **`manage_storage`**
    - 功能: 文件管理（列表/删除/移动/复制/元数据）
    - 输入: `bucket`, `action`, `params`
    - 输出: 操作结果
    - 示例:
      ```json
      {
        "bucket": "reports",
        "action": "list",
        "params": {"path_prefix": "2024/", "limit": 20}
      }
      ```

### 4.3 错误码体系

| 错误码 | 类别 | 说明 |
|--------|------|------|
| E001 | ConfigError | 环境变量未设置 |
| E002 | AuthError | Supabase认证失败 |
| E101 | FileNotFoundError | 文件不存在 |
| E102 | FileSizeError | 文件超过1MB限制 |
| E103 | BatchLimitError | 批量操作超过20个文件 |
| E104 | FileExistsError | 文件已存在且未设置覆盖 |
| E201 | InvalidJSONError | JSON格式错误 |
| E202 | InvalidCellRangeError | 单元格范围无效 |
| E203 | InvalidColorError | 颜色格式错误 |
| E301 | UnsupportedFormulaError | 不支持的公式 |
| E302 | FormulaSyntaxError | 公式语法错误 |
| E401 | SheetNotFoundError | Sheet不存在 |
| E501 | NetworkError | Supabase网络错误 |
| E502 | TimeoutError | 操作超时 |

### 4.4 依赖项清单

**核心依赖** (`requirements.txt`):
```txt
# Excel处理
openpyxl>=3.1.0,<4.0.0

# Supabase集成
supabase>=2.0.0,<3.0.0

# MCP框架
mcp>=1.0.0,<2.0.0

# 环境管理
python-dotenv>=1.0.0,<2.0.0

# 公式计算
formulas>=1.2.0,<2.0.0

# 数据验证
pydantic>=2.0.0,<3.0.0
```

**开发依赖**:
```txt
# 测试
pytest>=8.0.0
pytest-asyncio>=0.23.0
pytest-cov>=4.1.0
pytest-mock>=3.12.0

# 代码质量
black>=24.0.0
ruff>=0.3.0
mypy>=1.8.0

# 安全扫描
pip-audit>=2.6.0

# 文档生成
mkdocs>=1.5.0
mkdocs-material>=9.5.0
```

### 4.5 部署方案

#### 方案1: PyPI安装（推荐给最终用户）
```bash
# 安装
uvx mcp-excel-supabase

# 配置
cp .env.example .env
# 编辑.env文件设置SUPABASE_URL和SUPABASE_KEY

# 启动
mcp-excel-supabase
```

#### 方案2: GitHub直接安装（推荐给开发者）
```bash
# 安装最新开发版
uvx --from git+https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage mcp-excel-supabase

# 或安装特定版本
uvx --from git+https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage@v1.0.0 mcp-excel-supabase
```

#### 方案3: 本地开发
```bash
# 克隆仓库
git clone https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage
cd Excel-MCP-Server-with-Supabase-Storage

# 创建虚拟环境（可选）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 启动服务器
python -m mcp_excel_supabase.server
```

#### 方案4: Docker（高级场景）
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY src/ ./src/

# 设置环境变量
ENV PYTHONPATH=/app/src
ENV SUPABASE_URL=${SUPABASE_URL}
ENV SUPABASE_KEY=${SUPABASE_KEY}

# 启动服务
CMD ["python", "-m", "mcp_excel_supabase.server"]
```

**Docker使用**:
```bash
# 构建镜像
docker build -t mcp-excel-supabase .

# 运行容器
docker run -e SUPABASE_URL=xxx -e SUPABASE_KEY=xxx mcp-excel-supabase
```

---

## 5. 项目计划

### 5.1 开发阶段

#### 🚀 Phase 1: 基础功能开发 (Week 1-2)
**目标**: 实现核心读写功能，让项目发起人（第一用户）可以开始测试

**任务清单**:
- [ ] **Day 1-2**: 项目脚手架搭建
  - [ ] 创建GitHub仓库结构
  - [ ] 配置pyproject.toml和依赖管理
  - [ ] 编写.env.example模板
  - [ ] 设置CI/CD基础（GitHub Actions）
  
- [ ] **Day 3-5**: Supabase集成 (F6基础部分)
  - [ ] 封装Supabase客户端
  - [ ] 实现文件上传/下载
  - [ ] 实现文件列表和元数据获取
  - [ ] 编写单元测试（覆盖率>70%）
  
- [ ] **Day 6-9**: Excel解析为JSON (F1)
  - [ ] 实现基础数据解析
  - [ ] 实现格式信息提取（字体、颜色、尺寸）
  - [ ] 实现合并单元格识别
  - [ ] 支持批量解析（1-20个文件）
  - [ ] 编写测试用例和fixture文件
  
- [ ] **Day 10-14**: JSON生成Excel (F2)
  - [ ] 实现数据写入
  - [ ] 实现格式还原（字体、颜色、边框）
  - [ ] 实现合并单元格写入
  - [ ] 集成Supabase上传
  - [ ] 端到端测试（解析→修改→生成）

**交付物**:
- ✅ 可运行的MCP服务器（本地开发环境）
- ✅ 基础工具: `parse_excel_to_json`, `create_excel_from_json`, `manage_storage`
- ✅ 单元测试覆盖率 > 70%
- ✅ README初版（安装和快速开始）
- ✅ 第一用户可开始Alpha测试

**里程碑**: M1 - MVP可用 (Week 2结束)
- 标准: 项目发起人可以成功解析和生成Excel文件

---

#### 🎨 Phase 2: 格式与公式支持 (Week 3-4)
**目标**: 完善格式编辑和公式能力，达到生产可用标准

**任务清单**:
- [ ] **Day 15-18**: 单元格格式编辑 (F3)
  - [ ] 实现尺寸调整（行高、列宽）
  - [ ] 实现合并/取消合并单元格
  - [ ] 实现字体设置（名称、大小、颜色、粗斜体）
  - [ ] 实现单元格颜色（背景、前景）
  - [ ] 实现文本换行
  - [ ] 批量格式化支持
  
- [ ] **Day 19-22**: 公式引擎集成 (F4)
  - [ ] 集成`formulas`库
  - [ ] 实现20个常用函数支持
  - [ ] 实现单元格引用（相对/绝对）
  - [ ] 实现跨Sheet引用
  - [ ] 公式计算和错误处理
  - [ ] 公式测试套件
  
- [ ] **Day 23-26**: 多Sheet操作 (F5)
  - [ ] 实现Sheet创建/重命名/删除
  - [ ] 实现Sheet排序
  - [ ] 实现多文件合并（核心功能）
  - [ ] 处理Sheet名称冲突
  - [ ] 批量操作性能优化
  
- [ ] **Day 27-28**: 测试和文档
  - [ ] 补充单元测试（覆盖率>80%）
  - [ ] 编写集成测试
  - [ ] 编写API文档v1.0
  - [ ] 编写使用示例（至少3个）

**交付物**:
- ✅ 新增工具: `modify_cell_format`, `merge_cells`, `set_formula`, `merge_excel_files`, `manage_sheets`
- ✅ 测试覆盖率 > 80%
- ✅ API文档v1.0
- ✅ 使用示例库（3个完整示例）
- ✅ 第一用户Beta测试反馈收集

**里程碑**: M2 - 功能完整 (Week 4结束)
- 标准: 所有P0/P1功能实现，第一用户可进行全功能测试

---

#### 🚀 Phase 3: 优化与发布 (Week 5-6)
**目标**: 性能优化、文档完善、正式发布v1.0.0

**任务清单**:
- [ ] **Day 29-32**: 性能优化
  - [ ] 大文件流式处理（>500KB）
  - [ ] 批量操作并发优化（最多5并发）
  - [ ] 内存使用优化（峰值<500MB）
  - [ ] Supabase连接池优化
  - [ ] 性能基准测试
  
- [ ] **Day 33-35**: 错误处理完善
  - [ ] 统一错误码体系
  - [ ] 友好的错误提示（避免技术术语）
  - [ ] 异常场景全覆盖测试
  - [ ] 错误恢复机制
  - [ ] 日志系统完善
  
- [ ] **Day 36-38**: 文档完善
  - [ ] 完整API参考文档
  - [ ] 使用示例库（至少5个端到端示例）
  - [ ] 架构设计文档（流程图、组件图）
  - [ ] 故障排除指南
  - [ ] 贡献指南
  - [ ] 安全最佳实践
  
- [ ] **Day 39-42**: 发布准备
  - [ ] 版本号标记v1.0.0
  - [ ] 构建PyPI发布包
  - [ ] 测试uvx安装（多平台）
  - [ ] 编写CHANGELOG.md
  - [ ] 创建GitHub Release
  - [ ] 录制Demo视频（5分钟）
  - [ ] 准备社区推广素材

**交付物**:
- ✅ 生产就绪版本v1.0.0
- ✅ 完整文档站点
- ✅ 5+个端到端示例
- ✅ Demo视频
- ✅ PyPI发布
- ✅ GitHub Release
- ✅ 第一用户正式验收通过

**里程碑**: M3 - 正式发布 (Week 6结束)
- 标准: v1.0.0发布，第一用户满意度100%，社区推广启动

---

### 5.2 里程碑总览

| 里程碑 | 时间 | 标准 | 第一用户角色 |
|--------|------|------|-------------|
| **M1: MVP可用** | Week 2 | 基础读写功能完成，可解析和生成Excel | Alpha测试，提供核心功能反馈 |
| **M2: 功能完整** | Week 4 | 所有P0/P1功能实现，测试覆盖率>80% | Beta测试，提供全功能反馈 |
| **M3: 正式发布** | Week 6 | 发布v1.0.0，文档完整，第一用户验收通过 | 正式验收，确认满意度100% |

---

### 5.3 风险管理与应对策略

#### 🔴 高风险（概率高 + 影响高）

##### 风险1: 第一用户反馈导致需求变更
**描述**: 项目发起人（第一用户）在Alpha/Beta测试中提出新需求或重大修改  
**影响**: 开发进度延迟，可能影响M3发布  
**概率**: 高 | **影响**: 高  
**应对策略**:
- ✅ **预防措施**:
  - 在每个Phase结束前与第一用户进行演示和确认
  - 使用快速原型验证核心功能
  - 建立需求变更评估流程（影响分析、工作量估算）
  
- ✅ **缓解措施**:
  - 将新需求标记为P2（v1.1版本）
  - 为关键变更预留1周缓冲时间
  - 如果变更影响>3天工作量，延后至v1.1
  
- ✅ **监控指标**:
  - 需求变更次数（目标: ≤3次重大变更）
  - 变更影响的开发时间（目标: ≤5天总计）

---

#### 🟡 中风险

##### 风险2: openpyxl性能瓶颈
**描述**: 处理接近1MB的复杂Excel文件时可能超过2秒限制  
**影响**: 用户体验下降，不满足性能NFR  
**概率**: 中 | **影响**: 中  
**应对策略**:
- ✅ **预防措施**:
  - Phase 1期间进行性能基准测试
  - 使用性能分析工具（cProfile）识别瓶颈
  
- ✅ **缓解措施**:
  - 实现流式解析（按chunk读取）
  - 对大文件显示进度条（用户体验优化）
  - 文档中明确性能限制和最佳实践
  - P2阶段考虑使用xlsxwriter替代（写入场景）
  
- ✅ **监控指标**:
  - 解析1MB文件的实际耗时（目标: <2秒）
  - 生成1000行文件的实际耗时（目标: <3秒）

##### 风险3: 公式兼容性问题
**描述**: Excel公式种类繁多，`formulas`库可能不支持某些函数  
**影响**: 部分公式无法计算，功能不完整  
**概率**: 高 | **影响**: 中  
**应对策略**:
- ✅ **预防措施**:
  - MVP阶段仅承诺支持20个常用函数
  - 提前测试`formulas`库对这20个函数的支持情况
  
- ✅ **缓解措施**:
  - 不支持的公式保留为字符串（不中断操作）
  - 提供明确的公式兼容性列表（文档）
  - 收集第一用户的公式使用情况，优先支持高频函数
  - 为复杂公式提供替代方案建议
  
- ✅ **监控指标**:
  - 公式支持率（目标: 90%的用户公式可计算）
  - 用户反馈的不支持函数列表（用于P2规划）

##### 风险4: Supabase API限流或变更
**描述**: Supabase可能有API调用频率限制或SDK更新破坏兼容性  
**影响**: 批量操作失败，服务不可用  
**概率**: 低 | **影响**: 高  
**应对策略**:
- ✅ **预防措施**:
  - 了解Supabase Storage的API限流政策
  - 锁定SDK版本范围（supabase>=2.0,<3.0）
  - 实现指数退避重试机制
  
- ✅ **缓解措施**:
  - 批量操作时控制并发数（最多5个）
  - 缓存Supabase连接，避免频繁认证
  - 编写集成测试监控API变化
  - 监控Supabase更新日志（每周检查）
  
- ✅ **监控指标**:
  - Supabase API调用成功率（目标: >99%）
  - API响应时间（目标: <1秒）

##### 风险5: 跨平台兼容性问题
**描述**: Windows/Linux/macOS上的文件路径、编码等差异  
**影响**: 部分平台无法正常运行  
**概率**: 中 | **影响**: 中  
**应对策略**:
- ✅ **预防措施**:
  - 使用`pathlib`而非字符串拼接路径
  - 所有文本处理使用UTF-8编码
  - 在3个平台上进行CI测试
  
- ✅ **缓解措施**:
  - 提供平台特定的troubleshooting文档
  - 在GitHub Issues中收集平台问题
  - 为常见问题提供快速修复脚本
  
- ✅ **监控指标**:
  - 各平台安装成功率（目标: >95%）
  - 平台特定问题的数量（目标: ≤3个/平台）

---

#### 🟢 低风险

##### 风险6: UVX生态不成熟
**描述**: UVX是较新的工具，可能有未知bug  
**影响**: 安装失败，用户弃用  
**概率**: 低 | **影响**: 低  
**应对策略**:
- ✅ **预防措施**:
  - 提供pip安装备选方案
  - 详细的troubleshooting文档
  
- ✅ **缓解措施**:
  - 在多个环境测试uvx安装（CI中覆盖）
  - 社区支持渠道（GitHub Issues + Discussions）
  - 如果uvx严重不可用，切换到推荐pip安装
  
- ✅ **监控指标**:
  - uvx安装成功率（目标: >90%）
  - GitHub Issues中安装相关问题数量（目标: ≤5个）

---

### 5.4 质量保证计划

#### 测试策略

##### 单元测试（覆盖率目标: 80%+）
- 每个模块独立测试
- 使用pytest fixtures管理测试数据
- Mock Supabase API调用（避免依赖外部服务）
- 自动化测试报告生成

##### 集成测试
- 端到端场景测试（解析→修改→生成→上传）
- 真实Supabase Storage测试（使用测试bucket）
- 跨Sheet引用和公式计算测试
- 批量操作测试（10+文件）

##### 性能测试
- 基准测试套件（pytest-benchmark）
- 压力测试（20个文件并发）
- 内存泄漏检测
- 性能回归测试（每次提交）

##### 用户验收测试（UAT）
- 第一用户Alpha测试（M1后）
- 第一用户Beta测试（M2后）
- 第一用户最终验收（M3前）

#### CI/CD流程

```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ['3.9', '3.10', '3.11', '3.12']
    
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
      
      - name: Lint with ruff
        run: ruff check .
      
      - name: Type check with mypy
        run: mypy src/
      
      - name: Run tests
        run: pytest --cov --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## 6. 验收标准总结

### 6.1 功能验收（第一用户视角）

#### P0功能（必须100%通过）
- ✅ **F1: Excel解析为JSON**
  - 可成功解析20个1MB文件
  - 格式信息完整（字体、颜色、尺寸）
  - 合并单元格正确识别
  - 解析时间<10秒
  
- ✅ **F2: JSON生成Excel**
  - 格式100%还原
  - 文件可在无Office环境打开
  - 上传到Supabase成功
  - 生成时间<3秒
  
- ✅ **F5: 多Sheet操作**
  - 可合并10个文件为单个工作簿
  - Sheet名称可自定义
  - 格式保持不变
  
- ✅ **F6: Supabase集成**
  - 文件读写稳定可靠
  - 批量操作成功（20个文件）
  - 错误提示清晰
  
- ✅ **F7: 独立运行**
  - 在无Office软件环境可用
  - 跨平台测试通过
  
- ✅ **F8: UVX安装**
  - 一条命令完成安装
  - 配置过程<5分钟

#### P1功能（必须100%通过）
- ✅ **F3: 格式编辑**
  - 批量设置字体、颜色
  - 合并单元格稳定
  - 行高列宽调整准确
  
- ✅ **F4: 公式执行**
  - 20个常用函数正常工作
  - 公式引用正确
  - 错误处理友好

### 6.2 性能验收（严格标准）
| 操作 | 标准 | 实际 | 状态 |
|------|------|------|------|
| 单文件解析(1MB) | <2秒 | ___ | ⬜ |
| 批量解析(20个文件) | <10秒 | ___ | ⬜ |
| 单文件生成(1000行) | <3秒 | ___ | ⬜ |
| 合并10个文件 | <8秒 | ___ | ⬜ |
| 内存峰值 | <500MB | ___ | ⬜ |

### 6.3 质量验收
- ✅ 单元测试覆盖率 ≥80%
- ✅ 集成测试通过率 100%
- ✅ Ruff lint评分 A级
- ✅ mypy类型检查无错误
- ✅ 安全扫描(pip-audit)无高危漏洞

### 6.4 文档验收
- ✅ README完整（安装、配置、快速开始）
- ✅ API文档覆盖所有12个工具
- ✅ 至少5个端到端示例
- ✅ 架构图清晰（组件图、流程图）
- ✅ 故障排除指南完整

### 6.5 第一用户满意度验收
- ✅ 功能满足需求（核心场景可实现）
- ✅ 性能满足预期（符合NFR要求）
- ✅ 易用性良好（配置<5分钟，文档清晰）
- ✅ 稳定性可靠（Alpha/Beta测试无严重bug）
- ✅ **最终评分**: 满意度 = 100%

### 6.6 发布验收
- ✅ PyPI发布成功（可通过`pip install`安装）
- ✅ GitHub Release创建（v1.0.0标签）
- ✅ uvx安装测试通过（3个平台）
- ✅ Demo视频录制完成（5分钟演示）
- ✅ License文件存在（MIT）

---

## 7. 附录

### 7.1 参考资料

#### 技术文档
- [openpyxl官方文档](https://openpyxl.readthedocs.io/)
- [Supabase Storage API](https://supabase.com/docs/guides/storage)
- [MCP协议规范](https://modelcontextprotocol.io/)
- [UVX工具文档](https://docs.astral.sh/uv/)
- [formulas库文档](https://pypi.org/project/formulas/)

#### 最佳实践
- [Python项目结构最佳实践](https://realpython.com/python-application-layouts/)
- [pytest测试最佳实践](https://docs.pytest.org/en/stable/goodpractices.html)
- [API设计最佳实践](https://github.com/microsoft/api-guidelines)

### 7.2 竞品分析

| 产品 | 优势 | 劣势 | 我们的优势 |
|------|------|------|-----------|
| **pandas + openpyxl** | 功能强大，数据分析友好 | 非MCP协议，格式支持有限，依赖重 | MCP原生，格式完整，轻量 |
| **xlwings** | 格式完整，Excel功能全 | 依赖Excel软件，非云原生 | 无需Office，云集成 |
| **python-xlsx** | 轻量级 | 只读，无格式支持 | 读写完整，格式支持 |
| **xlsx2json (npm)** | 简单易用 | Node.js生态，无云集成 | Python生态，Supabase集成 |
| **本产品** | MCP原生，云集成，无依赖，格式完整 | 新产品，社区待建立 | 填补市场空白 |

### 7.3 术语表

| 术语 | 定义 |
|------|------|
| **MCP** | Model Context Protocol，AI与工具交互的标准协议 |
| **UVX** | Universal Virtual Environment eXecutor，Python包管理工具 |
| **Supabase** | 开源Firebase替代品，提供数据库、认证、Storage等服务 |
| **Storage Bucket** | Supabase中的文件存储容器 |
| **openpyxl** | Python库，用于读写Excel 2010 xlsx/xlsm文件 |
| **Cell Range** | Excel中的单元格范围，如A1:C10 |
| **Merged Cell** | 合并单元格，多个单元格合并为一个显示区域 |
| **Formula** | Excel公式，如=SUM(A1:A10) |
| **Sheet** | Excel工作簿中的单个工作表 |

### 7.4 后续规划（P2版本，v1.1+）

#### 功能增强
- ✅ 支持.xls格式（Excel 97-2003）
- ✅ 图表生成和编辑（柱状图、折线图、饼图）
- ✅ 数据验证规则（下拉列表、数值范围）
- ✅ 条件格式（颜色标尺、图标集）
- ✅ 批注和批注管理
- ✅ 打印设置（页边距、缩放、分页）
- ✅ 数组公式支持
- ✅ 更多公式函数（SUMIF, COUNTIF, INDEX+MATCH组合）

#### 性能优化
- ✅ 支持更大文件（5MB+）
- ✅ 流式处理优化
- ✅ C扩展加速（考虑使用Cython）

#### 用户体验
- ✅ WebUI控制面板（可视化配置）
- ✅ 交互式CLI（rich库）
- ✅ 进度条和状态显示

#### 集成扩展
- ✅ 支持Google Drive集成
- ✅ 支持AWS S3集成
- ✅ Webhook通知（操作完成后推送）
- ✅ 定时任务支持（cron表达式）

#### 社区建设
- ✅ 插件系统（自定义函数）
- ✅ 贡献者指南完善
- ✅ 社区示例库（awesome-mcp-excel）

---

## 📞 联系方式

**项目经理**: Product Manager  
**GitHub**: [1126misakp/Excel-MCP-Server-with-Supabase-Storage](https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage)  
**Issues**: [提交问题](https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage/issues)  
**Discussions**: [讨论区](https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage/discussions)

---

## 📜 变更记录

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|---------|------|
| v1.0 | 2025-10-17 | 初始版本，所有需求已与第一用户确认 | PM |

---

**文档状态**: ✅ 已完成  
**批准状态**: ⏳ 待第一用户最终确认  
**下一步**: 开发团队接手，启动Phase 1开发

---

*本PRD文档基于项目发起人（第一用户）的明确需求编写，所有技术约束和业务目标已确认。文档将作为开发团队的指导文件，并在每个里程碑后更新实际进展。*
