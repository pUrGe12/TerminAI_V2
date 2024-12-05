#!/bin/bash

username=$(whoami)
os_type=$(uname)

read -p "Submit your sudo password? Note that this data is not going anywhere, its saved in a file in this directory itself (y/n): " choice

if [[ "$choice" == "y" ]]; then
    read -sp "Please enter your sudo password: " sudo_password
    echo
else
    # If sudo password is not provided, we call it REDACTED
    sudo_password="REDACTED"
fi

# Saving that in data.py
cat > data.py <<EOF
user_dict = {
    "username": "$username",
    "operating_system": "$os_type",
    "sudo_password": "$sudo_password"
}
EOF

read -p "Enter your Supabase URL: " supabase_url
read -p "Enter your Supabase key (anon public): " supabase_key
read -p "Enter your Gemini API key: " api_key

cat > ../../.env <<EOF
API_KEY=$api_key
SUPABASE_URL=$supabase_url
SUPABASE_KEY=$supabase_key
EOF

# Also adding the command finder code here to figure out which commands are available in the system

# I am using compgen to find the commands present in the system that can be executed, excluding those starting with "_" cause those can be called
# from completion functions only (don't know what that means but anyway)

commands=$(compgen -c | grep -v '^_' | sort -u)             # Sorting and removing duplicates as well

output_file="system_commands.py"                            # saving that to a python file cause its easier to import a list

{
  echo "commands_list = ["
  for cmd in $commands; do
    echo "    \"$cmd\","
  done
  echo "]"
} > $output_file

# Creating a list and saving the commands. 

echo "Setup completed. Ensure that you have run the table_creation.sql command in the SQL editor of your database"