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
        spx_change = indicators.get('SPX', {}).get('change', 0)
        
        # Logica de interpretare
        analysis_points = []
        sentiment_score = 50 # 0 = Extreme Bearish, 100 = Extreme Bullish
        
        # 1. Analiza VIX (Fear Gauge)
        if vix < 14:
            vix_text = "Volatilitatea este extrem de scăzută (Complacere). Investitorii nu se așteaptă la riscuri majore, dar history sugerează că perioadele lungi de VIX scăzut preced corecții bruște."
            sentiment_score += 10
        elif vix < 20:
            vix_text = "Volatilitatea este în limite normale, susținând un trend de piață stabil."
            sentiment_score += 5
        elif vix < 30:
            vix_text = "Există tensiune ridicată în piață. Investitorii plătesc prime mari pentru protecție."
            sentiment_score -= 15
        else:
            vix_text = "Piața este în stare de panică (VIX > 30). De obicei, acestea sunt momente de 'capitulare' care pot marca un bottom."
            sentiment_score -= 30

        # 2. Analiza SKEW (Tail Risk)
        if skew > 145:
            skew_text = "Indicele SKEW este foarte ridicat, semnalând că 'banii inteligenți' se protejează agresiv împotriva unui eveniment de tip Black Swan."
            sentiment_score -= 10
        elif skew < 115:
            skew_text = "Cererea pentru protecție extremă este redusă (lipsă de îngrijorare)."
        else:
            skew_text = "Percepția riscului extrem este moderată."

        # 3. Analiza MOVE (Bond Market)
        if move > 120:
            move_text = "Volatilitatea pe piața obligațiunilor este critică, punând presiune pe acțiunile de creștere și tehnologie."
            sentiment_score -= 10
        else:
            move_text = ""

        # Construire Concluzie și Șanse
        if sentiment_score >= 60:
            outlook = "Bullish (Pozitiv)"
            prob_up = 65
            prob_down = 35
            conclusion = "Acesta pare un **Moment Bun de Cumpărare** sau Menținere. Trendul este susținut de calm, dar rămâneți vigilenți la SKEW ridicat."
            color = "#4caf50" # Green
        elif sentiment_score <= 30:
            outlook = "Bearish (Negativ) / Volatil"
            prob_up = 40
            prob_down = 60
            if vix > 35:
                conclusion = "Deși riscurile sunt mari, panica extremă poate oferi oportunități excelente de cumpărare pe termen lung ('Be greedy when others are fearful')."
                color = "#ff9800" # Orange
            else:
                conclusion = "Nu este un moment ideal pentru intrări agresive. Piața este sub presiune. Cash is king."
                color = "#f44336" # Red
        else:
            outlook = "Neutral / Incert"
            prob_up = 50
            prob_down = 50
            conclusion = "Piața caută o direcție clară. Se recomandă prudență și acumulare selectivă (Dollar Cost Averaging)."
            color = "#ffeb3b" # Yellow (sau alb)
            if color == "#ffeb3b": color = "#e0e0e0" # White for neutral

        # Formatare HTML
        html = f"""
        <div style="margin-top: 25px; background-color: #252526; border-radius: 8px; border: 1px solid #3e3e42; overflow: hidden;">
            <div style="background-color: #333; padding: 10px 15px; border-bottom: 1px solid #3e3e42; display: flex; align-items: center;">
                <span style="font-size: 1.2rem; margin-right: 10px;">🤖</span>
                <h3 style="margin: 0; font-size: 1rem; color: #e0e0e0;">Analiză & Prognoză (AI Model)</h3>
            </div>
            <div style="padding: 20px;">
                <p style="margin-bottom: 15px; color: #cccccc; line-height: 1.6;">
                    <strong>Interpretare:</strong> {vix_text} {skew_text} {move_text}
                </p>
                
                <div style="display: flex; gap: 20px; flex-wrap: wrap; margin-bottom: 20px;">
                    <div style="flex: 1; min-width: 200px; background: rgba(255,255,255,0.05); padding: 15px; border-radius: 5px;">
                        <div style="font-size: 0.8rem; color: #888; margin-bottom: 5px;">Șanse Estimate</div>
                        <div style="display: flex; align-items: center; justify-content: space-between; font-size: 0.9rem;">
                            <span style="color: #4caf50;">Creștere: <strong>{prob_up}%</strong></span>
                            <span style="color: #f44336;">Scădere: <strong>{prob_down}%</strong></span>
                        </div>
                        <div style="width: 100%; height: 6px; background: #555; margin-top: 8px; border-radius: 3px; overflow: hidden; display: flex;">
                            <div style="width: {prob_up}%; background: #4caf50; height: 100%;"></div>
                            <div style="width: {prob_down}%; background: #f44336; height: 100%;"></div>
                        </div>
                    </div>
                </div>

                <div style="border-top: 1px solid #444; padding-top: 15px;">
                    <span style="font-weight: bold; color: #888;">Concluzie: </span>
                    <span style="font-size: 1.1rem; font-weight: bold; color: {color};">{conclusion}</span>
                </div>
                <div style="margin-top: 10px; font-size: 0.75rem; color: #666; font-style: italic;">
                    * Această analiză este generată automat pe baza indicatorilor tehnici și nu reprezintă un sfat financiar certificat.
                </div>
            </div>
        </div>
        """
        return html
    except Exception as e:
        return f"<div style='color: red;'>Eroare generare analiză: {e}</div>"
