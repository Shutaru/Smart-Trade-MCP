# Smart-Trade MCP - Diagnostic Helper Script
# Run this before testing in Claude Desktop

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SMART-TRADE MCP - PRE-TEST DIAGNOSTICS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check if Claude Desktop is running
Write-Host "[1/6] Checking if Claude Desktop is running..." -ForegroundColor Yellow
$claudeProcess = Get-Process -Name "Claude" -ErrorAction SilentlyContinue

if ($claudeProcess) {
    Write-Host "  ? Claude Desktop is running (PID: $($claudeProcess.Id))" -ForegroundColor Green
    Write-Host "  ??  Recommendation: Restart Claude Desktop to load new code" -ForegroundColor Yellow
    
    $restart = Read-Host "  Do you want to restart Claude Desktop now? (y/n)"
    if ($restart -eq "y" -or $restart -eq "Y") {
        Write-Host "  Stopping Claude Desktop..." -ForegroundColor Yellow
        Stop-Process -Name "Claude" -Force
        Start-Sleep -Seconds 2
        Write-Host "  ? Claude Desktop stopped. Please start it manually." -ForegroundColor Green
    }
} else {
    Write-Host "  ? Claude Desktop is not running" -ForegroundColor Green
}

Write-Host ""

# 2. Check for orphaned Python processes
Write-Host "[2/6] Checking for orphaned Python MCP processes..." -ForegroundColor Yellow
$mcpProcesses = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $_.Path -like "*Smart-Trade-MCP*"
}

if ($mcpProcesses) {
    Write-Host "  ??  Found $($mcpProcesses.Count) orphaned Python process(es)" -ForegroundColor Yellow
    foreach ($proc in $mcpProcesses) {
        Write-Host "    PID: $($proc.Id) | Path: $($proc.Path)" -ForegroundColor Gray
    }
    
    $kill = Read-Host "  Kill these processes? (y/n)"
    if ($kill -eq "y" -or $kill -eq "Y") {
        $mcpProcesses | Stop-Process -Force
        Write-Host "  ? Processes terminated" -ForegroundColor Green
    }
} else {
    Write-Host "  ? No orphaned processes found" -ForegroundColor Green
}

Write-Host ""

# 3. Check Claude Desktop config
Write-Host "[3/6] Checking Claude Desktop configuration..." -ForegroundColor Yellow
$configPath = "$env:APPDATA\Claude\claude_desktop_config.json"

if (Test-Path $configPath) {
    Write-Host "  ? Config file found: $configPath" -ForegroundColor Green
    
    $config = Get-Content $configPath -Raw | ConvertFrom-Json
    
    if ($config.mcpServers."smart-trade") {
        Write-Host "  ? smart-trade MCP server configured" -ForegroundColor Green
        $serverConfig = $config.mcpServers."smart-trade"
        Write-Host "    CWD: $($serverConfig.cwd)" -ForegroundColor Gray
        Write-Host "    Command: $($serverConfig.command)" -ForegroundColor Gray
        
        # Verify CWD exists
        if (Test-Path $serverConfig.cwd) {
            Write-Host "  ? CWD directory exists" -ForegroundColor Green
        } else {
            Write-Host "  ? CWD directory NOT FOUND!" -ForegroundColor Red
        }
    } else {
        Write-Host "  ? smart-trade MCP server NOT configured!" -ForegroundColor Red
        Write-Host "  See: TESTE_CLAUDE_DESKTOP.md (Step 1, Option B)" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ? Config file NOT FOUND!" -ForegroundColor Red
    Write-Host "  Expected at: $configPath" -ForegroundColor Gray
}

Write-Host ""

# 4. Check Python environment
Write-Host "[4/6] Checking Python environment..." -ForegroundColor Yellow

$pythonCmd = Get-Command python -ErrorAction SilentlyContinue

if ($pythonCmd) {
    Write-Host "  ? Python found: $($pythonCmd.Path)" -ForegroundColor Green
    
    $pythonVersion = python --version 2>&1
    Write-Host "    Version: $pythonVersion" -ForegroundColor Gray
    
    # Check if we can import the MCP server
    Write-Host "  Testing MCP server import..." -ForegroundColor Yellow
    Push-Location "C:\Users\shuta\source\repos\Smart-Trade-MCP"
    
    $importTest = python -c "from src.mcp_server.server import SmartTradeMCPServer; print('OK')" 2>&1
    
    if ($importTest -eq "OK") {
        Write-Host "  ? MCP server imports successfully" -ForegroundColor Green
    } else {
        Write-Host "  ? MCP server import FAILED!" -ForegroundColor Red
        Write-Host "  Error: $importTest" -ForegroundColor Gray
    }
    
    Pop-Location
} else {
    Write-Host "  ? Python NOT FOUND in PATH!" -ForegroundColor Red
}

Write-Host ""

# 5. Check backtest tool version
Write-Host "[5/6] Checking backtest tool version..." -ForegroundColor Yellow
Push-Location "C:\Users\shuta\source\repos\Smart-Trade-MCP"

$versionCheck = python -c @"
from src.mcp_server.tools.backtest import BACKTEST_TOOL_VERSION
print(BACKTEST_TOOL_VERSION)
"@ 2>&1

if ($versionCheck -eq "2.0.1-debug") {
    Write-Host "  ? Backtest tool version: $versionCheck" -ForegroundColor Green
} else {
    Write-Host "  ??  Backtest tool version: $versionCheck" -ForegroundColor Yellow
    Write-Host "    Expected: 2.0.1-debug" -ForegroundColor Gray
}

Pop-Location
Write-Host ""

# 6. Check recent logs
Write-Host "[6/6] Checking Claude Desktop logs..." -ForegroundColor Yellow
$logPath = "$env:APPDATA\Claude\logs\mcp-server-smart-trade.log"

if (Test-Path $logPath) {
    Write-Host "  ? Log file found: $logPath" -ForegroundColor Green
    
    $logInfo = Get-Item $logPath
    Write-Host "    Size: $([math]::Round($logInfo.Length / 1KB, 2)) KB" -ForegroundColor Gray
    Write-Host "    Last modified: $($logInfo.LastWriteTime)" -ForegroundColor Gray
    
    # Check if logs are recent (within last hour)
    $ageMinutes = (Get-Date) - $logInfo.LastWriteTime
    if ($ageMinutes.TotalMinutes -lt 60) {
        Write-Host "  ? Logs are recent (updated $([math]::Round($ageMinutes.TotalMinutes, 0)) minutes ago)" -ForegroundColor Green
    } else {
        Write-Host "  ??  Logs are old (updated $([math]::Round($ageMinutes.TotalHours, 1)) hours ago)" -ForegroundColor Yellow
        Write-Host "    May indicate MCP server isn't running" -ForegroundColor Gray
    }
} else {
    Write-Host "  ??  Log file NOT FOUND" -ForegroundColor Yellow
    Write-Host "  This is normal if Claude Desktop hasn't been started yet" -ForegroundColor Gray
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DIAGNOSTICS COMPLETE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. Start Claude Desktop (if not running)" -ForegroundColor White
Write-Host "2. Wait for MCP server to load (~5 seconds)" -ForegroundColor White
Write-Host "3. Test with prompt from TESTE_CLAUDE_DESKTOP.md" -ForegroundColor White
Write-Host "4. Check logs if issues occur" -ForegroundColor White
Write-Host ""

$viewLogs = Read-Host "Do you want to view the latest logs now? (y/n)"
if ($viewLogs -eq "y" -or $viewLogs -eq "Y") {
    if (Test-Path $logPath) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "LATEST LOGS (Last 50 lines):" -ForegroundColor Cyan
        Write-Host "========================================" -ForegroundColor Cyan
        Get-Content $logPath -Tail 50
    } else {
        Write-Host "  No logs available yet" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
