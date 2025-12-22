
import re

file_path = 'market_scanner_analysis.py'

with open(file_path, 'r') as f:
    content = f.read()

# Noul cod care se va insera înainte de "return data" în get_swing_trading_data
history_logic = """
    # --- PCR HISTORY PERSISTENCE ---
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
            
            # Update today's value
            db['PCR'][today] = float(data['PCR_Value'])
            
            # Save
            with open(hist_file, 'w') as f:
                json.dump(db, f, indent=4)
                
            # Populate Chart from History
            # Get sorted dates
            dates = sorted(db['PCR'].keys())
            # Take last 60 points
            points = [db['PCR'][d] for d in dates[-60:]]
            
            # If we have enough history, use it. If singular, flatline it.
            if len(points) > 1:
                data['Chart_PCR'] = points
            else:
                # Keep existing flatline or create new one
                data['Chart_PCR'] = [data['PCR_Value']] * 60
                
        except Exception as e:
            print(f"Error saving PCR history: {e}")

    return data
"""

# Căutăm "return data" la sfârșitul funcției get_swing_trading_data
# E riscant cu replace simplu că poate apărea în mai multe locuri.
# Dar get_swing_trading_data e definita spre final.

# Voi înlocui `return data` din `get_swing_trading_data` cu noul bloc.
# Identificăm funcția prin semnătură.

pattern = r"(def get_swing_trading_data\(\):.*?)(return data)"
# Folosim re.DOTALL pentru a prinde tot body-ul, dar *lazy* pana la primul return data care incheie functia?
# Funcția include try/except blocuri care nu au return. Singurul return e la final.

# Totuși, regex pe blocuri mari de cod e periculos.
# Voi folosi un marker unic pe care știu că l-am pus: 
# "print(f\"Error Swing Data (PCR): {e}\")" este la sfârșitul blocului PCR, chiar înainte de return.

target_anchor = '        print(f"Error Swing Data (PCR): {e}")'
replacement = '        print(f"Error Swing Data (PCR): {e}")\n' + history_logic

if target_anchor in content:
    new_content = content.replace(target_anchor, replacement)
    # Dar trebuie să șterg și "return data" original care a rămas duplicat? 
    # Ah, history_logic conține "return data" la final.
    # Dar markerul meu e înauntrul unui `except` block, deci indentarea contează.
    # Și `return data` e în afara except-ului.
    
    # Mai bine: Folosesc append la sfârșitul fișierului, redefinind funcția complet? Nu, dă conflict.
    pass
else:
    print("Anchor not found!")

# Abordare simplificată:
# Redefinesc complet funcția `get_swing_trading_data` și o înlocuiesc pe cea veche.
# E cel mai curat.
