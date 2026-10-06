$ErrorActionPreference = "Stop"
Write-Host "Running pipeline..."
python -m pipeline.skyblink_pipeline.core.run
