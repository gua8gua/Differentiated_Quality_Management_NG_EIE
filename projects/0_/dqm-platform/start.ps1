param(
  [switch]$ApiOnly,
  [switch]$WebOnly,
  [switch]$KgOnly
)

$root = $PSScriptRoot
$selfRoot = Split-Path $root -Parent
$apiDir = Join-Path $root "apps\api"
$webDir = Join-Path $root "apps\web"
$kgDir = Join-Path $selfRoot "dqm-kg-rag"

function Start-Api {
  Write-Host "启动平台 API: http://127.0.0.1:8020" -ForegroundColor Cyan
  Write-Host "API 文档: http://127.0.0.1:8020/docs" -ForegroundColor Cyan
  Push-Location $apiDir
  if (-not (Test-Path ".venv")) {
    python -m venv .venv
  }
  & ".\.venv\Scripts\Activate.ps1"
  pip install -r requirements.txt | Out-Null
  uvicorn main:app --reload --host 127.0.0.1 --port 8020
  Pop-Location
}

function Start-KgRag {
  Write-Host "启动知识图谱 API: http://127.0.0.1:8010" -ForegroundColor Magenta
  Write-Host "图谱接口: http://127.0.0.1:8010/graph" -ForegroundColor Magenta
  Push-Location $kgDir
  if (-not (Test-Path ".venv")) {
    python -m venv .venv
  }
  & ".\.venv\Scripts\Activate.ps1"
  pip install -e . | Out-Null
  uvicorn dqm_kg_rag.api:app --reload --host 127.0.0.1 --port 8010
  Pop-Location
}

function Start-Web {
  Write-Host "启动平台前端: http://127.0.0.1:5173" -ForegroundColor Green
  Push-Location $webDir
  if (-not (Test-Path "node_modules")) {
    npm install
  }
  npm run dev -- --host 127.0.0.1 --port 5173
  Pop-Location
}

if ($ApiOnly) { Start-Api; exit }
if ($WebOnly) { Start-Web; exit }
if ($KgOnly) { Start-KgRag; exit }

Write-Host "将分别启动 kg-rag、platform API 与前端（三个新窗口）。" -ForegroundColor Yellow
Start-Process powershell -ArgumentList @("-NoExit", "-File", $PSCommandPath, "-KgOnly")
Start-Sleep -Seconds 2
Start-Process powershell -ArgumentList @("-NoExit", "-File", $PSCommandPath, "-ApiOnly")
Start-Sleep -Seconds 2
Start-Process powershell -ArgumentList @("-NoExit", "-File", $PSCommandPath, "-WebOnly")
Write-Host "访问演示页面: http://127.0.0.1:5173" -ForegroundColor Green
Write-Host "知识图谱 API: http://127.0.0.1:8010/graph" -ForegroundColor Green
