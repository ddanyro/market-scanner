import requests
import json

key = "AIzaSyBVcvEkLS9CqPDlJIEpmz4Mr4yblfodC34"
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"

print(f"Listing Models for key: {key}...")
try:
    resp = requests.get(url, timeout=10)
    print(f"Status Code: {resp.status_code}")
    if resp.status_code == 200:
        models = resp.json().get('models', [])
        for m in models:
            if 'generateContent' in m.get('supportedGenerationMethods', []):
                print(f" - {m['name']}")
    else:
        print(f"Response Body: {resp.text}")
except Exception as e:
    print(f"Request Failed: {e}")
