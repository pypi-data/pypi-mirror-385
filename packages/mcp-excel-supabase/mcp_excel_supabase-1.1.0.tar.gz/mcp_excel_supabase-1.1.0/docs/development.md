# Excel MCP Server 开发文档

本文档为开发者提供完整的开发指南，包括环境搭建、代码规范、测试指南和贡献流程。

## 📋 目录

- [开发环境搭建](#开发环境搭建)
- [项目结构](#项目结构)
- [代码规范](#代码规范)
- [测试指南](#测试指南)
- [性能测试](#性能测试)
- [调试技巧](#调试技巧)
- [贡献指南](#贡献指南)
- [发布流程](#发布流程)

---

## 开发环境搭建

### 1. 系统要求

- **Python**：3.9 或更高版本
- **操作系统**：Windows、macOS、Linux
- **内存**：建议 4GB 以上
- **磁盘空间**：至少 500MB

### 2. 克隆项目

```bash
git clone https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage.git
cd Excel-MCP-Server-with-Supabase-Storage
```

### 3. 创建虚拟环境

**Windows**：
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux**：
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. 安装依赖

```bash
# 安装生产依赖
pip install -e .

# 安装开发依赖
pip install -e ".[dev]"
```

### 5. 配置环境变量

创建 `.env` 文件：

```bash
# Supabase 配置
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key
SUPABASE_BUCKET=excel-files

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/mcp_excel.log

# 性能配置
CACHE_SIZE=128
MAX_WORKERS=8
```

### 6. 验证安装

```bash
# 运行测试
pytest

# 检查代码格式
black --check src tests

# 运行代码检查
ruff check src tests

# 运行类型检查
mypy src
```

---

## 项目结构

```
excel-mcp/
├── src/
│   └── mcp_excel_supabase/
│       ├── __init__.py
│       ├── server.py              # MCP 服务器入口
│       ├── excel/                 # Excel 处理模块
│       │   ├── parser.py          # Excel 解析器
│       │   ├── generator.py       # Excel 生成器
│       │   ├── format_editor.py   # 格式编辑器
│       │   ├── format_extractor.py # 格式提取器
│       │   ├── format_applier.py  # 格式应用器
│       │   ├── cell_merger.py     # 单元格合并器
│       │   ├── dimension_adjuster.py # 尺寸调整器
│       │   ├── formula_manager.py # 公式管理器
│       │   ├── formula_engine.py  # 公式引擎
│       │   ├── sheet_manager.py   # 工作表管理器
│       │   ├── file_merger.py     # 文件合并器
│       │   ├── data_validator.py  # 数据验证器
│       │   ├── stream_processor.py # 流式处理器
│       │   └── schemas.py         # Excel 数据模型
│       ├── storage/               # Supabase 存储模块
│       │   ├── client.py          # 存储客户端
│       │   ├── uploader.py        # 文件上传器
│       │   ├── downloader.py      # 文件下载器
│       │   └── manager.py         # 文件管理器
│       ├── tools/                 # MCP 工具模块
│       │   └── schemas.py         # 工具数据模型
│       └── utils/                 # 工具模块
│           ├── cache.py           # 缓存
│           ├── logger.py          # 日志记录器
│           ├── errors.py          # 错误定义
│           ├── error_handler.py   # 错误处理器
│           ├── validator.py       # 验证器
│           ├── monitor.py         # 监控器
│           └── concurrency.py     # 并发处理
├── tests/                         # 测试目录
│   ├── conftest.py                # Pytest 配置
│   ├── fixtures/                  # 测试数据
│   ├── test_parser.py             # 解析器测试
│   ├── test_generator.py          # 生成器测试
│   └── ...                        # 其他测试文件
├── docs/                          # 文档目录
│   ├── api.md                     # API 文档
│   ├── architecture.md            # 架构文档
│   ├── development.md             # 开发文档（本文档）
│   ├── troubleshooting.md         # 故障排查
│   └── examples/                  # 使用示例
├── pyproject.toml                 # 项目配置
├── README.md                      # 项目说明
└── .env.example                   # 环境变量示例
```

---

## 代码规范

### 1. Python 代码风格

遵循 **PEP 8** 规范，使用 **Black** 格式化代码。

**配置**（`pyproject.toml`）：
```toml
[tool.black]
line-length = 100
target-version = ["py39", "py310", "py311"]
```

**格式化代码**：
```bash
# 格式化所有代码
black src tests

# 检查格式（不修改）
black --check src tests
```

### 2. 代码检查

使用 **Ruff** 进行代码检查。

**配置**（`pyproject.toml`）：
```toml
[tool.ruff]
line-length = 100
target-version = "py39"
```

**运行检查**：
```bash
# 检查代码
ruff check src tests

# 自动修复
ruff check --fix src tests
```

### 3. 类型注解

所有函数必须有完整的类型注解，使用 **mypy** 进行类型检查。

**配置**（`pyproject.toml`）：
```toml
[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

**示例**：
```python
from typing import Dict, Any, Optional

def parse_file(file_path: str, extract_formats: bool = True) -> Dict[str, Any]:
    """解析 Excel 文件"""
    # 实现
    pass
```

**运行类型检查**：
```bash
mypy src
```

### 4. 文档字符串

使用 **Google 风格** 的文档字符串。

**示例**：
```python
def create_excel(data: Dict[str, Any], output_path: str) -> bool:
    """
    从数据创建 Excel 文件
    
    Args:
        data: 工作簿数据（JSON 格式）
        output_path: 输出文件路径
    
    Returns:
        是否创建成功
    
    Raises:
        FileCreationError: 文件创建失败
        ValidationError: 数据验证失败
    
    Example:
        >>> data = {"sheets": [{"name": "Sheet1", "rows": []}]}
        >>> create_excel(data, "output.xlsx")
        True
    """
    # 实现
    pass
```

### 5. 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 模块 | 小写+下划线 | `excel_parser.py` |
| 类 | 大驼峰 | `ExcelParser` |
| 函数 | 小写+下划线 | `parse_file()` |
| 变量 | 小写+下划线 | `file_path` |
| 常量 | 大写+下划线 | `MAX_FILE_SIZE` |
| 私有成员 | 前缀下划线 | `_internal_method()` |

### 6. 导入顺序

1. 标准库
2. 第三方库
3. 本地模块

**示例**：
```python
# 标准库
import os
import sys
from typing import Dict, Any

# 第三方库
from openpyxl import Workbook
from pydantic import BaseModel

# 本地模块
from mcp_excel_supabase.utils.logger import get_logger
from mcp_excel_supabase.excel.schemas import WorkbookData
```

---

## 测试指南

### 1. 测试框架

使用 **pytest** 进行单元测试。

**配置**（`pyproject.toml`）：
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "--cov=mcp_excel_supabase --cov-report=html --cov-report=term"
```

### 2. 运行测试

```bash
# 运行所有测试
pytest

# 运行特定文件
pytest tests/test_parser.py

# 运行特定测试
pytest tests/test_parser.py::test_parse_simple_file

# 显示详细输出
pytest -v

# 显示打印输出
pytest -s
```

### 3. 代码覆盖率

**目标**：≥ 80%

```bash
# 生成覆盖率报告
pytest --cov=mcp_excel_supabase --cov-report=html

# 查看报告
# 打开 htmlcov/index.html
```

### 4. 编写测试

**测试文件命名**：`test_<module_name>.py`

**示例**：
```python
import pytest
from mcp_excel_supabase.excel.parser import ExcelParser

class TestExcelParser:
    """Excel 解析器测试"""
    
    def test_parse_simple_file(self, temp_excel_file):
        """测试解析简单文件"""
        parser = ExcelParser()
        result = parser.parse_file(temp_excel_file)
        
        assert result is not None
        assert len(result.sheets) == 1
        assert result.sheets[0].name == "Sheet1"
    
    def test_parse_nonexistent_file(self):
        """测试解析不存在的文件"""
        parser = ExcelParser()
        
        with pytest.raises(FileNotFoundError):
            parser.parse_file("nonexistent.xlsx")
    
    @pytest.mark.parametrize("file_path,expected_sheets", [
        ("test1.xlsx", 1),
        ("test2.xlsx", 2),
        ("test3.xlsx", 3),
    ])
    def test_parse_multiple_files(self, file_path, expected_sheets):
        """测试解析多个文件"""
        parser = ExcelParser()
        result = parser.parse_file(file_path)
        
        assert len(result.sheets) == expected_sheets
```

### 5. Fixtures

在 `tests/conftest.py` 中定义共享的 fixtures。

**示例**：
```python
import pytest
from pathlib import Path
from openpyxl import Workbook

@pytest.fixture
def temp_excel_file(tmp_path):
    """创建临时 Excel 文件"""
    file_path = tmp_path / "test.xlsx"
    wb = Workbook()
    ws = wb.active
    ws.title = "Sheet1"
    ws["A1"] = "测试数据"
    wb.save(file_path)
    
    yield str(file_path)
    
    # 清理（pytest 会自动清理 tmp_path）

@pytest.fixture
def mock_supabase_client(mocker):
    """Mock Supabase 客户端"""
    mock_client = mocker.Mock()
    mock_client.storage.from_.return_value.upload.return_value = {"path": "test.xlsx"}
    return mock_client
```

### 6. Mock 对象

使用 `pytest-mock` 进行 Mock。

**示例**：
```python
def test_upload_file(mocker):
    """测试文件上传"""
    # Mock Supabase 客户端
    mock_client = mocker.Mock()
    mock_client.storage.from_.return_value.upload.return_value = {
        "path": "test.xlsx"
    }
    
    # 测试上传
    uploader = FileUploader(mock_client)
    result = uploader.upload("local.xlsx", "remote.xlsx")
    
    assert result["success"] is True
    mock_client.storage.from_.assert_called_once()
```

---

## 性能测试

### 1. 性能基准

在 `tests/` 目录下创建性能测试文件。

**示例**（`tests/performance_test_parser.py`）：
```python
import time
import pytest
from mcp_excel_supabase.excel.parser import ExcelParser

def test_parse_performance(large_excel_file):
    """测试解析性能"""
    parser = ExcelParser()
    
    start_time = time.time()
    result = parser.parse_file(large_excel_file)
    elapsed_time = time.time() - start_time
    
    # 1MB 文件应在 2 秒内完成
    assert elapsed_time < 2.0
    print(f"解析时间：{elapsed_time:.3f}s")
```

### 2. 运行性能测试

```bash
# 运行性能测试
pytest tests/performance_test_*.py -v -s

# 生成性能报告
pytest tests/performance_test_*.py --benchmark-only
```

---

## 调试技巧

### 1. 使用日志

```python
from mcp_excel_supabase.utils.logger import get_logger

logger = get_logger(__name__)

def my_function():
    logger.debug("调试信息")
    logger.info("普通信息")
    logger.warning("警告信息")
    logger.error("错误信息")
```

### 2. 使用 pdb

```python
import pdb

def my_function():
    # 设置断点
    pdb.set_trace()
    
    # 代码继续执行
    result = some_operation()
```

### 3. 使用 pytest 调试

```bash
# 在第一个失败处停止
pytest -x

# 进入 pdb 调试
pytest --pdb

# 在失败处进入 pdb
pytest --pdb --maxfail=1
```

---

## 贡献指南

### 1. 分支策略

- `main`：主分支，稳定版本
- `develop`：开发分支
- `feature/*`：功能分支
- `bugfix/*`：修复分支
- `hotfix/*`：紧急修复分支

### 2. 提交规范

使用 **Conventional Commits** 规范。

**格式**：
```
<type>(<scope>): <subject>

<body>

<footer>
```

**类型**：
- `feat`：新功能
- `fix`：修复 bug
- `docs`：文档更新
- `style`：代码格式（不影响功能）
- `refactor`：重构
- `test`：测试相关
- `chore`：构建/工具相关

**示例**：
```
feat(parser): 添加流式解析支持

- 实现流式读取大文件
- 减少内存占用
- 添加相关测试

Closes #123
```

### 3. Pull Request 流程

1. **Fork 项目**
2. **创建功能分支**：`git checkout -b feature/my-feature`
3. **编写代码**：遵循代码规范
4. **编写测试**：确保覆盖率 ≥ 80%
5. **运行测试**：`pytest`
6. **代码检查**：`black`, `ruff`, `mypy`
7. **提交代码**：遵循提交规范
8. **推送分支**：`git push origin feature/my-feature`
9. **创建 PR**：填写 PR 模板
10. **代码审查**：等待审查和反馈
11. **合并代码**：审查通过后合并

### 4. 代码审查标准

- ✅ 代码符合规范（Black、Ruff、mypy）
- ✅ 测试覆盖率 ≥ 80%
- ✅ 所有测试通过
- ✅ 文档完整（API 文档、注释）
- ✅ 无明显性能问题
- ✅ 无安全漏洞

---

## 发布流程

### 1. 版本号规范

遵循 **语义化版本** (Semantic Versioning)。

**格式**：`MAJOR.MINOR.PATCH`

- `MAJOR`：不兼容的 API 变更
- `MINOR`：向后兼容的功能新增
- `PATCH`：向后兼容的问题修复

**示例**：
- `1.0.0` → `1.0.1`：修复 bug
- `1.0.1` → `1.1.0`：新增功能
- `1.1.0` → `2.0.0`：破坏性变更

### 2. 发布步骤

1. **更新版本号**：修改 `pyproject.toml`
2. **更新 CHANGELOG**：记录变更内容
3. **运行完整测试**：`pytest`
4. **构建包**：`python -m build`
5. **创建 Git 标签**：`git tag v1.0.0`
6. **推送标签**：`git push origin v1.0.0`
7. **发布到 PyPI**：`twine upload dist/*`
8. **创建 GitHub Release**：附上 CHANGELOG

---

## 常见问题

### Q1：如何添加新的 MCP 工具？

1. 在 `excel/` 或 `storage/` 中创建新模块
2. 在 `tools/schemas.py` 中定义输入输出模型
3. 在 `server.py` 中注册工具
4. 编写测试
5. 更新文档

### Q2：如何添加新的 Excel 公式支持？

在 `excel/formula_engine.py` 中添加函数：
```python
SUPPORTED_FUNCTIONS = {
    'SUM': lambda *args: sum(args),
    'NEW_FUNC': lambda *args: custom_logic(args)
}
```

### Q3：如何提高测试覆盖率？

1. 查看覆盖率报告：`htmlcov/index.html`
2. 找到未覆盖的代码
3. 编写针对性测试
4. 重新运行测试

---

## 相关资源

- **API 文档**：[api.md](api.md)
- **架构文档**：[architecture.md](architecture.md)
- **故障排查**：[troubleshooting.md](troubleshooting.md)
- **使用示例**：[examples/](examples/)

---

**文档版本**：1.0.0  
**最后更新**：2025-10-20  
**维护者**：Excel MCP Server Team

