# import requests

# supabase_url = ""
# service_role_key = ""

# rpc_endpoint = f"{supabase_url}/rest/v1/rpc/sql"

# query = """
# CREATE TABLE test_table (
#     id SERIAL PRIMARY KEY,
#     name TEXT NOT NULL,
#     age INT
# );
# """
# headers = {
#     "apikey": service_role_key,
#     "Authorization": f"Bearer {service_role_key}",
#     "Content-Type": "application/json",
# }
# response = requests.post(rpc_endpoint, headers=headers, json={"query": query})

# if response.status_code == 200:
#     print("Table created successfully!")
# else:
#     print("Error:", response.json())

from supabase import create_client

url = ""
key = "" 
supabase = create_client(url, key)

query = """
CREATE TABLE my_table (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    age INT
);
"""

response = supabase.postgrest.execute_sql(query)

if response.get("error"):
    print("Error creating table:", response["error"]["message"])
else:
    print("Table created successfully!")
