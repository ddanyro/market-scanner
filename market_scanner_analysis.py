import requests
import pandas as pd
from io import StringIO
import datetime

def get_economic_events():
    """Scrapes Yahoo Finance for upcoming US economic events (Current & Next Week)."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        
        all_events = []
        seen_events = set()
        
        # Iterăm pentru săptămâna curentă și următoare (Yahoo afișează weekly view based on day param)
        today = datetime.date.today()
        dates_to_check = [today, today + datetime.timedelta(days=7)]
        
        for d in dates_to_check:
            url = f"https://finance.yahoo.com/calendar/economic?day={d}"
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
                    continue # Fără coloană țară nu putem filtra
                
                # Colectare evenimente
                # Keywords extinse
                keywords = ['Fed', 'FOMC', 'CPI', 'GDP', 'Nonfarm', 'Unemployment', 'PPI', 'Rate', 'Retail', 'Sentiment', 'Confidence', 'Manufacturing', 'Services', 'Home', 'Job']
                
                for idx, row in us_df.iterrows():
                    evt = str(row['Event'])
                    # Filtrare opțională: Doar cele relevante (conțin keywords) SAU toate dacă sunt puține
                    is_major = any(k.lower() in evt.lower() for k in keywords)
                    
                    if is_major:
                        evt_time = str(row['Event Time'])
                        unique_id = f"{evt}_{evt_time}"
                        
                        if unique_id not in seen_events:
                            seen_events.add(unique_id)
                            all_events.append(f"{evt} ({evt_time})")
                            
            except Exception as e:
                print(f"Sub-request error: {e}")
                continue
        
        return all_events[:8] # Returnăm primele 8
    except Exception as e:
        print(f"Calendar error: {e}")
        return []

def generate_market_analysis(indicators):
    """Generează o analiză narativă bazată pe indicatorii de piață (AI Simulated)."""
    try:
        # Extragem valorile cheie (cu fallback la 0 sau medii)
        def get_val(name):
            try:
                return float(indicators.get(name, {}).get('value', 0))
            except:
                return 0

        vix = get_val('VIX')
        skew = get_val('SKEW')
        move = get_val('MOVE')
        fear = get_val('Crypto Fear')
        
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

        # 2. Analiza SKEW
        if skew > 145:
            skew_text = "SKEW ridicat indică frică de 'Black Swan'."
            sentiment_score -= 10
        elif skew < 115:
            skew_text = "Protecția la risc este ieftină."
        else:
            skew_text = "Percepția riscului este moderată."

        # Construire Concluzie și Șanse
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
            conclusion = "Piață sub presiune. Posibilă oportunitate pentru investitori pe termen lung, dar riscant pe termen scurt."
            color = "#f44336"
        else:
            outlook = "Neutral"
            prob_up = 50
            prob_down = 50
            conclusion = "Piață incertă. Se recomandă prudență."
            color = "#e0e0e0"

        # Evenimente Economice
        events_list = get_economic_events()
        events_html = ""
        if events_list:
            events_html = "<div style='margin-top: 15px; border-top: 1px solid #444; padding-top: 10px;'>"
            events_html += "<strong style='color: #4dabf7; font-size: 0.9rem;'>⚠️ Evenimente Majore Următoare (SUA):</strong>"
            events_html += "<ul style='margin-top: 5px; padding-left: 20px; color: #ccc; font-size: 0.85rem;'>"
            for ev in events_list:
                # Traduceri sumare
                ev_ro = ev.replace('Fed', 'Fed').replace('CPI', 'Inflația CPI').replace('GDP', 'PIB').replace('Unemployment', 'Șomaj').replace('Confidence', 'Încredere').replace('Sales', 'Vânzări')
                events_html += f"<li>{ev_ro}</li>"
            events_html += "</ul></div>"

        # Formatare HTML Final
        html = f"""
        <div style="margin-top: 25px; background-color: #252526; border-radius: 8px; border: 1px solid #3e3e42; overflow: hidden;">
            <div style="background-color: #333; padding: 10px 15px; border-bottom: 1px solid #3e3e42; display: flex; align-items: center;">
                <span style="font-size: 1.2rem; margin-right: 10px;">🤖</span>
                <h3 style="margin: 0; font-size: 1rem; color: #e0e0e0;">Analiză de Piață & Calendar</h3>
            </div>
            <div style="padding: 20px;">
                <p style="margin-bottom: 15px; color: #cccccc; line-height: 1.6; font-size: 0.9rem;">
                    <strong>Sinteză:</strong> {vix_text} {skew_text}
                </p>
                
                <div style="display: flex; gap: 20px; flex-wrap: wrap; margin-bottom: 15px;">
                    <div style="flex: 1; min-width: 200px; background: rgba(255,255,255,0.05); padding: 10px; border-radius: 5px;">
                        <div style="font-size: 0.8rem; color: #888; margin-bottom: 5px;">Probabilități</div>
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

                <div style="border-top: 1px solid #444; padding-top: 10px;">
                    <span style="font-weight: bold; color: #888; font-size: 0.9rem;">Concluzie: </span>
                    <span style="font-size: 1rem; font-weight: bold; color: {color};">{conclusion}</span>
                </div>
                
                {events_html}
            </div>
        </div>
        """
        return html
    except Exception as e:
        return f"<div style='color: red;'>Eroare generare analiză: {e}</div>"
