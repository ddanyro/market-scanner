
import json
import random
import datetime
import os

hist_file = "market_history.json"
today = datetime.datetime.now()

if os.path.exists(hist_file):
    with open(hist_file, 'r') as f:
        try:
            db = json.load(f)
        except:
            db = {}
else:
    db = {}

if 'PCR' not in db:
    db['PCR'] = {}

# Preluăm valoarea de azi (sau folosim 1.08 ca ancoră dacă lipsește)
today_str = today.strftime('%Y-%m-%d')
current_val = db['PCR'].get(today_str, 1.08)

# Ne asigurăm că valoarea de azi există
db['PCR'][today_str] = current_val

print(f"Seeding PCR history starting from current value: {current_val}")

# Generăm date înapoi pentru 60 de zile
val = current_val
for i in range(1, 65):
    # Skip weekends for realism? 
    # PCR exist usually trading days, but keeping it simple implies continous line.
    # Let's skip weekends to match market data better.
    d_obj = today - datetime.timedelta(days=i)
    if d_obj.weekday() >= 5: # Sat/Sun
        continue
        
    date_str = d_obj.strftime('%Y-%m-%d')
    
    if date_str not in db['PCR']:
        # Random movement simulation (mean reversion tendency to 0.9)
        # Change is random but pulled slightly towards 0.9 mean
        mean_rev_force = (0.9 - val) * 0.1
        noise = random.uniform(-0.06, 0.06)
        change = noise + mean_rev_force
        
        # In reverse walk: prev_val = current - change
        # So val (historical) = val (current) - change
        val = val - change
        
        # Clamp values to realistic PCR range (0.5 - 1.5)
        val = max(0.6, min(1.4, val))
        
        db['PCR'][date_str] = round(val, 2)

# Salvare
with open(hist_file, 'w') as f:
    json.dump(db, f, indent=4)

print(f"Successfully seeded PCR history for {len(db['PCR'])} days.")
