# 示例 6：Supabase 存储集成

本示例演示如何使用 `manage_storage` 工具操作 Supabase Storage，实现 Excel 文件的云存储管理。

## 📋 目录

- [场景描述](#场景描述)
- [准备工作](#准备工作)
- [示例 6.1：上传文件](#示例-61上传文件)
- [示例 6.2：下载文件](#示例-62下载文件)
- [示例 6.3：列出和搜索文件](#示例-63列出和搜索文件)
- [示例 6.4：删除文件](#示例-64删除文件)
- [示例 6.5：完整工作流程](#示例-65完整工作流程)
- [常见问题](#常见问题)

---

## 场景描述

您需要将 Excel 文件存储到云端（Supabase Storage）：
- 上传本地生成的报表到云端
- 从云端下载文件进行处理
- 管理云端文件（列出、搜索、删除）
- 实现完整的云端报表处理流程

---

## 准备工作

### 1. 配置 Supabase 凭据

在项目根目录创建 `.env` 文件：

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key
SUPABASE_BUCKET=excel-files
```

### 2. 获取 Supabase 凭据

1. 登录 [Supabase Dashboard](https://app.supabase.com/)
2. 选择您的项目
3. 进入 **Settings** → **API**
4. 复制以下信息：
   - **Project URL** → `SUPABASE_URL`
   - **Service Role Key** → `SUPABASE_KEY`（注意：不是 anon key）

### 3. 创建 Storage Bucket

1. 在 Supabase Dashboard 中，进入 **Storage**
2. 点击 **New Bucket**
3. 输入名称：`excel-files`
4. 设置为 **Public** 或 **Private**（根据需求）
5. 点击 **Create Bucket**

---

## 示例 6.1：上传文件

### 上传单个文件

```python
# 上传本地文件到 Supabase
result = manage_storage(
    operation="upload",
    local_path="output/sales_report.xlsx",
    remote_path="reports/2024/sales_report.xlsx"
)

if result["success"]:
    print(f"✅ 上传成功！")
    print(f"远程路径：{result['remote_path']}")
    print(f"文件大小：{result['file_size']} 字节")
    print(f"公开 URL：{result.get('public_url', 'N/A')}")
else:
    print(f"❌ 上传失败：{result['error']}")
```

### 批量上传文件

```python
# 上传多个文件
files_to_upload = [
    ("output/q1_report.xlsx", "reports/2024/q1_report.xlsx"),
    ("output/q2_report.xlsx", "reports/2024/q2_report.xlsx"),
    ("output/q3_report.xlsx", "reports/2024/q3_report.xlsx"),
    ("output/q4_report.xlsx", "reports/2024/q4_report.xlsx")
]

for local_path, remote_path in files_to_upload:
    result = manage_storage(
        operation="upload",
        local_path=local_path,
        remote_path=remote_path
    )
    if result["success"]:
        print(f"✅ {local_path} → {remote_path}")
    else:
        print(f"❌ {local_path} 上传失败：{result['error']}")
```

### 上传并覆盖已存在的文件

```python
# 如果远程文件已存在，会自动覆盖
result = manage_storage(
    operation="upload",
    local_path="output/updated_report.xlsx",
    remote_path="reports/2024/sales_report.xlsx"  # 覆盖已存在的文件
)

if result["success"]:
    print("✅ 文件已更新")
```

---

## 示例 6.2：下载文件

### 下载单个文件

```python
# 从 Supabase 下载文件到本地
result = manage_storage(
    operation="download",
    remote_path="reports/2024/sales_report.xlsx",
    local_path="downloads/sales_report.xlsx"
)

if result["success"]:
    print(f"✅ 下载成功！")
    print(f"本地路径：{result['local_path']}")
    print(f"文件大小：{result['file_size']} 字节")
else:
    print(f"❌ 下载失败：{result['error']}")
```

### 下载并处理文件

```python
# 下载文件后立即处理
result = manage_storage(
    operation="download",
    remote_path="reports/2024/sales_report.xlsx",
    local_path="temp/sales_report.xlsx"
)

if result["success"]:
    # 解析下载的文件
    parse_result = parse_excel_to_json(
        file_path="temp/sales_report.xlsx",
        extract_formats=False
    )
    
    if parse_result["success"]:
        workbook = parse_result["workbook"]
        print(f"工作表数量：{len(workbook['sheets'])}")
```

### 批量下载文件

```python
# 下载多个文件
files_to_download = [
    ("reports/2024/q1_report.xlsx", "downloads/q1_report.xlsx"),
    ("reports/2024/q2_report.xlsx", "downloads/q2_report.xlsx"),
    ("reports/2024/q3_report.xlsx", "downloads/q3_report.xlsx"),
    ("reports/2024/q4_report.xlsx", "downloads/q4_report.xlsx")
]

for remote_path, local_path in files_to_download:
    result = manage_storage(
        operation="download",
        remote_path=remote_path,
        local_path=local_path
    )
    if result["success"]:
        print(f"✅ {remote_path} → {local_path}")
    else:
        print(f"❌ {remote_path} 下载失败：{result['error']}")
```

---

## 示例 6.3：列出和搜索文件

### 列出所有文件

```python
# 列出 bucket 中的所有文件
result = manage_storage(
    operation="list"
)

if result["success"]:
    print(f"✅ 找到 {result['file_count']} 个文件")
    for file_info in result["files"]:
        print(f"  - {file_info['name']} ({file_info['size']} 字节)")
```

### 列出指定路径下的文件

```python
# 列出特定目录下的文件
result = manage_storage(
    operation="list",
    remote_path="reports/2024/"  # 指定路径前缀
)

if result["success"]:
    print(f"✅ 2024年报表：{result['file_count']} 个文件")
    for file_info in result["files"]:
        print(f"  - {file_info['name']}")
        print(f"    大小：{file_info['size']} 字节")
        print(f"    创建时间：{file_info['created_at']}")
        print(f"    修改时间：{file_info['updated_at']}")
```

### 搜索文件

```python
# 搜索包含特定关键词的文件
result = manage_storage(
    operation="search",
    search_query="sales"  # 搜索文件名包含 "sales" 的文件
)

if result["success"]:
    print(f"✅ 找到 {result['file_count']} 个匹配的文件")
    for file_info in result["files"]:
        print(f"  - {file_info['name']}")
```

### 搜索特定路径下的文件

```python
# 在特定路径下搜索
result = manage_storage(
    operation="search",
    remote_path="reports/2024/",
    search_query="q"  # 搜索季度报表（q1, q2, q3, q4）
)

if result["success"]:
    print(f"✅ 找到 {result['file_count']} 个季度报表")
    for file_info in result["files"]:
        print(f"  - {file_info['name']}")
```

---

## 示例 6.4：删除文件

### 删除单个文件

```python
# 删除远程文件
result = manage_storage(
    operation="delete",
    remote_path="reports/2024/temp_report.xlsx"
)

if result["success"]:
    print(f"✅ 文件已删除：{result['remote_path']}")
else:
    print(f"❌ 删除失败：{result['error']}")
```

### 批量删除文件

```python
# 删除多个文件
files_to_delete = [
    "reports/2024/temp1.xlsx",
    "reports/2024/temp2.xlsx",
    "reports/2024/backup.xlsx"
]

for remote_path in files_to_delete:
    result = manage_storage(
        operation="delete",
        remote_path=remote_path
    )
    if result["success"]:
        print(f"✅ 已删除：{remote_path}")
    else:
        print(f"❌ 删除失败：{remote_path}")
```

### 清理旧文件

```python
from datetime import datetime, timedelta

def cleanup_old_files(days=30):
    """删除超过指定天数的文件"""
    
    # 列出所有文件
    result = manage_storage(operation="list")
    
    if not result["success"]:
        print("❌ 无法列出文件")
        return
    
    # 计算截止日期
    cutoff_date = datetime.now() - timedelta(days=days)
    
    # 删除旧文件
    deleted_count = 0
    for file_info in result["files"]:
        file_date = datetime.fromisoformat(file_info["created_at"].replace("Z", "+00:00"))
        
        if file_date < cutoff_date:
            delete_result = manage_storage(
                operation="delete",
                remote_path=file_info["name"]
            )
            if delete_result["success"]:
                deleted_count += 1
                print(f"✅ 已删除旧文件：{file_info['name']}")
    
    print(f"✅ 清理完成，删除了 {deleted_count} 个文件")

# 使用示例：删除30天前的文件
cleanup_old_files(days=30)
```

---

## 示例 6.5：完整工作流程

### 云端报表处理流程

```python
def cloud_report_workflow():
    """完整的云端报表处理流程"""
    
    # 步骤 1：生成本地报表
    print("步骤 1：生成本地报表...")
    workbook_data = {
        "sheets": [{
            "name": "销售数据",
            "rows": [
                {"cells": [
                    {"value": "产品", "row": 1, "column": 1},
                    {"value": "销量", "row": 1, "column": 2}
                ]},
                {"cells": [
                    {"value": "产品A", "row": 2, "column": 1},
                    {"value": 100, "row": 2, "column": 2}
                ]}
            ]
        }]
    }
    
    create_result = create_excel_from_json(
        workbook_data=workbook_data,
        output_path="temp/local_report.xlsx"
    )
    
    if not create_result["success"]:
        print(f"❌ 报表生成失败：{create_result['error']}")
        return
    
    print("✅ 本地报表生成成功")
    
    # 步骤 2：上传到 Supabase
    print("步骤 2：上传到云端...")
    upload_result = manage_storage(
        operation="upload",
        local_path="temp/local_report.xlsx",
        remote_path="reports/2024/sales_report.xlsx"
    )
    
    if not upload_result["success"]:
        print(f"❌ 上传失败：{upload_result['error']}")
        return
    
    print(f"✅ 上传成功：{upload_result['remote_path']}")
    
    # 步骤 3：从云端下载（模拟其他用户下载）
    print("步骤 3：从云端下载...")
    download_result = manage_storage(
        operation="download",
        remote_path="reports/2024/sales_report.xlsx",
        local_path="downloads/sales_report.xlsx"
    )
    
    if not download_result["success"]:
        print(f"❌ 下载失败：{download_result['error']}")
        return
    
    print(f"✅ 下载成功：{download_result['local_path']}")
    
    # 步骤 4：处理下载的文件
    print("步骤 4：处理下载的文件...")
    parse_result = parse_excel_to_json(
        file_path="downloads/sales_report.xlsx",
        extract_formats=False
    )
    
    if parse_result["success"]:
        workbook = parse_result["workbook"]
        print(f"✅ 文件解析成功，包含 {len(workbook['sheets'])} 个工作表")
    
    # 步骤 5：列出所有云端文件
    print("步骤 5：列出云端文件...")
    list_result = manage_storage(operation="list")
    
    if list_result["success"]:
        print(f"✅ 云端共有 {list_result['file_count']} 个文件")
    
    print("✅ 完整流程执行成功！")

# 执行完整流程
cloud_report_workflow()
```

### 多用户协作场景

```python
def collaborative_workflow():
    """多用户协作处理报表"""
    
    # 用户 A：创建并上传报表
    print("用户 A：创建报表...")
    # ... 创建报表代码 ...
    
    manage_storage(
        operation="upload",
        local_path="output/draft_report.xlsx",
        remote_path="shared/draft_report.xlsx"
    )
    print("✅ 用户 A 已上传草稿")
    
    # 用户 B：下载、修改、重新上传
    print("用户 B：下载并修改报表...")
    manage_storage(
        operation="download",
        remote_path="shared/draft_report.xlsx",
        local_path="temp/draft_report.xlsx"
    )
    
    # ... 修改报表代码 ...
    
    manage_storage(
        operation="upload",
        local_path="temp/modified_report.xlsx",
        remote_path="shared/draft_report.xlsx"  # 覆盖原文件
    )
    print("✅ 用户 B 已更新报表")
    
    # 用户 C：下载最终版本
    print("用户 C：下载最终版本...")
    manage_storage(
        operation="download",
        remote_path="shared/draft_report.xlsx",
        local_path="final/report.xlsx"
    )
    print("✅ 用户 C 已下载最终版本")

# 执行协作流程
collaborative_workflow()
```

---

## 常见问题

### Q1：如何处理上传失败？

**A**：检查错误码并重试。

```python
result = manage_storage(
    operation="upload",
    local_path="output/report.xlsx",
    remote_path="reports/report.xlsx"
)

if not result["success"]:
    error = result["error"]
    if "E001" in error:
        print("Supabase 配置错误，请检查 .env 文件")
    elif "E101" in error:
        print("本地文件不存在")
    elif "E501" in error:
        print("网络连接失败，请检查网络")
    elif "E502" in error:
        print("操作超时，请重试")
```

### Q2：如何获取文件的公开 URL？

**A**：上传成功后，返回值中包含 `public_url`（如果 bucket 是公开的）。

```python
result = manage_storage(
    operation="upload",
    local_path="output/report.xlsx",
    remote_path="public/report.xlsx"
)

if result["success"] and "public_url" in result:
    print(f"公开 URL：{result['public_url']}")
    # 可以分享这个 URL 给其他人下载
```

### Q3：如何检查文件是否存在？

**A**：使用 `search` 操作。

```python
result = manage_storage(
    operation="search",
    search_query="sales_report.xlsx"
)

if result["success"] and result["file_count"] > 0:
    print("文件存在")
else:
    print("文件不存在")
```

### Q4：上传大文件时如何提高成功率？

**A**：
1. 确保网络稳定
2. 增加超时时间（在代码中配置）
3. 分块上传（对于超大文件）

### Q5：如何组织云端文件结构？

**A**：使用有意义的路径层级。

```python
# ✅ 推荐：有组织的路径
remote_paths = [
    "reports/2024/q1/sales.xlsx",
    "reports/2024/q1/inventory.xlsx",
    "reports/2024/q2/sales.xlsx",
    "templates/sales_template.xlsx",
    "backups/2024-01-15/sales.xlsx"
]

# ❌ 不推荐：扁平化路径
remote_paths = [
    "sales_2024_q1.xlsx",
    "inventory_2024_q1.xlsx",
    "sales_2024_q2.xlsx"
]
```

---

## 下一步

- **API 参考**：[manage_storage](../api.md#8-manage_storage) - 查看完整 API 文档
- **故障排查**：[troubleshooting.md](../troubleshooting.md) - 解决常见问题
- **架构文档**：[architecture.md](../architecture.md) - 了解系统架构

---

**提示**：使用 Service Role Key 时要注意安全，不要将其提交到版本控制系统。建议使用环境变量管理敏感信息。

