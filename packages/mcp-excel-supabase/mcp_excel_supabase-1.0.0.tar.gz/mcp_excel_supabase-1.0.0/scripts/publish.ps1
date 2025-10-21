# Excel MCP Server - 发布脚本
# 用于自动化发布流程

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("github", "testpypi", "pypi", "all")]
    [string]$Target = "github",
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipTests,
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipClean
)

# 颜色输出函数
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

# 错误处理
$ErrorActionPreference = "Stop"

Write-ColorOutput "========================================" "Cyan"
Write-ColorOutput "  Excel MCP Server - 发布脚本" "Cyan"
Write-ColorOutput "========================================" "Cyan"
Write-Host ""

# 1. 检查虚拟环境
Write-ColorOutput "[1/7] 检查虚拟环境..." "Yellow"
if (-not (Test-Path "venv")) {
    Write-ColorOutput "错误: 未找到虚拟环境，请先运行 python -m venv venv" "Red"
    exit 1
}

# 激活虚拟环境
& ".\venv\Scripts\Activate.ps1"
Write-ColorOutput "✓ 虚拟环境已激活" "Green"
Write-Host ""

# 2. 清理项目
if (-not $SkipClean) {
    Write-ColorOutput "[2/7] 清理项目..." "Yellow"
    
    # 删除缓存
    Get-ChildItem -Path . -Include __pycache__,.pytest_cache,.mypy_cache,.ruff_cache -Recurse -Force -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    
    # 删除测试产物
    Remove-Item -Path htmlcov,.coverage,logs,Formal-unit-testing -Recurse -Force -ErrorAction SilentlyContinue
    
    # 删除构建产物
    Remove-Item -Path dist,build -Recurse -Force -ErrorAction SilentlyContinue
    Get-ChildItem -Path . -Filter "*.egg-info" -Recurse -Force -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    
    Write-ColorOutput "✓ 项目清理完成" "Green"
} else {
    Write-ColorOutput "[2/7] 跳过清理" "Gray"
}
Write-Host ""

# 3. 运行测试
if (-not $SkipTests) {
    Write-ColorOutput "[3/7] 运行测试..." "Yellow"
    
    # 运行 pytest
    Write-ColorOutput "  运行单元测试..." "Cyan"
    pytest --tb=short
    if ($LASTEXITCODE -ne 0) {
        Write-ColorOutput "错误: 测试失败，请修复后再发布" "Red"
        exit 1
    }
    
    # 运行代码质量检查
    Write-ColorOutput "  运行 Ruff 检查..." "Cyan"
    ruff check .
    if ($LASTEXITCODE -ne 0) {
        Write-ColorOutput "警告: Ruff 检查发现问题" "Yellow"
    }
    
    Write-ColorOutput "  运行 Black 检查..." "Cyan"
    black --check .
    if ($LASTEXITCODE -ne 0) {
        Write-ColorOutput "警告: Black 检查发现格式问题" "Yellow"
    }
    
    Write-ColorOutput "✓ 测试通过" "Green"
} else {
    Write-ColorOutput "[3/7] 跳过测试" "Gray"
}
Write-Host ""

# 4. 构建包
Write-ColorOutput "[4/7] 构建分发包..." "Yellow"

# 安装构建工具
pip install --upgrade build twine --quiet

# 构建
python -m build
if ($LASTEXITCODE -ne 0) {
    Write-ColorOutput "错误: 构建失败" "Red"
    exit 1
}

# 检查构建结果
Write-ColorOutput "  检查构建产物..." "Cyan"
twine check dist/*
if ($LASTEXITCODE -ne 0) {
    Write-ColorOutput "错误: 包检查失败" "Red"
    exit 1
}

Write-ColorOutput "✓ 构建完成" "Green"
Write-Host ""

# 5. 发布到 GitHub
if ($Target -eq "github" -or $Target -eq "all") {
    Write-ColorOutput "[5/7] 准备发布到 GitHub..." "Yellow"
    
    # 检查 Git 状态
    $gitStatus = git status --porcelain
    if ($gitStatus) {
        Write-ColorOutput "警告: 有未提交的更改" "Yellow"
        Write-ColorOutput "未提交的文件:" "Yellow"
        git status --short
        Write-Host ""
        
        $response = Read-Host "是否继续? (y/N)"
        if ($response -ne "y" -and $response -ne "Y") {
            Write-ColorOutput "已取消发布" "Yellow"
            exit 0
        }
    }
    
    # 检查远程仓库
    $remoteUrl = git remote get-url origin 2>$null
    if (-not $remoteUrl) {
        Write-ColorOutput "错误: 未配置远程仓库" "Red"
        Write-ColorOutput "请先运行: git remote add origin <仓库URL>" "Yellow"
        exit 1
    }
    
    Write-ColorOutput "  远程仓库: $remoteUrl" "Cyan"
    Write-ColorOutput "✓ GitHub 准备就绪" "Green"
    Write-Host ""
    Write-ColorOutput "请手动执行以下步骤:" "Yellow"
    Write-ColorOutput "  1. git add ." "White"
    Write-ColorOutput "  2. git commit -m 'Release v1.0.0'" "White"
    Write-ColorOutput "  3. git push origin main" "White"
    Write-ColorOutput "  4. 在 GitHub 上创建 Release (tag: v1.0.0)" "White"
} else {
    Write-ColorOutput "[5/7] 跳过 GitHub 发布" "Gray"
}
Write-Host ""

# 6. 发布到 TestPyPI
if ($Target -eq "testpypi" -or $Target -eq "all") {
    Write-ColorOutput "[6/7] 发布到 TestPyPI..." "Yellow"
    
    $response = Read-Host "确认上传到 TestPyPI? (y/N)"
    if ($response -eq "y" -or $response -eq "Y") {
        twine upload --repository testpypi dist/*
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✓ 已上传到 TestPyPI" "Green"
            Write-ColorOutput "测试安装: uvx --index-url https://test.pypi.org/simple/ mcp-excel-supabase" "Cyan"
        } else {
            Write-ColorOutput "错误: 上传失败" "Red"
        }
    } else {
        Write-ColorOutput "已跳过 TestPyPI 上传" "Yellow"
    }
} else {
    Write-ColorOutput "[6/7] 跳过 TestPyPI 发布" "Gray"
}
Write-Host ""

# 7. 发布到 PyPI
if ($Target -eq "pypi" -or $Target -eq "all") {
    Write-ColorOutput "[7/7] 发布到 PyPI..." "Yellow"
    Write-ColorOutput "警告: 这将发布到正式 PyPI，无法撤回！" "Red"
    
    $response = Read-Host "确认上传到 PyPI? (y/N)"
    if ($response -eq "y" -or $response -eq "Y") {
        twine upload dist/*
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✓ 已上传到 PyPI" "Green"
            Write-ColorOutput "安装命令: uvx mcp-excel-supabase" "Cyan"
        } else {
            Write-ColorOutput "错误: 上传失败" "Red"
        }
    } else {
        Write-ColorOutput "已跳过 PyPI 上传" "Yellow"
    }
} else {
    Write-ColorOutput "[7/7] 跳过 PyPI 发布" "Gray"
}
Write-Host ""

# 完成
Write-ColorOutput "========================================" "Cyan"
Write-ColorOutput "  发布流程完成！" "Cyan"
Write-ColorOutput "========================================" "Cyan"
Write-Host ""

# 显示下一步操作
Write-ColorOutput "下一步操作:" "Yellow"
if ($Target -eq "github" -or $Target -eq "all") {
    Write-ColorOutput "  1. 推送代码到 GitHub" "White"
    Write-ColorOutput "  2. 创建 GitHub Release (v1.0.0)" "White"
}
if ($Target -eq "pypi" -or $Target -eq "all") {
    Write-ColorOutput "  3. 测试安装: uvx mcp-excel-supabase" "White"
    Write-ColorOutput "  4. 更新 README 中的安装说明" "White"
}
Write-Host ""
Write-ColorOutput "详细文档: docs/PUBLISHING_GUIDE.md" "Cyan"

