# Check IIS Configuration for Enhanced Media Scraper
Write-Host "Checking IIS Configuration..." -ForegroundColor Cyan

# Check if IIS is installed
$iisFeature = Get-WindowsOptionalFeature -Online -FeatureName IIS-WebServerRole
if ($iisFeature.State -eq "Enabled") {
    Write-Host "✓ IIS is installed" -ForegroundColor Green
} else {
    Write-Host "✗ IIS is not installed" -ForegroundColor Red
    exit 1
}

# List all sites
Write-Host "`nExisting IIS Sites:" -ForegroundColor Yellow
Import-Module WebAdministration
Get-Website | Format-Table Name, State, PhysicalPath -AutoSize

# Check for scraper site
$scraperSite = Get-Website | Where-Object { $_.Name -like "*scraper*" }
if ($scraperSite) {
    Write-Host "`n✓ Scraper site found: $($scraperSite.Name)" -ForegroundColor Green
} else {
    Write-Host "`n✗ No scraper site found in IIS" -ForegroundColor Yellow
}

Write-Host "`nPort 3050 will be used for Flask (Scraper project range: 3000-3099)" -ForegroundColor Cyan