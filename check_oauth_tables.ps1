# Check OAuth-related database tables
$query = @"
SELECT
    c.COLUMN_NAME,
    c.DATA_TYPE,
    c.IS_NULLABLE,
    c.CHARACTER_MAXIMUM_LENGTH
FROM INFORMATION_SCHEMA.COLUMNS c
WHERE TABLE_NAME = 'users'
ORDER BY ORDINAL_POSITION;
"@

Write-Host "Checking users table structure for OAuth fields..." -ForegroundColor Cyan
sqlcmd -S localhost\SQLEXPRESS -d Scraped -Q $query -W

Write-Host "`nChecking for Google ID column specifically..." -ForegroundColor Cyan
$googleQuery = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'users' AND COLUMN_NAME LIKE '%google%'"
sqlcmd -S localhost\SQLEXPRESS -d Scraped -Q $googleQuery -W