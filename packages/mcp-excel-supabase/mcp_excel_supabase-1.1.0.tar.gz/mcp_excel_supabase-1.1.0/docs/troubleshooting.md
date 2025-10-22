# Excel MCP Server - 故障排查指南

本文档提供常见问题的诊断和解决方案，帮助快速定位和解决系统问题。

---

## 📋 目录

1. [错误码对照表](#错误码对照表)
2. [常见问题和解决方案](#常见问题和解决方案)
3. [日志分析指南](#日志分析指南)
4. [性能问题诊断](#性能问题诊断)
5. [调试技巧](#调试技巧)

---

## 错误码对照表

### 配置和认证错误 (E001-E099)

| 错误码 | 错误类型 | 描述 | 常见原因 | 解决方案 |
|--------|---------|------|---------|---------|
| E001 | EnvironmentVariableNotSetError | 环境变量未设置 | .env文件缺失或配置不完整 | 检查.env文件，确保所有必需的环境变量已设置 |
| E002 | SupabaseAuthError | Supabase认证失败 | URL或Key配置错误 | 验证SUPABASE_URL和SUPABASE_KEY是否正确 |

### 文件操作错误 (E101-E199)

| 错误码 | 错误类型 | 描述 | 常见原因 | 解决方案 |
|--------|---------|------|---------|---------|
| E101 | FileNotFoundError | 文件不存在 | 文件路径错误或文件已删除 | 检查文件路径，确认文件存在 |
| E102 | FileSizeError | 文件大小超限 | 文件超过1MB限制 | 使用流式处理或分割文件 |
| E103 | BatchLimitError | 批量操作超限 | 批量文件数超过20个 | 分批处理，每批不超过20个文件 |
| E104 | FileExistsError | 文件已存在 | 目标文件已存在且未设置覆盖 | 设置overwrite=True或使用不同文件名 |
| E105 | FileReadError | 文件读取错误 | 文件损坏或权限不足 | 检查文件完整性和读取权限 |
| E106 | FileWriteError | 文件写入错误 | 磁盘空间不足或权限不足 | 检查磁盘空间和写入权限 |

### 数据验证错误 (E201-E299)

| 错误码 | 错误类型 | 描述 | 常见原因 | 解决方案 |
|--------|---------|------|---------|---------|
| E201 | InvalidJSONError | JSON格式错误 | JSON语法错误 | 使用JSON验证工具检查格式 |
| E202 | InvalidCellRangeError | 单元格范围无效 | 范围格式错误 | 使用正确格式如'A1:B10' |
| E203 | InvalidColorError | 颜色格式错误 | 颜色值格式不正确 | 使用十六进制格式如'#FF0000' |
| E204 | InvalidParameterError | 参数无效 | 参数类型或值不符合要求 | 检查参数文档，使用正确的参数 |
| E205 | DataRangeError | 数据范围错误 | 数值超出有效范围 | 确保数值在允许的范围内 |

### 公式相关错误 (E301-E399)

| 错误码 | 错误类型 | 描述 | 常见原因 | 解决方案 |
|--------|---------|------|---------|---------|
| E301 | UnsupportedFormulaError | 不支持的公式 | 使用了不支持的Excel函数 | 查看支持的公式列表，使用替代函数 |
| E302 | FormulaSyntaxError | 公式语法错误 | 公式语法不正确 | 检查括号匹配和函数名拼写 |
| E303 | FormulaCalculationError | 公式计算错误 | 引用的单元格不存在或类型错误 | 检查单元格引用和数据类型 |

### Sheet操作错误 (E401-E499)

| 错误码 | 错误类型 | 描述 | 常见原因 | 解决方案 |
|--------|---------|------|---------|---------|
| E401 | SheetNotFoundError | Sheet不存在 | Sheet名称错误 | 检查Sheet名称，查看可用Sheet列表 |
| E402 | SheetAlreadyExistsError | Sheet已存在 | 创建重名Sheet | 使用不同的Sheet名称或先删除现有Sheet |

### 网络和超时错误 (E501-E599)

| 错误码 | 错误类型 | 描述 | 常见原因 | 解决方案 |
|--------|---------|------|---------|---------|
| E501 | SupabaseNetworkError | Supabase网络错误 | 网络连接问题 | 检查网络连接，稍后重试 |
| E502 | TimeoutError | 操作超时 | 操作时间过长 | 增加超时时间或优化操作 |

---

## 常见问题和解决方案

### 1. 环境配置问题

#### 问题：启动时提示环境变量未设置

**错误信息：**
```
[E001] 环境变量 'SUPABASE_URL' 未设置
```

**解决方案：**
1. 检查项目根目录是否存在`.env`文件
2. 确保`.env`文件包含以下配置：
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   LOG_LEVEL=INFO
   ```
3. 重启应用程序

#### 问题：Supabase认证失败

**错误信息：**
```
[E002] Supabase 认证失败
```

**解决方案：**
1. 验证SUPABASE_URL格式：`https://xxx.supabase.co`
2. 验证SUPABASE_KEY是否为有效的service_role key
3. 检查Supabase项目是否处于活动状态
4. 测试网络连接到Supabase服务器

### 2. 文件操作问题

#### 问题：文件大小超限

**错误信息：**
```
[E102] 文件大小 5.23MB 超过限制 1.0MB
```

**解决方案：**
1. 使用流式处理：
   ```python
   from mcp_excel_supabase.excel import StreamReader, StreamWriter
   
   reader = StreamReader(file_path, chunk_size=1000)
   for chunk in reader.read_chunks():
       # 处理数据块
       pass
   ```
2. 或者调整文件大小限制（需要管理员权限）

#### 问题：批量操作超限

**错误信息：**
```
[E103] 批量操作文件数 25 超过限制 20
```

**解决方案：**
```python
from mcp_excel_supabase.utils import ConcurrentExecutor

# 分批处理
batch_size = 20
for i in range(0, len(files), batch_size):
    batch = files[i:i+batch_size]
    # 处理当前批次
    process_batch(batch)
```

### 3. 数据验证问题

#### 问题：JSON格式错误

**错误信息：**
```
[E201] JSON 格式错误
```

**解决方案：**
1. 使用JSON验证工具检查格式
2. 常见错误：
   - 缺少逗号或多余逗号
   - 引号不匹配
   - 括号不匹配
3. 使用Pydantic模型验证：
   ```python
   from mcp_excel_supabase.excel.schemas import Workbook
   
   try:
       workbook = Workbook.model_validate(json_data)
   except ValidationError as e:
       print(e.errors())
   ```

#### 问题：单元格范围格式错误

**错误信息：**
```
[E202] 单元格范围无效: A1-B10
```

**解决方案：**
使用正确的范围格式：
- ✅ 正确：`A1:B10`
- ✅ 正确：`Sheet1!A1:B10`
- ❌ 错误：`A1-B10`
- ❌ 错误：`A1..B10`

### 4. 公式问题

#### 问题：不支持的公式

**错误信息：**
```
[E301] 不支持的公式: XLOOKUP
```

**解决方案：**
1. 查看支持的公式列表（20+常用函数）
2. 使用替代函数：
   - XLOOKUP → VLOOKUP 或 INDEX/MATCH
   - FILTER → 使用Python过滤逻辑
3. 或者在Excel中预先计算结果

#### 问题：公式计算错误

**错误信息：**
```
[E303] 公式计算失败: =SUM(A1:A10)
```

**解决方案：**
1. 检查引用的单元格是否存在
2. 确保数据类型正确（数值计算需要数字类型）
3. 检查是否有循环引用
4. 使用调试模式查看详细错误：
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

### 5. 性能问题

#### 问题：大文件处理缓慢

**症状：**
- 处理1MB文件超过2秒
- 内存使用持续增长

**解决方案：**
1. 使用流式处理：
   ```python
   from mcp_excel_supabase.excel import stream_copy
   
   stats = stream_copy(source_path, dest_path, chunk_size=1000)
   print(f"Memory growth: {stats['memory_growth_mb']}MB")
   ```

2. 启用缓存：
   ```python
   from mcp_excel_supabase.utils import parse_cache
   
   # 缓存会自动生效
   result = parser.parse_file(file_path)
   ```

3. 使用并发处理：
   ```python
   from mcp_excel_supabase.utils import ConcurrentExecutor
   
   executor = ConcurrentExecutor()
   results = executor.map_concurrent(process_file, file_list)
   ```

---

## 日志分析指南

### 日志文件位置

```
logs/
├── mcp_excel.log          # 主日志（所有级别）
├── error.log              # 错误日志（ERROR及以上）
├── audit.log              # 审计日志（操作记录）
├── performance.log        # 性能日志（性能指标）
├── structured.jsonl       # 结构化日志（JSON格式）
└── error_tracking.jsonl   # 错误追踪（JSON格式）
```

### 日志级别

- **DEBUG**: 详细的调试信息
- **INFO**: 一般信息性消息
- **WARNING**: 警告信息，不影响正常运行
- **ERROR**: 错误信息，操作失败
- **CRITICAL**: 严重错误，系统可能无法继续运行

### 查看日志

#### 查看最近的错误
```bash
# Windows PowerShell
Get-Content logs/error.log -Tail 50

# Linux/Mac
tail -n 50 logs/error.log
```

#### 搜索特定错误码
```bash
# Windows PowerShell
Select-String -Path logs/mcp_excel.log -Pattern "E101"

# Linux/Mac
grep "E101" logs/mcp_excel.log
```

#### 分析性能日志
```bash
# 查看慢操作（超过1000ms）
Select-String -Path logs/performance.log -Pattern "DURATION=[1-9][0-9]{3,}"
```

### 结构化日志分析

结构化日志以JSON Lines格式存储，每行一个JSON对象：

```python
import json

# 读取并分析结构化日志
with open('logs/structured.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        log = json.loads(line)
        if log['level'] == 'ERROR':
            print(f"{log['timestamp']}: {log['message']}")
```

---

## 性能问题诊断

### 性能监控

使用内置监控系统：

```python
from mcp_excel_supabase.utils import get_performance_monitor

monitor = get_performance_monitor()

# 查看所有操作的统计信息
stats = monitor.get_all_stats()
for operation, metrics in stats.items():
    print(f"{operation}:")
    print(f"  平均耗时: {metrics['avg_duration_ms']:.2f}ms")
    print(f"  P95耗时: {metrics['p95_duration_ms']:.2f}ms")
    print(f"  成功率: {metrics['success_rate']*100:.1f}%")
```

### 资源监控

```python
from mcp_excel_supabase.utils import get_resource_monitor

monitor = get_resource_monitor()

# 查看当前资源使用
usage = monitor.get_current_usage()
print(f"CPU: {usage['cpu_percent']:.1f}%")
print(f"内存: {usage['memory_mb']:.1f}MB")

# 查看平均使用情况（最近5分钟）
avg_usage = monitor.get_average_usage(minutes=5)
print(f"平均CPU: {avg_usage['avg_cpu_percent']:.1f}%")
print(f"平均内存: {avg_usage['avg_memory_mb']:.1f}MB")
```

### 性能优化建议

1. **启用缓存**：对重复操作启用缓存
2. **使用并发**：批量操作使用并发处理
3. **流式处理**：大文件使用流式处理
4. **调整参数**：根据实际情况调整chunk_size、max_workers等参数

---

## 调试技巧

### 1. 启用详细日志

```python
import os
os.environ['LOG_LEVEL'] = 'DEBUG'

# 或在.env文件中设置
# LOG_LEVEL=DEBUG
```

### 2. 使用错误追踪器

```python
from mcp_excel_supabase.utils.logger import error_tracker

# 查看错误统计
stats = error_tracker.get_error_stats()
print(f"总错误数: {stats['total_errors']}")
print(f"错误类型: {stats['error_counts']}")

# 查看最频繁的错误
top_errors = error_tracker.get_top_errors(limit=5)
for error_key, count in top_errors:
    print(f"{error_key}: {count}次")
```

### 3. 使用性能装饰器

```python
from mcp_excel_supabase.utils import monitor_performance

@monitor_performance(operation_name="custom_operation")
def my_function():
    # 函数执行时间会自动记录
    pass
```

### 4. 使用错误恢复机制

```python
from mcp_excel_supabase.utils import with_retry, with_fallback

# 自动重试（适用于网络操作）
@with_retry(max_retries=3, retry_delay=1.0)
def upload_file(path):
    # 失败会自动重试
    pass

# 使用降级值（适用于非关键操作）
@with_fallback(fallback_value=[])
def get_optional_data():
    # 失败返回空列表
    pass
```

---

## 获取帮助

如果以上方法无法解决问题，请：

1. 收集以下信息：
   - 错误码和完整错误消息
   - 相关日志（logs/error.log）
   - 操作步骤和输入数据
   - 系统环境信息

2. 提交Issue到GitHub仓库
3. 或联系技术支持

---

**文档版本**: 1.0  
**最后更新**: 2025-10-20

