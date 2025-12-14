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

def generate_market_analysis(indicators):
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

        # 3. News Summary (AI sau Fallback)
        news_items = get_market_news()
        news_html = "<div style='margin-top: 20px; border-top: 1px solid #444; padding-top: 15px;'>"
        news_html += "<strong style='color: #4dabf7; font-size: 0.95rem; display: block; margin-bottom: 10px;'>📰 Market News Overview</strong>"
        
        ai_summary_html = ""
        # Încercăm AI Summary
        try:
            import google.generativeai as genai
            api_key = os.environ.get("GOOGLE_API_KEY")
            if not api_key and os.path.exists("gemini_key.txt"):
                 with open("gemini_key.txt", "r") as f: api_key = f.read().strip()
            
            if api_key:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-pro')
                
                # Check desc text valid
                news_text_list = []
                for n in news_items:
                    d = n['desc'].strip() if n['desc'] else ""
                    news_text_list.append(f"- {n['title']}: {d}")
                
                news_text = "\n".join(news_text_list)
                
                prompt = f"""
                Ești un analist financiar senior. Scrie un "Market Overview" concis (1-2 paragrafe), în limba română, care sintetizează starea pieței bazându-te pe aceste știri recente și pe VIX ({vix}):
                {news_text}
                Fără liste cu puncte. Doar narațiune fluidă. Folosește taguri <b> pentru concepte cheie.
                """
                resp = model.generate_content(prompt)
                if resp and resp.text:
                    ai_summary_html = f"<div style='color: #ddd; font-size: 0.95rem; line-height: 1.5; background: #333; padding: 10px; border-radius: 5px; margin-bottom: 15px;'>{resp.text}</div>"
            else:
                 ai_summary_html = "<div style='color:orange'>Lipsă cheie Gemini (gemini_key.txt).</div>"

        except Exception as e:
            ai_summary_html = f"<div style='color: red; padding: 10px; border: 1px solid red;'>Eroare Generare AI: {e}</div>"

        if ai_summary_html:
            news_html += ai_summary_html
            # Afișăm și link-uri mici dedesubt
            news_html += "<div style='font-size: 0.8rem; color: #888; margin-top: 10px;'>Surse: "
            for n in news_items[:3]:
                 news_html += f"<a href='{n['link']}' target='_blank' style='color: #aaa; text-decoration: none; margin-right: 10px;'>{n['title'][:20]}...</a>"
            news_html += "</div>"
        elif news_items:
            # Fallback la lista detaliată
            news_html += "<ul style='margin: 0; padding-left: 20px; color: #ccc; font-size: 0.9rem; list-style-type: none;'>"
            for item in news_items:
                news_html += f"""
                <li style="margin-bottom: 12px;">
                    <a href='{item['link']}' target='_blank' style='color: #e0e0e0; font-weight: bold; text-decoration: none;'>{item['title']}</a>
                    <div style="color: #aaa; font-size: 0.85rem; margin-top: 3px;">{item['desc'][:150]}...</div>
                </li>
                """
            news_html += "</ul>"
        else:
            news_html += "<div style='color: #aaa;'>Nu au fost preluate știri.</div>"
            
        news_html += "</div>"

        # 4. Calendar (Fix Disappearing)
        events_list = get_economic_events()
        events_html = "<div style='margin-top: 20px; border-top: 1px solid #444; padding-top: 15px;'>"
        events_html += "<strong style='color: #ffb74d; font-size: 0.95rem; display: block; margin-bottom: 10px;'>⚠️ Evenimente Majore Următoare:</strong>"
        
        if events_list:
            events_html += "<ul style='margin: 0; padding-left: 20px; color: #ccc; font-size: 0.9rem; list-style-type: none;'>"
            for ev in events_list:
                name = ev['name']
                name_ro = name.replace('Fed', 'Fed').replace('CPI', 'Inflația CPI').replace('GDP', 'PIB').replace('Unemployment', 'Șomaj')
                desc = get_event_impact(name)
                
                events_html += f"""
                <li style="margin-bottom: 10px; padding-left: 10px; border-left: 3px solid #666;">
                    <div>
                        <strong style="color: #fff;">{name_ro}</strong> 
                        <span style="color: #888; font-size: 0.8rem;">({ev['week']})</span>
                    </div>
                    <div style="font-size: 0.85rem; color: #aaa; margin-top: 2px;">{desc}</div>
                </li>
                """
            events_html += "</ul>"
        else:
            events_html += "<div style='color: #888; font-style: italic;'>Niciun eveniment major detectat pentru perioada următoare.</div>"
        
        events_html += "</div>"

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
        return html
    except Exception as e:
        return f"<div style='color: red;'>Eroare generare analiză: {e}</div>"
        skew = get_val('SKEW')
        move = get_val('MOVE')
        fear = get_val('Crypto Fear')
        
        # Logica de interpretare
        # Logica de interpretare
        vix_text = ""
        sentiment_score = 50 
        
        # 1. Analiza VIX
        if vix < 14:
            vix_text = "Volatilitatea este extrem de scăzută (Complacere). Risc de 'wake-up call'."
            sentiment_score += 10
        elif vix < 20:
            vix_text = "Volatilitatea este în limite normale."
            sentiment_score += 5
        elif vix < 30:
            vix_text = "Tensiune ridicată în piață."
            sentiment_score -= 15
        else:
            vix_text = "Piața este în stare de panică (VIX > 30)."
            sentiment_score -= 30

        # Building Conclusions
        if sentiment_score >= 60:
            outlook = "Bullish"
            prob_up = 65
            prob_down = 35
            conclusion = "Moment Bun de Cumpărare, dar cu atenție la riscuri extreme (SKEW)."
            color = "#4caf50"
        elif sentiment_score <= 30:
            outlook = "Bearish"
            prob_up = 40
            prob_down = 60
            conclusion = "Piață sub presiune. Posibilă oportunitate pentru investitori pe termen lung."
            color = "#f44336"
        else:
            outlook = "Neutral"
            prob_up = 50
            prob_down = 50
            conclusion = "Piață incertă. Se recomandă prudență."
            color = "#e0e0e0"

        # Evenimente Economice - Calendar
        events_list = get_economic_events()
        events_html = ""
        if events_list:
            events_html = "<div style='margin-top: 20px; border-top: 1px solid #444; padding-top: 15px;'>"
            events_html += "<strong style='color: #ffb74d; font-size: 0.95rem; display: block; margin-bottom: 10px;'>⚠️ Evenimente Majore Următoare:</strong>"
            events_html += "<ul style='margin: 0; padding-left: 20px; color: #ccc; font-size: 0.9rem; list-style-type: none;'>"
            
            for ev in events_list:
                name = ev['name']
                name_ro = name.replace('Fed', 'Fed').replace('CPI', 'Inflația CPI').replace('GDP', 'PIB').replace('Unemployment', 'Șomaj')
                
                # Check for detailed description match
                desc = get_event_impact(name)
                
                events_html += f"""
                <li style="margin-bottom: 10px; padding-left: 10px; border-left: 3px solid #666;">
                    <div>
                        <strong style="color: #fff;">{name_ro}</strong> 
                        <span style="color: #888; font-size: 0.8rem;">({ev['week']})</span>
                    </div>
                    <div style="font-size: 0.85rem; color: #aaa; margin-top: 2px;">
                        {desc}
                    </div>
                </li>
                """
            events_html += "</ul></div>"

        # News Section
        news_section = get_market_news()

        # Formatare HTML Final
        # Ordine: Analiză (Probabilități) -> News -> Calendar
        
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
                </div>

                <div style="border-bottom: 1px solid #444; padding-bottom: 10px; margin-bottom: 10px;">
                    <span style="font-weight: bold; color: #888; font-size: 0.9rem;">Concluzie: </span>
                    <span style="font-size: 1rem; font-weight: bold; color: {color};">{conclusion}</span>
                    <br>
                    <span style="font-size: 0.9rem; color: #aaa;">{vix_text}</span>
                </div>
                
                <!-- News -->
                {news_section}
                
                <!-- Calendar (deasupra glosarului, in bloc separat) -->
                {events_html}
            </div>
        </div>
        """
        return html
    except Exception as e:
        return f"<div style='color: red;'>Eroare generare analiză: {e}</div>"
