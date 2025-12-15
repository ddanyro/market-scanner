import requests
import time
import xml.etree.ElementTree as ET
import os

path = 'ibkr_config.txt'
if not os.path.exists(path):
    print("No ibkr_config.txt")
    exit()

with open(path, 'r') as f:
    lines = f.read().splitlines()
    token = lines[0].strip()
    query_id = lines[1].strip()

# 1. Initiate Generation
url = f"https://www.interactivebrokers.com/Universal/servlet/FlexStatementService.SendRequest?t={token}&q={query_id}&v=3"
print(f"Requesting Generation... Query: {query_id}")
print(f"URL: {url.replace(token, 'HIDDEN')}")

resp = requests.get(url)
print(f"Gen Response Code: {resp.status_code}")
print(f"Gen Response Text: {resp.text}")

try:
    root = ET.fromstring(resp.content)
    status_node = root.find('Status')
    if status_node is not None:
        status = status_node.text
        print(f"IBKR Status: {status}")
        
        if status == 'Success':
            ref = root.find('ReferenceCode').text
            base_url = root.find('Url').text
            dl_url = f"{base_url}?q={ref}&t={token}&v=3"
            print(f"Download URL constructed (Ref: {ref})")
            
            # 2. Polling for Download
            for i in range(10):
                print(f"\nPolling attempt {i+1}/10...")
                time.sleep(3) # Wait 3s between checks
                
                r2 = requests.get(dl_url)
                print(f"DL Status: {r2.status_code}")
                # Print start of content to see if it's XML or Error
                print(f"DL Content Start: {r2.text[:300]}")
                
                # Check if ready
                if "<FlexStatementResponse" in r2.text and "<Status>Success</Status>" not in r2.text:
                     # This usually means we got the real report (which starts with FlexStatementResponse but usually NO Status tag at root level like the simple response)
                     # Wait, actually the file download XML structure is complex.
                     # If it contains <FlexStatements>, it's good.
                     if "<FlexStatements>" in r2.text:
                         print("Report Ready!")
                         break
                
                if "<ErrorCode>" in r2.text:
                    err = r2.text.split("<ErrorCode>")[1].split("</ErrorCode>")[0]
                    msg = r2.text.split("<ErrorMessage>")[1].split("</ErrorMessage>")[0]
                    print(f"Not Ready Code: {err} ({msg})")
                    if err == '1019': # Statement generation in progress
                        continue
                    else:
                         pass # Other error
    else:
        code = root.find('ErrorCode').text
        msg = root.find('ErrorMessage').text
        print(f"Gen Error: {code} - {msg}")

except Exception as e:
    print(f"Python Error: {e}")
