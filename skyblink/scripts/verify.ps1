$ErrorActionPreference = "Stop"
Write-Host "Running Verification Script..."

Write-Host "Testing Python..."
python -m pytest -v
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Generating data..."
python -m pipeline.skyblink_pipeline.synth.generate
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Testing Web..."
Push-Location web
npm test
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
npm run build
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Pop-Location

Write-Host "============================"
Write-Host "Verify OK"
Write-Host "============================"
