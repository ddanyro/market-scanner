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

if __name__ == '__main__':
    unittest.main()
