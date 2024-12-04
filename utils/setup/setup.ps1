# System username
$username = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name

# operating system type
$os_type = (Get-WmiObject -Class Win32_OperatingSystem).Caption

# No concept of sudo in windows so we don't really need this. We can't execute powershell commands unless execution policy is bypassed.
$sudo_password = "REDACTED"

$data_py_content = @"
user_dict = {
    "username": "$username",
    "operating_system": "$os_type",
    "sudo_password": "$sudo_password"
}
"@
Set-Content -Path "data.py" -Value $data_py_content


$supabase_url = Read-Host "Enter your Supabase URL"
$supabase_key = Read-Host "Enter your Supabase KEY"
$api_key = Read-Host "Enter your API_KEY"

$env_content = @"
API_KEY=$api_key
SUPABASE_URL=$supabase_url
SUPABASE_KEY=$supabase_key
"@

Set-Content -Path "../../.env" -Value $env_content

Write-Host "Setup completed. Ensure that you have run the table_creation.sql command in the SQL editor of your database"
