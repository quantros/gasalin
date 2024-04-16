import requests
import sqlite3
import time
from dotenv import load_dotenv
import os

load_dotenv()

CHAINBASE_API_KEY = os.getenv('CHAINBASE_API_KEY')
GRAPHQL_URL = os.getenv('GRAPHQL_URL')
CHAINBASE_URL = os.getenv('CHAINBASE_URL')
DATABASE_PATH = os.getenv('DATABASE_PATH')
CHAIN_ID = os.getenv('CHAIN_ID')
TOKEN_ADDR = os.getenv('TOKEN_ADDR')

print("Loaded environment variables:")
print(f"CHAINBASE_API_KEY: {CHAINBASE_API_KEY}")
print(f"GRAPHQL_URL: {GRAPHQL_URL}")
print(f"CHAINBASE_URL: {CHAINBASE_URL}")
print(f"DATABASE_PATH: {DATABASE_PATH}")
print(f"CHAIN_ID: {CHAIN_ID}")
print(f"TOKEN_ADDR: {TOKEN_ADDR}")

conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS user_info (
    id INTEGER PRIMARY KEY,
    wallet_address TEXT,
    date_registration TEXT,
    earned REAL,
    id_blockchain TEXT,
    queue_position TEXT,
    activations TEXT,
    partners TEXT,
    reload TEXT,
    user_level INTEGER,
    price_platform TEXT,
    total_earned REAL,
    users_last_24_hours INTEGER,
    total_participants INTEGER,
    tokens_balance TEXT
);
''')
conn.commit()

def fetch_holders():
    page = 1
    headers = {'x-api-key': CHAINBASE_API_KEY, 'accept': 'application/json'}
    print("Starting to fetch token holders...")
    while True:
        url = f'{CHAINBASE_URL}/v1/token/top-holders?chain_id={CHAIN_ID}&contract_address={TOKEN_ADDR}&page={page}&limit=50'
        print(f"Requesting: {url}")
        response = requests.get(url, headers=headers)
        print(f"Response Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json().get('data')
            if not data:
                print("No data received, breaking loop.")
                break
            for holder in data:
                print(f"Address: {holder['wallet_address']}, Amount: {holder['amount']}")
                fetch_and_save_user_data(holder['wallet_address'])
            page += 1
            time.sleep(1)
        elif response.status_code == 429:
            print("Rate limit exceeded, sleeping...")
            time.sleep(60)
        else:
            print(f'Error with request: {response.status_code}')
            break

def fetch_and_save_user_data(wallet_address):
    print(f"Fetching and saving data for {wallet_address}")
    token = create_token(wallet_address)
    if token:
        print(f"Token received: {token}")
        user_data = fetch_data_with_token(wallet_address, token)
        print(f"User data received: {user_data}")
        if user_data:
            save_to_db(wallet_address, user_data)

def create_token(wallet_address):
    url = GRAPHQL_URL
    query = "mutation createToken($addressUser: String!) { createToken(addressUser: $addressUser) }"
    variables = {"addressUser": wallet_address}
    print(f"Creating token for {wallet_address}")
    response = requests.post(url, json={'query': query, 'variables': variables})
    print(f"Token creation response: {response.status_code}")
    if response.status_code == 200:
        return response.json().get('data', {}).get('createToken')
    else:
        print(f"Error creating token: {response.status_code}")
        return None

def fetch_data_with_token(wallet_address, token):
    url = GRAPHQL_URL
    query = """
    query FullData($addressUser: String!) {
      userProfileInfo(addressUser: $addressUser) {
        dateRegistration
        earned
        idBlockchain
      }
      queuePosition(addressUser: $addressUser)
      checkActivations(addressUser: $addressUser)
      checkPartners(addressUser: $addressUser)
      checkReload(addressUser: $addressUser)
      checkUserLevel(addressUser: $addressUser)
      pricePlatform
      totalEarned
      countUsersLast24Hours
      totalParticipants
      tokensBalance(addressUser: $addressUser)
    }
    """
    variables = {"addressUser": wallet_address}
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
    print(f"Fetching data with token for {wallet_address}")
    response = requests.post(url, json={'query': query, 'variables': variables}, headers=headers)
    print(f"Data fetch response: {response.status_code}")
    if response.status_code == 200:
        return response.json().get('data')
    else:
        print(f"Error fetching data: {response.status_code}")
        return {}

def save_to_db(wallet_address, user_data):
    print(f"Saving data to DB for {wallet_address}")
    if user_data and 'userProfileInfo' in user_data and user_data['userProfileInfo']:
        cursor.execute('''
            INSERT INTO user_info (
                wallet_address, date_registration, earned, id_blockchain, queue_position,
                activations, partners, reload, user_level, price_platform, total_earned,
                users_last_24_hours, total_participants, tokens_balance
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            wallet_address,
            user_data['userProfileInfo'].get('dateRegistration'),
            user_data['userProfileInfo'].get('earned'),
            user_data['userProfileInfo'].get('idBlockchain'),
            ','.join(map(str, user_data.get('queuePosition', []))),
            ','.join(map(str, user_data.get('checkActivations', []))),
            ','.join(map(str, user_data.get('checkPartners', []))),
            ','.join(map(str, user_data.get('checkReload', []))),
            user_data.get('checkUserLevel', ''),
            ','.join(map(str, user_data.get('pricePlatform', []))),
            user_data.get('totalEarned', 0),
            user_data.get('countUsersLast24Hours', 0),
            user_data.get('totalParticipants', 0),
            ','.join(map(str, user_data.get('tokensBalance', []))),
        ))
        conn.commit()
    else:
        print(f"Not enough data to save for address {wallet_address}")

fetch_holders()
conn.close()
