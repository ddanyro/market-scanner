import requests
import pandas as pd
from io import StringIO
import datetime
import yfinance as yf
import numpy as np
import json
import os

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
    Returnează (full_html, ai_summary_text, sentiment_score)
    """
    try:
        # 1. Header
        news_html = "<div class='news-section' style='background: var(--bg-white); padding: 24px; border-radius: var(--radius-md); margin-top: 24px; border: 1px solid var(--border-light); box-shadow: var(--shadow-sm);'>"
        news_html += "<strong style='color: var(--primary-purple); font-size: 18px; font-weight: 700; display: block; margin-bottom: 16px;'>Market News Overview</strong>"
        
        ai_summary_html = ""
        ai_raw_text = ""
        ai_sentiment_score = 50 # Default Neutral
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
                
                # Context din indicatori pentru AI
                vix_val = indicators.get('VIX', {}).get('value', 'N/A')
                spx_val = indicators.get('SPX', {}).get('value', 'N/A')
                
                prompt = (
                    f"Analizează următoarele știri financiare și indicatori de piață pentru a determina sentimentul general.\n"
                    f"Context Tehnic: VIX={vix_val}, SPX={spx_val}.\n\n"
                    f"Știri Recente:\n{news_text}\n\n"
                    f"Te rog să răspunzi EXACT în următorul format:\n"
                    f"SENTIMENT_SCORE: <un număr între 0 și 100, unde 0=Extreme Bearish, 50=Neutral, 100=Extreme Bullish>\n"
                    f"REZUMAT_HTML: <un rezumat succint (max 150 cuvinte) în format HTML (fără tag-uri <html> sau <body>, doar <p>, <b>, <ul> etc.), în limba ROMÂNĂ, analizând riscurile și oportunitățile.>\n"
                )
                
                # OpenAI Request logic
                url = "https://api.openai.com/v1/chat/completions"
                headers = {"Content-Type": "application/json", "Authorization": f"Bearer {openai_key}"}
                payload = {
                    "model": "gpt-4o", 
                    "messages": [{"role": "system", "content": "Ești un analist financiar expert. Răspunde strict în formatul cerut."}, {"role": "user", "content": prompt}],
                    "temperature": 0.5
                }
                
                resp = requests.post(url, headers=headers, json=payload, timeout=20)
                
                if resp.status_code == 200:
                    data = resp.json()
                    content = data['choices'][0]['message']['content']
                    ai_raw_text = content
                    
                    # Parsing Response
                    score_line = [l for l in content.split('\n') if 'SENTIMENT_SCORE:' in l]
                    if score_line:
                        try:
                            score_str = score_line[0].split(':')[1].strip()
                            ai_sentiment_score = int(float(score_str))
                        except:
                            ai_sentiment_score = 50
                    
                    # Extract Summary HTML (everything after SENTIMENT_SCORE line)
                    summary_part = content
                    if 'REZUMAT_HTML:' in content:
                        summary_part = content.split('REZUMAT_HTML:')[1].strip()
                    elif 'SENTIMENT_SCORE:' in content:
                         parts = content.split('\n')
                         summary_part = "\n".join([p for p in parts if 'SENTIMENT_SCORE' not in p]).strip()

                    ai_summary_html = f"<div style='color: var(--text-primary); font-size: 15px; line-height: 1.6; background: var(--light-purple-bg); padding: 16px; border-radius: var(--radius-sm); margin-bottom: 16px; border-left: 3px solid var(--primary-purple);'><strong style='color: var(--primary-purple);'>Analiză OpenAI:</strong><br>{summary_part}</div>"
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
                  print("  -> Folosim rezumat AI din cache.")
                  # Try to extract previous score if saved in raw text, otherwise default
                  if 'SENTIMENT_SCORE:' in cached_summary:
                      try:
                          ai_sentiment_score = int(float(cached_summary.split('SENTIMENT_SCORE:')[1].split()[0]))
                      except: pass
                  
                  summary_display = cached_summary
                  if 'REZUMAT_HTML:' in cached_summary:
                       summary_display = cached_summary.split('REZUMAT_HTML:')[1].strip()

                  ai_summary_html = f"<div style='color: var(--text-primary); font-size: 15px; line-height: 1.6; background: var(--light-purple-bg); padding: 16px; border-radius: var(--radius-sm); margin-bottom: 16px; border-left: 3px solid var(--primary-purple);'><strong style='color: var(--primary-purple);'>Analiză OpenAI (Cached):</strong><br>{summary_display}</div>"
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
        
        return news_html, ai_raw_text, ai_sentiment_score

    except Exception as e:
        print(f"Gen Market Analysis Error: {e}")
        return "<div>Error generating analysis</div>", "", 50

def generate_market_analysis(indicators, cached_ai_summary=None):
    """Generează o analiză de piață Hibridă (Algoritmică Multi-Factor + AI)."""
    try:
        # 1. Extragere Valori (Safe)
        def get_val(name):
            try: return float(indicators.get(name, {}).get('value', 0))
            except: return 0
            
        def get_spark(name):
            try: return indicators.get(name, {}).get('sparkline', [])
            except: return []

        vix = get_val('VIX')
        vix3m = get_val('VIX3M')
        skew = get_val('SKEW')
        move = get_val('MOVE')
        
        # 2. Market News & AI Sentiment
        news_items = get_market_news()
        news_html, ai_summary_raw, ai_score = _generate_news_and_ai_summary_html(news_items, indicators, cached_ai_summary)
        
        # 3. Calcul Scor Algoritmic (0-100, unde 100 = Bullish Perfect)
        # Factori Refined:
        # - VIX (Weight 15%): Panic check
        # - VIX Structure (Weight 10%): Contango check
        # - SKEW (Weight 5%): Tail Risk
        # - MOVE (Weight 5%): Bond Vol
        # - SPX Trend (Weight 30%): Price Action & Momentum (SMA20 + 5d Return)
        # - AI Sentiment (Weight 35%): Fundamental/News Context
        
        algo_score = 0
        total_weight = 0
        
        # --- VIX Score (Inverse) ---
        # 10-15: 100pts
        # 15-20: 75pts
        # 20-25: 50pts
        # 25-30: 25pts
        # >30: 0pts
        vix_s = 0
        if vix > 0:
            if vix < 15: vix_s = 100
            elif vix < 20: vix_s = 75
            elif vix < 25: vix_s = 50
            elif vix < 30: vix_s = 25
            else: vix_s = 0
            algo_score += vix_s * 0.15
            total_weight += 0.15
            
        # --- Term Structure (Contango vs Backwardation) ---
        # VIX3M / VIX > 1.1 -> Bullish (100)
        # 1.0 - 1.1 -> Neutral (50)
        # < 1.0 -> Bearish (0)
        if vix > 0 and vix3m > 0:
            ratio = vix3m / vix
            ts_s = 0
            if ratio > 1.1: ts_s = 100
            elif ratio > 1.0: ts_s = 50
            else: ts_s = 0
            algo_score += ts_s * 0.10
            total_weight += 0.10
            
        # --- SKEW ---
        # > 145 -> Bearish (Black Swan Risk) -> 20pts
        # 115-135 -> Normal Bullish -> 90pts
        if skew > 0:
            skew_s = 50
            if skew > 145: skew_s = 25
            elif skew > 135: skew_s = 50
            elif 115 <= skew <= 135: skew_s = 90
            else: skew_s = 80
            algo_score += skew_s * 0.05
            total_weight += 0.05
        
        # --- MOVE (Bond Vol) ---
        # < 100 -> Bullish (100)
        # 100-120 -> Neutral (50)
        # > 120 -> Bearish (0)
        if move > 0:
            move_s = 50
            if move < 100: move_s = 100
            elif move > 125: move_s = 0
            algo_score += move_s * 0.05
            total_weight += 0.05

        # --- Market Indices Trend (SPX + NASDAQ) ---
        # Calculate trend for both SPX and NASDAQ, then average
        indices_scores = []
        
        for index_name in ['SPX', 'NASDAQ']:
            index_points = get_spark(index_name)
            score_trend = 50  # Default neutral
            
            if index_points and len(index_points) >= 20:
                last = index_points[-1]
                # SMA 20 (Short Term)
                sma_20 = sum(index_points[-20:]) / 20
                # Momentum (5 days)
                idx_5d = -5 if len(index_points) >= 5 else 0
                mom_5d = (last / index_points[idx_5d]) - 1 if index_points[idx_5d] > 0 else 0
                 
                if last > sma_20:
                     if mom_5d > -0.01: score_trend = 100  # Uptrend solid
                     else: score_trend = 60  # Uptrend but recent pullback
                else:
                     # Sub SMA20
                     if mom_5d < -0.02: score_trend = 0  # Strong Downtrend
                     else: score_trend = 25  # Weak/Correction
                
                indices_scores.append(score_trend)
            elif index_points:
                # Fallback if less than 20 points
                indices_scores.append(50)
        
        # Average the scores from both indices
        if indices_scores:
            avg_index_score = sum(indices_scores) / len(indices_scores)
            algo_score += avg_index_score * 0.30
            total_weight += 0.30
            
        # --- AI Sentiment ---
        if ai_score >= 0: 
            algo_score += ai_score * 0.35
            total_weight += 0.35
            
        # Final Norm
        if total_weight > 0:
            final_score = algo_score / total_weight
        else:
            final_score = 50 # Fallback
            
        # Interpretare
        prob_up = int(final_score)
        prob_down = 100 - prob_up
        
        conclusion = "Neutral"
        color = "#e0e0e0"
        if final_score >= 65: 
            conclusion = "Bullish"
            color = "#4caf50"
        elif final_score <= 35: 
            conclusion = "Bearish"
            color = "#f44336"
            
        # Detalii Factori Text (Simplificat)
        # Eliminăm VIX și SKEW din afișare vizuală (sunt deja sus), păstrăm doar Term Structure și AI Sentiment cu explicații.
        factors_html = f"""
        <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 10px; margin-top: 15px;'>
            
            <div style='background: rgba(255,255,255,0.05); padding: 8px; border-radius: 6px; text-align: center; border: 1px solid #444;'>
                <div style='font-size: 0.75rem; color: #aaa; margin-bottom: 2px;'>Analiză VIX Futures (Term Structure)</div>
                <div style='font-weight: bold; font-size: 1.1rem; color: {"#fc5c65" if (vix>0 and vix3m/vix<1) else "#26de81"}'>{(vix3m/vix if vix>0 else 0):.2f}</div>
                <div style='font-size: 0.65rem; color: #888; margin-top: 4px; line-height: 1.2;'>
                    Raport VIX Futures (3M) / VIX Spot.<br>
                    <span style='color: #26de81;'>> 1.1 (Contango)</span> = Normal/Bullish<br>
                    <span style='color: #fc5c65;'>< 1.0 (Backwardation)</span> = Panică/Bearish
                </div>
            </div>

            <div style='background: rgba(255,255,255,0.05); padding: 8px; border-radius: 6px; text-align: center; border: 1px solid #444;'>
                <div style='font-size: 0.75rem; color: #aaa; margin-bottom: 2px;'>AI Market Sentiment</div>
                <div style='font-weight: bold; font-size: 1.1rem; color: {"#4caf50" if ai_score>60 else "#f44336" if ai_score<40 else "#fbbf24"}'>{ai_score}/100</div>
                <div style='font-size: 0.65rem; color: #888; margin-top: 4px; line-height: 1.2;'>
                    Analiză semantică știri.<br>
                    <span style='color: #4caf50;'>> 60</span> = Știri Pozitive<br>
                    <span style='color: #f44336;'>< 40</span> = Știri Negative
                </div>
            </div>
            
        </div>
        <div style='font-size: 0.7rem; color: #666; margin-top: 8px; text-align: center;'>
            *Scorul "Verdict Sistem" include și factori invizibili aici: VIX Level, MOVE Index (Bond Vol) și SKEW (Black Swan Risk), afișați în secțiunea "Indicatori".
        </div>
        """

        # 4. Calendar logic (Forced Fallback if Empty)
        events_list = get_economic_events()
        
        # DYNAMIC FALLBACK if scraper returns empty list
        if not events_list:
            from datetime import datetime, timedelta
            
            # Calculate next week's dates dynamically
            today = datetime.now()
            
            # Find next Monday
            days_until_monday = (7 - today.weekday()) % 7
            if days_until_monday == 0:
                days_until_monday = 7  # If today is Monday, get next Monday
            next_monday = today + timedelta(days=days_until_monday)
            
            # Generate events for next week (Monday-Friday)
            events_list = []
            days_ro = ['Lun', 'Mar', 'Mie', 'Joi', 'Vin']
            
            event_templates = [
                {'name': 'Consumer Confidence (US)', 'desc': 'Încrederea consumatorilor. Impact retail și spending.'},
                {'name': 'New Home Sales (US)', 'desc': 'Vânzări case noi. Indicator sănătate piață imobiliară.'},
                {'name': 'Durable Goods Orders', 'desc': 'Comenzi bunuri durabile. Indicator activitate industrială.'},
                {'name': 'Initial Jobless Claims', 'desc': 'Cereri șomaj săptămânale. Impact piață muncă.'},
                {'name': 'Pending Home Sales', 'desc': 'Vânzări case în așteptare. Indicator anticipativ imobiliare.'}
            ]
            
            for i, template in enumerate(event_templates):
                event_date = next_monday + timedelta(days=i)
                month_names = {
                    1: 'Ian', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'Mai', 6: 'Iun',
                    7: 'Iul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
                }
                date_str = f"{days_ro[i]} {event_date.day} {month_names[event_date.month]}"
                
                events_list.append({
                    'name': template['name'],
                    'week': date_str,
                    'desc': template['desc']
                })

        events_html = "<div style='margin-top: 32px; border-top: 2px solid var(--border-light); padding-top: 24px;'>"
        events_html += "<h4 style='color: var(--primary-purple); font-size: 18px; font-weight: 700; margin-bottom: 20px; text-transform: uppercase; letter-spacing: 0.5px;'>Evenimente Majore Următoare</h4>"
        
        events_html += "<div style='display: grid; gap: 12px;'>"
        for ev in events_list:
            name = ev['name']
            name_ro = name.replace('Fed', 'Fed').replace('CPI', 'Inflația CPI').replace('GDP', 'PIB').replace('Unemployment', 'Șomaj')
            
            # Try to get better desc
            desc = get_event_impact(name)
            if desc == "Indicator economic. Poate genera volatilitate intraday." and ev.get('desc') != 'Mock Data':
                 # Keep existing desc if specific impact not found
                 desc = ev.get('desc', desc)
            
            events_html += f"""
            <div style="background: var(--light-purple-bg); border-left: 4px solid var(--primary-purple); padding: 16px 20px; border-radius: var(--radius-sm); transition: all 0.2s ease;">
                <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 8px;">
                    <strong style="color: var(--text-primary); font-size: 15px; font-weight: 600;">{name_ro}</strong>
                    <span style="color: var(--text-secondary); font-size: 13px; font-weight: 500; white-space: nowrap; margin-left: 12px;">{ev['week']}</span>
                </div>
                <div style="font-size: 14px; color: var(--text-secondary); line-height: 1.5;">{desc}</div>
            </div>
            """
        events_html += "</div></div>"

        # Formatare HTML Final 
        html = f"""
        <div style="margin-top: 32px; background-color: var(--bg-white); border-radius: var(--radius-md); border: 1px solid var(--border-light); overflow: hidden; box-shadow: var(--shadow-sm); animation: fadeIn 0.8s ease-out 0.6s backwards;">
            <div style="background: linear-gradient(135deg, var(--primary-purple) 0%, var(--dark-purple) 100%); padding: 16px 20px; border-bottom: 1px solid var(--border-light); display: flex; align-items: center;">

                <h3 style="margin: 0; font-size: 20px; font-weight: 700; color: white;">Market Cortex - Multi-Factor Analysis</h3>
            </div>
            <div style="padding: 20px;">
                
                <!-- Probabilități Section -->
                <div style="display: flex; gap: 20px; flex-wrap: wrap; margin-bottom: 15px;">
                    <div style="flex: 1; min-width: 200px; background: rgba(255,255,255,0.05); padding: 10px; border-radius: 5px;">
                        <div style="font-size: 0.8rem; color: #888; margin-bottom: 5px;">Probabilitate Direcție (Agregată)</div>
                        <div style="display: flex; align-items: center; justify-content: space-between; font-size: 0.85rem;">
                            <span style="color: #4caf50;">Bullish: <strong>{prob_up}%</strong></span>
                            <span style="color: #f44336;">Bearish: <strong>{prob_down}%</strong></span>
                        </div>
                        <div style="width: 100%; height: 6px; background: #555; margin-top: 5px; border-radius: 3px; overflow: hidden; display: flex;">
                            <div style="width: {prob_up}%; background: #4caf50; height: 100%;"></div>
                            <div style="width: {prob_down}%; background: #f44336; height: 100%;"></div>
                        </div>
                    </div>
                    
                    <div style="flex: 1; padding: 5px;">
                        <span style="font-weight: bold; color: #888; font-size: 0.9rem;">Verdict Sistem: </span>
                        <span style="font-size: 1.2rem; font-weight: bold; color: {color};">{conclusion}</span>
                        {factors_html}
                    </div>
                </div>

                {news_html}
                {events_html}
            </div>
        </div>
        """
        return html, ai_summary_raw, ai_score
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"<div style='color: red;'>Eroare generare analiză: {e}</div>", "", 50


# --- SWING TRADING COMPONENT ---

def get_swing_trading_data():
    """ Fetches data for Swing Trading Analysis including historical context. """
    data = {}
    
    # 1. SPX Data
    try:
        spx = yf.Ticker("^GSPC")
        hist = spx.history(period="2y") 
        if not hist.empty:
            current_price = hist['Close'].iloc[-1]
            hist['SMA10'] = hist['Close'].rolling(window=10).mean()
            hist['SMA50'] = hist['Close'].rolling(window=50).mean()
            hist['SMA200'] = hist['Close'].rolling(window=200).mean()
            
            data['SPX_Price'] = current_price
            data['SPX_SMA10'] = hist['SMA10'].iloc[-1]
            data['SPX_SMA50'] = hist['SMA50'].iloc[-1]
            data['SPX_SMA200'] = hist['SMA200'].iloc[-1]
            
            # RSI(14) calculation
            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            hist['RSI'] = 100 - (100 / (1 + rs))
            data['SPX_RSI'] = hist['RSI'].iloc[-1]
            
            lookback = 60
            subset = hist.iloc[-lookback:]
            
            data['Chart_SPX'] = {
                'labels': [d.strftime('%m-%d') for d in subset.index],
                'price': subset['Close'].fillna(0).tolist(),
                'sma10': subset['SMA10'].fillna(0).tolist(),
                'sma50': subset['SMA50'].fillna(0).tolist(),
                'sma200': subset['SMA200'].fillna(0).tolist(),
                'rsi': subset['RSI'].fillna(50).tolist()
            }
    except Exception as e:
        print(f"Error Swing Data (SPX): {e}")

    # 1b. Nasdaq (NDX) Data - "Motorul" pieței tech
    try:
        ndx = yf.Ticker("^NDX")
        hist_ndx = ndx.history(period="2y")
        if not hist_ndx.empty:
            ndx_price = hist_ndx['Close'].iloc[-1]
            hist_ndx['SMA10'] = hist_ndx['Close'].rolling(window=10).mean()
            hist_ndx['SMA50'] = hist_ndx['Close'].rolling(window=50).mean()
            hist_ndx['SMA200'] = hist_ndx['Close'].rolling(window=200).mean()
            
            data['NDX_Price'] = ndx_price
            data['NDX_SMA10'] = hist_ndx['SMA10'].iloc[-1]
            data['NDX_SMA50'] = hist_ndx['SMA50'].iloc[-1]
            data['NDX_SMA200'] = hist_ndx['SMA200'].iloc[-1]
            
            # RSI(14) calculation for NDX
            delta_ndx = hist_ndx['Close'].diff()
            gain_ndx = (delta_ndx.where(delta_ndx > 0, 0)).rolling(window=14).mean()
            loss_ndx = (-delta_ndx.where(delta_ndx < 0, 0)).rolling(window=14).mean()
            rs_ndx = gain_ndx / loss_ndx
            hist_ndx['RSI'] = 100 - (100 / (1 + rs_ndx))
            data['NDX_RSI'] = hist_ndx['RSI'].iloc[-1]
            
            lookback = 60
            subset_ndx = hist_ndx.iloc[-lookback:]
            
            data['Chart_NDX'] = {
                'labels': [d.strftime('%m-%d') for d in subset_ndx.index],
                'price': subset_ndx['Close'].fillna(0).tolist(),
                'sma10': subset_ndx['SMA10'].fillna(0).tolist(),
                'sma50': subset_ndx['SMA50'].fillna(0).tolist(),
                'sma200': subset_ndx['SMA200'].fillna(0).tolist(),
                'rsi': subset_ndx['RSI'].fillna(50).tolist()
            }
            print(f"    -> NDX fetched (Price: {ndx_price:.0f}, SMA200: {data['NDX_SMA200']:.0f}, RSI: {data['NDX_RSI']:.1f})")
    except Exception as e:
        print(f"Error Swing Data (NDX): {e}")

    # 1c. VIX Volatility Data
    try:
        vix = yf.Ticker("^VIX")
        hist_vix = vix.history(period="6mo")
        if not hist_vix.empty:
            vix_current = hist_vix['Close'].iloc[-1]
            data['VIX_Current'] = vix_current
            data['VIX_SMA20'] = hist_vix['Close'].rolling(window=20).mean().iloc[-1]
            
            # Calculate percentile (how current VIX compares to last 6 months)
            vix_percentile = (hist_vix['Close'] < vix_current).sum() / len(hist_vix) * 100
            data['VIX_Percentile'] = vix_percentile
            
            lookback = 60
            subset_vix = hist_vix.iloc[-lookback:]
            
            data['Chart_VIX'] = {
                'labels': [d.strftime('%m-%d') for d in subset_vix.index],
                'values': subset_vix['Close'].fillna(20).tolist()
            }
            print(f"    -> VIX fetched (Current: {vix_current:.1f}, Percentile: {vix_percentile:.0f}%)")
    except Exception as e:
        print(f"Error Swing Data (VIX): {e}")

    # 2. Fear & Greed AND PCR from CNN
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Referer': 'https://edition.cnn.com',
            'Origin': 'https://edition.cnn.com'
        }
        r = requests.get("https://production.dataviz.cnn.io/index/fearandgreed/graphdata", headers=headers, timeout=10)
        pcr_fetched_from_cnn = False
        
        if r.status_code == 200:
            j = r.json()
            
            # F&G Logic
            data['FG_Score'] = j.get('fear_and_greed', {}).get('score', 50)
            data['FG_Rating'] = j.get('fear_and_greed', {}).get('rating', 'neutral')
            hist = j.get('fear_and_greed_historical', {}).get('data', [])
            if hist:
                sorted_hist = sorted(hist, key=lambda x: x['x'])
                data['Chart_FG'] = [item['y'] for item in sorted_hist[-60:]]
            else:
                data['Chart_FG'] = [data['FG_Score']] * 60
                
            # PCR Logic from CNN (Priority)
            if 'put_call_options' in j:
                 try:
                     pcr_list = j['put_call_options'].get('data', [])
                     if pcr_list:
                         sorted_pcr = sorted(pcr_list, key=lambda x: x['x'])
                         last_item = sorted_pcr[-1]
                         data['PCR_Value'] = last_item['y']
                         data['Chart_PCR'] = [item['y'] for item in sorted_pcr[-60:]]
                         
                         # Calculate MA10
                         pcr_vals = [item['y'] for item in sorted_pcr[-70:]] # Get a bit more for rolling window
                         if len(pcr_vals) >= 10:
                             ma_series = pd.Series(pcr_vals).rolling(window=10).mean().iloc[-1]
                             data['PCR_MA10'] = float(ma_series)
                             
                             # Generate MA10 Series for Chart
                             # Need to align with Chart_PCR (last 60)
                             # So we compute rolling on full history then slice last 60
                             full_series = pd.Series([item['y'] for item in sorted_pcr])
                             ma_full = full_series.rolling(window=10).mean()
                             data['Chart_PCR_MA10'] = ma_full.iloc[-60:].fillna(0).tolist()
                             
                         pcr_fetched_from_cnn = True
                         print(f"    -> PCR fetched from CNN (Value: {data['PCR_Value']:.2f}, MA10: {data.get('PCR_MA10', 'N/A')})")
                 except Exception as e:
                     print(f"Error parsing CNN PCR: {e}")

    except Exception as e:
        print(f"Error Swing Data (CNN): {e}")
        if 'FG_Score' not in data:
            data['FG_Score'] = 50; data['FG_Rating'] = 'neutral'; data['Chart_FG'] = []

    # 3. PCR Fallback (Only if CNN failed)
    if not data.get('PCR_Value'):
        try:
            # Try Yahoo Tickers
            tickers = ['^CPC', '^PCR', '^PCX']
            pcr_found = False
            for t in tickers:
                try:
                    temp = yf.Ticker(t).history(period="3mo")
                    if not temp.empty:
                        data['PCR_Value'] = temp['Close'].iloc[-1]
                        data['Chart_PCR'] = temp['Close'].iloc[-60:].tolist()
                        pcr_found = True
                        break
                except: continue
                
            if not pcr_found: # Fallback SPY Options
                try:
                    spy = yf.Ticker("SPY")
                    exps = spy.options
                    if exps:
                        total_c = 0; total_p = 0
                        for date in exps[:2]:
                            opt = spy.option_chain(date)
                            total_c += opt.calls['volume'].fillna(0).sum()
                            total_p += opt.puts['volume'].fillna(0).sum()
                        if total_c > 0:
                            data['PCR_Value'] = total_p / total_c
                            print(f"    -> Calculated SPY Option PCR: {data['PCR_Value']:.2f}")
                except Exception as opt_e:
                    print(f"    PCR Fallback failed: {opt_e}")
                    data['PCR_Value'] = 0.8
                    data['Chart_PCR'] = []
        except Exception:
            pass

    return data

def generate_swing_trading_html():
    """ Generates HTML Card for Swing Trading with Explicit Numerical Values. """
    data = get_swing_trading_data()
    
    # Extract SPX Data
    spx_price = data.get('SPX_Price', 0)
    sma_200 = data.get('SPX_SMA200', 0)
    sma_50 = data.get('SPX_SMA50', 0)
    sma_10 = data.get('SPX_SMA10', 0)
    
    # Extract NDX Data
    ndx_price = data.get('NDX_Price', 0)
    ndx_sma_200 = data.get('NDX_SMA200', 0)
    ndx_sma_50 = data.get('NDX_SMA50', 0)
    ndx_sma_10 = data.get('NDX_SMA10', 0)
    
    # Extract RSI Data
    spx_rsi = data.get('SPX_RSI', 50)
    ndx_rsi = data.get('NDX_RSI', 50)
    
    fg_score = data.get('FG_Score', 50)
    fg_rating = str(data.get('FG_Rating', 'neutral')).capitalize()
    pcr_val = data.get('PCR_Value', 0.8) if data.get('PCR_Value') else 0.8
    pcr_ma10 = data.get('PCR_MA10', pcr_val) if data.get('PCR_MA10') else pcr_val
    
    # Chart Data JSON
    default_spx = {'labels': [], 'price': [], 'sma10': [], 'sma50': [], 'sma200': [], 'rsi': []}
    chart_spx_json = json.dumps(data.get('Chart_SPX', default_spx))
    chart_ndx_json = json.dumps(data.get('Chart_NDX', default_spx))
    chart_fg_json = json.dumps(data.get('Chart_FG', []))
    chart_pcr_json = json.dumps(data.get('Chart_PCR', []))
    chart_pcr_ma_json = json.dumps(data.get('Chart_PCR_MA10', []))
    
    # VIX Data
    vix_current = data.get('VIX_Current', 20)
    vix_sma20 = data.get('VIX_SMA20', 20)
    vix_percentile = data.get('VIX_Percentile', 50)
    default_vix = {'labels': [], 'values': []}
    chart_vix_json = json.dumps(data.get('Chart_VIX', default_vix))
    
    # VIX Interpretation (Volatility zones)
    if vix_current < 15:
        vix_zone = "COMPLAZENȚĂ"
        vix_color = "#ff9800"  # Orange - warning (too calm)
        vix_hint = "⚠️ Piață prea calmă - potențial de corecție"
    elif vix_current < 20:
        vix_zone = "NORMAL"
        vix_color = "#4caf50"  # Green
        vix_hint = "✅ Volatilitate normală"
    elif vix_current < 30:
        vix_zone = "FRICĂ"
        vix_color = "#2196f3"  # Blue - opportunity in bull
        vix_hint = "🎯 Frică = oportunitate (dacă trend bullish)"
    else:
        vix_zone = "PANICĂ"
        vix_color = "#f44336"  # Red
        vix_hint = "⛔ Volatilitate extremă - prudență maximă"
    
    # RSI Interpretation is done AFTER trend analysis (context-aware) - see below

    # --- Analysis Logic SPX ---
    trend_bullish = spx_price > sma_200
    trend_text = "BULLISH" if trend_bullish else "BEARISH"
    trend_color = "#4caf50" if trend_bullish else "#f44336"

    breadth_ok = spx_price > sma_50
    breadth_color = "#4caf50" if breadth_ok else "#ff9800"
    breadth_text = "PUTERNIC" if breadth_ok else "SLAB"

    # SPX SMA10 Short-term Timing
    spx_timing_ok = spx_price > sma_10 if sma_10 else True
    spx_timing_color = "#4caf50" if spx_timing_ok else "#f44336"
    spx_timing_text = "UP" if spx_timing_ok else "DOWN"

    # --- Analysis Logic NDX (Nasdaq - "Motorul" Tech) ---
    ndx_trend_bullish = ndx_price > ndx_sma_200 if ndx_sma_200 else True
    ndx_trend_text = "BULLISH" if ndx_trend_bullish else "BEARISH"
    ndx_trend_color = "#4caf50" if ndx_trend_bullish else "#f44336"

    ndx_momentum_ok = ndx_price > ndx_sma_50 if ndx_sma_50 else True
    ndx_momentum_color = "#4caf50" if ndx_momentum_ok else "#ff9800"
    ndx_momentum_text = "PUTERNIC" if ndx_momentum_ok else "SLAB"

    # NDX SMA10 Short-term Timing
    ndx_timing_ok = ndx_price > ndx_sma_10 if ndx_sma_10 else True
    ndx_timing_color = "#4caf50" if ndx_timing_ok else "#f44336"
    ndx_timing_text = "UP" if ndx_timing_ok else "DOWN"

    # --- RSI Context-Aware Interpretation ---
    # RSI = CONFIRMARE, nu semnal! Interpretarea depinde de trend.
    def interpret_rsi_with_context(rsi_val, is_bullish_trend):
        if is_bullish_trend:
            # În trend BULLISH: RSI 40-80 e normal, pullback 40-50 = oportunitate
            if rsi_val >= 80:
                return "EXTINS", "#ff9800", "⚠️ Supraextins - evită intrări noi"
            elif rsi_val >= 50:
                return "MOMENTUM OK", "#4caf50", "✅ Trend sănătos (40-80)"
            elif rsi_val >= 40:
                return "BUY DIP", "#2196f3", "🎯 Pullback ideal pentru intrare!"
            else:
                return "SLĂBIT", "#ff9800", "⚠️ Momentum sub 40 - atenție"
        else:
            # În trend BEARISH: orice RSI e un warning
            if rsi_val >= 70:
                return "BOUNCE", "#ff9800", "⚠️ Bounce temporar, nu trend"
            elif rsi_val >= 50:
                return "NEUTRU", "#ff9800", "⚠️ Bear market - risc crescut"
            else:
                return "SLAB", "#f44336", "⛔ Bear market + momentum slab"
    
    spx_rsi_text, spx_rsi_color, spx_rsi_hint = interpret_rsi_with_context(spx_rsi, trend_bullish)
    ndx_rsi_text, ndx_rsi_color, ndx_rsi_hint = interpret_rsi_with_context(ndx_rsi, ndx_trend_bullish)

    # Divergence Detection (SPX vs NDX)
    divergence = trend_bullish != ndx_trend_bullish
    divergence_warning = ""
    if divergence:
        if trend_bullish and not ndx_trend_bullish:
            divergence_warning = "⚠️ DIVERGENȚĂ: SPX bullish dar NDX bearish - Tech în pericol!"
        elif ndx_trend_bullish and not trend_bullish:
            divergence_warning = "⚠️ DIVERGENȚĂ: NDX bullish dar SPX bearish - Tech rezistă."

    if fg_score < 25: fg_zone = "Extreme Fear"; fg_color = "#4caf50" 
    elif fg_score < 45: fg_zone = "Fear"; fg_color = "#8bc34a"
    elif fg_score < 55: fg_zone = "Neutral"; fg_color = "#ff9800"
    elif fg_score < 75: fg_zone = "Greed"; fg_color = "#f44336"
    else: fg_zone = "Extreme Greed"; fg_color = "#d32f2f"

    if pcr_val > 1.0:
        pcr_text = "OPORTUNITATE (Fear)"
        pcr_color = "#4caf50"
        panic_signal = True
    elif pcr_val < 0.7:
        pcr_text = "GREED"
        pcr_color = "#f44336"
        panic_signal = False
    else:
        pcr_text = "NEUTRAL"
        pcr_color = "#ff9800"
        panic_signal = False
    
    verdict = "WAIT"
    verdict_color = "#ff9800"
    verdict_reason = ""
    verdict_expl = ""
    
    # Combined analysis: Both SPX and NDX must align for strong signals
    both_bullish = trend_bullish and ndx_trend_bullish
    both_momentum = breadth_ok and ndx_momentum_ok
    both_timing = spx_timing_ok and ndx_timing_ok  # SMA10 timing
    
    if both_bullish:
        if fg_score < 50:
            if both_timing:
                verdict = "BUY"
                verdict_color = "#4caf50"
                verdict_reason = "Trend UP (SPX+NDX) + Frica + Timing OK"
                verdict_expl = "Configurație ideală 'Buy the Dip'. Ambii indici sunt în trend ascendent, SMA10 confirmă timing-ul, iar sentimentul de frică oferă prețuri bune."
            else:
                verdict = "WAIT DIP"
                verdict_color = "#ff9800"
                verdict_reason = "Trend UP + Frica, dar SMA10 DOWN"
                verdict_expl = f"Trendul major e bullish și există frică, dar prețul e sub SMA10 (SPX: {spx_timing_text}, NDX: {ndx_timing_text}). Așteaptă revenire peste SMA10 pentru intrare."
        else:
            verdict = "WAIT"
            verdict_color = "#ff9800"
            verdict_reason = "Trend UP + Euforie"
            verdict_expl = (
                f"Trendul este pozitiv (Bull Market pe SPX și NDX), dar sentimentul actual ({fg_rating}, scor {fg_score:.0f}) nu oferă un punct de intrare sigur. "
                "Așteaptă o corecție sau creștere a fricii (PCR > 1.0)."
            )
    elif trend_bullish and not ndx_trend_bullish:
        verdict = "AVOID TECH"
        verdict_color = "#f44336"
        verdict_reason = "⚠️ Divergență: SPX UP dar NDX DOWN"
        verdict_expl = "SPX este bullish dar Nasdaq a căzut sub SMA200. Evită acțiunile de Tech/Growth - rotație sectorială în curs. Preferă sectoare defensive sau cash."
    elif ndx_trend_bullish and not trend_bullish:
        verdict = "TECH ONLY"
        verdict_color = "#ff9800"
        verdict_reason = "Divergență: NDX UP dar SPX DOWN"
        verdict_expl = "Nasdaq rezistă dar SPX este slab. Tech poate performa, dar riscul general este ridicat. Intrări selective doar pe liderii tech."
    else:
        verdict = "CASH"
        verdict_color = "#f44336"
        verdict_reason = "Trend DOWN (Bear Market)"
        verdict_expl = "Ambii indici (SPX și NDX) sunt sub SMA200. Statistic, pozițiile Long au rată mică de succes. Păstrează cash sau joacă defensiv."

    if panic_signal and both_bullish and both_timing:
        verdict += " (STRONG)"
        verdict_expl += " Panica semnalată de Put/Call confirmă un potențial minim local iminent."
    
    # --- Individual SPX Verdict ---
    if trend_bullish:
        if fg_score < 50:
            spx_verdict = "BUY"
            spx_verdict_color = "#4caf50"
            spx_verdict_text = "Bull Market + Frica oferă oportunitate de cumpărare."
        else:
            spx_verdict = "WAIT"
            spx_verdict_color = "#ff9800"
            spx_verdict_text = "Bull Market, dar euforie excesivă. Așteaptă corecție."
    else:
        spx_verdict = "CASH"
        spx_verdict_color = "#f44336"
        spx_verdict_text = "Bear Market (sub SMA200). Risc ridicat pentru poziții Long."
    
    # --- Individual NDX Verdict ---
    if ndx_trend_bullish:
        if fg_score < 50:
            ndx_verdict = "BUY TECH"
            ndx_verdict_color = "#4caf50"
            ndx_verdict_text = "Nasdaq bullish + Frica = oportunitate pe Growth/Tech."
        else:
            ndx_verdict = "HOLD TECH"
            ndx_verdict_color = "#ff9800"
            ndx_verdict_text = "Tech în trend ascendent, dar greed = riscant pentru intrări noi."
    else:
        ndx_verdict = "AVOID TECH"
        ndx_verdict_color = "#f44336"
        ndx_verdict_text = "Nasdaq sub SMA200. Acțiunile Tech/Growth sunt vulnerabile."
    
    uid = str(int(datetime.datetime.now().timestamp()))

    html = f"""
    <div style="margin: 32px 0; background: #fff; border-radius: 12px; border: 1px solid #e0e0e0; box-shadow: 0 4px 12px rgba(0,0,0,0.08); overflow: hidden; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
        
        <div style="background: {verdict_color}; padding: 16px 24px; color: white; display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 10px;">
            <div>
                <h3 style="margin: 0; font-size: 18px; font-weight: 700;">🏦 Swing Trading Signal (Long-only)</h3>
                <div style="font-size: 13px; opacity: 0.9; margin-top: 4px;">Analiză Context SPX + NDX • Strategie Trend Following</div>
            </div>
            <div style="text-align: right;">
                 <div style="background: rgba(255,255,255,0.2); padding: 6px 16px; border-radius: 20px; font-weight: bold; font-size: 16px; border: 1px solid rgba(255,255,255,0.3); box-shadow: 0 2px 4px rgba(0,0,0,0.1);">{verdict}</div>
            </div>
        </div>

        <div style="padding: 24px;">
            
            <!-- SECTION 1: METRICS & CHARTS (4 Columns) -->
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 24px; margin-bottom: 32px;">
                
                <!-- 1. TREND CARD -->
                <div style="border: 1px solid #eee; border-radius: 8px; padding: 16px; background: #fdfdfd; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <span style="font-weight: 600; color: #555;">Trend (SMA200)</span>
                        <div style="text-align: right;">
                             <div style="font-weight: 800; color: {trend_color};">{trend_text}</div>
                        </div>
                    </div>
                    <div style="position: relative; height: 160px; width: 100%;">
                        <canvas id="chart_trend_{uid}"></canvas>
                    </div>
                    <div style="font-size: 12px; color: #555; margin-top: 8px; text-align: center; background: #f5f5f5; padding: 4px; border-radius: 4px;">
                        Preț: <b>{spx_price:.0f}</b> / <span style="color:#f9a825">SMA200: <b>{sma_200:.0f}</b></span>
                    </div>
                </div>

                <!-- 2. BREADTH CARD -->
                <div style="border: 1px solid #eee; border-radius: 8px; padding: 16px; background: #fdfdfd; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <span style="font-weight: 600; color: #555;">Momentum (SMA50)</span>
                        <div style="text-align: right;">
                             <div style="font-weight: 800; color: {breadth_color};">{breadth_text}</div>
                        </div>
                    </div>
                    <div style="position: relative; height: 160px; width: 100%;">
                        <canvas id="chart_breadth_{uid}"></canvas>
                    </div>
                    <div style="font-size: 12px; color: #555; margin-top: 8px; text-align: center; background: #f5f5f5; padding: 4px; border-radius: 4px;">
                        Preț: <b>{spx_price:.0f}</b> / <span style="color:#2e7d32">SMA50: <b>{sma_50:.0f}</b></span>
                    </div>
                </div>

                <!-- 2b. TIMING CARD (SMA10) -->
                <div style="border: 1px solid #e3f2fd; border-radius: 8px; padding: 16px; background: #f8fbff; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <span style="font-weight: 600; color: #555;">Timing (SMA10)</span>
                        <div style="text-align: right;">
                             <div style="font-weight: 800; color: {spx_timing_color};">{spx_timing_text}</div>
                        </div>
                    </div>
                    <div style="position: relative; height: 160px; width: 100%;">
                        <canvas id="chart_timing_{uid}"></canvas>
                    </div>
                    <div style="font-size: 12px; color: #555; margin-top: 8px; text-align: center; background: #e3f2fd; padding: 4px; border-radius: 4px;">
                        Preț: <b>{spx_price:.0f}</b> / <span style="color:#1976d2">SMA10: <b>{sma_10:.0f}</b></span>
                    </div>
                </div>

                <!-- 3. SENTIMENT CARD -->
                <div style="border: 1px solid #eee; border-radius: 8px; padding: 16px; background: #fdfdfd; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <span style="font-weight: 600; color: #555;">Sentiment (F&G)</span>
                        <div style="text-align: right;">
                             <div style="font-weight: 800; color: {fg_color};">{fg_zone} ({fg_score:.0f})</div>
                        </div>
                    </div>
                    <div style="position: relative; height: 120px; width: 100%;">
                        <canvas id="chart_fg_{uid}"></canvas>
                    </div>
                    <div style="font-size: 12px; color: #555; margin-top: 8px; text-align: center;">
                        Scor: <b>{fg_score:.0f}</b> / 100
                    </div>
                </div>

                <!-- 4. TIMING CARD -->
                <div style="border: 1px solid #eee; border-radius: 8px; padding: 16px; background: #fdfdfd; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <div>
                            <span style="font-weight: 600; color: #555;">Timing (PCR)</span>
                            <div style="font-size: 10px; color: #999;">Total Market (Vol)</div>
                        </div>
                        <div style="text-align: right;">
                             <div style="font-weight: 800; color: {pcr_color};">{pcr_text}</div>
                        </div>
                    </div>
                     <div style="position: relative; height: 120px; width: 100%;">
                        <canvas id="chart_pcr_{uid}"></canvas>
                    </div>
                    <div style="font-size: 16px; color: {pcr_color}; font-weight: 800; margin-top: 8px; text-align: center;">
                        {pcr_val:.2f}
                    </div>
                    <div style="font-size: 10px; color: #777; margin-top: 4px; text-align: center; font-style: italic;">
                        *Notă: PCR Equity-only poate fi mai mic (~{(pcr_val*0.85):.2f})
                    </div>
                    <div style="font-size: 10px; color: #555; margin-top: 6px; text-align: center; display: flex; justify-content: center; gap: 16px;">
                        <span style="display: flex; align-items: center;"><span style="width: 12px; height: 3px; background: {pcr_color}; margin-right: 4px;"></span>Zilnic: <b style="margin-left: 2px;">{pcr_val:.2f}</b></span>
                        <span style="display: flex; align-items: center;"><span style="width: 12px; height: 2px; border-top: 2px dotted #999; margin-right: 4px;"></span>MA10: <b style="margin-left: 2px;">{pcr_ma10:.2f}</b></span>
                    </div>
                </div>

                <!-- 5. RSI MOMENTUM CARD (SPX) -->
                <div style="border: 1px solid #ffe0b2; border-radius: 8px; padding: 16px; background: #fff8e1; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <div>
                            <span style="font-weight: 600; color: #555;">Momentum (RSI14)</span>
                            <div style="font-size: 10px; color: #999;">Confirmation Signal</div>
                        </div>
                        <div style="text-align: right;">
                             <div style="font-weight: 800; color: {spx_rsi_color};">{spx_rsi_text}</div>
                        </div>
                    </div>
                    <div style="position: relative; height: 100px; width: 100%;">
                        <canvas id="chart_rsi_{uid}"></canvas>
                    </div>
                    <div style="font-size: 14px; color: {spx_rsi_color}; font-weight: 800; margin-top: 8px; text-align: center;">
                        RSI: {spx_rsi:.1f}
                    </div>
                    <div style="font-size: 10px; color: #555; margin-top: 4px; text-align: center;">
                        {spx_rsi_hint}
                    </div>
                </div>

                <!-- 6. VIX VOLATILITY CARD -->
                <div style="border: 1px solid #ffcdd2; border-radius: 8px; padding: 16px; background: #fff5f5; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <div>
                            <span style="font-weight: 600; color: #555;">Volatilitate (VIX)</span>
                            <div style="font-size: 10px; color: #999;">Fear Index</div>
                        </div>
                        <div style="text-align: right;">
                             <div style="font-weight: 800; color: {vix_color};">{vix_zone}</div>
                        </div>
                    </div>
                    <div style="position: relative; height: 100px; width: 100%;">
                        <canvas id="chart_vix_{uid}"></canvas>
                    </div>
                    <div style="font-size: 14px; color: {vix_color}; font-weight: 800; margin-top: 8px; text-align: center;">
                        VIX: {vix_current:.1f}
                    </div>
                    <div style="font-size: 10px; color: #555; margin-top: 4px; text-align: center;">
                        {vix_hint}
                    </div>
                    <div style="font-size: 9px; color: #888; margin-top: 4px; text-align: center;">
                        Percentilă 6M: {vix_percentile:.0f}% | SMA20: {vix_sma20:.1f}
                    </div>
                </div>

            </div>

            <!-- SECTION 1b: NASDAQ (Tech Motor) -->
            <div style="margin-bottom: 32px;">
                <div style="font-size: 14px; font-weight: 700; color: #7b1fa2; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 2px solid #e1bee7;">
                    📊 NASDAQ (NDX) — „Motorul" Tech
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 24px;">
                    
                    <!-- NDX TREND CARD -->
                    <div style="border: 1px solid #e1bee7; border-radius: 8px; padding: 16px; background: #faf5fc; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                            <div>
                                <span style="font-weight: 600; color: #555;">NDX Trend (SMA200)</span>
                                <div style="font-size: 10px; color: #999;">Nasdaq 100</div>
                            </div>
                            <div style="text-align: right;">
                                 <div style="font-weight: 800; color: {ndx_trend_color};">{ndx_trend_text}</div>
                            </div>
                        </div>
                        <div style="position: relative; height: 140px; width: 100%;">
                            <canvas id="chart_ndx_trend_{uid}"></canvas>
                        </div>
                        <div style="font-size: 12px; color: #555; margin-top: 8px; text-align: center; background: #f3e5f5; padding: 4px; border-radius: 4px;">
                            Preț: <b>{ndx_price:.0f}</b> / <span style="color:#f9a825">SMA200: <b>{ndx_sma_200:.0f}</b></span>
                        </div>
                    </div>

                    <!-- NDX MOMENTUM CARD -->
                    <div style="border: 1px solid #e1bee7; border-radius: 8px; padding: 16px; background: #faf5fc; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                            <div>
                                <span style="font-weight: 600; color: #555;">NDX Momentum (SMA50)</span>
                                <div style="font-size: 10px; color: #999;">Nasdaq 100</div>
                            </div>
                            <div style="text-align: right;">
                                 <div style="font-weight: 800; color: {ndx_momentum_color};">{ndx_momentum_text}</div>
                            </div>
                        </div>
                        <div style="position: relative; height: 140px; width: 100%;">
                            <canvas id="chart_ndx_momentum_{uid}"></canvas>
                        </div>
                        <div style="font-size: 12px; color: #555; margin-top: 8px; text-align: center; background: #f3e5f5; padding: 4px; border-radius: 4px;">
                            Preț: <b>{ndx_price:.0f}</b> / <span style="color:#2e7d32">SMA50: <b>{ndx_sma_50:.0f}</b></span>
                        </div>
                    </div>

                    <!-- NDX TIMING CARD (SMA10) -->
                    <div style="border: 1px solid #e1bee7; border-radius: 8px; padding: 16px; background: #faf5fc; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                            <div>
                                <span style="font-weight: 600; color: #555;">NDX Timing (SMA10)</span>
                                <div style="font-size: 10px; color: #999;">Nasdaq 100</div>
                            </div>
                            <div style="text-align: right;">
                                 <div style="font-weight: 800; color: {ndx_timing_color};">{ndx_timing_text}</div>
                            </div>
                        </div>
                        <div style="position: relative; height: 140px; width: 100%;">
                            <canvas id="chart_ndx_timing_{uid}"></canvas>
                        </div>
                        <div style="font-size: 12px; color: #555; margin-top: 8px; text-align: center; background: #f3e5f5; padding: 4px; border-radius: 4px;">
                            Preț: <b>{ndx_price:.0f}</b> / <span style="color:#1976d2">SMA10: <b>{ndx_sma_10:.0f}</b></span>
                        </div>
                    </div>

                    <!-- NDX RSI MOMENTUM CARD -->
                    <div style="border: 1px solid #e1bee7; border-radius: 8px; padding: 16px; background: #faf5fc; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                            <div>
                                <span style="font-weight: 600; color: #555;">NDX Momentum (RSI14)</span>
                                <div style="font-size: 10px; color: #999;">Confirmation Signal</div>
                            </div>
                            <div style="text-align: right;">
                                 <div style="font-weight: 800; color: {ndx_rsi_color};">{ndx_rsi_text}</div>
                            </div>
                        </div>
                        <div style="position: relative; height: 100px; width: 100%;">
                            <canvas id="chart_ndx_rsi_{uid}"></canvas>
                        </div>
                        <div style="font-size: 14px; color: {ndx_rsi_color}; font-weight: 800; margin-top: 8px; text-align: center;">
                            RSI: {ndx_rsi:.1f}
                        </div>
                        <div style="font-size: 10px; color: #555; margin-top: 4px; text-align: center;">
                            {ndx_rsi_hint}
                        </div>
                    </div>

                </div>
            </div>

            <!-- SECTION 2: ANALYSIS DETAILS -->
            <div style="border-top: 2px solid #f0f0f0; padding-top: 24px;">
                <h4 style="margin: 0 0 16px 0; color: {verdict_color}; font-size: 18px; text-transform: uppercase;">
                   ⚠️ Analiză: {verdict_reason}
                </h4>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
                    
                    <!-- S&P 500 Analysis -->
                    <div style="background: #e3f2fd; padding: 16px; border-radius: 8px; border-left: 4px solid {spx_verdict_color};">
                        <div style="font-size: 11px; font-weight: bold; color: #1565c0; text-transform: uppercase; margin-bottom: 4px;">📈 S&P 500 (Corpul)</div>
                        <div style="font-size: 18px; font-weight: 800; color: {spx_verdict_color}; margin-bottom: 8px;">{spx_verdict}</div>
                        <div style="font-size: 12px; color: #333; margin-bottom: 6px;">
                            <b>Trend:</b> <span style="color:{trend_color}">{trend_text}</span> | <b>Momentum:</b> <span style="color:{breadth_color}">{breadth_text}</span>
                        </div>
                        <div style="font-size: 13px; color: #444; font-style: italic;">"{spx_verdict_text}"</div>
                    </div>

                    <!-- Nasdaq Analysis -->
                    <div style="background: #f3e5f5; padding: 16px; border-radius: 8px; border-left: 4px solid {ndx_verdict_color};">
                        <div style="font-size: 11px; font-weight: bold; color: #7b1fa2; text-transform: uppercase; margin-bottom: 4px;">🚀 NASDAQ (Motorul Tech)</div>
                        <div style="font-size: 18px; font-weight: 800; color: {ndx_verdict_color}; margin-bottom: 8px;">{ndx_verdict}</div>
                        <div style="font-size: 12px; color: #333; margin-bottom: 6px;">
                            <b>Trend:</b> <span style="color:{ndx_trend_color}">{ndx_trend_text}</span> | <b>Momentum:</b> <span style="color:{ndx_momentum_color}">{ndx_momentum_text}</span>
                        </div>
                        <div style="font-size: 13px; color: #444; font-style: italic;">"{ndx_verdict_text}"</div>
                    </div>

                    <!-- Combined Conclusion -->
                    <div style="background: {verdict_color}15; padding: 16px; border-radius: 8px; border: 2px solid {verdict_color}60; grid-column: 1 / -1;">
                        <div style="font-size: 11px; font-weight: bold; color: {verdict_color}; text-transform: uppercase; margin-bottom: 4px;">🎯 CONCLUZIE GENERALĂ</div>
                        <div style="font-size: 22px; font-weight: 800; color: {verdict_color}; margin-bottom: 8px;">{verdict}</div>
                        <div style="font-size: 14px; color: #333;">
                            {verdict_expl}
                        </div>
                    </div>

                </div>
            </div>

        </div>
    </div>

    <script>
    (function() {{
        const spxData = {chart_spx_json};
        const ndxData = {chart_ndx_json};
        const fgData = {chart_fg_json};
        const pcrData = {chart_pcr_json};
        const pcrMA = {chart_pcr_ma_json};
        const vixData = {chart_vix_json};

        if (typeof Chart !== 'undefined') {{
            new Chart(document.getElementById('chart_trend_{uid}').getContext('2d'), {{
                type: 'line',
                data: {{ labels: spxData.labels, datasets: [{{ label: 'Preț', data: spxData.price, borderColor: '#cad5e2', borderWidth: 1.5, pointRadius: 0 }}, {{ label: 'SMA200', data: spxData.sma200, borderColor: '#fbc02d', borderWidth: 2, pointRadius: 0, borderDash: [2,2] }}] }},
                options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }}, scales: {{ x: {{ display: false }}, y: {{ display: true }} }} }}
            }});
            new Chart(document.getElementById('chart_breadth_{uid}').getContext('2d'), {{
                type: 'line',
                data: {{ labels: spxData.labels, datasets: [{{ label: 'Preț', data: spxData.price, borderColor: '#cad5e2', borderWidth: 1.5, pointRadius: 0 }}, {{ label: 'SMA50', data: spxData.sma50, borderColor: '#4caf50', borderWidth: 2, pointRadius: 0 }}] }},
                options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }}, scales: {{ x: {{ display: false }}, y: {{ display: true }} }} }}
            }});
            // SPX SMA10 Timing Chart
            new Chart(document.getElementById('chart_timing_{uid}').getContext('2d'), {{
                type: 'line',
                data: {{ labels: spxData.labels, datasets: [{{ label: 'Preț', data: spxData.price, borderColor: '#cad5e2', borderWidth: 1.5, pointRadius: 0 }}, {{ label: 'SMA10', data: spxData.sma10, borderColor: '#1976d2', borderWidth: 2, pointRadius: 0 }}] }},
                options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }}, scales: {{ x: {{ display: false }}, y: {{ display: true }} }} }}
            }});
            new Chart(document.getElementById('chart_fg_{uid}').getContext('2d'), {{
                type: 'line',
                data: {{ labels: Array(fgData.length).fill(''), datasets: [{{ label: 'F&G', data: fgData, borderColor: '{fg_color}', backgroundColor: '{fg_color}20', fill: true, pointRadius: 0, tension: 0.4 }}] }},
                options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }}, scales: {{ x: {{ display: false }}, y: {{ min: 0, max: 100 }} }} }}
            }});
            new Chart(document.getElementById('chart_pcr_{uid}').getContext('2d'), {{
                type: 'line',
                data: {{ 
                    labels: Array(pcrData.length).fill(''), 
                    datasets: [
                        {{ label: 'PCR', data: pcrData, borderColor: '{pcr_color}', borderWidth: 1.5, pointRadius: 0, tension: 0.2 }},
                        {{ label: 'MA10', data: pcrMA, borderColor: '#999', borderWidth: 1, pointRadius: 0, borderDash: [2,2], tension: 0.2 }}
                    ] 
                }},
                options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }}, scales: {{ x: {{ display: false }} }} }}
            }});
            
            // NDX Charts (Nasdaq - Purple theme)
            if (ndxData && ndxData.price && ndxData.price.length > 0) {{
                new Chart(document.getElementById('chart_ndx_trend_{uid}').getContext('2d'), {{
                    type: 'line',
                    data: {{ labels: ndxData.labels, datasets: [{{ label: 'Preț', data: ndxData.price, borderColor: '#d1c4e9', borderWidth: 1.5, pointRadius: 0 }}, {{ label: 'SMA200', data: ndxData.sma200, borderColor: '#9c27b0', borderWidth: 2, pointRadius: 0, borderDash: [2,2] }}] }},
                    options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }}, scales: {{ x: {{ display: false }}, y: {{ display: true }} }} }}
                }});
                new Chart(document.getElementById('chart_ndx_momentum_{uid}').getContext('2d'), {{
                    type: 'line',
                    data: {{ labels: ndxData.labels, datasets: [{{ label: 'Preț', data: ndxData.price, borderColor: '#d1c4e9', borderWidth: 1.5, pointRadius: 0 }}, {{ label: 'SMA50', data: ndxData.sma50, borderColor: '#7b1fa2', borderWidth: 2, pointRadius: 0 }}] }},
                    options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }}, scales: {{ x: {{ display: false }}, y: {{ display: true }} }} }}
                }});
                // NDX SMA10 Timing Chart
                new Chart(document.getElementById('chart_ndx_timing_{uid}').getContext('2d'), {{
                    type: 'line',
                    data: {{ labels: ndxData.labels, datasets: [{{ label: 'Preț', data: ndxData.price, borderColor: '#d1c4e9', borderWidth: 1.5, pointRadius: 0 }}, {{ label: 'SMA10', data: ndxData.sma10, borderColor: '#1976d2', borderWidth: 2, pointRadius: 0 }}] }},
                    options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }}, scales: {{ x: {{ display: false }}, y: {{ display: true }} }} }}
                }});
                // NDX RSI Chart
                new Chart(document.getElementById('chart_ndx_rsi_{uid}').getContext('2d'), {{
                    type: 'line',
                    data: {{ labels: ndxData.labels, datasets: [{{ label: 'RSI', data: ndxData.rsi, borderColor: '#9c27b0', backgroundColor: '#9c27b020', fill: true, borderWidth: 2, pointRadius: 0, tension: 0.3 }}] }},
                    options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }}, scales: {{ x: {{ display: false }}, y: {{ min: 0, max: 100, ticks: {{ callback: (v) => v === 30 || v === 70 ? v : '' }} }} }} }}
                }});
            }}
            
            // SPX RSI Chart
            if (spxData && spxData.rsi && spxData.rsi.length > 0) {{
                new Chart(document.getElementById('chart_rsi_{uid}').getContext('2d'), {{
                    type: 'line',
                    data: {{ labels: spxData.labels, datasets: [{{ label: 'RSI', data: spxData.rsi, borderColor: '#ff9800', backgroundColor: '#ff980020', fill: true, borderWidth: 2, pointRadius: 0, tension: 0.3 }}] }},
                    options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }}, scales: {{ x: {{ display: false }}, y: {{ min: 0, max: 100, ticks: {{ callback: (v) => v === 30 || v === 70 ? v : '' }} }} }} }}
                }});
            }}
            
            // VIX Chart with color zones
            if (vixData && vixData.values && vixData.values.length > 0) {{
                new Chart(document.getElementById('chart_vix_{uid}').getContext('2d'), {{
                    type: 'line',
                    data: {{ 
                        labels: vixData.labels, 
                        datasets: [{{ 
                            label: 'VIX', 
                            data: vixData.values, 
                            borderColor: '{vix_color}', 
                            backgroundColor: '{vix_color}20', 
                            fill: true, 
                            borderWidth: 2, 
                            pointRadius: 0, 
                            tension: 0.3 
                        }}] 
                    }},
                    options: {{ 
                        responsive: true, 
                        maintainAspectRatio: false, 
                        plugins: {{ legend: {{ display: false }} }}, 
                        scales: {{ 
                            x: {{ display: false }}, 
                            y: {{ min: 10, max: 40, ticks: {{ callback: (v) => [15, 20, 30].includes(v) ? v : '' }} }} 
                        }} 
                    }}
                }});
            }}
        }}
    }})();
    </script>
    """
    
    return html