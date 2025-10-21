# 示例 4：公式操作

本示例演示如何使用 `set_formula` 和 `recalculate_formulas` 工具在 Excel 文件中设置和计算公式。

## 📋 目录

- [场景描述](#场景描述)
- [支持的公式函数](#支持的公式函数)
- [示例 4.1：基础公式](#示例-41基础公式)
- [示例 4.2：统计函数](#示例-42统计函数)
- [示例 4.3：逻辑函数](#示例-43逻辑函数)
- [示例 4.4：文本函数](#示例-44文本函数)
- [示例 4.5：批量设置公式](#示例-45批量设置公式)
- [示例 4.6：重新计算公式](#示例-46重新计算公式)
- [常见问题](#常见问题)

---

## 场景描述

您需要在 Excel 文件中：
- 计算销售总额（单价 × 数量）
- 统计总销量和平均值
- 根据条件显示不同结果
- 处理文本数据

---

## 支持的公式函数

Excel MCP Server 支持以下 20+ 常用函数：

### 数学函数
- `SUM`：求和
- `AVERAGE`：平均值
- `MIN`：最小值
- `MAX`：最大值
- `ROUND`：四舍五入
- `ABS`：绝对值
- `SQRT`：平方根
- `POWER`：幂运算

### 统计函数
- `COUNT`：计数（数值）
- `COUNTA`：计数（非空）
- `COUNTIF`：条件计数

### 逻辑函数
- `IF`：条件判断
- `AND`：逻辑与
- `OR`：逻辑或
- `NOT`：逻辑非

### 文本函数
- `CONCATENATE`：连接文本
- `LEFT`：左侧字符
- `RIGHT`：右侧字符
- `MID`：中间字符
- `LEN`：文本长度
- `UPPER`：转大写
- `LOWER`：转小写

---

## 示例 4.1：基础公式

### 计算总额（单价 × 数量）

```python
# 在 D2 单元格设置公式：=B2*C2
result = set_formula(
    file_path="data/sales.xlsx",
    sheet_name="Sheet1",
    cell_reference="D2",
    formula="=B2*C2"
)

if result["success"]:
    print(f"公式设置成功：{result['formula']}")
    print(f"计算结果：{result['calculated_value']}")
```

### 批量设置相同类型的公式

```python
# 为 D2:D10 设置公式
for row in range(2, 11):
    result = set_formula(
        file_path="data/sales.xlsx",
        sheet_name="Sheet1",
        cell_reference=f"D{row}",
        formula=f"=B{row}*C{row}"
    )
    if result["success"]:
        print(f"D{row}: {result['calculated_value']}")
```

---

## 示例 4.2：统计函数

### 求和

```python
# 计算总销量：=SUM(B2:B10)
result = set_formula(
    file_path="data/sales.xlsx",
    sheet_name="Sheet1",
    cell_reference="B11",
    formula="=SUM(B2:B10)"
)

if result["success"]:
    print(f"总销量：{result['calculated_value']}")
```

### 平均值

```python
# 计算平均单价：=AVERAGE(C2:C10)
result = set_formula(
    file_path="data/sales.xlsx",
    sheet_name="Sheet1",
    cell_reference="C11",
    formula="=AVERAGE(C2:C10)"
)

if result["success"]:
    print(f"平均单价：{result['calculated_value']:.2f}")
```

### 最大值和最小值

```python
# 最大销量
result = set_formula(
    file_path="data/sales.xlsx",
    sheet_name="Sheet1",
    cell_reference="E2",
    formula="=MAX(B2:B10)"
)
print(f"最大销量：{result['calculated_value']}")

# 最小销量
result = set_formula(
    file_path="data/sales.xlsx",
    sheet_name="Sheet1",
    cell_reference="E3",
    formula="=MIN(B2:B10)"
)
print(f"最小销量：{result['calculated_value']}")
```

### 计数

```python
# 统计有多少个产品
result = set_formula(
    file_path="data/sales.xlsx",
    sheet_name="Sheet1",
    cell_reference="E4",
    formula="=COUNTA(A2:A10)"
)
print(f"产品数量：{result['calculated_value']}")

# 统计销量大于100的产品数量
result = set_formula(
    file_path="data/sales.xlsx",
    sheet_name="Sheet1",
    cell_reference="E5",
    formula="=COUNTIF(B2:B10,\">100\")"
)
print(f"销量>100的产品：{result['calculated_value']}")
```

---

## 示例 4.3：逻辑函数

### IF 条件判断

```python
# 如果销量>100，显示"优秀"，否则显示"一般"
result = set_formula(
    file_path="data/sales.xlsx",
    sheet_name="Sheet1",
    cell_reference="E2",
    formula='=IF(B2>100,"优秀","一般")'
)

if result["success"]:
    print(f"评级：{result['calculated_value']}")
```

### 嵌套 IF

```python
# 多级评级：>200优秀，>100良好，否则一般
result = set_formula(
    file_path="data/sales.xlsx",
    sheet_name="Sheet1",
    cell_reference="E2",
    formula='=IF(B2>200,"优秀",IF(B2>100,"良好","一般"))'
)

if result["success"]:
    print(f"评级：{result['calculated_value']}")
```

### AND/OR 逻辑

```python
# 销量>100 且 单价>50
result = set_formula(
    file_path="data/sales.xlsx",
    sheet_name="Sheet1",
    cell_reference="F2",
    formula='=IF(AND(B2>100,C2>50),"高价值","普通")'
)

# 销量>200 或 单价>100
result = set_formula(
    file_path="data/sales.xlsx",
    sheet_name="Sheet1",
    cell_reference="G2",
    formula='=IF(OR(B2>200,C2>100),"重点关注","正常")'
)
```

---

## 示例 4.4：文本函数

### 连接文本

```python
# 连接产品名称和销量：产品A (100)
result = set_formula(
    file_path="data/sales.xlsx",
    sheet_name="Sheet1",
    cell_reference="E2",
    formula='=CONCATENATE(A2," (",B2,")")'
)

if result["success"]:
    print(f"结果：{result['calculated_value']}")
```

### 提取文本

```python
# 提取产品名称的前3个字符
result = set_formula(
    file_path="data/sales.xlsx",
    sheet_name="Sheet1",
    cell_reference="F2",
    formula="=LEFT(A2,3)"
)

# 提取后2个字符
result = set_formula(
    file_path="data/sales.xlsx",
    sheet_name="Sheet1",
    cell_reference="G2",
    formula="=RIGHT(A2,2)"
)

# 提取中间字符（从第2个开始，提取3个）
result = set_formula(
    file_path="data/sales.xlsx",
    sheet_name="Sheet1",
    cell_reference="H2",
    formula="=MID(A2,2,3)"
)
```

### 文本长度和大小写

```python
# 获取文本长度
result = set_formula(
    file_path="data/sales.xlsx",
    sheet_name="Sheet1",
    cell_reference="I2",
    formula="=LEN(A2)"
)

# 转大写
result = set_formula(
    file_path="data/sales.xlsx",
    sheet_name="Sheet1",
    cell_reference="J2",
    formula="=UPPER(A2)"
)

# 转小写
result = set_formula(
    file_path="data/sales.xlsx",
    sheet_name="Sheet1",
    cell_reference="K2",
    formula="=LOWER(A2)"
)
```

---

## 示例 4.5：批量设置公式

### 创建完整的计算表

```python
def create_sales_report_with_formulas(file_path):
    """创建带公式的销售报表"""
    
    # 步骤 1：为每行设置总额公式（D列 = B列 * C列）
    print("设置总额公式...")
    for row in range(2, 11):
        set_formula(
            file_path=file_path,
            sheet_name="Sheet1",
            cell_reference=f"D{row}",
            formula=f"=B{row}*C{row}"
        )
    
    # 步骤 2：设置汇总行公式
    print("设置汇总公式...")
    
    # 总销量
    set_formula(
        file_path=file_path,
        sheet_name="Sheet1",
        cell_reference="B11",
        formula="=SUM(B2:B10)"
    )
    
    # 平均单价
    set_formula(
        file_path=file_path,
        sheet_name="Sheet1",
        cell_reference="C11",
        formula="=AVERAGE(C2:C10)"
    )
    
    # 总金额
    set_formula(
        file_path=file_path,
        sheet_name="Sheet1",
        cell_reference="D11",
        formula="=SUM(D2:D10)"
    )
    
    # 步骤 3：设置评级列
    print("设置评级公式...")
    for row in range(2, 11):
        set_formula(
            file_path=file_path,
            sheet_name="Sheet1",
            cell_reference=f"E{row}",
            formula=f'=IF(B{row}>150,"优秀",IF(B{row}>100,"良好","一般"))'
        )
    
    print("✅ 公式设置完成！")

# 使用示例
create_sales_report_with_formulas("data/sales.xlsx")
```

---

## 示例 4.6：重新计算公式

### 修改数据后重新计算

```python
# 场景：修改了某些单元格的值，需要重新计算所有公式

# 步骤 1：修改数据（假设通过其他方式修改了 B2 的值）

# 步骤 2：重新计算所有公式
result = recalculate_formulas(
    file_path="data/sales.xlsx",
    sheet_name="Sheet1"
)

if result["success"]:
    print(f"重新计算成功：{result['formulas_recalculated']} 个公式")
    print(f"更新的单元格：{result['cells_updated']}")
```

### 检查计算结果

```python
# 重新计算后，解析文件查看结果
result = recalculate_formulas(
    file_path="data/sales.xlsx",
    sheet_name="Sheet1"
)

if result["success"]:
    # 解析文件
    parse_result = parse_excel_to_json(
        file_path="data/sales.xlsx",
        extract_formats=False
    )
    
    # 查看 D11（总金额）的值
    sheet = parse_result["workbook"]["sheets"][0]
    for row in sheet["rows"]:
        for cell in row["cells"]:
            if cell["row"] == 11 and cell["column"] == 4:
                print(f"总金额：{cell['value']}")
```

---

## 常见问题

### Q1：公式必须以 = 开头吗？

**A**：是的，所有公式必须以 `=` 开头。

```python
# ✅ 正确
formula = "=SUM(A1:A10)"

# ❌ 错误
formula = "SUM(A1:A10)"  # 缺少 =
```

### Q2：如何引用其他工作表的单元格？

**A**：使用 `工作表名!单元格` 格式。

```python
# 引用 Sheet2 的 A1 单元格
formula = "=Sheet2!A1"

# 引用 Sheet2 的区域
formula = "=SUM(Sheet2!A1:A10)"
```

### Q3：支持数组公式吗？

**A**：不支持。当前仅支持单个单元格的公式。

### Q4：如何处理循环引用？

**A**：系统会自动检测循环引用并返回错误（E303）。

```python
# 这会导致循环引用错误
set_formula(file_path="data.xlsx", sheet_name="Sheet1", cell_reference="A1", formula="=B1")
set_formula(file_path="data.xlsx", sheet_name="Sheet1", cell_reference="B1", formula="=A1")
# 错误：E303 循环引用检测到
```

### Q5：公式计算失败怎么办？

**A**：检查错误信息，常见原因：
- 引用的单元格不存在（E302）
- 公式语法错误（E301）
- 不支持的函数
- 数据类型不匹配

```python
result = set_formula(
    file_path="data.xlsx",
    sheet_name="Sheet1",
    cell_reference="A1",
    formula="=SUM(B1:B10)"
)

if not result["success"]:
    error = result["error"]
    if "E301" in error:
        print("公式语法错误")
    elif "E302" in error:
        print("引用的单元格不存在")
    elif "E304" in error:
        print("公式计算失败")
```

### Q6：如何获取单元格的公式（而不是值）？

**A**：当前 API 主要返回计算结果。如果需要获取公式本身，可以使用 openpyxl 直接读取。

---

## 下一步

- **示例 5**：[文件合并](05-file-merging.md) - 学习如何合并多个 Excel 文件
- **示例 6**：[Supabase 集成](06-supabase-integration.md) - 学习云存储操作
- **API 参考**：[公式工具](../api.md#9-set_formula) - 查看完整 API 文档

---

**提示**：复杂公式建议先在 Excel 中测试，确认语法正确后再使用 API 设置。

