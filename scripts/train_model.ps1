$ErrorActionPreference = "Stop"
$Python = if ($env:PYTHON) { $env:PYTHON } else { "python" }
& $Python -m fraud_detection.models.train --no-tune
