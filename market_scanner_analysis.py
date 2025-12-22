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
            hist['SMA50'] = hist['Close'].rolling(window=50).mean()
            hist['SMA200'] = hist['Close'].rolling(window=200).mean()
            
            data['SPX_Price'] = current_price
            data['SPX_SMA50'] = hist['SMA50'].iloc[-1]
            data['SPX_SMA200'] = hist['SMA200'].iloc[-1]
            
            lookback = 60
            subset = hist.iloc[-lookback:]
            
            data['Chart_SPX'] = {
                'labels': [d.strftime('%m-%d') for d in subset.index],
                'price': subset['Close'].fillna(0).tolist(),
                'sma50': subset['SMA50'].fillna(0).tolist(),
                'sma200': subset['SMA200'].fillna(0).tolist()
            }
    except Exception as e:
        print(f"Error Swing Data (SPX): {e}")

    # 2. Fear & Greed
    try:
        headers = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://edition.cnn.com/'}
        r = requests.get("https://production.dataviz.cnn.io/index/fearandgreed/graphdata", headers=headers, timeout=5)
        if r.status_code == 200:
            j = r.json()
            data['FG_Score'] = j.get('fear_and_greed', {}).get('score', 50)
            data['FG_Rating'] = j.get('fear_and_greed', {}).get('rating', 'neutral')
            hist = j.get('fear_and_greed_historical', {}).get('data', [])
            if hist:
                sorted_hist = sorted(hist, key=lambda x: x['x'])
                data['Chart_FG'] = [item['y'] for item in sorted_hist[-60:]]
            else:
                data['Chart_FG'] = [data['FG_Score']] * 60
    except Exception as e:
        print(f"Error Swing Data (F&G): {e}")
        data['FG_Score'] = 50
        data['FG_Rating'] = 'neutral'
        data['Chart_FG'] = []

    # 3. PCR (Put/Call Ratio) - Persistence
    try:
        tickers = ['^CPC', '^PCR', '^PCX'] # Try real
        pcr_found = False
        for t in tickers:
            try:
                temp = yf.Ticker(t).history(period="3mo")
                if not temp.empty:
                    data['PCR_Value'] = temp['Close'].iloc[-1]
                    pcr_found = True
                    break
            except: continue
            
        if not pcr_found: # Fallback SPY
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

    except Exception as e:
        print(f"Error Swing Data (PCR): {e}")

    # Persistence Logic
    if 'PCR_Value' in data:
        try:
            hist_file = "market_history.json"
            today = datetime.datetime.now().strftime('%Y-%m-%d')
            db = {}
            if os.path.exists(hist_file):
                with open(hist_file, 'r') as f:
                    try: db = json.load(f)
                    except: db = {}
            
            if 'PCR' not in db: db['PCR'] = {}
            db['PCR'][today] = float(data['PCR_Value'])
            
            with open(hist_file, 'w') as f:
                json.dump(db, f, indent=4)
            
            # Chart from History
            dates = sorted(db['PCR'].keys())
            chart_vals = [db['PCR'][d] for d in dates[-60:]]
            
            if len(chart_vals) < 2:
                data['Chart_PCR'] = [data['PCR_Value']] * 60
            else:
                data['Chart_PCR'] = chart_vals
                
        except Exception as e:
            print(f"Error saving PCR history: {e}")
            if 'Chart_PCR' not in data: data['Chart_PCR'] = [data.get('PCR_Value', 0.8)] * 60
    else:
        data['PCR_Value'] = 0.8
        data['Chart_PCR'] = []

    return data

def generate_swing_trading_html():
    """ Generates HTML Card for Swing Trading Context (Long Only). """
    data = get_swing_trading_data()
    
    # Extract Data
    spx_price = data.get('SPX_Price', 0)
    sma_200 = data.get('SPX_SMA200', 0)
    sma_50 = data.get('SPX_SMA50', 0)
    fg_score = data.get('FG_Score', 50)
    fg_rating = str(data.get('FG_Rating', 'neutral')).capitalize()
    pcr_val = data.get('PCR_Value', 0.8) if data.get('PCR_Value') else 0.8
    
    # Prepare JSONs for JS Charting
    default_spx = {'labels': [], 'price': [], 'sma50': [], 'sma200': []}
    chart_spx_json = json.dumps(data.get('Chart_SPX', default_spx))
    chart_fg_json = json.dumps(data.get('Chart_FG', []))
    chart_pcr_json = json.dumps(data.get('Chart_PCR', []))

    # --- Analysis Logic ---
    
    # 1. Trend
    trend_bullish = spx_price > sma_200
    trend_text = "BULLISH" if trend_bullish else "BEARISH"
    trend_color = "#4caf50" if trend_bullish else "#f44336"
    trend_desc = f"Preț ({spx_price:.0f}) > SMA200 ({sma_200:.0f})" if trend_bullish else f"Preț ({spx_price:.0f}) < SMA200 ({sma_200:.0f})"

    # 2. Sentiment
    if fg_score < 25: fg_zone = "Extreme Fear"; fg_color = "#4caf50" 
    elif fg_score < 45: fg_zone = "Fear"; fg_color = "#8bc34a"
    elif fg_score < 55: fg_zone = "Neutral"; fg_color = "#ff9800"
    elif fg_score < 75: fg_zone = "Greed"; fg_color = "#f44336"
    else: fg_zone = "Extreme Greed"; fg_color = "#d32f2f"

    # 3. Breadth
    breadth_ok = spx_price > sma_50
    breadth_color = "#4caf50" if breadth_ok else "#ff9800"
    breadth_text = "Peste SMA50" if breadth_ok else "Sub SMA50"

    # 4. Timing
    panic_signal = pcr_val > 1.0
    pcr_color = "#4caf50" if panic_signal else "#aaa"
    pcr_text = "OPORTUNITATE (Fear)" if panic_signal else "Normal"
    
    # Verdict
    verdict = "WAIT"
    verdict_color = "#ff9800"
    verdict_reason = ""
    
    if trend_bullish:
        if fg_score < 50:
            verdict = "BUY"
            verdict_color = "#4caf50"
            verdict_reason = "Trend Up + Fear"
        else:
            verdict = "WAIT"
            verdict_color = "#ff9800"
            verdict_reason = "Trend Up + Greed"
    else:
        verdict = "CASH"
        verdict_color = "#f44336"
        verdict_reason = "Trend Down"

    if panic_signal and trend_bullish:
        verdict += " (STRONG)"
    
    # Unique ID for charts to avoid conflicts
    uid = str(int(datetime.datetime.now().timestamp()))

    html = f"""
    <div style="margin: 32px 0; background: #fff; border-radius: 12px; border: 1px solid #e0e0e0; box-shadow: 0 4px 12px rgba(0,0,0,0.08); overflow: hidden;">
        
        <!-- Header -->
        <div style="background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%); padding: 16px 24px; color: white; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h3 style="margin: 0; font-size: 18px; font-weight: 700;">🏦 Swing Trading Signal (Long-only)</h3>
                <div style="font-size: 12px; opacity: 0.8; margin-top: 4px;">Analiză Multi-Factor: Trend, Sentiment, Breadth, Timing</div>
            </div>
            <div style="text-align: right;">
                 <div style="background: rgba(255,255,255,0.2); padding: 4px 12px; border-radius: 20px; font-weight: bold;">{verdict}</div>
            </div>
        </div>

        <div style="padding: 24px;">
            <!-- Grid Layout -->
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 24px;">
                
                <!-- 1. TREND CARD -->
                <div style="border: 1px solid #eee; border-radius: 8px; padding: 16px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <span style="font-weight: 600; color: #555;">Trend (SPX vs SMA200)</span>
                        <span style="font-weight: 800; color: {trend_color};">{trend_text}</span>
                    </div>
                    <div style="position: relative; height: 160px; width: 100%;"><canvas id="chart_trend_{uid}"></canvas></div>
                    <div style="font-size: 11px; color: #888; margin-top: 8px; text-align: center;">Preț (Albastru) vs SMA50 (Verde) vs SMA200 (Rosu)</div>
                </div>

                <!-- 2. SENTIMENT CARD -->
                <div style="border: 1px solid #eee; border-radius: 8px; padding: 16px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <span style="font-weight: 600; color: #555;">Sentiment (CNN F&G)</span>
                        <span style="font-weight: 800; color: {fg_color};">{fg_zone} ({fg_score})</span>
                    </div>
                    <div style="position: relative; height: 120px; width: 100%;"><canvas id="chart_fg_{uid}"></canvas></div>
                </div>

                <!-- 3. TIMING CARD (PCR) -->
                <div style="border: 1px solid #eee; border-radius: 8px; padding: 16px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <span style="font-weight: 600; color: #555;">Timing (Put/Call Ratio)</span>
                        <span style="font-weight: 800; color: {pcr_color};">{pcr_val:.2f} ({pcr_text})</span>
                    </div>
                    <div style="position: relative; height: 120px; width: 100%;"><canvas id="chart_pcr_{uid}"></canvas></div>
                </div>
                
                <!-- 4. VERDICT DETAILS -->
                <div style="background: {verdict_color}10; border-radius: 8px; padding: 16px; border: 1px solid {verdict_color};">
                    <h4 style="margin: 0 0 10px 0; color: {verdict_color};">Detalii Verdict: {verdict}</h4>
                    <ul style="margin: 0; padding-left: 20px; font-size: 14px; color: #444; line-height: 1.6;">
                        <li><strong>Trend:</strong> {trend_desc}</li>
                        <li><strong>Breadth:</strong> <span style="color: {breadth_color}; font-weight: bold;">{breadth_text}</span></li>
                        <li><strong>Concluzie:</strong> {verdict_reason}</li>
                    </ul>
                </div>

            </div>
        </div>
    </div>

    <script>
    (function() {{
        // Data passed from Python
        const spxData = {chart_spx_json};
        const fgData = {chart_fg_json};
        const pcrData = {chart_pcr_json};

        // --- CHART 1: SPX TREND ---
        const ctxTrend = document.getElementById('chart_trend_{uid}').getContext('2d');
        // Simple line drawing logic (no external lib dependency if we want standalone, but Chart.js is better if included)
        // Checks if Chart.js is available. It is usually included in standard templates.
        // Assuming Chart.js is present (standard in this dashboard).
        
        if (typeof Chart !== 'undefined') {{
            new Chart(ctxTrend, {{
                type: 'line',
                data: {{
                    labels: spxData.labels,
                    datasets: [
                        {{
                            label: 'SPX Price',
                            data: spxData.price,
                            borderColor: '#2196f3',
                            borderWidth: 2,
                            pointRadius: 0
                        }},
                        {{
                            label: 'SMA 50',
                            data: spxData.sma50,
                            borderColor: '#4caf50',
                            borderWidth: 1.5,
                            borderDash: [5, 5],
                            pointRadius: 0
                        }},
                        {{
                            label: 'SMA 200',
                            data: spxData.sma200,
                            borderColor: '#f44336',
                            borderWidth: 1.5,
                            pointRadius: 0
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{ legend: {{ display: false }} }},
                    scales: {{ 
                        x: {{ display: false }},
                        y: {{ display: true }}
                    }}
                }}
            }});

            // --- CHART 2: F&G ---
            const ctxFG = document.getElementById('chart_fg_{uid}').getContext('2d');
            new Chart(ctxFG, {{
                type: 'line',
                data: {{
                    labels: Array(fgData.length).fill(''),
                    datasets: [{{
                        label: 'Fear & Greed',
                        data: fgData,
                        borderColor: '#ff9800',
                        backgroundColor: 'rgba(255, 152, 0, 0.1)',
                        fill: true,
                        pointRadius: 0,
                        tension: 0.4
                    }}]
                }},
                options: {{
                    responsive: true, maintainAspectRatio: false,
                    plugins: {{ legend: {{ display: false }} }},
                    scales: {{ x: {{ display: false }}, y: {{ min:0, max:100 }} }}
                }}
            }});

            // --- CHART 3: PCR ---
            const ctxPCR = document.getElementById('chart_pcr_{uid}').getContext('2d');
            new Chart(ctxPCR, {{
                type: 'line',
                data: {{
                    labels: Array(pcrData.length).fill(''),
                    datasets: [{{
                        label: 'Put/Call Ratio',
                        data: pcrData,
                        borderColor: '#9c27b0',
                        pointRadius: 0,
                        tension: 0.3
                    }}]
                }},
                options: {{
                    responsive: true, maintainAspectRatio: false,
                    plugins: {{ legend: {{ display: false }} }},
                    scales: {{ x: {{ display: false }} }}
                }}
            }});
        }} else {{
            // Fallback text if Chart.js missing
            document.getElementById('chart_trend_{uid}').parentNode.innerHTML += '<div style="color:red">Chart.js missing</div>';
        }}
    }})();
    </script>
    """
    
    return html
