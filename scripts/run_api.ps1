Set-Location $PSScriptRoot\..
if (-not (Test-Path .\.venv\Scripts\Activate.ps1)) {
    Write-Error "Crea el venv: py -3 -m venv .venv"
    exit 1
}
.\.venv\Scripts\Activate.ps1
python -m app.main
