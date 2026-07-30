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
        self.assertIn("function drawCandles(canvas, candles, levels, currency, markers)", content)
        self.assertIn("function drawLineSeries(canvas, series, dates, levels, currency, markers)", content)
        self.assertIn("ctx.fillText(formatDetailNumber(value,currency),pad.left-8,py)", content)
        self.assertIn("formatRomanianDate(dates[index],false,true)", content)
        self.assertIn("formatRomanianDate(item.date,false,true)", content)
        self.assertIn("function formatRomanianDate(", content)
        self.assertIn("Istoric zilnic real afișat liniar", content)

    def test_portfolio_mini_chart_opens_encrypted_candlestick_details(self):
        """Doar mini-graficul portofoliului deschide istoricul mare, păstrat în payload-ul criptat."""
        file_path = os.path.join(os.path.dirname(__file__), '..', 'market_scanner.py')
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn("onclick=\"openPortfolioDetail('", content)
        self.assertIn('"chart_details": portfolio_detail_data', content)
        self.assertIn('"buy_chart_details": buy_recommendation_detail_data', content)
        self.assertIn("'Chart_OHLC': chart_ohlc", content)
        self.assertIn("'Chart_History': chart_history", content)
        self.assertIn("portfolioDetailData = data.chart_details || {}", content)
        self.assertIn(
            "buyRecommendationDetailData = data.buy_chart_details || {}",
            content,
        )
        self.assertIn("function openPortfolioDetail(symbol)", content)
        self.assertIn("function openBuyRecommendationDetail(symbol)", content)
        self.assertIn("openMarketDetailWindow(detail, symbol)", content)
        self.assertIn("if(event.key==='Escape'){event.preventDefault();window.close();}", content)
        self.assertIn('"Stop activ" if len(active_stops) == 1', content)
        self.assertIn("for price_column in ('Calculated_Stop', 'Stop_Price', 'Aux_Price')", content)
        self.assertIn('"label": "Stop propus"', content)
        self.assertIn("quantity_label", content)
        self.assertIn('"color": "#2563eb"', content)
        self.assertIn("drawHorizontalLevels(ctx,width,pad,min,max,levels,currency)", content)
        self.assertIn("formatDetailNumber(value,currency)", content)
        self.assertIn("detail.currency", content)
        self.assertIn("Grafic zilnic${detail.currency?", content)
        self.assertIn("detailChartLayout(width, currency, levels.length > 0, false)", content)
        self.assertIn("ctx.setLineDash([7,5])", content)
        self.assertIn("function drawRecommendationMarkers(", content)
        self.assertIn("ctx.moveTo(x,y-9)", content)
        self.assertIn("detail.markers || []", content)
        self.assertIn("Recomandări de cumpărare marcate punctual", content)
        self.assertIn("_build_history_chart_candidates(", content)

    def test_detail_charts_are_readable_on_mobile(self):
        """Graficul mobil folosește toată lățimea și mută etichetele nivelurilor sub canvas."""
        root = os.path.join(os.path.dirname(__file__), '..')
        for filename in ('market_scanner.py', 'index.html'):
            with self.subTest(filename=filename):
                with open(os.path.join(root, filename), 'r', encoding='utf-8') as f:
                    content = f.read()

                self.assertIn("const compact = width <= 640", content)
                self.assertIn("left: currency ? 62 : 48", content)
                self.assertIn("right: 10", content)
                self.assertIn("if (pad.compact)", content)
                self.assertIn("detailChartTickIndexes(candles.length,chartW)", content)
                self.assertIn("detailChartTickIndexes(series.length,chartW)", content)
                self.assertIn("Math.floor(chartWidth / 58)", content)
                self.assertIn("renderHorizontalLevelLegend(detail.levels || []", content)
                self.assertIn("class='level-legend'", content)
                self.assertIn(
                    "window.matchMedia('(max-width: 640px)').matches?22:66",
                    content,
                )

    def test_buy_now_web_push_is_configured_without_exposing_api_key(self):
        root = os.path.join(os.path.dirname(__file__), '..')
        with open(
            os.path.join(root, 'market_scanner.py'),
            'r',
            encoding='utf-8',
        ) as f:
            generator = f.read()
        with open(
            os.path.join(root, '.github', 'workflows', 'update_dashboard.yml'),
            'r',
            encoding='utf-8',
        ) as f:
            workflow = f.read()
        with open(
            os.path.join(
                root, 'push', 'onesignal', 'OneSignalSDKWorker.js'
            ),
            'r',
            encoding='utf-8',
        ) as f:
            worker = f.read()

        self.assertIn('send_new_buy_now_notifications(', generator)
        self.assertIn('ONESIGNAL_APP_ID', generator)
        self.assertIn('OneSignalSDK.page.js', generator)
        self.assertIn('Activează alertele BUY', generator)
        self.assertIn('Instalează pentru alerte BUY', generator)
        self.assertIn('repairBuyNowPushSubscription', generator)
        self.assertIn(
            'marketScannerOneSignalSubscriptionRepair:',
            generator,
        )
        self.assertIn('validBuyNowPushSubscriptionId', generator)
        self.assertIn('waitForBuyNowPushSubscription', generator)
        self.assertIn('Alerte BUY – reconectare', generator)
        self.assertIn("':v2'", generator)
        self.assertIn(
            'await OneSignal.User.PushSubscription.optOut()',
            generator,
        )
        self.assertIn(
            'await OneSignal.User.PushSubscription.optIn()',
            generator,
        )
        self.assertIn('OneSignal.User.PushSubscription.id', generator)
        self.assertIn('manifest.webmanifest', generator)
        self.assertIn('secrets.ONESIGNAL_APP_ID', workflow)
        self.assertIn('secrets.ONESIGNAL_API_KEY', workflow)
        self.assertIn('Retry pending BUY alerts', workflow)
        self.assertIn(
            'python buy_now_push.py --retry-state dashboard_state.json',
            workflow,
        )
        self.assertIn('OneSignalSDK.sw.js', worker)
        with open(
            os.path.join(root, 'index.html'),
            'r',
            encoding='utf-8',
        ) as f:
            generated_dashboard = f.read()
        self.assertNotIn('ONESIGNAL_API_KEY', generated_dashboard)

    def test_portfolio_ai_analysis_is_in_encrypted_payload(self):
        """Analiza nouă trebuie să rămână în spatele PIN-ului portofoliului."""
        file_path = os.path.join(os.path.dirname(__file__), '..', 'market_scanner.py')
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        analysis_path = os.path.join(
            os.path.dirname(__file__), '..', 'market_scanner_analysis.py'
        )
        with open(analysis_path, 'r', encoding='utf-8') as f:
            analysis_content = f.read()
        workflow_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            '.github',
            'workflows',
            'update_dashboard.yml',
        )
        with open(workflow_path, 'r', encoding='utf-8') as f:
            workflow = f.read()
        index_path = os.path.join(
            os.path.dirname(__file__), '..', 'index.html'
        )
        with open(index_path, 'r', encoding='utf-8') as f:
            generated_content = f.read()

        self.assertIn('id="portfolio-ai-container"', content)
        self.assertIn("portfolioAi.innerHTML = data.portfolio_ai_html || ''", content)
        self.assertIn('"portfolio_ai_html": portfolio_ai_html', content)
        self.assertIn('generate_portfolio_ai_analysis(', content)
        self.assertIn("with open('tws_account.json', 'r'", content)
        self.assertIn("with open('tws_account.enc.json', 'r'", content)
        self.assertIn('market_security.decrypt_from_js(', content)
        self.assertIn("with open('tws_account_risk.json', 'r'", content)
        self.assertIn("os.environ.get('TWS_ACCOUNT_PASSWORD', '') or password", content)
        self.assertIn("with open('tradeville_account.enc.json', 'r'", content)
        self.assertIn("'IBKR TWS + Tradeville manual'", content)
        self.assertIn("ibkr_account['source'] = 'IBKR TWS'", content)
        self.assertIn("'IBKR' if len(raw_ibkr_accounts) == 1", content)
        self.assertIn("Solduri brute brokeri", analysis_content)
        self.assertIn("('NetLiquidation', 'Valoare totală / NAV')", analysis_content)
        self.assertIn("('TotalCashValue', 'Cash total')", analysis_content)
        self.assertIn("'broker': str(row.get('Broker', '')).strip()", analysis_content)
        self.assertIn("'Tradeville' if symbol.endswith('.RO') else 'IBKR'", analysis_content)
        self.assertIn("TVBETETF (proxy BET-TR)", analysis_content)
        self.assertIn("Ce fac piețele relevante", analysis_content)
        self.assertIn('account_data=tws_account_data', content)
        self.assertIn('portfolio_market_context = analysis.build_portfolio_market_context(', content)
        self.assertIn('market_context=portfolio_market_context', content)
        self.assertIn("full_state['broker_totals_history_enc']", content)
        self.assertIn('market_security.encrypt_for_js(', content)
        self.assertNotIn('initBrokerTotalsMiniChart', content)
        self.assertIn("id='brokerTotalsHistoryButton'", analysis_content)
        self.assertIn('>Evoluție</button>', analysis_content)
        self.assertIn('openBrokerTotalsDetail', content)
        self.assertIn('parseIBKRNavHistory', content)
        self.assertIn('parseIBKRCashHistory', content)
        self.assertIn("import ibkr_web_api", content)
        self.assertIn("ibkr_web_api.sync_account_snapshot()", content)
        self.assertLess(
            content.index('ib_tws_sync.fetch_active_orders('),
            content.index('IBKR Web API fallback:'),
        )
        self.assertIn(
            'ib_sync.sync_ibkr(allow_flex=not tws_synced)',
            content,
        )
        self.assertIn('sync_before_load=False', content)
        self.assertIn(
            'tws_account.enc.json tws_account_risk.json',
            workflow,
        )
        self.assertNotIn('git add tws_account.json', workflow)
        self.assertIn("label:'Valoare totală'", content)
        self.assertIn("label:'Cash total'", content)
        self.assertIn("label:'NAV IBKR'", content)
        self.assertIn("label:'Cash IBKR'", content)
        self.assertIn(
            'history.map(item=>timestampKey(item.timestamp))',
            content,
        )
        self.assertIn(
            "series(history,'timestamp','net_liquidation',timestampKey)",
            content,
        )
        self.assertIn(
            "{dateStyle:'short',timeStyle:'short'}",
            content,
        )
        self.assertIn('spanGaps:true', content)
        self.assertIn(
            'history.map(item=>timestampKey(item.timestamp))',
            generated_content,
        )
        self.assertIn('window.close();', content)

    def test_portfolio_auth_is_remembered_implicitly_for_thirty_days(self):
        """Deblocarea este memorată criptat, fără parolă în local/session storage."""
        root = os.path.join(os.path.dirname(__file__), '..')
        with open(
            os.path.join(root, 'market_scanner.py'),
            'r',
            encoding='utf-8',
        ) as handle:
            content = handle.read()
        with open(
            os.path.join(root, 'portfolio_auth.js'),
            'r',
            encoding='utf-8',
        ) as handle:
            auth_content = handle.read()
        with open(
            os.path.join(root, 'index.html'),
            'r',
            encoding='utf-8',
        ) as handle:
            generated_content = handle.read()

        self.assertIn('<script src="portfolio_auth.js"></script>', content)
        self.assertIn(
            '<script src="portfolio_auth.js"></script>',
            generated_content,
        )
        self.assertIn('void restorePortfolioAccess()', content)
        self.assertIn('void restorePortfolioAccess()', generated_content)
        self.assertIn('remember: true', content)
        self.assertIn('remember: true, silent: true', content)
        self.assertIn('remember: true, silent: true', generated_content)
        self.assertNotIn('remember: false, silent: true', content)
        self.assertNotIn(
            'remember: false, silent: true',
            generated_content,
        )
        self.assertIn(
            'await window.PortfolioAuthPersistence\n'
            '                            .rememberCredential(input);',
            content,
        )
        self.assertIn('Deconectare de pe acest dispozitiv', content)
        self.assertIn(
            'Deconectare de pe acest dispozitiv',
            generated_content,
        )
        self.assertIn(
            'Accesul rămâne activ 30 de zile de la ultima autentificare '
            'manuală sau automată în acest browser.',
            content,
        )
        self.assertIn(
            'Accesul rămâne activ 30 de zile de la ultima autentificare '
            'manuală sau automată în acest browser.',
            generated_content,
        )
        self.assertNotIn("sessionStorage.setItem('pf_auth'", content)
        self.assertIn(
            'const SESSION_TTL_MS = 30 * 24 * 60 * 60 * 1000;',
            auth_content,
        )
        self.assertIn("const DB_NAME = 'market-scanner-portfolio-auth';", auth_content)
        self.assertIn("{ name: 'AES-GCM', length: 256 }", auth_content)
        self.assertIn('false,', auth_content)
        self.assertIn('lastAuthenticatedAt: now', auth_content)
        self.assertIn('expiresAt: now + SESSION_TTL_MS', auth_content)
        self.assertIn('session.expiresAt <= Date.now()', auth_content)
        self.assertIn('additionalData: additionalData()', auth_content)
        self.assertNotIn('localStorage', auth_content)
        self.assertNotIn('sessionStorage', auth_content)

    def test_empty_order_tables_do_not_trigger_datatables_column_warning(self):
        """Rândurile cu colspan pentru liste goale nu trebuie trimise către DataTables."""
        file_path = os.path.join(os.path.dirname(__file__), '..', 'market_scanner.py')
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn("const initPortfolioDataTable = function(selector)", content)
        self.assertIn("row.querySelector('[colspan], [rowspan]')", content)
        self.assertIn("row.children.length !== columnCount", content)
        self.assertIn("if (hasUnsupportedRow) return", content)
        self.assertIn("initPortfolioDataTable('#buying-orders-table')", content)
        self.assertIn("initPortfolioDataTable('#selling-orders-table')", content)

    def test_buy_orders_are_last_and_followed_by_market_recommendations(self):
        file_path = os.path.join(os.path.dirname(__file__), '..', 'market_scanner.py')
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        analysis_path = os.path.join(
            os.path.dirname(__file__), '..', 'market_scanner_analysis.py'
        )
        with open(analysis_path, 'r', encoding='utf-8') as f:
            analysis_content = f.read()
        index_path = os.path.join(
            os.path.dirname(__file__), '..', 'index.html'
        )
        with open(index_path, 'r', encoding='utf-8') as f:
            generated_content = f.read()

        self.assertNotIn(
            'Auto-generated by Antigravity Market Scanner', content
        )
        self.assertNotIn(
            'Auto-generated by Antigravity Market Scanner',
            analysis_content,
        )
        self.assertNotIn(
            'Auto-generated by Antigravity Market Scanner',
            generated_content,
        )
        sell_title = 'Ordine Active de Vânzare (IBKR / Tradeville)'
        buy_title = 'Ordine Active de Cumpărare (IBKR / Tradeville)'
        recommendation_container = 'id="buy-recommendations-container"'
        self.assertLess(content.index(sell_title), content.index(buy_title))
        self.assertLess(content.index(buy_title), content.index(recommendation_container))
        self.assertIn("consensus in {'buy', 'strong buy'}", content)
        self.assertIn("float(item.get('RR_Ratio') or 0) >= 3", content)
        self.assertIn('EXTERNAL_RESEARCH_MIN_RR = 1.8', content)
        self.assertIn('BUY_FINALIST_TTL_HOURS = 1.0', content)
        self.assertIn('Apartenența la watchlist nu mai blochează cercetarea', content)
        self.assertIn("'TLV.RO', 'SNP.RO', 'SNG.RO', 'H2O.RO'", content)
        self.assertIn("'entry_eur': _buy_candidate_entry_eur(item)", content)
        self.assertIn('_buy_candidate_execution_values(', content)
        self.assertIn("'execution_currency': currency", content)
        self.assertIn("'entry_native': to_native(_buy_candidate_entry_eur(item))", content)
        self.assertIn("'decision': item.get('Decision')", content)
        self.assertIn("'data_fresh': bool(", content)
        self.assertIn("'external_min_rr': item.get('External_Min_RR')", content)
        self.assertIn('render_buy_recommendations_html(', analysis_content)
        self.assertIn('BUY + consensus Buy/Strong Buy + R:R ≥ 3', analysis_content)
        self.assertIn('nu afirma că lipsesc semnalul BUY sau nivelul de intrare', analysis_content)
        self.assertIn('Scannerul confirmă BUY, consensus', analysis_content)
        self.assertIn('external_min_rr (în prezent 1,8)', analysis_content)
        self.assertIn('nu inventa un consens', analysis_content)
        self.assertIn('Acțiunile SUA se discută în USD, cele BVB în RON', analysis_content)
        self.assertIn('Moneda ordinului:', analysis_content)
        self.assertIn('📈 Grafic mare OHLC', analysis_content)
        self.assertIn(
            'openBuyRecommendationDetail(this.dataset.symbol)',
            analysis_content,
        )
        self.assertIn('_format_execution_money(', analysis_content)
        self.assertIn('<b>Validarea nivelurilor:</b>', analysis_content)
        self.assertIn('universul local este cercetat separat de watchlist', analysis_content)
        self.assertIn('sumă orientativă pentru cumpărare acum', analysis_content)
        self.assertIn('buget pentru ordin condiționat la trigger', analysis_content)
        self.assertIn("['IBKR', 'Tradeville']", content)
        self.assertIn('sizing_by_broker', analysis_content)
        self.assertIn('update_buy_recommendation_history(', content)
        self.assertIn(
            'update_buy_recommendation_history_from_cache(', content
        )
        self.assertIn('Istoric recomandări executabile', analysis_content)
        self.assertIn(
            'const BUY_RECOMMENDATION_HISTORY_DISPLAY_LIMIT = 50;',
            content,
        )
        self.assertIn(
            'function limitBuyRecommendationHistoryDisplay(container)',
            content,
        )
        self.assertIn(
            'limitBuyRecommendationHistoryDisplay(buyRecommendations)',
            content,
        )
        self.assertIn(
            'const BUY_RECOMMENDATION_HISTORY_DISPLAY_LIMIT = 50;',
            generated_content,
        )
        self.assertIn('📈 Grafic OHLC · marcaj', analysis_content)
        self.assertIn('_buy_recommendation_marker_labels(', analysis_content)
        self.assertIn('_size_buy_candidates(', analysis_content)
        self.assertIn("economic_calendar și piața poziției", analysis_content)
        self.assertIn("<b>Calendar:</b>", analysis_content)
        self.assertIn("'economic_calendar': snapshot.get('economic_calendar', [])", analysis_content)

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
        self.assertIn("_chart_detail_native_payload(", content)
        self.assertIn("'currency': native_detail['currency']", content)
        self.assertIn("'Smart_Entry_EUR': round(s_entry * rate, 2)", content)
        self.assertIn("row.get('Decision') == 'BUY'", content)
        self.assertIn("'label': f'Entry recomandat · {entry_type}'", content)
        self.assertIn("and spark_data[-2] != 0", content)

if __name__ == '__main__':
    unittest.main()
