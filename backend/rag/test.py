import requests
from backend.services.config import settings

url = settings.SCALEWAY_EMBEDDINGS_URL
headers = {
    "Authorization": f"Bearer {settings.scaleway_api_key}",
    "Content-Type": "application/json"
}
payload = {
    "model": "bge-multilingual-gemma2",
    "input": ["Orange wprowadza nowy pakiet 50GB za 19,99 PLN."]
}

r = requests.post(url, headers=headers, json=payload)
print(r.status_code)
print(r.json())