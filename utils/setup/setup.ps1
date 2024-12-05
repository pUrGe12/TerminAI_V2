# System username
$username = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name

# Operating system type
$os_type = (Get-WmiObject -Class Win32_OperatingSystem).Caption

# No concept of sudo in Windows
$sudo_password = "REDACTED"

# Data for user details
$data_py_content = @"
user_dict = {
    "username": "$username",
    "operating_system": "$os_type",
    "sudo_password": "$sudo_password"
}
"@
Set-Content -Path "data.py" -Value $data_py_content

# Retrieve Supabase credentials
$supabase_url = Read-Host "Enter your Supabase URL"
$supabase_key = Read-Host "Enter your Supabase KEY"
$api_key = Read-Host "Enter your API_KEY"

$env_content = @"
API_KEY=$api_key
SUPABASE_URL=$supabase_url
SUPABASE_KEY=$supabase_key
"@
Set-Content -Path "../../.env" -Value $env_content


# Fetching all PowerShell commands and saving that as a list 
$commands = Get-Command | Select-Object -ExpandProperty Name
$commands_list = $commands -join "', '"
$system_commands_py_content = @"
commands_list = [
    '$commands_list'
]
"@

Set-Content -Path "system_commands.py" -Value $system_commands_py_content

Write-Host "Setup completed. Ensure that you have run the table_creation.sql command in the SQL editor of your database"