$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

Write-Host '== Limpeza build/dist/__pycache__ =='
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue build, dist
Get-ChildItem -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

$venvPython = Join-Path $projectRoot '.venv\Scripts\python.exe'
if (-not (Test-Path $venvPython)) {
    Write-Host '== Criando venv =='
    python -m venv .venv
}

Write-Host '== Instalando dependencias =='
& $venvPython -m pip install -r requirements.txt
& $venvPython -m pip install pyinstaller

Write-Host '== Teste de execucao (feche a janela para continuar) =='
& $venvPython .\app\main.py

$useCollectAll = $false
$buildOnefile = $false

Write-Host '== Build onedir =='
$collectArgs = @()
if ($useCollectAll) {
    $collectArgs = @('--collect-all', 'matplotlib', '--collect-all', 'ttkbootstrap')
}
& $venvPython -m PyInstaller --noconsole --onedir --name 'FluxoCaixa' @collectArgs .\app\main.py

$distDir = Join-Path $projectRoot 'dist\FluxoCaixa'
$batPath = Join-Path $distDir 'Run_FluxoCaixa.bat'
$batContent = @(
    '@echo off',
    'setlocal',
    'start "" "%~dp0FluxoCaixa.exe"'
)
$batContent | Set-Content -Path $batPath -Encoding ASCII
Write-Host "OK: Run_FluxoCaixa.bat criado em $batPath"

if ($buildOnefile) {
    Write-Host '== Build onefile =='
    & $venvPython -m PyInstaller --noconsole --onefile --name 'FluxoCaixa' @collectArgs .\app\main.py
}

Write-Host '== Build concluido =='
