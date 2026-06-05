$ErrorActionPreference = "Stop"
$Python = if ($env:PYTHON) { $env:PYTHON } else { "python" }
& $Python -m uvicorn fraud_detection.api.main:app --host 0.0.0.0 --port 8000
