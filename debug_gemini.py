import requests

key = "AIzaSyBVcvEkLS9CqPDlJIEpmz4Mr4yblfodC34"
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
payload = {"contents": [{"parts": [{"text": "Hello"}]}]}

print(f"Testing Gemini API with key: {key}...")
try:
    resp = requests.post(url, json=payload, timeout=10)
    print(f"Status Code: {resp.status_code}")
    print(f"Response Body: {resp.text}")
except Exception as e:
    print(f"Request Failed: {e}")
