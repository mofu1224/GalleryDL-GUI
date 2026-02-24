<#
  build.ps1 — Gallery-DL GUI
  Produces a portable folder distribution in dist\GalleryDL-GUI\
#>

$ErrorActionPreference = "Stop"
$ROOT = Get-Location
$PYTHON = "$ROOT\python\python.exe"
$VERSION = "1.0.0"
$DIST_DIR = "$ROOT\dist\GalleryDL-GUI"
$ZIP_NAME = "GalleryDL-GUI-v${VERSION}-win64.zip"
$ZIP_PATH = "$ROOT\$ZIP_NAME"

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Gallery-DL GUI  v$VERSION  — Build Script"      -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# 1. Generate icon
Write-Host "[1/5] Generating icon..." -ForegroundColor Yellow
if (Test-Path "$ROOT\make_icon.py") {
    & $PYTHON "$ROOT\make_icon.py"
}

# 2. Clean
Write-Host "[2/5] Cleaning previous build artifacts..." -ForegroundColor Yellow
@("build", "dist", "__pycache__") | ForEach-Object {
    if (Test-Path "$ROOT\$_") { Remove-Item "$ROOT\$_" -Recurse -Force }
}

# 3. PyInstaller
Write-Host "[3/5] Running PyInstaller..." -ForegroundColor Yellow
& $PYTHON -m PyInstaller --clean --noconfirm "$ROOT\gallery_dl_gui.spec"

if (-not (Test-Path "$DIST_DIR\GalleryDL-GUI.exe")) {
    Write-Error "PyInstaller failed."
    exit 1
}

# 4. Assets
Write-Host "[4/5] Copying runtime assets..." -ForegroundColor Yellow
@("cookies", "json_input", "DownloadData") | ForEach-Object {
    $dir = "$DIST_DIR\$_"
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory $dir | Out-Null }
}

if (Test-Path "$ROOT\gallery-dl.conf") { Copy-Item "$ROOT\gallery-dl.conf" "$DIST_DIR\" -Force }
if (Test-Path "$ROOT\convert_cookies.py") { Copy-Item "$ROOT\convert_cookies.py" "$DIST_DIR\" -Force }

# Copy python dir (excluding the exe and site-packages if we want to save space, but let's follow the previous script)
# Since we are using this python to run the script, we should be careful.
# But Copy-Item usually works if we don't try to overwrite.
Write-Host "  Copying Python environment..." -ForegroundColor Gray
Copy-Item "$ROOT\python" "$DIST_DIR\python" -Recurse -Force

# README
@"
# Gallery-DL GUI  v$VERSION
Download images and galleries with ease.

## Quick Start
1. Run **GalleryDL-GUI.exe**
2. Paste URL and click **Start Download**
"@ | Out-File -FilePath "$DIST_DIR\README.txt" -Encoding UTF8

# 5. Zip
Write-Host "[5/5] Creating ZIP archive..." -ForegroundColor Yellow
if (Test-Path $ZIP_PATH) { Remove-Item $ZIP_PATH -Force }
# Wait a bit for file handles to clear (OS indexers, etc.)
Start-Sleep -Seconds 5
Compress-Archive -Path "$DIST_DIR\*" -DestinationPath $ZIP_PATH

Write-Host "Build complete! ZIP: $ZIP_PATH" -ForegroundColor Green
