try {
    $r = Invoke-WebRequest -Uri 'http://localhost:5175/' -UseBasicParsing -TimeoutSec 5
    Write-Output "FRONTEND STATUS: $($r.StatusCode)"
    Write-Output "CONTENT LENGTH: $($r.Content.Length) bytes"
    if ($r.Content -match 'Career') { Write-Output "FRONTEND: Career-Ops page FOUND" }
} catch {
    Write-Output "FRONTEND FAILED: $($_.Exception.Message)"
}

Write-Output "---"

try {
    $r = Invoke-WebRequest -Uri 'http://localhost:5000/api/stats' -UseBasicParsing -TimeoutSec 5
    Write-Output "BACKEND STATUS: $($r.StatusCode)"
    Write-Output "BACKEND DATA: $($r.Content)"
} catch {
    Write-Output "BACKEND FAILED: $($_.Exception.Message)"
}

Write-Output "---"

try {
    $r = Invoke-WebRequest -Uri 'http://localhost:5000/api/doctor' -UseBasicParsing -TimeoutSec 5
    Write-Output "DOCTOR STATUS: $($r.StatusCode)"
    Write-Output "DOCTOR DATA: $($r.Content)"
} catch {
    Write-Output "DOCTOR FAILED: $($_.Exception.Message)"
}
