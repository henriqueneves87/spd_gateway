import requests
import base64

CLIENT_ID = "A40A208C-0914-479D-BA17-BBD6E9063991"
CLIENT_SECRET = "D597E2B5-2BF2-48D1-A682-26C58F83D0EF"

# 1. Obter token OAuth
url_auth = "https://ecommerce-hml.adiq.io/auth/oauth2/v1/token"
credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
basic_auth = base64.b64encode(credentials.encode()).decode()

headers_auth = {
    "Authorization": f"Basic {basic_auth}",
    "Content-Type": "application/json"
}
payload_auth = {"grantType": "client_credentials"}

response = requests.post(url_auth, headers=headers_auth, json=payload_auth, timeout=10)
access_token = response.json()["accessToken"]

print(f"Token obtido: {access_token[:50]}...")

# 2. Tokenizar cartão Visa
url_token = "https://ecommerce-hml.adiq.io/v1/tokens/cards"
headers_token = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

print("\nTokenizando Visa...")
payload = {"cardNumber": "4761739001010036"}
response = requests.post(url_token, headers=headers_token, json=payload, timeout=10)
visa_token = response.json()["numberToken"]
print(f"Visa Token: {visa_token}")

print("\nTokenizando Mastercard...")
payload = {"cardNumber": "5201561050025011"}
response = requests.post(url_token, headers=headers_token, json=payload, timeout=10)
mc_token = response.json()["numberToken"]
print(f"Mastercard Token: {mc_token}")

print("\n" + "="*60)
print("Atualize run_tests.py com estes tokens:")
print("="*60)
print(f'    "Visa": {{"card_token": "{visa_token}", ...')
print(f'    "Mastercard": {{"card_token": "{mc_token}", ...')
