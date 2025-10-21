# 示例 3：单元格格式编辑

本示例演示如何使用格式编辑工具修改 Excel 文件中的单元格格式、合并单元格、设置行高列宽。

## 📋 目录

- [场景描述](#场景描述)
- [示例 3.1：修改单元格格式](#示例-31修改单元格格式)
- [示例 3.2：批量格式化](#示例-32批量格式化)
- [示例 3.3：合并和取消合并单元格](#示例-33合并和取消合并单元格)
- [示例 3.4：设置行高和列宽](#示例-34设置行高和列宽)
- [示例 3.5：创建专业报表](#示例-35创建专业报表)
- [常见问题](#常见问题)

---

## 场景描述

您有一个已存在的 Excel 文件，需要：
- 美化标题行（加粗、背景色、居中）
- 为数据添加边框
- 合并标题单元格
- 调整列宽以适应内容
- 设置数字格式

---

## 示例 3.1：修改单元格格式

### 修改单个单元格

```python
# 修改 A1 单元格的格式
result = modify_cell_format(
    file_path="data/report.xlsx",
    sheet_name="Sheet1",
    cell_range="A1",
    format_options={
        "font": {
            "name": "Arial",
            "size": 14,
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

if result["success"]:
    print(f"格式应用成功：{result['cells_modified']} 个单元格")
```

### 修改单元格区域

```python
# 修改 A1:D1 区域（标题行）
result = modify_cell_format(
    file_path="data/report.xlsx",
    sheet_name="Sheet1",
    cell_range="A1:D1",
    format_options={
        "font": {
            "bold": True,
            "size": 12,
            "color": "#FFFFFF"
        },
        "fill": {
            "background_color": "#4472C4"
        },
        "alignment": {
            "horizontal": "center"
        }
    }
)

if result["success"]:
    print(f"标题行格式化完成：{result['cells_modified']} 个单元格")
```

---

## 示例 3.2：批量格式化

### 为数据区域添加边框

```python
# 为 A2:D10 添加边框
result = modify_cell_format(
    file_path="data/report.xlsx",
    sheet_name="Sheet1",
    cell_range="A2:D10",
    format_options={
        "border": {
            "top": {"style": "thin", "color": "#000000"},
            "bottom": {"style": "thin", "color": "#000000"},
            "left": {"style": "thin", "color": "#000000"},
            "right": {"style": "thin", "color": "#000000"}
        }
    }
)

if result["success"]:
    print(f"边框添加成功：{result['cells_modified']} 个单元格")
```

### 设置数字格式

```python
# 为金额列设置货币格式
result = modify_cell_format(
    file_path="data/report.xlsx",
    sheet_name="Sheet1",
    cell_range="D2:D10",  # 金额列
    format_options={
        "number_format": "¥#,##0.00",  # 人民币格式
        "alignment": {
            "horizontal": "right"
        }
    }
)

if result["success"]:
    print("金额格式设置成功")
```

### 设置百分比格式

```python
# 为百分比列设置格式
result = modify_cell_format(
    file_path="data/report.xlsx",
    sheet_name="Sheet1",
    cell_range="E2:E10",
    format_options={
        "number_format": "0.00%",
        "alignment": {
            "horizontal": "center"
        }
    }
)
```

---

## 示例 3.3：合并和取消合并单元格

### 合并单元格

```python
# 合并标题单元格 A1:D1
result = merge_cells(
    file_path="data/report.xlsx",
    sheet_name="Sheet1",
    cell_range="A1:D1"
)

if result["success"]:
    print(f"单元格合并成功：{result['merged_range']}")
    
    # 为合并后的单元格设置格式
    modify_cell_format(
        file_path="data/report.xlsx",
        sheet_name="Sheet1",
        cell_range="A1",  # 合并后只需指定左上角单元格
        format_options={
            "font": {"bold": True, "size": 16},
            "alignment": {"horizontal": "center", "vertical": "center"}
        }
    )
```

### 合并多个区域

```python
# 合并多个标题区域
ranges = ["A1:D1", "A2:B2", "C2:D2"]

for cell_range in ranges:
    result = merge_cells(
        file_path="data/report.xlsx",
        sheet_name="Sheet1",
        cell_range=cell_range
    )
    if result["success"]:
        print(f"合并成功：{cell_range}")
```

### 取消合并

```python
# 取消合并 A1:D1
result = unmerge_cells(
    file_path="data/report.xlsx",
    sheet_name="Sheet1",
    cell_range="A1:D1"
)

if result["success"]:
    print(f"取消合并成功：{result['unmerged_range']}")
```

---

## 示例 3.4：设置行高和列宽

### 设置单行高度

```python
# 设置第1行高度为 30 磅
result = set_row_heights(
    file_path="data/report.xlsx",
    sheet_name="Sheet1",
    row_heights=[
        {"row_number": 1, "height": 30.0}
    ]
)

if result["success"]:
    print(f"行高设置成功：{result['rows_modified']} 行")
```

### 批量设置行高

```python
# 设置多行高度
result = set_row_heights(
    file_path="data/report.xlsx",
    sheet_name="Sheet1",
    row_heights=[
        {"row_number": 1, "height": 30.0},  # 标题行
        {"row_number": 2, "height": 20.0},  # 数据行
        {"row_number": 3, "height": 20.0},
        {"row_number": 4, "height": 20.0}
    ]
)

if result["success"]:
    print(f"批量设置行高成功：{result['rows_modified']} 行")
```

### 设置列宽

```python
# 设置列宽
result = set_column_widths(
    file_path="data/report.xlsx",
    sheet_name="Sheet1",
    column_widths=[
        {"column_letter": "A", "width": 20.0},  # 产品名称列
        {"column_letter": "B", "width": 10.0},  # 销量列
        {"column_letter": "C", "width": 12.0},  # 单价列
        {"column_letter": "D", "width": 15.0}   # 总额列
    ]
)

if result["success"]:
    print(f"列宽设置成功：{result['columns_modified']} 列")
```

### 自动调整列宽

```python
# 根据内容自动设置列宽（模拟）
def auto_fit_columns(file_path, sheet_name, columns):
    """根据内容自动调整列宽"""
    # 解析文件获取内容
    parse_result = parse_excel_to_json(
        file_path=file_path,
        extract_formats=False
    )
    
    if not parse_result["success"]:
        return
    
    # 计算每列的最大内容长度
    sheet = next(s for s in parse_result["workbook"]["sheets"] if s["name"] == sheet_name)
    max_lengths = {}
    
    for row in sheet["rows"]:
        for cell in row["cells"]:
            col_letter = chr(64 + cell["column"])  # 1->A, 2->B
            content_length = len(str(cell["value"]))
            max_lengths[col_letter] = max(max_lengths.get(col_letter, 0), content_length)
    
    # 设置列宽（字符数 * 1.2 + 2）
    column_widths = [
        {"column_letter": col, "width": min(length * 1.2 + 2, 50)}
        for col, length in max_lengths.items()
        if col in columns
    ]
    
    return set_column_widths(
        file_path=file_path,
        sheet_name=sheet_name,
        column_widths=column_widths
    )

# 使用示例
result = auto_fit_columns("data/report.xlsx", "Sheet1", ["A", "B", "C", "D"])
```

---

## 示例 3.5：创建专业报表

### 完整的报表格式化流程

```python
def format_professional_report(file_path, sheet_name):
    """将普通表格格式化为专业报表"""
    
    # 步骤 1：格式化标题行
    print("步骤 1：格式化标题行...")
    modify_cell_format(
        file_path=file_path,
        sheet_name=sheet_name,
        cell_range="A1:D1",
        format_options={
            "font": {
                "name": "微软雅黑",
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
    
    # 步骤 2：为数据区域添加边框
    print("步骤 2：添加边框...")
    modify_cell_format(
        file_path=file_path,
        sheet_name=sheet_name,
        cell_range="A1:D10",
        format_options={
            "border": {
                "top": {"style": "thin", "color": "#000000"},
                "bottom": {"style": "thin", "color": "#000000"},
                "left": {"style": "thin", "color": "#000000"},
                "right": {"style": "thin", "color": "#000000"}
            }
        }
    )
    
    # 步骤 3：设置数字格式
    print("步骤 3：设置数字格式...")
    modify_cell_format(
        file_path=file_path,
        sheet_name=sheet_name,
        cell_range="D2:D10",
        format_options={
            "number_format": "¥#,##0.00",
            "alignment": {"horizontal": "right"}
        }
    )
    
    # 步骤 4：设置行高
    print("步骤 4：设置行高...")
    set_row_heights(
        file_path=file_path,
        sheet_name=sheet_name,
        row_heights=[
            {"row_number": 1, "height": 25.0}  # 标题行
        ] + [
            {"row_number": i, "height": 18.0}  # 数据行
            for i in range(2, 11)
        ]
    )
    
    # 步骤 5：设置列宽
    print("步骤 5：设置列宽...")
    set_column_widths(
        file_path=file_path,
        sheet_name=sheet_name,
        column_widths=[
            {"column_letter": "A", "width": 20.0},
            {"column_letter": "B", "width": 12.0},
            {"column_letter": "C", "width": 12.0},
            {"column_letter": "D", "width": 15.0}
        ]
    )
    
    print("✅ 报表格式化完成！")

# 使用示例
format_professional_report("data/sales_report.xlsx", "Sheet1")
```

---

## 常见问题

### Q1：如何设置交替行颜色（斑马纹）？

**A**：循环设置奇偶行的背景色。

```python
# 设置奇数行为白色，偶数行为浅灰色
for row_num in range(2, 11):
    bg_color = "#FFFFFF" if row_num % 2 == 0 else "#F2F2F2"
    modify_cell_format(
        file_path="data/report.xlsx",
        sheet_name="Sheet1",
        cell_range=f"A{row_num}:D{row_num}",
        format_options={
            "fill": {"background_color": bg_color}
        }
    )
```

### Q2：如何设置条件格式（如负数显示为红色）？

**A**：先解析数据，然后根据条件应用格式。

```python
# 解析数据
result = parse_excel_to_json(file_path="data/report.xlsx")
sheet = result["workbook"]["sheets"][0]

# 找出负数单元格并设置为红色
for row in sheet["rows"]:
    for cell in row["cells"]:
        if isinstance(cell["value"], (int, float)) and cell["value"] < 0:
            cell_ref = f"{chr(64 + cell['column'])}{cell['row']}"
            modify_cell_format(
                file_path="data/report.xlsx",
                sheet_name="Sheet1",
                cell_range=cell_ref,
                format_options={
                    "font": {"color": "#FF0000"}
                }
            )
```

### Q3：格式修改会覆盖原有格式吗？

**A**：是的，`modify_cell_format` 会覆盖指定的格式属性。如果要保留部分格式，需要先解析获取原格式，然后合并。

```python
# 先解析获取原格式
result = parse_excel_to_json(file_path="data/report.xlsx", extract_formats=True)
# 获取 A1 的原格式
original_format = result["workbook"]["sheets"][0]["rows"][0]["cells"][0]["format"]

# 合并格式（只修改字体颜色，保留其他格式）
new_format = original_format.copy()
new_format["font"]["color"] = "#FF0000"

# 应用新格式
modify_cell_format(
    file_path="data/report.xlsx",
    sheet_name="Sheet1",
    cell_range="A1",
    format_options=new_format
)
```

---

## 下一步

- **示例 4**：[公式操作](04-formula-operations.md) - 学习如何使用公式
- **示例 5**：[文件合并](05-file-merging.md) - 学习如何合并多个文件
- **API 参考**：[格式编辑工具](../api.md#3-modify_cell_format) - 查看完整 API 文档

---

**提示**：批量格式化时，建议一次性设置多个单元格的格式，而不是逐个设置，以提高性能。

