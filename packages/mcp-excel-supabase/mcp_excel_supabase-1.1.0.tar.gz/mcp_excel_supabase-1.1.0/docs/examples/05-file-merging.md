# 示例 5：文件合并

本示例演示如何使用 `merge_excel_files` 工具合并多个 Excel 文件，以及如何使用 `manage_sheets` 工具管理工作表。

## 📋 目录

- [场景描述](#场景描述)
- [示例 5.1：合并多个文件](#示例-51合并多个文件)
- [示例 5.2：处理重名工作表](#示例-52处理重名工作表)
- [示例 5.3：合并指定工作表](#示例-53合并指定工作表)
- [示例 5.4：工作表管理](#示例-54工作表管理)
- [示例 5.5：批量处理季度报表](#示例-55批量处理季度报表)
- [常见问题](#常见问题)

---

## 场景描述

您有多个 Excel 文件需要合并：
- 4 个季度报表需要合并为年度报表
- 多个部门的数据需要汇总
- 处理工作表重名问题
- 管理工作表（创建、删除、重命名、移动）

---

## 示例 5.1：合并多个文件

### 基础合并

```python
# 合并 4 个季度报表
result = merge_excel_files(
    file_paths=[
        "data/q1_report.xlsx",
        "data/q2_report.xlsx",
        "data/q3_report.xlsx",
        "data/q4_report.xlsx"
    ],
    output_path="output/annual_report.xlsx"
)

if result["success"]:
    print(f"✅ 合并成功！")
    print(f"合并的工作表数：{result['merged_sheets']}")
    print(f"跳过的工作表数：{result['skipped_sheets']}")
    print(f"重命名的工作表数：{result['renamed_sheets']}")
    print(f"输出文件：{result['output_path']}")
```

### 输出示例

```
✅ 合并成功！
合并的工作表数：12
跳过的工作表数：0
重命名的工作表数：3
输出文件：output/annual_report.xlsx
```

---

## 示例 5.2：处理重名工作表

### 策略 1：自动重命名（默认）

```python
# 重名工作表会自动重命名：Sheet1 → Sheet1_2
result = merge_excel_files(
    file_paths=[
        "data/file1.xlsx",  # 包含 Sheet1
        "data/file2.xlsx"   # 也包含 Sheet1
    ],
    output_path="output/merged.xlsx",
    handle_duplicates="rename"  # 默认策略
)

if result["success"]:
    print(f"重命名的工作表：{result['renamed_sheets']}")
    # 输出：重命名的工作表：1
    # file2.xlsx 的 Sheet1 被重命名为 Sheet1_2
```

### 策略 2：跳过重名工作表

```python
# 跳过重名的工作表（保留第一个）
result = merge_excel_files(
    file_paths=[
        "data/file1.xlsx",  # 包含 Sheet1
        "data/file2.xlsx"   # 也包含 Sheet1（会被跳过）
    ],
    output_path="output/merged.xlsx",
    handle_duplicates="skip"
)

if result["success"]:
    print(f"跳过的工作表：{result['skipped_sheets']}")
    # 输出：跳过的工作表：1
```

### 策略 3：覆盖重名工作表

```python
# 后面的文件覆盖前面的同名工作表
result = merge_excel_files(
    file_paths=[
        "data/file1.xlsx",  # 包含 Sheet1（会被覆盖）
        "data/file2.xlsx"   # 也包含 Sheet1（保留这个）
    ],
    output_path="output/merged.xlsx",
    handle_duplicates="overwrite"
)

if result["success"]:
    print("后面的文件覆盖了前面的同名工作表")
```

---

## 示例 5.3：合并指定工作表

### 只合并特定工作表

```python
# 只合并名为"销售数据"和"库存数据"的工作表
result = merge_excel_files(
    file_paths=[
        "data/dept1.xlsx",
        "data/dept2.xlsx",
        "data/dept3.xlsx"
    ],
    output_path="output/selected_sheets.xlsx",
    sheet_names=["销售数据", "库存数据"]  # 只合并这两个工作表
)

if result["success"]:
    print(f"合并了 {result['merged_sheets']} 个指定的工作表")
```

### 不保留格式（提高性能）

```python
# 合并大文件时，不保留格式可以提高性能
result = merge_excel_files(
    file_paths=[
        "data/large1.xlsx",
        "data/large2.xlsx",
        "data/large3.xlsx"
    ],
    output_path="output/merged_data_only.xlsx",
    preserve_formats=False  # 只合并数据，不保留格式
)

if result["success"]:
    print("数据合并完成（不含格式）")
```

---

## 示例 5.4：工作表管理

### 创建工作表

```python
# 在文件中创建新工作表
result = manage_sheets(
    file_path="data/report.xlsx",
    operation="create",
    sheet_name="新数据",
    position=0  # 插入到第一个位置
)

if result["success"]:
    print(f"✅ {result['message']}")
```

### 删除工作表

```python
# 删除不需要的工作表
result = manage_sheets(
    file_path="data/report.xlsx",
    operation="delete",
    sheet_name="临时数据"
)

if result["success"]:
    print(f"✅ {result['message']}")
```

### 重命名工作表

```python
# 重命名工作表
result = manage_sheets(
    file_path="data/report.xlsx",
    operation="rename",
    sheet_name="Sheet1",
    new_name="销售数据"
)

if result["success"]:
    print(f"✅ 工作表已重命名")
```

### 复制工作表

```python
# 复制工作表作为模板
result = manage_sheets(
    file_path="data/report.xlsx",
    operation="copy",
    sheet_name="模板",
    new_name="2024年1月",
    position=1  # 插入到第2个位置
)

if result["success"]:
    print(f"✅ 工作表已复制")
```

### 移动工作表

```python
# 移动工作表到指定位置
result = manage_sheets(
    file_path="data/report.xlsx",
    operation="move",
    sheet_name="汇总",
    position=0  # 移动到第一个位置
)

if result["success"]:
    print(f"✅ 工作表已移动")
```

---

## 示例 5.5：批量处理季度报表

### 完整的季度报表合并流程

```python
def merge_quarterly_reports(year):
    """合并季度报表并整理工作表"""
    
    # 步骤 1：合并 4 个季度的文件
    print(f"步骤 1：合并 {year} 年季度报表...")
    merge_result = merge_excel_files(
        file_paths=[
            f"data/{year}_q1.xlsx",
            f"data/{year}_q2.xlsx",
            f"data/{year}_q3.xlsx",
            f"data/{year}_q4.xlsx"
        ],
        output_path=f"output/{year}_annual.xlsx",
        handle_duplicates="rename"
    )
    
    if not merge_result["success"]:
        print(f"❌ 合并失败：{merge_result['error']}")
        return
    
    print(f"✅ 合并完成：{merge_result['merged_sheets']} 个工作表")
    
    # 步骤 2：创建汇总工作表
    print("步骤 2：创建汇总工作表...")
    manage_sheets(
        file_path=f"output/{year}_annual.xlsx",
        operation="create",
        sheet_name="年度汇总",
        position=0  # 放在第一个位置
    )
    
    # 步骤 3：重命名季度工作表
    print("步骤 3：重命名工作表...")
    quarters = ["Q1", "Q2", "Q3", "Q4"]
    for i, quarter in enumerate(quarters):
        # 假设原工作表名为 "销售数据"
        old_name = f"销售数据_{i+1}" if i > 0 else "销售数据"
        new_name = f"{year}年{quarter}销售"
        
        manage_sheets(
            file_path=f"output/{year}_annual.xlsx",
            operation="rename",
            sheet_name=old_name,
            new_name=new_name
        )
    
    # 步骤 4：删除临时工作表
    print("步骤 4：清理临时工作表...")
    temp_sheets = ["临时数据", "备份"]
    for sheet_name in temp_sheets:
        manage_sheets(
            file_path=f"output/{year}_annual.xlsx",
            operation="delete",
            sheet_name=sheet_name
        )
    
    print(f"✅ {year} 年度报表处理完成！")

# 使用示例
merge_quarterly_reports(2024)
```

### 批量合并多个部门的数据

```python
def merge_department_reports(departments, month):
    """合并多个部门的月度报表"""
    
    # 构建文件路径列表
    file_paths = [
        f"data/{dept}_{month}.xlsx"
        for dept in departments
    ]
    
    # 合并文件
    result = merge_excel_files(
        file_paths=file_paths,
        output_path=f"output/all_departments_{month}.xlsx",
        handle_duplicates="rename"
    )
    
    if result["success"]:
        print(f"✅ 合并了 {len(departments)} 个部门的数据")
        
        # 为每个部门的工作表添加前缀
        for i, dept in enumerate(departments):
            # 假设每个文件有一个名为 "数据" 的工作表
            old_name = f"数据_{i+1}" if i > 0 else "数据"
            new_name = f"{dept}_数据"
            
            manage_sheets(
                file_path=f"output/all_departments_{month}.xlsx",
                operation="rename",
                sheet_name=old_name,
                new_name=new_name
            )
        
        print("✅ 工作表重命名完成")

# 使用示例
departments = ["销售部", "市场部", "技术部", "财务部"]
merge_department_reports(departments, "2024-01")
```

---

## 常见问题

### Q1：合并后的工作表顺序是什么？

**A**：按照 `file_paths` 列表的顺序，每个文件的工作表按原顺序添加。

```python
# 文件顺序：file1.xlsx, file2.xlsx
# file1.xlsx 包含：SheetA, SheetB
# file2.xlsx 包含：SheetC, SheetD
# 合并后顺序：SheetA, SheetB, SheetC, SheetD
```

### Q2：如何在合并前预览工作表名称？

**A**：先解析每个文件，查看工作表名称。

```python
def preview_sheets(file_paths):
    """预览所有文件的工作表名称"""
    for file_path in file_paths:
        result = parse_excel_to_json(
            file_path=file_path,
            extract_formats=False
        )
        if result["success"]:
            sheet_names = [s["name"] for s in result["workbook"]["sheets"]]
            print(f"{file_path}: {sheet_names}")

# 使用示例
preview_sheets([
    "data/q1.xlsx",
    "data/q2.xlsx",
    "data/q3.xlsx"
])
```

### Q3：可以合并不同格式的文件吗？

**A**：不可以。所有文件必须是 `.xlsx` 格式。

### Q4：合并大文件时如何提高性能？

**A**：设置 `preserve_formats=False`。

```python
result = merge_excel_files(
    file_paths=large_files,
    output_path="output/merged.xlsx",
    preserve_formats=False  # 不保留格式，提高性能
)
```

### Q5：如何处理合并失败？

**A**：检查错误码并处理。

```python
result = merge_excel_files(
    file_paths=file_paths,
    output_path="output/merged.xlsx"
)

if not result["success"]:
    error = result["error"]
    if "E101" in error:
        print("某个文件不存在，请检查路径")
    elif "E102" in error:
        print("某个文件读取失败，可能已损坏")
    elif "E201" in error:
        print("文件列表为空")
```

### Q6：删除工作表时的限制？

**A**：不能删除最后一个工作表（错误码 E404）。

```python
# 确保至少保留一个工作表
result = manage_sheets(
    file_path="data/report.xlsx",
    operation="delete",
    sheet_name="Sheet1"
)

if not result["success"] and "E404" in result["error"]:
    print("不能删除最后一个工作表")
```

---

## 下一步

- **示例 6**：[Supabase 集成](06-supabase-integration.md) - 学习云存储操作
- **API 参考**：[merge_excel_files](../api.md#12-merge_excel_files) - 查看完整 API 文档
- **API 参考**：[manage_sheets](../api.md#11-manage_sheets) - 查看工作表管理 API

---

**提示**：合并大量文件时，建议先测试小批量，确认策略正确后再批量处理。

