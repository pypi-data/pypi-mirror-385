# 示例 2：Excel 文件生成

本示例演示如何使用 `create_excel_from_json` 工具从 JSON 数据创建格式化的 Excel 文件。

## 📋 目录

- [场景描述](#场景描述)
- [示例 2.1：创建简单表格](#示例-21创建简单表格)
- [示例 2.2：创建带格式的表格](#示例-22创建带格式的表格)
- [示例 2.3：创建多工作表文件](#示例-23创建多工作表文件)
- [示例 2.4：从数据库数据生成报表](#示例-24从数据库数据生成报表)
- [示例 2.5：设置行高和列宽](#示例-25设置行高和列宽)
- [常见问题](#常见问题)

---

## 场景描述

您需要根据程序中的数据生成 Excel 报表，包括：
- 从数据库查询结果生成表格
- 应用专业的格式（标题行、数据行）
- 设置合适的列宽和行高
- 创建多个工作表

---

## 示例 2.1：创建简单表格

### 代码

```python
# 准备数据
workbook_data = {
    "sheets": [
        {
            "name": "销售数据",
            "rows": [
                {
                    "cells": [
                        {"value": "产品", "row": 1, "column": 1},
                        {"value": "销量", "row": 1, "column": 2},
                        {"value": "单价", "row": 1, "column": 3},
                        {"value": "总额", "row": 1, "column": 4}
                    ]
                },
                {
                    "cells": [
                        {"value": "产品A", "row": 2, "column": 1},
                        {"value": 100, "row": 2, "column": 2},
                        {"value": 50.00, "row": 2, "column": 3},
                        {"value": 5000.00, "row": 2, "column": 4}
                    ]
                },
                {
                    "cells": [
                        {"value": "产品B", "row": 3, "column": 1},
                        {"value": 150, "row": 3, "column": 2},
                        {"value": 30.00, "row": 3, "column": 3},
                        {"value": 4500.00, "row": 3, "column": 4}
                    ]
                }
            ]
        }
    ]
}

# 创建 Excel 文件
result = create_excel_from_json(
    workbook_data=workbook_data,
    output_path="output/sales_report.xlsx",
    apply_formats=False  # 不应用格式，仅创建数据
)

if result["success"]:
    print(f"文件创建成功：{result['file_path']}")
else:
    print(f"创建失败：{result['error']}")
```

### 输出

```
文件创建成功：output/sales_report.xlsx
```

---

## 示例 2.2：创建带格式的表格

### 代码

```python
# 准备带格式的数据
workbook_data = {
    "sheets": [
        {
            "name": "销售报表",
            "rows": [
                {
                    # 标题行
                    "cells": [
                        {
                            "value": "产品",
                            "row": 1,
                            "column": 1,
                            "format": {
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
                        },
                        {
                            "value": "销量",
                            "row": 1,
                            "column": 2,
                            "format": {
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
                        },
                        {
                            "value": "单价",
                            "row": 1,
                            "column": 3,
                            "format": {
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
                        },
                        {
                            "value": "总额",
                            "row": 1,
                            "column": 4,
                            "format": {
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
                        }
                    ]
                },
                {
                    # 数据行
                    "cells": [
                        {
                            "value": "产品A",
                            "row": 2,
                            "column": 1,
                            "format": {
                                "border": {
                                    "top": {"style": "thin", "color": "#000000"},
                                    "bottom": {"style": "thin", "color": "#000000"},
                                    "left": {"style": "thin", "color": "#000000"},
                                    "right": {"style": "thin", "color": "#000000"}
                                }
                            }
                        },
                        {
                            "value": 100,
                            "row": 2,
                            "column": 2,
                            "format": {
                                "alignment": {"horizontal": "right"},
                                "border": {
                                    "top": {"style": "thin", "color": "#000000"},
                                    "bottom": {"style": "thin", "color": "#000000"},
                                    "left": {"style": "thin", "color": "#000000"},
                                    "right": {"style": "thin", "color": "#000000"}
                                }
                            }
                        },
                        {
                            "value": 50.00,
                            "row": 2,
                            "column": 3,
                            "format": {
                                "number_format": "#,##0.00",
                                "alignment": {"horizontal": "right"},
                                "border": {
                                    "top": {"style": "thin", "color": "#000000"},
                                    "bottom": {"style": "thin", "color": "#000000"},
                                    "left": {"style": "thin", "color": "#000000"},
                                    "right": {"style": "thin", "color": "#000000"}
                                }
                            }
                        },
                        {
                            "value": 5000.00,
                            "row": 2,
                            "column": 4,
                            "format": {
                                "number_format": "#,##0.00",
                                "alignment": {"horizontal": "right"},
                                "border": {
                                    "top": {"style": "thin", "color": "#000000"},
                                    "bottom": {"style": "thin", "color": "#000000"},
                                    "left": {"style": "thin", "color": "#000000"},
                                    "right": {"style": "thin", "color": "#000000"}
                                }
                            }
                        }
                    ]
                }
            ]
        }
    ]
}

# 创建带格式的 Excel 文件
result = create_excel_from_json(
    workbook_data=workbook_data,
    output_path="output/formatted_report.xlsx",
    apply_formats=True  # 应用格式
)

if result["success"]:
    print(f"格式化报表创建成功：{result['file_path']}")
```

---

## 示例 2.3：创建多工作表文件

### 代码

```python
# 准备多工作表数据
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
        },
        {
            "name": "库存数据",
            "rows": [
                {
                    "cells": [
                        {"value": "产品", "row": 1, "column": 1},
                        {"value": "库存", "row": 1, "column": 2}
                    ]
                },
                {
                    "cells": [
                        {"value": "产品A", "row": 2, "column": 1},
                        {"value": 500, "row": 2, "column": 2}
                    ]
                }
            ]
        },
        {
            "name": "汇总",
            "rows": [
                {
                    "cells": [
                        {"value": "总销量", "row": 1, "column": 1},
                        {"value": 100, "row": 1, "column": 2}
                    ]
                }
            ]
        }
    ]
}

# 创建多工作表文件
result = create_excel_from_json(
    workbook_data=workbook_data,
    output_path="output/multi_sheet_report.xlsx"
)

if result["success"]:
    print(f"多工作表文件创建成功：{result['file_path']}")
```

---

## 示例 2.4：从数据库数据生成报表

### 代码

```python
# 模拟从数据库获取数据
def get_sales_data_from_db():
    """模拟数据库查询"""
    return [
        {"product": "产品A", "quantity": 100, "price": 50.00, "total": 5000.00},
        {"product": "产品B", "quantity": 150, "price": 30.00, "total": 4500.00},
        {"product": "产品C", "quantity": 200, "price": 25.00, "total": 5000.00}
    ]

# 获取数据
db_data = get_sales_data_from_db()

# 构建工作簿数据
workbook_data = {
    "sheets": [
        {
            "name": "销售报表",
            "rows": []
        }
    ]
}

# 添加标题行
header_row = {
    "cells": [
        {"value": "产品", "row": 1, "column": 1},
        {"value": "销量", "row": 1, "column": 2},
        {"value": "单价", "row": 1, "column": 3},
        {"value": "总额", "row": 1, "column": 4}
    ]
}
workbook_data["sheets"][0]["rows"].append(header_row)

# 添加数据行
for idx, record in enumerate(db_data, start=2):
    data_row = {
        "cells": [
            {"value": record["product"], "row": idx, "column": 1},
            {"value": record["quantity"], "row": idx, "column": 2},
            {"value": record["price"], "row": idx, "column": 3},
            {"value": record["total"], "row": idx, "column": 4}
        ]
    }
    workbook_data["sheets"][0]["rows"].append(data_row)

# 创建 Excel 文件
result = create_excel_from_json(
    workbook_data=workbook_data,
    output_path="output/db_report.xlsx"
)

if result["success"]:
    print(f"数据库报表生成成功：{result['file_path']}")
```

---

## 示例 2.5：设置行高和列宽

### 代码

```python
# 准备数据（包含列宽信息）
workbook_data = {
    "sheets": [
        {
            "name": "格式化表格",
            "rows": [
                {
                    "cells": [
                        {"value": "产品名称", "row": 1, "column": 1},
                        {"value": "销量", "row": 1, "column": 2},
                        {"value": "备注", "row": 1, "column": 3}
                    ],
                    "height": 25.0  # 设置行高
                },
                {
                    "cells": [
                        {"value": "产品A", "row": 2, "column": 1},
                        {"value": 100, "row": 2, "column": 2},
                        {"value": "这是一个很长的备注信息", "row": 2, "column": 3}
                    ],
                    "height": 20.0
                }
            ],
            "column_widths": {
                "A": 20.0,  # 产品名称列宽
                "B": 10.0,  # 销量列宽
                "C": 30.0   # 备注列宽
            }
        }
    ]
}

# 创建文件
result = create_excel_from_json(
    workbook_data=workbook_data,
    output_path="output/sized_report.xlsx"
)

if result["success"]:
    print(f"带尺寸设置的报表创建成功：{result['file_path']}")
```

---

## 常见问题

### Q1：如何快速生成大量数据？

**A**：使用循环批量生成单元格数据。

```python
# 生成 1000 行数据
rows = []

# 标题行
rows.append({
    "cells": [
        {"value": "序号", "row": 1, "column": 1},
        {"value": "数据", "row": 1, "column": 2}
    ]
})

# 数据行
for i in range(2, 1002):
    rows.append({
        "cells": [
            {"value": i - 1, "row": i, "column": 1},
            {"value": f"数据{i-1}", "row": i, "column": 2}
        ]
    })

workbook_data = {"sheets": [{"name": "大数据", "rows": rows}]}
result = create_excel_from_json(
    workbook_data=workbook_data,
    output_path="output/large_data.xlsx"
)
```

### Q2：如何复用格式？

**A**：定义格式模板并复用。

```python
# 定义格式模板
header_format = {
    "font": {"bold": True, "color": "#FFFFFF"},
    "fill": {"background_color": "#4472C4"},
    "alignment": {"horizontal": "center"}
}

data_format = {
    "border": {
        "top": {"style": "thin", "color": "#000000"},
        "bottom": {"style": "thin", "color": "#000000"},
        "left": {"style": "thin", "color": "#000000"},
        "right": {"style": "thin", "color": "#000000"}
    }
}

# 应用格式
cells = [
    {"value": "标题1", "row": 1, "column": 1, "format": header_format},
    {"value": "标题2", "row": 1, "column": 2, "format": header_format},
    {"value": "数据1", "row": 2, "column": 1, "format": data_format}
]
```

### Q3：如何处理日期和时间？

**A**：使用 ISO 格式字符串或 Python datetime 对象。

```python
from datetime import datetime

cells = [
    {
        "value": datetime.now().isoformat(),
        "row": 1,
        "column": 1,
        "format": {
            "number_format": "yyyy-mm-dd hh:mm:ss"
        }
    }
]
```

---

## 下一步

- **示例 3**：[格式编辑](03-formatting-cells.md) - 学习如何修改现有文件的格式
- **示例 4**：[公式操作](04-formula-operations.md) - 学习如何使用公式
- **API 参考**：[create_excel_from_json](../api.md#2-create_excel_from_json) - 查看完整 API 文档

---

**提示**：生成大文件时建议禁用格式应用（`apply_formats=False`）以提高性能。

