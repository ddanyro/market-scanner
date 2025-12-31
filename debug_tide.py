
import requests
from bs4 import BeautifulSoup
import re

def get_finviz_market_tide():
    print("Testing Finviz Market Tide...")
    url = "https://finviz.com"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://finviz.com/',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive'
    }
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        
        with open("finviz_home.html", "w") as f:
            f.write(r.text)
            
        print(f"Status Code: {r.status_code}")
        if r.status_code != 200:
            print(f"Failed to fetch content.")
            return None
            
        soup = BeautifulSoup(r.text, 'html.parser')
        stats_divs = soup.find_all('div', class_='market-stats')
        print(f"Found {len(stats_divs)} stats divs.")
        
        def extract_val(param_text):
            match = re.search(r'\((\d+)\)', param_text)
            if match:
                return int(match.group(1))
            return None

        
        tide_data = {}
        for div in stats_divs:
            # Replicating logic
            labels_left = div.find('div', class_='market-stats_labels_left')
            labels_right = div.find('div', class_='market-stats_labels_right')
            
            if labels_left and labels_right:
                left_ps = labels_left.find_all('p')
                right_ps = labels_right.find_all('p')
                
                if len(left_ps) >= 2 and len(right_ps) >= 2:
                    label_l = left_ps[0].get_text(strip=True)
                    val_l_str = left_ps[1].get_text(strip=True)
                    val_l = extract_val(val_l_str)
                    
                    label_r = right_ps[0].get_text(strip=True)
                    val_r_str = right_ps[1].get_text(strip=True)
                    val_r = extract_val(val_r_str)
                    
                    if val_l is not None and val_r is not None:
                        full_div_text = div.get_text()
                        if "Advancing" in label_l:
                            tide_data['Advancing'] = val_l
                            tide_data['Declining'] = val_r
                            print(f" -> Found Adv/Dec: {val_l}/{val_r}")
                        elif "New High" in label_l:
                            tide_data['NewHighs'] = val_l
                            tide_data['NewLows'] = val_r
                            print(f" -> Found High/Low: {val_l}/{val_r}")
                        elif "SMA50" in full_div_text:
                            tide_data['SMA50_Above'] = val_l
                            tide_data['SMA50_Below'] = val_r
                            print(f" -> Found SMA50: {val_l}/{val_r}")
                        elif "SMA200" in full_div_text:
                            tide_data['SMA200_Above'] = val_l
                            tide_data['SMA200_Below'] = val_r
                            print(f" -> Found SMA200: {val_l}/{val_r}")

    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    get_finviz_market_tide()
