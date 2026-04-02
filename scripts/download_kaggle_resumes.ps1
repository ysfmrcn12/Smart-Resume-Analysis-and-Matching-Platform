param(
  [string]$Dataset = "gauravduttakiit/resume-dataset",
  [string]$OutDir = "data/resumes"
)

# Optional helper to download resume datasets using the Kaggle CLI.
# Prereqs:
#   - Install Kaggle CLI: `pip install kaggle`
#   - Add credentials to ~/.kaggle/kaggle.json
#
# Usage:
#   .\scripts\download_kaggle_resumes.ps1
#   .\scripts\download_kaggle_resumes.ps1 -Dataset "hadikp/resume-data-pdf" -OutDir "data/resumes"

Write-Host "Kaggle dataset: $Dataset"
Write-Host "Output directory: $OutDir"

if (-not (Get-Command kaggle -ErrorAction SilentlyContinue)) {
  Write-Host "[ERROR] Kaggle CLI not found."
  Write-Host "Install it: pip install kaggle"
  Write-Host "Then add your API credentials to ~/.kaggle/kaggle.json"
  exit 1
}

if (-not (Test-Path $OutDir)) {
  New-Item -ItemType Directory -Path $OutDir | Out-Null
}

Write-Host "Downloading..."
kaggle datasets download -d $Dataset -p $OutDir -f

Write-Host "Extracting zip files..."
Get-ChildItem -Path $OutDir -Filter "*.zip" | ForEach-Object {
  $zipPath = $_.FullName
  # Extract next to the zip file (may create extra top-level folders depending on the dataset).
  Expand-Archive -Path $zipPath -DestinationPath $OutDir -Force
}

Write-Host "Done."

