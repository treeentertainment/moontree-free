import json
import os
import requests
import logging

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

# Set up logging
LOG_FILE = "dns_update_log.txt"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,  # Set to DEBUG to capture all levels of logs
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def update_cname_record(subdomain, cname):
    full_subdomain = f"{subdomain}.{BASE_DOMAIN}"
    full_cname = f"{cname}.{BASE_DOMAIN}"

    # Search for existing CNAME record
    params = {
        'type': 'CNAME',
        'name': full_subdomain
    }

    logging.info(f"{full_subdomain}에 대한 CNAME 기록 검색 중...")

    response = requests.get(CF_API_URL, headers=headers, params=params)

    # Log API request response
    logging.debug(f"CNAME 검색 응답 상태 코드: {response.status_code}")
    logging.debug(f"CNAME 검색 응답 내용: {response.text}")

    records = response.json().get('result', [])

    if records:
        record_id = records[0]['id']
        logging.info(f"기존 CNAME 기록 존재: {record_id}. 업데이트 시도 중...")

        # Update existing CNAME record
        data = {
            'type': 'CNAME',
            'name': full_subdomain,
            'content': full_cname,
            'ttl': 3600,
            'proxied': False
        }
        response = requests.put(f"{CF_API_URL}/{record_id}", headers=headers, json=data)

        # Log update result
        logging.debug(f"CNAME 업데이트 응답 상태 코드: {response.status_code}")
        logging.debug(f"CNAME 업데이트 응답 내용: {response.text}")

        if response.status_code == 200:
            logging.info(f"{full_subdomain}의 CNAME이 {full_cname}로 업데이트됨.")
        else:
            logging.error(f"{full_subdomain}의 CNAME 업데이트 실패: {response.text}")
    else:
        logging.info(f"기존 CNAME 기록 없음. 새로 생성 시도 중...")

        # Create a new CNAME record
        data = {
            'type': 'CNAME',
            'name': full_subdomain,
            'content': full_cname,
            'ttl': 3600,
            'proxied': False
        }
        response = requests.post(CF_API_URL, headers=headers, json=data)

        # Log create result
        logging.debug(f"CNAME 생성 응답 상태 코드: {response.status_code}")
        logging.debug(f"CNAME 생성 응답 내용: {response.text}")

        if response.status_code == 200:
            logging.info(f"{full_subdomain}의 CNAME이 {full_cname}로 생성됨.")
        else:
            logging.error(f"{full_subdomain}의 CNAME 생성 실패: {response.text}")

# Iterate over each subdomain and update its CNAME
for subdomain, cname in subdomains.items():
    update_cname_record(subdomain, cname)

logging.info("모든 작업 완료.")
