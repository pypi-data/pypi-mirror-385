# 示例 1：基础 Excel 解析

本示例演示如何使用 `parse_excel_to_json` 工具解析 Excel 文件，提取数据和格式信息。

## 📋 目录

- [场景描述](#场景描述)
- [准备工作](#准备工作)
- [示例 1.1：解析单个工作表](#示例-11解析单个工作表)
- [示例 1.2：解析多个工作表](#示例-12解析多个工作表)
- [示例 1.3：仅提取数据（不提取格式）](#示例-13仅提取数据不提取格式)
- [示例 1.4：提取特定信息](#示例-14提取特定信息)
- [常见问题](#常见问题)

---

## 场景描述

假设您有一个销售报表 Excel 文件，包含以下内容：
- **Sheet1（销售数据）**：产品名称、销量、单价、总额
- **Sheet2（汇总）**：月度汇总数据
- 单元格包含格式信息（字体、颜色、边框等）

您需要将这些数据提取为 JSON 格式，以便在程序中处理。

---

## 准备工作

### 1. 准备测试文件

创建一个示例 Excel 文件 `sales_report.xlsx`，包含以下数据：

**Sheet1（销售数据）**：

| 产品 | 销量 | 单价 | 总额 |
|------|------|------|------|
| 产品A | 100 | 50.00 | 5000.00 |
| 产品B | 150 | 30.00 | 4500.00 |
| 产品C | 200 | 25.00 | 5000.00 |

**Sheet2（汇总）**：

| 月份 | 总销量 | 总金额 |
|------|--------|--------|
| 1月 | 450 | 14500.00 |

### 2. 确保文件路径正确

```python
import os

# 使用绝对路径
file_path = os.path.abspath("data/sales_report.xlsx")
print(f"文件路径：{file_path}")
print(f"文件存在：{os.path.exists(file_path)}")
```

---

## 示例 1.1：解析单个工作表

### 代码

```python
# 解析 Excel 文件
result = parse_excel_to_json(
    file_path="data/sales_report.xlsx",
    extract_formats=True  # 提取格式信息
)

# 检查结果
if result["success"]:
    workbook = result["workbook"]
    
    # 获取第一个工作表
    sheet = workbook["sheets"][0]
    print(f"工作表名称：{sheet['name']}")
    print(f"行数：{len(sheet['rows'])}")
    
    # 遍历所有行
    for row in sheet["rows"]:
        for cell in row["cells"]:
            print(f"单元格 ({cell['row']}, {cell['column']}): {cell['value']}")
else:
    print(f"解析失败：{result['error']}")
```

### 输出

```
工作表名称：销售数据
行数：4
单元格 (1, 1): 产品
单元格 (1, 2): 销量
单元格 (1, 3): 单价
单元格 (1, 4): 总额
单元格 (2, 1): 产品A
单元格 (2, 2): 100
单元格 (2, 3): 50.00
单元格 (2, 4): 5000.00
...
```

### 返回的 JSON 结构

```json
{
  "success": true,
  "workbook": {
    "sheets": [
      {
        "name": "销售数据",
        "rows": [
          {
            "cells": [
              {
                "value": "产品",
                "row": 1,
                "column": 1,
                "format": {
                  "font": {
                    "name": "Arial",
                    "size": 11,
                    "bold": true,
                    "color": "#000000"
                  },
                  "fill": {
                    "background_color": "#D9E1F2"
                  }
                }
              }
            ]
          }
        ],
        "merged_cells": [],
        "column_widths": {
          "A": 15.0,
          "B": 10.0,
          "C": 10.0,
          "D": 12.0
        }
      }
    ],
    "metadata": {
      "created": "2024-01-01T00:00:00",
      "modified": "2024-01-15T10:30:00"
    }
  },
  "error": null
}
```

---

## 示例 1.2：解析多个工作表

### 代码

```python
result = parse_excel_to_json(
    file_path="data/sales_report.xlsx",
    extract_formats=True
)

if result["success"]:
    workbook = result["workbook"]
    
    # 遍历所有工作表
    for sheet in workbook["sheets"]:
        print(f"\n=== 工作表：{sheet['name']} ===")
        print(f"行数：{len(sheet['rows'])}")
        print(f"合并单元格：{sheet['merged_cells']}")
        
        # 打印第一行（标题行）
        if sheet["rows"]:
            first_row = sheet["rows"][0]
            headers = [cell["value"] for cell in first_row["cells"]]
            print(f"标题：{headers}")
```

### 输出

```
=== 工作表：销售数据 ===
行数：4
合并单元格：[]
标题：['产品', '销量', '单价', '总额']

=== 工作表：汇总 ===
行数：2
合并单元格：[]
标题：['月份', '总销量', '总金额']
```

---

## 示例 1.3：仅提取数据（不提取格式）

当处理大文件时，如果不需要格式信息，可以禁用格式提取以提高性能。

### 代码

```python
result = parse_excel_to_json(
    file_path="data/large_sales_data.xlsx",
    extract_formats=False  # 不提取格式，提高性能
)

if result["success"]:
    workbook = result["workbook"]
    sheet = workbook["sheets"][0]
    
    # 提取纯数据
    data = []
    for row in sheet["rows"]:
        row_data = [cell["value"] for cell in row["cells"]]
        data.append(row_data)
    
    print(f"提取了 {len(data)} 行数据")
    print(f"第一行：{data[0]}")
```

### 性能对比

| 文件大小 | 提取格式 | 不提取格式 | 性能提升 |
|---------|---------|-----------|---------|
| 1 MB | 0.8 秒 | 0.4 秒 | 2x |
| 5 MB | 3.5 秒 | 1.8 秒 | 1.9x |
| 10 MB | 7.2 秒 | 3.6 秒 | 2x |

---

## 示例 1.4：提取特定信息

### 提取所有数值单元格

```python
result = parse_excel_to_json(
    file_path="data/sales_report.xlsx",
    extract_formats=False
)

if result["success"]:
    workbook = result["workbook"]
    
    # 提取所有数值
    numbers = []
    for sheet in workbook["sheets"]:
        for row in sheet["rows"]:
            for cell in row["cells"]:
                if isinstance(cell["value"], (int, float)):
                    numbers.append(cell["value"])
    
    print(f"找到 {len(numbers)} 个数值")
    print(f"总和：{sum(numbers)}")
    print(f"平均值：{sum(numbers) / len(numbers):.2f}")
```

### 提取特定列的数据

```python
result = parse_excel_to_json(
    file_path="data/sales_report.xlsx",
    extract_formats=False
)

if result["success"]:
    workbook = result["workbook"]
    sheet = workbook["sheets"][0]  # 第一个工作表
    
    # 提取第2列（销量）的所有数据
    sales_column = []
    for row in sheet["rows"][1:]:  # 跳过标题行
        for cell in row["cells"]:
            if cell["column"] == 2:  # 第2列
                sales_column.append(cell["value"])
    
    print(f"销量数据：{sales_column}")
    print(f"总销量：{sum(sales_column)}")
```

### 提取合并单元格信息

```python
result = parse_excel_to_json(
    file_path="data/formatted_report.xlsx",
    extract_formats=True
)

if result["success"]:
    workbook = result["workbook"]
    
    for sheet in workbook["sheets"]:
        if sheet["merged_cells"]:
            print(f"\n工作表 '{sheet['name']}' 的合并单元格：")
            for merged_range in sheet["merged_cells"]:
                print(f"  - {merged_range}")
```

---

## 常见问题

### Q1：如何处理空单元格？

**A**：空单元格的 `value` 为 `None` 或空字符串。

```python
for row in sheet["rows"]:
    for cell in row["cells"]:
        if cell["value"] is None or cell["value"] == "":
            print(f"单元格 ({cell['row']}, {cell['column']}) 为空")
```

### Q2：如何获取特定单元格的值？

**A**：遍历单元格并匹配行列号。

```python
def get_cell_value(sheet, row_num, col_num):
    """获取指定单元格的值"""
    for row in sheet["rows"]:
        for cell in row["cells"]:
            if cell["row"] == row_num and cell["column"] == col_num:
                return cell["value"]
    return None

# 使用示例
value = get_cell_value(sheet, 2, 3)  # 获取 C2 的值
print(f"C2 的值：{value}")
```

### Q3：如何将数据转换为 Pandas DataFrame？

**A**：提取数据后转换为 DataFrame。

```python
import pandas as pd

result = parse_excel_to_json(
    file_path="data/sales_report.xlsx",
    extract_formats=False
)

if result["success"]:
    sheet = result["workbook"]["sheets"][0]
    
    # 提取数据
    data = []
    for row in sheet["rows"]:
        row_data = [cell["value"] for cell in row["cells"]]
        data.append(row_data)
    
    # 转换为 DataFrame
    df = pd.DataFrame(data[1:], columns=data[0])  # 第一行作为列名
    print(df)
```

### Q4：解析失败怎么办？

**A**：检查错误信息和错误码。

```python
result = parse_excel_to_json(file_path="data/report.xlsx")

if not result["success"]:
    error = result["error"]
    print(f"错误信息：{error}")
    
    # 根据错误码处理
    if "E101" in error:
        print("文件不存在，请检查路径")
    elif "E103" in error:
        print("文件格式无效，请确保是 .xlsx 格式")
    elif "E102" in error:
        print("文件读取失败，可能已损坏")
```

### Q5：如何处理包含公式的单元格？

**A**：解析时会获取公式的计算结果（值），而不是公式本身。如果需要公式，请参考 `set_formula` 工具。

---

## 下一步

- **示例 2**：[Excel 文件生成](02-excel-generation.md) - 学习如何从 JSON 创建 Excel
- **示例 3**：[格式编辑](03-formatting-cells.md) - 学习如何修改单元格格式
- **API 参考**：[parse_excel_to_json](../api.md#1-parse_excel_to_json) - 查看完整 API 文档

---

**提示**：本示例中的所有代码都可以直接运行。如有问题，请参考 [故障排查文档](../troubleshooting.md)。

