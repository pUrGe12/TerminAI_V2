#!/bin/bash

username=$(whoami)
os_type=$(uname)

read -p "Want to submit your sudo password, if you're planning on using these privileges? (y/n): " choice

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

echo "Setup completed. Ensure that you have run the table_creation.sql command in the SQL editor of your database"