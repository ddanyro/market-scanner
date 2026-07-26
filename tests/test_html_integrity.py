import unittest
import re
import os

class TestHtmlIntegrity(unittest.TestCase):
    
    def test_volatility_calculator_ids(self):
        """
        Verify that all element IDs referenced in the Volatility Calculator JS
        actually exist in the HTML structure.
        """
        file_path = os.path.join(os.path.dirname(__file__), '..', 'market_scanner.py')
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract the Volatility Calculator HTML/JS section
        # We assume it starts around "Volatility Calculator" and ends around "</script>"
        # Using a broad search to ensure we catch the relevant parts
        
        # 1. Find all referenced IDs in JS: document.getElementById('xyz')
        # Regex captures the ID inside quote
        js_ref_pattern = re.compile(r"document\.getElementById\(['\"]([^'\"]+)['\"]\)")
        references = set(js_ref_pattern.findall(content))
        
        # Filter references to only those that look like calculator IDs (res-, vol-, stop-, suggested-)
        calc_refs = {ref for ref in references if ref.startswith(('res-', 'vol-', 'stop-', 'suggested-'))}
        
        # 2. Find all defined IDs in HTML: id="xyz"
        html_id_pattern = re.compile(r'id=["\']([^"\']+)["\']')
        definitions = set(html_id_pattern.findall(content))
        
        # 3. Check for missing IDs
        missing = []
        for ref in calc_refs:
            if ref not in definitions:
                # Exclude dynamic IDs or other known exceptions if any
                missing.append(ref)
                
        # Assert no missing IDs
        self.assertEqual(missing, [], f"The following IDs are referenced in JS but not defined in HTML: {missing}")

    def test_js_logic_completeness(self):
        """
        Verify that critical JS variables are correctly populated.
        """
        file_path = os.path.join(os.path.dirname(__file__), '..', 'market_scanner.py')
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check that res-day is populated (was missing before)
        self.assertIn("getElementById('res-day').innerText", content, "JS should populate res-day")
        
        # Check that res-atr-pct is used instead of res-atr
        self.assertIn("getElementById('res-atr-pct')", content, "JS should use correct ID res-atr-pct")
        self.assertNotIn("getElementById('res-atr').innerText", content, "JS should NOT use incorrect ID res-atr")

    def test_market_indicators_open_detail_window_with_real_ohlc(self):
        """Indicatorii trebuie să păstreze tabelul și să deschidă detalii într-o filă nouă."""
        file_path = os.path.join(os.path.dirname(__file__), '..', 'market_scanner.py')
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn("onclick=\"openIndicatorDetail('", content)
        self.assertIn("window.open('', '_blank')", content)
        self.assertIn("'ohlc': ohlc_data", content)
        self.assertIn("'history': data_points[-60:]", content)
        self.assertIn("'history_dates': [x['date'] for x in history_db[name]][-60:]", content)
        self.assertIn("hasUsableIndicatorOhlc(detail.ohlc)", content)
        self.assertIn("candles.length < 5", content)
        self.assertIn("nonFlat.length / valid.length >= 0.2", content)
        self.assertIn("drawCandles(canvas, detail.ohlc.slice(-count), detail.levels || [])", content)
        self.assertIn("drawLineSeries(canvas, series, dates, levels)", content)
        self.assertIn("ctx.fillText(formatIndicatorNumber(value),pad.left-8,py)", content)
        self.assertIn("String(dates[index]).slice(5)", content)
        self.assertIn("Istoric zilnic real afișat liniar", content)

    def test_portfolio_mini_chart_opens_encrypted_candlestick_details(self):
        """Doar mini-graficul portofoliului deschide istoricul mare, păstrat în payload-ul criptat."""
        file_path = os.path.join(os.path.dirname(__file__), '..', 'market_scanner.py')
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn("onclick=\"openPortfolioDetail('", content)
        self.assertIn('"chart_details": portfolio_detail_data', content)
        self.assertIn("'Chart_OHLC': chart_ohlc", content)
        self.assertIn("'Chart_History': chart_history", content)
        self.assertIn("portfolioDetailData = data.chart_details || {}", content)
        self.assertIn("function openPortfolioDetail(symbol)", content)
        self.assertIn("openMarketDetailWindow(detail, symbol)", content)
        self.assertIn("if(event.key==='Escape'){event.preventDefault();window.close();}", content)
        self.assertIn('"Stop activ" if len(active_stops) == 1', content)
        self.assertIn("for price_column in ('Calculated_Stop', 'Stop_Price', 'Aux_Price')", content)
        self.assertIn('"label": "Stop propus"', content)
        self.assertIn("quantity_label", content)
        self.assertIn('"color": "#2563eb"', content)
        self.assertIn("drawHorizontalLevels(ctx,width,pad,min,max,levels)", content)
        self.assertIn("ctx.setLineDash([7,5])", content)

    def test_portfolio_ai_analysis_is_in_encrypted_payload(self):
        """Analiza nouă trebuie să rămână în spatele PIN-ului portofoliului."""
        file_path = os.path.join(os.path.dirname(__file__), '..', 'market_scanner.py')
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn('id="portfolio-ai-container"', content)
        self.assertIn("portfolioAi.innerHTML = data.portfolio_ai_html || ''", content)
        self.assertIn('"portfolio_ai_html": portfolio_ai_html', content)
        self.assertIn('generate_portfolio_ai_analysis(', content)
        self.assertIn("with open('tws_account.json', 'r'", content)
        self.assertIn("with open('tws_account.enc.json', 'r'", content)
        self.assertIn('market_security.decrypt_from_js(', content)
        self.assertIn("with open('tws_account_risk.json', 'r'", content)
        self.assertIn('account_data=tws_account_data', content)

    def test_watchlist_mini_chart_opens_detail_window(self):
        """Mini-graficul watchlistului deschide aceeași fereastră OHLC, fără a schimba click-ul simbolului."""
        file_path = os.path.join(os.path.dirname(__file__), '..', 'market_scanner.py')
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn("onclick=\"openWatchlistDetail('", content)
        self.assertIn("'Chart_OHLC': watch_chart_ohlc", content)
        self.assertIn("'Chart_History': watch_chart_history", content)
        self.assertIn("const watchlistDetailData =", content)
        self.assertIn("function openWatchlistDetail(symbol)", content)
        self.assertIn("openMarketDetailWindow(detail, symbol)", content)
        self.assertIn("detail.kind === 'watchlist'", content)
        self.assertIn("'label': 'Stop recomandat'", content)
        self.assertIn("'levels': watchlist_levels", content)
        self.assertIn("'Smart_Entry_EUR': round(s_entry * rate, 2)", content)
        self.assertIn("row.get('Decision') == 'BUY'", content)
        self.assertIn("'label': f'Entry recomandat · {entry_type}'", content)
        self.assertIn("and spark_data[-2] != 0", content)

if __name__ == '__main__':
    unittest.main()
