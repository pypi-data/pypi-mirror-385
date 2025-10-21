# 推送到 GitHub 脚本
# 用于将代码和标签推送到 GitHub

param(
    [Parameter(Mandatory=$false)]
    [switch]$Force
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  推送到 GitHub" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Git 状态
Write-Host "[1/4] 检查 Git 状态..." -ForegroundColor Yellow
$status = git status --porcelain
if ($status) {
    Write-Host "警告: 有未提交的更改" -ForegroundColor Yellow
    git status --short
    Write-Host ""
    
    if (-not $Force) {
        $response = Read-Host "是否继续推送? (y/N)"
        if ($response -ne "y" -and $response -ne "Y") {
            Write-Host "已取消推送" -ForegroundColor Yellow
            exit 0
        }
    }
}
Write-Host "✓ Git 状态检查完成" -ForegroundColor Green
Write-Host ""

# 检查远程仓库
Write-Host "[2/4] 检查远程仓库..." -ForegroundColor Yellow
$remoteUrl = git remote get-url origin 2>$null
if (-not $remoteUrl) {
    Write-Host "错误: 未配置远程仓库" -ForegroundColor Red
    Write-Host "请先运行: git remote add origin <仓库URL>" -ForegroundColor Yellow
    exit 1
}
Write-Host "  远程仓库: $remoteUrl" -ForegroundColor Cyan
Write-Host "✓ 远程仓库配置正确" -ForegroundColor Green
Write-Host ""

# 推送代码
Write-Host "[3/4] 推送代码到 main 分支..." -ForegroundColor Yellow
Write-Host "  执行: git push origin main" -ForegroundColor Cyan
git push origin main
if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: 推送失败" -ForegroundColor Red
    Write-Host ""
    Write-Host "可能的原因:" -ForegroundColor Yellow
    Write-Host "  1. 网络连接问题" -ForegroundColor White
    Write-Host "  2. 需要认证（请在浏览器中完成）" -ForegroundColor White
    Write-Host "  3. 权限不足" -ForegroundColor White
    Write-Host ""
    Write-Host "请解决问题后重新运行此脚本" -ForegroundColor Yellow
    exit 1
}
Write-Host "✓ 代码推送成功" -ForegroundColor Green
Write-Host ""

# 推送标签
Write-Host "[4/4] 推送标签..." -ForegroundColor Yellow
Write-Host "  执行: git push origin v1.0.0" -ForegroundColor Cyan
git push origin v1.0.0
if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: 标签推送失败" -ForegroundColor Red
    exit 1
}
Write-Host "✓ 标签推送成功" -ForegroundColor Green
Write-Host ""

# 完成
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  推送完成！" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "下一步操作:" -ForegroundColor Yellow
Write-Host "  1. 访问 GitHub 仓库:" -ForegroundColor White
Write-Host "     $remoteUrl" -ForegroundColor Cyan
Write-Host ""
Write-Host "  2. 创建 GitHub Release:" -ForegroundColor White
Write-Host "     - 点击 'Releases' -> 'Create a new release'" -ForegroundColor White
Write-Host "     - 选择标签: v1.0.0" -ForegroundColor White
Write-Host "     - 标题: v1.0.0 - Initial Release" -ForegroundColor White
Write-Host "     - 复制 .github/RELEASE_TEMPLATE.md 的内容" -ForegroundColor White
Write-Host "     - 点击 'Publish release'" -ForegroundColor White
Write-Host ""
Write-Host "  3. 测试安装:" -ForegroundColor White
Write-Host "     uvx --from git+$remoteUrl mcp-excel-supabase" -ForegroundColor Cyan
Write-Host ""

