# Excel MCP Server API 参考文档

本文档提供 Excel MCP Server 所有工具的完整 API 参考。

## 📚 目录

- [概述](#概述)
- [快速参考](#快速参考)
- [工具详细文档](#工具详细文档)
  - [1. parse_excel_to_json](#1-parse_excel_to_json)
  - [2. create_excel_from_json](#2-create_excel_from_json)
  - [3. modify_cell_format](#3-modify_cell_format)
  - [4. merge_cells](#4-merge_cells)
  - [5. unmerge_cells](#5-unmerge_cells)
  - [6. set_row_heights](#6-set_row_heights)
  - [7. set_column_widths](#7-set_column_widths)
  - [8. manage_storage](#8-manage_storage)
  - [9. set_formula](#9-set_formula)
  - [10. recalculate_formulas](#10-recalculate_formulas)
  - [11. manage_sheets](#11-manage_sheets)
  - [12. merge_excel_files](#12-merge_excel_files)
- [错误码对照表](#错误码对照表)
- [数据模型](#数据模型)

---

## 概述

Excel MCP Server 提供 12 个强大的工具，用于处理 Excel 文件和 Supabase 存储操作。所有工具都遵循统一的输入输出格式，并提供完善的错误处理。

### 核心特性

- ✅ **无需 Office**：不依赖 Microsoft Office 或 WPS
- ✅ **完整格式支持**：保留字体、颜色、边框、对齐等格式
- ✅ **公式计算**：支持 20+ 常用 Excel 公式
- ✅ **云存储集成**：直接操作 Supabase Storage
- ✅ **高性能**：批量处理、缓存、并发优化
- ✅ **类型安全**：完整的 Pydantic 模型验证

### 通用约定

**返回值格式**：所有工具都返回包含以下字段的字典：
- `success` (bool)：操作是否成功
- `error` (str, optional)：错误信息（失败时）
- 其他字段：根据具体工具而定

**错误处理**：所有错误都包含错误码（如 E001）和详细信息，参见[错误码对照表](#错误码对照表)。

---

## 快速参考

| 工具名称 | 功能 | 主要用途 |
|---------|------|---------|
| `parse_excel_to_json` | Excel → JSON | 解析 Excel 文件为 JSON 格式 |
| `create_excel_from_json` | JSON → Excel | 从 JSON 数据创建 Excel 文件 |
| `modify_cell_format` | 格式编辑 | 修改单元格字体、颜色、边框等 |
| `merge_cells` | 合并单元格 | 合并指定范围的单元格 |
| `unmerge_cells` | 取消合并 | 取消单元格合并 |
| `set_row_heights` | 设置行高 | 批量设置行高 |
| `set_column_widths` | 设置列宽 | 批量设置列宽 |
| `manage_storage` | 存储管理 | 上传/下载/列出/删除 Supabase 文件 |
| `set_formula` | 设置公式 | 为单元格设置 Excel 公式 |
| `recalculate_formulas` | 重新计算 | 重新计算工作表中的公式 |
| `manage_sheets` | 工作表管理 | 创建/删除/重命名/复制/移动工作表 |
| `merge_excel_files` | 文件合并 | 合并多个 Excel 文件 |

---

## 工具详细文档

### 1. parse_excel_to_json

**功能描述**：将 Excel 文件解析为 JSON 格式，提取所有数据和格式信息。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `file_path` | string | ✅ | - | Excel 文件路径（本地路径） |
| `extract_formats` | boolean | ❌ | `true` | 是否提取单元格格式信息 |

#### 返回值

```json
{
  "success": true,
  "workbook": {
    "sheets": [
      {
        "name": "Sheet1",
        "rows": [...],
        "merged_cells": [...],
        "column_widths": {...}
      }
    ],
    "metadata": {...}
  },
  "error": null
}
```

**字段说明**：
- `success`：操作是否成功
- `workbook`：工作簿数据（包含所有工作表、单元格数据和格式）
- `error`：错误信息（失败时）

#### 使用示例

**示例 1：基础解析**

```python
result = parse_excel_to_json(
    file_path="data/sales_report.xlsx"
)

if result["success"]:
    workbook = result["workbook"]
    print(f"解析成功，包含 {len(workbook['sheets'])} 个工作表")
```

**示例 2：仅提取数据（不提取格式）**

```python
result = parse_excel_to_json(
    file_path="data/large_file.xlsx",
    extract_formats=False  # 提高性能
)
```

#### 错误码

- `E101`：文件不存在
- `E102`：文件读取失败
- `E103`：文件格式无效（不是有效的 Excel 文件）
- `E201`：数据验证失败

#### 性能

- 1MB 文件：约 0.6 秒
- 支持缓存（相同文件重复解析更快）

---

### 2. create_excel_from_json

**功能描述**：从 JSON 数据创建格式化的 Excel 文件。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `workbook_data` | object | ✅ | - | 工作簿数据（JSON 格式） |
| `output_path` | string | ✅ | - | 输出文件路径 |
| `apply_formats` | boolean | ❌ | `true` | 是否应用单元格格式 |

#### 返回值

```json
{
  "success": true,
  "file_path": "output/report.xlsx",
  "error": null
}
```

#### 使用示例

**示例 1：创建简单表格**

```python
workbook_data = {
    "sheets": [
        {
            "name": "销售数据",
            "rows": [
                {
                    "cells": [
                        {"value": "产品", "row": 1, "column": 1},
                        {"value": "销量", "row": 1, "column": 2}
                    ]
                },
                {
                    "cells": [
                        {"value": "产品A", "row": 2, "column": 1},
                        {"value": 100, "row": 2, "column": 2}
                    ]
                }
            ]
        }
    ]
}

result = create_excel_from_json(
    workbook_data=workbook_data,
    output_path="output/sales.xlsx"
)
```

**示例 2：创建带格式的表格**

```python
workbook_data = {
    "sheets": [
        {
            "name": "报表",
            "rows": [
                {
                    "cells": [
                        {
                            "value": "标题",
                            "row": 1,
                            "column": 1,
                            "format": {
                                "font": {
                                    "name": "Arial",
                                    "size": 14,
                                    "bold": true,
                                    "color": "#FFFFFF"
                                },
                                "fill": {
                                    "background_color": "#4472C4"
                                }
                            }
                        }
                    ]
                }
            ]
        }
    ]
}

result = create_excel_from_json(
    workbook_data=workbook_data,
    output_path="output/formatted_report.xlsx",
    apply_formats=True
)
```

#### 错误码

- `E104`：文件写入失败
- `E201`：数据验证失败（JSON 结构不正确）
- `E202`：格式数据无效

#### 性能

- 1000 行数据：约 0.03 秒
- 支持大文件流式写入

---

### 3. modify_cell_format

**功能描述**：修改单元格的格式（字体、颜色、边框、对齐等）。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `file_path` | string | ✅ | - | Excel 文件路径 |
| `sheet_name` | string | ✅ | - | 工作表名称 |
| `cell_range` | string | ✅ | - | 单元格范围（如 "A1" 或 "A1:B10"） |
| `format_data` | object | ✅ | - | 格式数据（JSON 格式） |
| `output_path` | string | ❌ | `null` | 输出文件路径（默认覆盖原文件） |

#### 格式数据结构

```json
{
  "font": {
    "name": "Arial",
    "size": 12,
    "bold": true,
    "italic": false,
    "underline": false,
    "color": "#000000"
  },
  "fill": {
    "background_color": "#FFFF00",
    "pattern_type": "solid"
  },
  "border": {
    "top": {"style": "thin", "color": "#000000"},
    "bottom": {"style": "thin", "color": "#000000"},
    "left": {"style": "thin", "color": "#000000"},
    "right": {"style": "thin", "color": "#000000"}
  },
  "alignment": {
    "horizontal": "center",
    "vertical": "center",
    "wrap_text": false
  },
  "number_format": "0.00"
}
```

#### 返回值

```json
{
  "success": true,
  "file_path": "data/formatted.xlsx",
  "cells_modified": 10,
  "error": null
}
```

#### 使用示例

**示例 1：设置标题行格式**

```python
result = modify_cell_format(
    file_path="data/report.xlsx",
    sheet_name="Sheet1",
    cell_range="A1:J1",
    format_data={
        "font": {
            "name": "Arial",
            "size": 12,
            "bold": True,
            "color": "#FFFFFF"
        },
        "fill": {
            "background_color": "#4472C4"
        },
        "alignment": {
            "horizontal": "center",
            "vertical": "center"
        }
    }
)
```

**示例 2：设置数字格式**

```python
result = modify_cell_format(
    file_path="data/sales.xlsx",
    sheet_name="数据",
    cell_range="B2:B100",
    format_data={
        "number_format": "#,##0.00"  # 千分位，保留两位小数
    }
)
```

#### 错误码

- `E101`：文件不存在
- `E201`：工作表不存在
- `E202`：单元格范围无效
- `E203`：格式数据无效

---

### 4. merge_cells

**功能描述**：合并指定范围的单元格。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `file_path` | string | ✅ | - | Excel 文件路径 |
| `sheet_name` | string | ✅ | - | 工作表名称 |
| `cell_range` | string | ✅ | - | 要合并的单元格范围（如 "A1:B2"） |
| `output_path` | string | ❌ | `null` | 输出文件路径（默认覆盖原文件） |

#### 返回值

```json
{
  "success": true,
  "file_path": "data/merged.xlsx",
  "merged_range": "A1:B2",
  "error": null
}
```

#### 使用示例

```python
# 合并标题单元格
result = merge_cells(
    file_path="data/report.xlsx",
    sheet_name="Sheet1",
    cell_range="A1:D1"
)

if result["success"]:
    print(f"成功合并单元格：{result['merged_range']}")
```

#### 错误码

- `E101`：文件不存在
- `E201`：工作表不存在
- `E401`：单元格范围无效
- `E402`：单元格已合并（存在重叠）

---

### 5. unmerge_cells

**功能描述**：取消单元格合并。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `file_path` | string | ✅ | - | Excel 文件路径 |
| `sheet_name` | string | ✅ | - | 工作表名称 |
| `cell_range` | string | ✅ | - | 要取消合并的单元格范围（如 "A1:B2"） |
| `output_path` | string | ❌ | `null` | 输出文件路径（默认覆盖原文件） |

#### 返回值

```json
{
  "success": true,
  "file_path": "data/unmerged.xlsx",
  "unmerged_range": "A1:B2",
  "error": null
}
```

#### 使用示例

```python
result = unmerge_cells(
    file_path="data/report.xlsx",
    sheet_name="Sheet1",
    cell_range="A1:D1"
)
```

#### 错误码

- `E101`：文件不存在
- `E201`：工作表不存在
- `E403`：单元格未合并

---

### 6. set_row_heights

**功能描述**：批量设置行高。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `file_path` | string | ✅ | - | Excel 文件路径 |
| `sheet_name` | string | ✅ | - | 工作表名称 |
| `row_heights` | array | ✅ | - | 行高规格列表 |
| `output_path` | string | ❌ | `null` | 输出文件路径（默认覆盖原文件） |

**行高规格对象**：
```json
{
  "row_number": 1,  // 行号（从 1 开始）
  "height": 20.0    // 行高（单位：磅，范围 0-409）
}
```

#### 返回值

```json
{
  "success": true,
  "file_path": "data/adjusted.xlsx",
  "rows_modified": 3,
  "error": null
}
```

#### 使用示例

```python
result = set_row_heights(
    file_path="data/report.xlsx",
    sheet_name="Sheet1",
    row_heights=[
        {"row_number": 1, "height": 30.0},  # 标题行
        {"row_number": 2, "height": 20.0},
        {"row_number": 3, "height": 20.0}
    ]
)
```

#### 错误码

- `E101`：文件不存在
- `E201`：工作表不存在
- `E202`：行号无效
- `E203`：行高超出范围（0-409）

---

### 7. set_column_widths

**功能描述**：批量设置列宽。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `file_path` | string | ✅ | - | Excel 文件路径 |
| `sheet_name` | string | ✅ | - | 工作表名称 |
| `column_widths` | array | ✅ | - | 列宽规格列表 |
| `output_path` | string | ❌ | `null` | 输出文件路径（默认覆盖原文件） |

**列宽规格对象**：
```json
{
  "column_letter": "A",  // 列字母（如 "A", "B", "AA"）
  "width": 15.0          // 列宽（单位：字符宽度，范围 0-255）
}
```

#### 返回值

```json
{
  "success": true,
  "file_path": "data/adjusted.xlsx",
  "columns_modified": 3,
  "error": null
}
```

#### 使用示例

```python
result = set_column_widths(
    file_path="data/report.xlsx",
    sheet_name="Sheet1",
    column_widths=[
        {"column_letter": "A", "width": 20.0},
        {"column_letter": "B", "width": 15.0},
        {"column_letter": "C", "width": 30.0}
    ]
)
```

#### 错误码

- `E101`：文件不存在
- `E201`：工作表不存在
- `E202`：列字母无效
- `E203`：列宽超出范围（0-255）

---

### 8. manage_storage

**功能描述**：管理 Supabase Storage 中的文件（上传、下载、列出、删除、搜索）。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `operation` | string | ✅ | - | 操作类型：`upload`, `download`, `list`, `delete`, `search` |
| `file_path` | string | ❌ | `null` | 本地文件路径（用于 upload/download） |
| `remote_path` | string | ❌ | `null` | 远程文件路径（用于 upload/download/delete） |
| `bucket_name` | string | ❌ | `null` | 存储桶名称（默认使用环境变量配置） |
| `search_pattern` | string | ❌ | `null` | 搜索模式（用于 search，支持通配符） |
| `prefix` | string | ❌ | `null` | 路径前缀（用于 list） |

#### 返回值

```json
{
  "success": true,
  "operation": "upload",
  "result": {
    // 操作结果数据（根据操作类型不同）
  },
  "error": null
}
```

#### 使用示例

**示例 1：上传文件**

```python
result = manage_storage(
    operation="upload",
    file_path="local/report.xlsx",
    remote_path="reports/2024/report.xlsx",
    bucket_name="my-bucket"
)
```

**示例 2：下载文件**

```python
result = manage_storage(
    operation="download",
    file_path="local/downloaded.xlsx",
    remote_path="reports/2024/report.xlsx",
    bucket_name="my-bucket"
)
```

**示例 3：列出文件**

```python
result = manage_storage(
    operation="list",
    bucket_name="my-bucket",
    prefix="reports/2024/"
)

if result["success"]:
    files = result["result"]
    print(f"找到 {len(files)} 个文件")
```

**示例 4：搜索文件**

```python
result = manage_storage(
    operation="search",
    bucket_name="my-bucket",
    search_pattern="*.xlsx"
)
```

**示例 5：删除文件**

```python
result = manage_storage(
    operation="delete",
    remote_path="reports/old/report.xlsx",
    bucket_name="my-bucket"
)
```

#### 错误码

- `E001`：Supabase 配置错误
- `E002`：认证失败
- `E501`：网络连接失败
- `E502`：操作超时
- `E101`：文件不存在（download）
- `E104`：文件上传失败

---

### 9. set_formula

**功能描述**：为单元格设置 Excel 公式。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `file_path` | string | ✅ | - | Excel 文件路径 |
| `sheet_name` | string | ✅ | - | 工作表名称 |
| `cell` | string | ✅ | - | 单元格位置（如 "A1"） |
| `formula` | string | ✅ | - | 公式字符串（如 "=SUM(A1:A10)"） |
| `save` | boolean | ❌ | `true` | 是否保存文件 |

#### 返回值

```json
{
  "success": true,
  "cell": "A10",
  "formula": "=SUM(A1:A9)",
  "message": "公式设置成功",
  "error": null
}
```

#### 使用示例

**示例 1：设置求和公式**

```python
result = set_formula(
    file_path="data/sales.xlsx",
    sheet_name="数据",
    cell="B10",
    formula="=SUM(B2:B9)"
)
```

**示例 2：设置条件公式**

```python
result = set_formula(
    file_path="data/report.xlsx",
    sheet_name="分析",
    cell="C2",
    formula='=IF(B2>100,"优秀","良好")'
)
```

**示例 3：设置复杂公式**

```python
result = set_formula(
    file_path="data/analysis.xlsx",
    sheet_name="Sheet1",
    cell="D2",
    formula="=VLOOKUP(A2,Sheet2!A:B,2,FALSE)"
)
```

#### 支持的公式函数

**数学函数**：SUM, AVERAGE, MAX, MIN, COUNT, ROUND, ABS, POWER, SQRT

**逻辑函数**：IF, AND, OR, NOT

**文本函数**：CONCATENATE, LEN, LEFT, RIGHT, MID, UPPER, LOWER

**日期函数**：TODAY, NOW, DATE, YEAR, MONTH, DAY

**查找函数**：VLOOKUP, HLOOKUP, INDEX, MATCH

#### 错误码

- `E101`：文件不存在
- `E201`：工作表不存在
- `E301`：公式语法错误
- `E302`：公式引用无效

---

### 10. recalculate_formulas

**功能描述**：重新计算 Excel 文件中的所有公式。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `file_path` | string | ✅ | - | Excel 文件路径 |
| `sheet_name` | string | ❌ | `null` | 工作表名称（null 表示计算所有工作表） |

#### 返回值

```json
{
  "success": true,
  "count": 15,
  "results": {
    "Sheet1!A10": 450,
    "Sheet1!B10": 380,
    // ... 其他计算结果
  },
  "message": "成功计算 15 个公式",
  "error": null
}
```

#### 使用示例

**示例 1：计算所有工作表**

```python
result = recalculate_formulas(
    file_path="data/report.xlsx"
)

if result["success"]:
    print(f"计算了 {result['count']} 个公式")
```

**示例 2：计算指定工作表**

```python
result = recalculate_formulas(
    file_path="data/analysis.xlsx",
    sheet_name="数据分析"
)
```

#### 错误码

- `E101`：文件不存在
- `E201`：工作表不存在
- `E303`：循环引用检测到
- `E304`：公式计算失败

---

### 11. manage_sheets

**功能描述**：管理 Excel 工作表（创建、删除、重命名、复制、移动）。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `file_path` | string | ✅ | - | Excel 文件路径 |
| `operation` | string | ✅ | - | 操作类型：`create`, `delete`, `rename`, `copy`, `move` |
| `sheet_name` | string | ❌ | `null` | 工作表名称 |
| `new_name` | string | ❌ | `null` | 新名称（用于 rename 和 copy） |
| `position` | integer | ❌ | `null` | 位置（用于 create、copy 和 move，从 0 开始） |

#### 返回值

```json
{
  "success": true,
  "operation": "create",
  "message": "工作表创建成功",
  "error": null
}
```

#### 使用示例

**示例 1：创建工作表**

```python
result = manage_sheets(
    file_path="data/report.xlsx",
    operation="create",
    sheet_name="新数据",
    position=0  # 插入到第一个位置
)
```

**示例 2：删除工作表**

```python
result = manage_sheets(
    file_path="data/report.xlsx",
    operation="delete",
    sheet_name="临时数据"
)
```

**示例 3：重命名工作表**

```python
result = manage_sheets(
    file_path="data/report.xlsx",
    operation="rename",
    sheet_name="Sheet1",
    new_name="销售数据"
)
```

**示例 4：复制工作表**

```python
result = manage_sheets(
    file_path="data/report.xlsx",
    operation="copy",
    sheet_name="模板",
    new_name="2024年数据",
    position=1
)
```

**示例 5：移动工作表**

```python
result = manage_sheets(
    file_path="data/report.xlsx",
    operation="move",
    sheet_name="汇总",
    position=0  # 移动到第一个位置
)
```

#### 错误码

- `E101`：文件不存在
- `E401`：工作表不存在
- `E402`：工作表名称已存在
- `E403`：工作表名称无效（长度超过 31 或包含非法字符）
- `E404`：不能删除最后一个工作表
- `E405`：位置无效

---

### 12. merge_excel_files

**功能描述**：合并多个 Excel 文件为一个文件。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `file_paths` | array | ✅ | - | 要合并的 Excel 文件路径列表 |
| `output_path` | string | ✅ | - | 输出文件路径 |
| `handle_duplicates` | string | ❌ | `"rename"` | 重名处理策略：`rename`, `skip`, `overwrite` |
| `preserve_formats` | boolean | ❌ | `true` | 是否保留格式信息 |
| `sheet_names` | array | ❌ | `null` | 要合并的工作表名称列表（null 表示全部） |

#### 返回值

```json
{
  "success": true,
  "merged_sheets": 15,
  "skipped_sheets": 2,
  "renamed_sheets": 3,
  "output_path": "output/merged.xlsx",
  "error": null
}
```

#### 使用示例

**示例 1：合并所有工作表**

```python
result = merge_excel_files(
    file_paths=[
        "data/q1.xlsx",
        "data/q2.xlsx",
        "data/q3.xlsx",
        "data/q4.xlsx"
    ],
    output_path="output/annual_report.xlsx"
)

if result["success"]:
    print(f"成功合并 {result['merged_sheets']} 个工作表")
```

**示例 2：合并指定工作表**

```python
result = merge_excel_files(
    file_paths=["data/file1.xlsx", "data/file2.xlsx"],
    output_path="output/merged.xlsx",
    sheet_names=["销售数据", "库存数据"]  # 只合并这两个工作表
)
```

**示例 3：使用不同的重名策略**

```python
# 策略 1：重命名（默认）
result = merge_excel_files(
    file_paths=["data/a.xlsx", "data/b.xlsx"],
    output_path="output/merged.xlsx",
    handle_duplicates="rename"  # Sheet1 → Sheet1_2
)

# 策略 2：跳过
result = merge_excel_files(
    file_paths=["data/a.xlsx", "data/b.xlsx"],
    output_path="output/merged.xlsx",
    handle_duplicates="skip"  # 跳过重名的工作表
)

# 策略 3：覆盖
result = merge_excel_files(
    file_paths=["data/a.xlsx", "data/b.xlsx"],
    output_path="output/merged.xlsx",
    handle_duplicates="overwrite"  # 后面的覆盖前面的
)
```

**示例 4：不保留格式（提高性能）**

```python
result = merge_excel_files(
    file_paths=["data/large1.xlsx", "data/large2.xlsx"],
    output_path="output/merged.xlsx",
    preserve_formats=False  # 只合并数据，不保留格式
)
```

#### 错误码

- `E101`：文件不存在
- `E102`：文件读取失败
- `E104`：文件写入失败
- `E201`：文件列表为空
- `E202`：重名处理策略无效

#### 性能

- 合并 10 个文件（30 个工作表）：约 0.12 秒
- 支持大文件合并

---

## 错误码对照表

所有错误都包含错误码和详细信息。错误码体系如下：

### 配置和认证错误 (E001-E099)

| 错误码 | 描述 | 常见原因 | 解决方案 |
|--------|------|---------|---------|
| E001 | Supabase 配置错误 | 环境变量未设置 | 检查 `.env` 文件中的 `SUPABASE_URL` 和 `SUPABASE_KEY` |
| E002 | 认证失败 | Service Role Key 无效 | 验证 Supabase 项目设置中的密钥 |

### 文件操作错误 (E101-E199)

| 错误码 | 描述 | 常见原因 | 解决方案 |
|--------|------|---------|---------|
| E101 | 文件不存在 | 文件路径错误 | 检查文件路径是否正确 |
| E102 | 文件读取失败 | 文件损坏或权限不足 | 检查文件完整性和访问权限 |
| E103 | 文件格式无效 | 不是有效的 Excel 文件 | 确保文件是 .xlsx 格式 |
| E104 | 文件写入失败 | 磁盘空间不足或权限不足 | 检查磁盘空间和写入权限 |

### 数据验证错误 (E201-E299)

| 错误码 | 描述 | 常见原因 | 解决方案 |
|--------|------|---------|---------|
| E201 | 工作表不存在 | 工作表名称错误 | 检查工作表名称是否正确 |
| E202 | 参数验证失败 | 参数类型或范围错误 | 检查参数是否符合要求 |
| E203 | 数据格式无效 | JSON 结构不正确 | 验证 JSON 数据结构 |

### 公式相关错误 (E301-E399)

| 错误码 | 描述 | 常见原因 | 解决方案 |
|--------|------|---------|---------|
| E301 | 公式语法错误 | 公式格式不正确 | 检查公式语法（必须以 = 开头） |
| E302 | 公式引用无效 | 引用的单元格不存在 | 验证单元格引用是否正确 |
| E303 | 循环引用 | 公式之间存在循环依赖 | 检查并消除循环引用 |
| E304 | 公式计算失败 | 公式执行出错 | 检查公式逻辑和数据类型 |

### Sheet 操作错误 (E401-E499)

| 错误码 | 描述 | 常见原因 | 解决方案 |
|--------|------|---------|---------|
| E401 | 工作表不存在 | 工作表名称错误 | 检查工作表名称 |
| E402 | 工作表名称已存在 | 重名冲突 | 使用不同的名称 |
| E403 | 工作表名称无效 | 名称过长或包含非法字符 | 使用有效的名称（≤31 字符，不含 `[]:/\?*`） |
| E404 | 不能删除最后一个工作表 | 工作簿必须至少有一个工作表 | 保留至少一个工作表 |
| E405 | 位置无效 | 位置超出范围 | 使用有效的位置索引（0 到 sheet_count-1） |

### 网络和超时错误 (E501-E599)

| 错误码 | 描述 | 常见原因 | 解决方案 |
|--------|------|---------|---------|
| E501 | 网络连接失败 | 网络不可用 | 检查网络连接 |
| E502 | 操作超时 | 请求超时 | 增加超时时间或检查网络 |

---

## 数据模型

本节描述 API 中使用的主要数据模型（基于 Pydantic）。

### CellData（单元格数据）

```python
{
  "value": Any,              # 单元格值（字符串、数字、布尔值等）
  "row": int,                # 行号（从 1 开始）
  "column": int,             # 列号（从 1 开始）
  "format": CellFormat       # 单元格格式（可选）
}
```

### CellFormat（单元格格式）

```python
{
  "font": {
    "name": str,             # 字体名称（如 "Arial"）
    "size": int,             # 字体大小（如 12）
    "bold": bool,            # 是否粗体
    "italic": bool,          # 是否斜体
    "underline": bool,       # 是否下划线
    "color": str             # 字体颜色（十六进制，如 "#000000"）
  },
  "fill": {
    "background_color": str, # 背景颜色（十六进制，如 "#FFFF00"）
    "pattern_type": str      # 填充模式（如 "solid"）
  },
  "border": {
    "top": BorderStyle,      # 上边框
    "bottom": BorderStyle,   # 下边框
    "left": BorderStyle,     # 左边框
    "right": BorderStyle     # 右边框
  },
  "alignment": {
    "horizontal": str,       # 水平对齐（"left", "center", "right"）
    "vertical": str,         # 垂直对齐（"top", "center", "bottom"）
    "wrap_text": bool        # 是否自动换行
  },
  "number_format": str       # 数字格式（如 "0.00", "#,##0.00"）
}
```

### BorderStyle（边框样式）

```python
{
  "style": str,              # 边框样式（"thin", "medium", "thick", "double"）
  "color": str               # 边框颜色（十六进制，如 "#000000"）
}
```

### RowData（行数据）

```python
{
  "cells": List[CellData],   # 单元格列表
  "height": float            # 行高（可选，单位：磅）
}
```

### SheetData（工作表数据）

```python
{
  "name": str,               # 工作表名称
  "rows": List[RowData],     # 行数据列表
  "merged_cells": List[str], # 合并单元格范围列表（如 ["A1:B2", "C3:D4"]）
  "column_widths": Dict[str, float]  # 列宽字典（如 {"A": 15.0, "B": 20.0}）
}
```

### WorkbookData（工作簿数据）

```python
{
  "sheets": List[SheetData], # 工作表列表
  "metadata": {
    "created": str,          # 创建时间（ISO 8601 格式）
    "modified": str,         # 修改时间（ISO 8601 格式）
    "creator": str           # 创建者
  }
}
```

### RowHeightSpec（行高规格）

```python
{
  "row_number": int,         # 行号（从 1 开始）
  "height": float            # 行高（单位：磅，范围 0-409）
}
```

### ColumnWidthSpec（列宽规格）

```python
{
  "column_letter": str,      # 列字母（如 "A", "B", "AA"）
  "width": float             # 列宽（单位：字符宽度，范围 0-255）
}
```

---

## 最佳实践

### 1. 错误处理

始终检查返回值中的 `success` 字段：

```python
result = parse_excel_to_json(file_path="data.xlsx")

if result["success"]:
    # 处理成功情况
    workbook = result["workbook"]
else:
    # 处理错误
    print(f"错误：{result['error']}")
```

### 2. 性能优化

**使用缓存**：相同文件的重复解析会自动使用缓存。

**批量操作**：使用批量设置行高/列宽而不是逐个设置。

```python
# ✅ 推荐：批量设置
set_row_heights(
    file_path="data.xlsx",
    sheet_name="Sheet1",
    row_heights=[
        {"row_number": i, "height": 20.0}
        for i in range(1, 101)
    ]
)

# ❌ 不推荐：逐个设置（会多次打开/保存文件）
for i in range(1, 101):
    set_row_heights(
        file_path="data.xlsx",
        sheet_name="Sheet1",
        row_heights=[{"row_number": i, "height": 20.0}]
    )
```

**禁用格式提取**：处理大文件时，如果不需要格式信息，可以禁用格式提取：

```python
result = parse_excel_to_json(
    file_path="large_file.xlsx",
    extract_formats=False  # 提高性能
)
```

### 3. 文件路径管理

**使用绝对路径**：避免相对路径导致的问题。

```python
import os

file_path = os.path.abspath("data/report.xlsx")
result = parse_excel_to_json(file_path=file_path)
```

**检查文件存在**：在操作前检查文件是否存在。

```python
import os

if os.path.exists(file_path):
    result = parse_excel_to_json(file_path=file_path)
else:
    print("文件不存在")
```

### 4. Supabase 存储

**配置环境变量**：在 `.env` 文件中配置 Supabase 凭据。

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key
SUPABASE_BUCKET=your-bucket-name
```

**使用有意义的路径**：组织远程文件路径。

```python
# ✅ 推荐：有组织的路径
remote_path = f"reports/{year}/{month}/report.xlsx"

# ❌ 不推荐：扁平化路径
remote_path = "report.xlsx"
```

### 5. 公式使用

**验证公式语法**：确保公式以 `=` 开头。

```python
# ✅ 正确
formula = "=SUM(A1:A10)"

# ❌ 错误
formula = "SUM(A1:A10)"  # 缺少 =
```

**避免循环引用**：确保公式之间没有循环依赖。

```python
# ❌ 错误：循环引用
# A1: =B1+1
# B1: =A1+1
```

---

## 常见问题

### Q1：如何处理大文件？

**A**：使用以下策略：
1. 禁用格式提取（`extract_formats=False`）
2. 分批处理数据
3. 使用流式处理（对于超大文件）

### Q2：支持哪些 Excel 格式？

**A**：仅支持 `.xlsx` 格式（Office 2007+）。不支持旧版 `.xls` 格式。

### Q3：如何保留所有格式？

**A**：确保在解析和生成时都启用格式处理：
```python
# 解析时
result = parse_excel_to_json(file_path="input.xlsx", extract_formats=True)

# 生成时
result = create_excel_from_json(workbook_data=data, apply_formats=True)
```

### Q4：公式计算的限制是什么？

**A**：
- 支持 20+ 常用函数（见 `set_formula` 文档）
- 不支持数组公式
- 不支持外部引用
- 复杂公式可能需要手动验证

### Q5：如何处理合并文件时的重名工作表？

**A**：使用 `handle_duplicates` 参数：
- `"rename"`：自动重命名（Sheet1 → Sheet1_2）
- `"skip"`：跳过重名的工作表
- `"overwrite"`：后面的覆盖前面的

---

## 更多资源

- **使用示例**：查看 [examples/](examples/) 目录获取更多端到端示例
- **架构文档**：了解系统架构，参见 [architecture.md](architecture.md)
- **开发指南**：参与项目开发，参见 [development.md](development.md)
- **故障排查**：遇到问题？查看 [troubleshooting.md](troubleshooting.md)

---

**文档版本**：1.0.0
**最后更新**：2025-10-20
**维护者**：Excel MCP Server Team


