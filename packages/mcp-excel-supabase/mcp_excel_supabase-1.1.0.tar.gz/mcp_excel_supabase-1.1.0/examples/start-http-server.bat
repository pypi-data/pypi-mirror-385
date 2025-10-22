@echo off
REM Excel MCP Server - HTTP 传输模式启动脚本
REM 适用于 Cherry Studio 等 Web 客户端

echo ========================================
echo   Excel MCP Server - HTTP Mode
echo ========================================
echo.

REM 配置传输模式
set MCP_TRANSPORT=http
set MCP_HOST=127.0.0.1
set MCP_PORT=8000

REM 配置 Supabase（请替换为你的实际凭证）
set SUPABASE_URL=https://yourproject.supabase.co
set SUPABASE_KEY=your-service-role-key-here

echo 配置信息:
echo   传输模式: %MCP_TRANSPORT%
echo   服务器地址: http://%MCP_HOST%:%MCP_PORT%/mcp/
echo   Supabase URL: %SUPABASE_URL%
echo.
echo 启动服务器...
echo.

REM 启动服务器
uvx mcp-excel-supabase

pause

