import json
import os
import requests

# Load environment variables
CF_API_TOKEN = os.getenv('CF_API_TOKEN')
CF_ZONE_ID = os.getenv('CF_ZONE_ID')

# Define base domain
BASE_DOMAIN = "moontree.me"

# Load subdomain.json
with open('subdomain.json', 'r') as f:
    subdomains = json.load(f)

# Cloudflare API endpoint
CF_API_URL = f"https://api.cloudflare.com/client/v4/zones/{CF_ZONE_ID}/dns_records"

# Headers for Cloudflare API
headers = {
    'Authorization': f'Bearer {CF_API_TOKEN}',
    'Content-Type': 'application/json',
}

def update_cname_record(subdomain, cname):
    # Complete subdomain and cname with base domain
    full_subdomain = f"{subdomain}.{BASE_DOMAIN}"
    full_cname = f"{cname}.{BASE_DOMAIN}"

    # Search for existing CNAME record
    params = {
        'type': 'CNAME',
        'name': full_subdomain
    }
    response = requests.get(CF_API_URL, headers=headers, params=params)
    records = response.json().get('result', [])

    if records:
        record_id = records[0]['id']
        # Update existing CNAME record
        data = {
            'type': 'CNAME',
            'name': full_subdomain,
            'content': full_cname,
            'ttl': 3600,
            'proxied': False
        }
        response = requests.put(f"{CF_API_URL}/{record_id}", headers=headers, json=data)
        if response.status_code == 200:
            print(f"Updated CNAME for {full_subdomain} to {full_cname}")
        else:
            print(f"Failed to update CNAME for {full_subdomain}: {response.text}")
    else:
        # Create a new CNAME record
        data = {
            'type': 'CNAME',
            'name': full_subdomain,
            'content': full_cname,
            'ttl': 3600,
            'proxied': False
        }
        response = requests.post(CF_API_URL, headers=headers, json=data)
        if response.status_code == 200:
            print(f"Created CNAME for {full_subdomain} to {full_cname}")
        else:
            print(f"Failed to create CNAME for {full_subdomain}: {response.text}")

# Iterate over each subdomain and update its CNAME
for subdomain, cname in subdomains.items():
    update_cname_record(subdomain, cname)
