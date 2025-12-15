import requests
import json
import os

API_KEY = ""
if os.path.exists("gemini_key.txt"):
    with open("gemini_key.txt", "r") as f:
        API_KEY = f.read().strip()

    # Fallback to env
    if not API_KEY and "GOOGLE_API_KEY" in os.environ:
         API_KEY = os.environ["GOOGLE_API_KEY"]

if not API_KEY:
    print("No API KEY found in gemini_key.txt or env")
    exit()

print(f"Testing Gemini API with key: {API_KEY[:5]}...{API_KEY[-3:] if len(API_KEY)>5 else ''}")

# 1. Test List Models
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
print(f"Requesting: {url.replace(API_KEY, 'HIDDEN')}")
response = requests.get(url)

print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    try:
        data = response.json()
        if 'models' in data:
            print("Models available:")
            valid_models = []
            for m in data['models']:
                if 'generateContent' in m['supportedGenerationMethods']:
                    print(f" - {m['name']}")
                    valid_models.append(m['name'])
            
            # 2. Test Generation
            if valid_models:
                target = "models/gemini-2.0-flash-exp" if "models/gemini-2.0-flash-exp" in valid_models else valid_models[0]
                print(f"\nTesting generation with {target}...")
                gen_url = f"https://generativelanguage.googleapis.com/v1beta/{target}:generateContent?key={API_KEY}"
                payload = {"contents": [{"parts": [{"text": "Hello"}]}]}
                r2 = requests.post(gen_url, json=payload)
                print(f"Gen Status: {r2.status_code}")
                print(f"Gen Response: {r2.text[:200]}...")
        else:
            print("Error/Response:", data)
    except Exception as e:
        print("JSON Error:", e)
        print("Raw:", response.text)
else:
    print("Error Response:", response.text)
