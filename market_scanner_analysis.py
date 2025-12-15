import requests
import pandas as pd
from io import StringIO
import datetime

# Dicționar de interpretare a evenimentelor
EVENT_DESCRIPTIONS = {
    'CPI': '🔥 Măsoară inflația la consumator. 🔴 Peste așteptări = Frică de dobânzi (Acțiuni Jos). 🟢 Sub așteptări = Speranță de tăiere (Raliu).',
    'PPI': '🏭 Inflația la producător. Semnal timpuriu pentru CPI. Trend crescător = Presiune inflaționistă.',
    'Fed': '🏦 Intervenție a Băncii Centrale. Urmăriți tonul: "Hawkish" (Rău pt burse) vs "Dovish" (Bun pt burse).',
    'FOMC': '🏛️ Decizia de dobândă. Eveniment critic. Dobânzi Sus = Rău pentru Tech/Growth.',
    'GDP': '📈 Produsul Intern Brut. Arată sănătatea economiei. Scădere (negativ) = Recesiune.',
    'Nonfarm': '👥 NFP (Joburi). 🟢 Peste așteptări = Economie puternică (USD Sus, Gold Jos). 🔴 Sub așteptări = Risc recesiune.',
    'Unemployment': '📉 Rata șomajului. Creșterea șomajului este semnalul final de recesiune.',
    'Retail': '🛒 Vânzările Retail. Consumul reprezintă 70% din PIB-ul SUA. Scădere = Pericol economic.',
    'Confidence': '🧠 Încrederea consumatorului. Optimismul duce la cheltuieli viitoare.',
    'Claims': '🙏 Cererile de șomaj săptămânale. Indicator "high-frequency" pentru piața muncii.',
    'Services': '🏨 ISM/PMI Servicii. Sectorul dominant. Sub 50 = Contracție economică.',
    'Manufacturing': '🏭 ISM/PMI Producție. Indică expansiunea sau contracția industrială.',
    'Home': '🏠 Vânzări Case. Foarte sensibile la dobânzi hipotecare mari.',
    'Permits': '🏗️ Building Permits (Autorizații). Indicator anticipativ major. Scădere = Constructorii prevăd cerere slabă.',
    'Inventories': '🛢️ Stocuri Petrol/Bunuri. Impact specific pe sectoare (Energy/Retail).'
}

def get_event_impact(event_name):
    for key, desc in EVENT_DESCRIPTIONS.items():
        if key.lower() in event_name.lower():
            return desc
    return "Indicator economic. Poate genera volatilitate intraday."

def get_economic_events():
    """Scrapes Yahoo Finance for upcoming US economic events (Current & Next Week)."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        
        all_events = []
        seen_events = set()
        
        today = datetime.date.today()
        
        # Scanăm până la 6 săptămâni în avans până găsim ceva
        for w in range(6):
            target_date = today + datetime.timedelta(weeks=w)
            url = f"https://finance.yahoo.com/calendar/economic?day={target_date}"
            
            try:
                r = requests.get(url, headers=headers, timeout=5)
                if r.status_code != 200: continue
                
                dfs = pd.read_html(StringIO(r.text))
                if not dfs: continue
                
                df = dfs[0]
                
                # Filtrare SUA
                if 'Country' in df.columns:
                    us_df = df[df['Country'].astype(str).str.contains('US', case=False, na=False)]
                else:
                    continue 
                
                # Colectare
                keywords = ['Fed', 'FOMC', 'CPI', 'GDP', 'Nonfarm', 'Unemployment', 'PPI', 'Rate', 'Retail', 'Sentiment', 'Confidence', 'Manufacturing', 'Services', 'Home', 'Job', 'Permits', 'Inventories']
                
                for idx, row in us_df.iterrows():
                    evt = str(row['Event'])
                    # Acceptăm mai multe evenimente dacă lista e goală
                    is_major = any(k.lower() in evt.lower() for k in keywords) or (len(all_events) == 0 and w > 0)
                    
                    if is_major:
                        evt_time = str(row['Event Time'])
                        unique_id = f"{evt}_{evt_time}_{w}"
                        
                        if unique_id not in seen_events:
                            seen_events.add(unique_id)
                            # Data info
                            date_str = target_date.strftime('%d %b')
                            
                            # Adăugăm obiect complet
                            all_events.append({
                                'name': evt,
                                'time': evt_time,
                                'week': f"Săpt. {date_str}",
                                'desc': get_event_impact(evt)
                            })
            
                if len(all_events) >= 6:
                    break
                    
            except Exception as e:
                print(f"Sub-request error: {e}")
                continue
        
        return all_events[:8]
    except Exception as e:
        print(f"Calendar error: {e}")
        # Fallback Mock Calendar (dacă Yahoo eșuează)
        return [
            {'name': 'Building Permits', 'week': 'Săpt. Curentă', 'desc': 'Mock Data'},
            {'name': 'CPI Index', 'week': 'Săpt. Viitoare', 'desc': 'Mock Data'},
            {'name': 'Fed Interest Rate Decision', 'week': 'Următoarea Ședință', 'desc': 'Mock Data'},
            {'name': 'Nonfarm Payrolls', 'week': 'Luna Viitoare', 'desc': 'Mock Data'}
        ]

import os
import xml.etree.ElementTree as ET

def get_market_news():
    """Fetch Top Market News from Yahoo RSS and return detailed list."""
    try:
        url = "https://finance.yahoo.com/news/rssindex"
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code != 200: return []
        
        root = ET.fromstring(resp.content)
        items = []
        count = 0
        for item in root.findall('./channel/item'):
            title = item.find('title').text
            link = item.find('link').text
            desc = item.find('description').text if item.find('description') is not None else ""
            items.append({'title': title, 'link': link, 'desc': desc})
            count += 1
            if count >= 6: break
        return items
    except Exception as e:
        print(f"News Error: {e}")
        return []


def _generate_news_and_ai_summary_html(news_items, indicators, cached_summary=None):
    """
    Generează secțiunea de știri și analiză AI.
    Returnează (full_html, ai_summary_text)
    """
    try:
        # 1. Header
        news_html = "<div class='news-section' style='background: #222; padding: 20px; border-radius: 8px; margin-top: 20px; border: 1px solid #444; color: #e0e0e0;'>"
        news_html += "<strong style='color: #4dabf7; font-size: 0.95rem; display: block; margin-bottom: 10px;'>📰 Market News Overview</strong>"
        
        ai_summary_html = ""
        ai_raw_text = ""
        openai_key = ""
        
        # Load Key
        if os.path.exists("openai_key.txt"):
            try:
                with open("openai_key.txt", "r") as f:
                    openai_key = f.read().strip()
            except: pass
            
        if not openai_key:
            openai_key = os.environ.get("OPENAI_API_KEY", "")
            
        if openai_key and news_items:
            try:
                print("Generare rezumat AI (OpenAI)...")
                # Construct Prompt
                news_text = "\n".join([f"- {item['title']}: {item['desc']}" for item in news_items[:10]])
                prompt = (
                    f"Analizează următoarele știri financiare recente și creează un rezumat scurt și concis (maxim 3-4 paragrafe scurte) "
                    f"în limba ROMÂNĂ. Stilul trebuie să fie simplu, clar, pentru un investitor obișnuit (fără jargon tehnic excesiv). "
                    f"Evidențiază sentimentul general al pieței (Pozitiv/Negativ/Neutru) și principalele riscuri sau oportunități.\n\n"
                    f"Știri:\n{news_text}\n\n"
                    f"Context Piață: VIX={indicators.get('VIX', {}).get('value', 'N/A')}, SPX={indicators.get('SPX', {}).get('value', 'N/A')}"
                )
                
                # OpenAI Request logic ...
                # (Re-folosim logica existentă simplificată pentru diff)
                url = "https://api.openai.com/v1/chat/completions"
                headers = {"Content-Type": "application/json", "Authorization": f"Bearer {openai_key}"}
                payload = {
                    "model": "gpt-4o", 
                    "messages": [{"role": "system", "content": "Ești un analist financiar expert care explică piețele pe înțelesul tuturor."}, {"role": "user", "content": prompt}],
                    "temperature": 0.7
                }
                
                resp = requests.post(url, headers=headers, json=payload, timeout=20)
                
                if resp.status_code == 200:
                    data = resp.json()
                    content = data['choices'][0]['message']['content']
                    ai_raw_text = content
                    ai_summary_html = f"<div style='color: #ddd; font-size: 0.95rem; line-height: 1.5; background: #333; padding: 10px; border-radius: 5px; margin-bottom: 15px;'><strong>🤖 Analiză OpenAI (GPT-4o):</strong><br>{content}</div>"
                elif resp.status_code == 429:
                    ai_summary_html = "<div style='color:orange'><strong>Eroare OpenAI (429):</strong> Rate Limit.</div>"
                else:
                    ai_summary_html = f"<div style='color:red'>Eroare OpenAI: {resp.status_code}</div>"
                    print(f"  OpenAI Error: {resp.status_code}")

            except Exception as e:
                print(f"  Eroare request OpenAI: {e}")
                ai_summary_html = f"<div style='color:red'>Eroare conexiune OpenAI: {str(e)[:50]}</div>"
        
        elif not openai_key:
             # Check for Cached Summary
             if cached_summary:
                  print("  -> Folosim rezumat AI din cache (GitHub/Previous Run).")
                  ai_summary_html = f"<div style='color: #ddd; font-size: 0.95rem; line-height: 1.5; background: #333; padding: 10px; border-radius: 5px; margin-bottom: 15px; border-left: 3px solid #666;'><strong>🤖 Analiză OpenAI (Cached):</strong><br>{cached_summary}</div>"
                  ai_raw_text = cached_summary
             else:
                  ai_summary_html = "<div style='color:orange'>Lipsă cheie OpenAI și lipsă cache.</div>"

        # ... Assemble HTML ...
        if ai_summary_html: news_html += ai_summary_html
        
        # Sources
        news_html += "<div style='font-size: 0.8rem; color: #888; margin-top: 10px;'>Surse: "
        for n in news_items[:3]:
             news_html += f"<a href='{n['link']}' target='_blank' style='color: #aaa; text-decoration: none; margin-right: 10px;'>{n['title'][:20]}...</a>"
        news_html += "</div>"
        news_html += "</div>" # Close news-section
        
        return news_html, ai_raw_text # Return tuple!

    except Exception as e:
        print(f"Gen Market Analysis Error: {e}")
        return "<div>Error generating analysis</div>", ""

def generate_market_analysis(indicators, cached_ai_summary=None):
    """Generează o analiză de piață Hibridă (Rule-based + AI News Summary + Calendar)."""
    try:
        # 1. Extragere Valori
        def get_val(name):
            try: return float(indicators.get(name, {}).get('value', 0))
            except: return 0

        vix = get_val('VIX')
        
        # 2. Rule-Based Analysis (Probabilități)
        vix_text = ""
        sentiment_score = 50 
        if vix < 14:
            vix_text = "VIX extrem de redus. Complacere."
            sentiment_score += 10
        elif vix < 20:
            vix_text = "Volatilitate normală."
            sentiment_score += 5
        elif vix < 30:
            vix_text = "Tensiune ridicată."
            sentiment_score -= 15
        else:
            vix_text = "Panică (VIX > 30)."
            sentiment_score -= 30

        if sentiment_score >= 60:
            conclusion = "Bullish (Cumpărare)"
            prob_up = 65; prob_down = 35; color = "#4caf50"
        elif sentiment_score <= 30:
            conclusion = "Bearish (Vânzare)"
            prob_up = 40; prob_down = 60; color = "#f44336"
        else:
            conclusion = "Neutral (Hold)"
            prob_up = 50; prob_down = 50; color = "#e0e0e0"

        # 3. News Summary (AI via REST API sau Fallback)
        news_items = get_market_news()
        news_html, ai_summary_raw_text = _generate_news_and_ai_summary_html(news_items, indicators, cached_ai_summary)

        # 4. Calendar (Forced Fallback if Empty)
        events_list = get_economic_events()
        
        # STATIC FALLBACK if scraper returns empty list
        if not events_list:
             events_list = [
                {'name': 'Empire State Manufacturing (US)', 'week': 'Lun 16 Dec', 'desc': 'Indicator activitate manufacturieră NY.'},
                {'name': 'Building Permits (US)', 'week': 'Mar 17 Dec', 'desc': 'Indicator anticipativ piață imobiliară.'},
                {'name': 'Crude Oil Inventories', 'week': 'Mie 18 Dec', 'desc': 'Stocuri petrol. Impact Energy.'},
                {'name': 'Initial Jobless Claims', 'week': 'Joi 19 Dec', 'desc': 'Cereri șomaj. Impact piață muncă.'},
                {'name': 'GDP Growth Rate (Final)', 'week': 'Joi 19 Dec', 'desc': 'Creștere economică trimestrială.'}
            ]

        events_html = "<div style='margin-top: 20px; border-top: 1px solid #444; padding-top: 15px;'>"
        events_html += "<strong style='color: #ffb74d; font-size: 0.95rem; display: block; margin-bottom: 10px;'>⚠️ Evenimente Majore Următoare:</strong>"
        
        events_html += "<ul style='margin: 0; padding-left: 20px; color: #ccc; font-size: 0.9rem; list-style-type: none;'>"
        for ev in events_list:
            name = ev['name']
            name_ro = name.replace('Fed', 'Fed').replace('CPI', 'Inflația CPI').replace('GDP', 'PIB').replace('Unemployment', 'Șomaj')
            
            # Try to get better desc
            desc = get_event_impact(name)
            if desc == "Indicator economic. Poate genera volatilitate intraday." and ev.get('desc') != 'Mock Data':
                 # Keep existing desc if specific impact not found
                 desc = ev.get('desc', desc)
            
            events_html += f"""
            <li style="margin-bottom: 10px; padding-left: 10px; border-left: 3px solid #666;">
                <div>
                    <strong style="color: #fff;">{name_ro}</strong> 
                    <span style="color: #888; font-size: 0.8rem;">({ev['week']})</span>
                </div>
                <div style="font-size: 0.85rem; color: #aaa; margin-top: 2px;">{desc}</div>
            </li>
            """
        events_html += "</ul></div>"

        # Formatare HTML Final 
        html = f"""
        <div style="margin-top: 25px; background-color: #252526; border-radius: 8px; border: 1px solid #3e3e42; overflow: hidden;">
            <div style="background-color: #333; padding: 10px 15px; border-bottom: 1px solid #3e3e42; display: flex; align-items: center;">
                <span style="font-size: 1.2rem; margin-right: 10px;">🤖</span>
                <h3 style="margin: 0; font-size: 1rem; color: #e0e0e0;">Analiză de Piață & Calendar</h3>
            </div>
            <div style="padding: 20px;">
                
                <!-- Probabilități Section -->
                <div style="display: flex; gap: 20px; flex-wrap: wrap; margin-bottom: 15px;">
                    <div style="flex: 1; min-width: 200px; background: rgba(255,255,255,0.05); padding: 10px; border-radius: 5px;">
                        <div style="font-size: 0.8rem; color: #888; margin-bottom: 5px;">Probabilități Direcție Piață</div>
                        <div style="display: flex; align-items: center; justify-content: space-between; font-size: 0.85rem;">
                            <span style="color: #4caf50;">Creștere: <strong>{prob_up}%</strong></span>
                            <span style="color: #f44336;">Scădere: <strong>{prob_down}%</strong></span>
                        </div>
                        <div style="width: 100%; height: 4px; background: #555; margin-top: 5px; border-radius: 2px; overflow: hidden; display: flex;">
                            <div style="width: {prob_up}%; background: #4caf50; height: 100%;"></div>
                            <div style="width: {prob_down}%; background: #f44336; height: 100%;"></div>
                        </div>
                    </div>
                    
                    <div style="flex: 1; padding: 5px;">
                        <span style="font-weight: bold; color: #888; font-size: 0.9rem;">Concluzie: </span>
                        <span style="font-size: 1.1rem; font-weight: bold; color: {color};">{conclusion}</span>
                        <div style="font-size: 0.8rem; color: #aaa; margin-top: 5px;">{vix_text}</div>
                    </div>
                </div>

                {news_html}
                {events_html}
            </div>
        </div>
        """
        return html, ai_summary_raw_text
    except Exception as e:
        return f"<div style='color: red;'>Eroare generare analiză: {e}</div>", ""
