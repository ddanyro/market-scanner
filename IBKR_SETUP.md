# Configurare Sincronizare Automată Interactive Brokers (Flex Service)

Această metodă permite preluarea portofoliului direct din serverele IBKR (Cloud), similar cu modul în care funcționează agregatoarele financiare (ex: Yahoo Finance), fără a necesita aplicația TWS deschisă.

## 🟢 Pasul 1: Activare Flex Web Service
1. Loghează-te în **[Client Portal](https://www.interactivebrokers.com/sso/Login)** pe site-ul Interactive Brokers.
2. Mergi la **Settings** > **User Settings** (iconița omuleț dreapta-sus).
3. În secțiunea **Reporting**, caută opțiunea **Flex Web Service**.
4. Apasă pe rotița de configurare.
5. Bifează **Enable Flex Web Service**.
6. Se va genera un **Current Token** (un șir lung de caractere).
   - ⚠️ **Copiază-l și salvează-l!** (Nu îl vei mai putea vedea complet mai târziu).
   - Setează perioada de valabilitate la maxim (1 an).
7. Apasă **Save**.

### ⚠️ NU GĂSEȘTI MENIUL?
Interfața IBKR se schimbă frecvent. Încearcă această cale alternativă:
1. Mergi la meniul **Performance & Reports** > **Flex Queries**.
2. În pagina Flex Queries, uită-te în partea dreaptă, lângă titlu sau butoane, după o iconiță mică de **Rotiță (Configurare)** ⚙️.
3. Acolo ar trebui să fie setarea pentru "Flex Web Service".
4. Dacă tot nu apare, asigură-te că nu ești pe un cont "Lite" (care are acces limitat la API-uri avansate).

**Notă despre "Linked Accounts" (Yahoo Finance):**
Yahoo Finance folosește parteneriate bancare (agregatoare precum Yodlee) pentru a se conecta prin OAuth la contul tău. Această metodă este disponibilă doar instituțiilor financiare mari.
Pentru utilizatorii individuali și developeri, **Flex Web Service** este singura metodă oficială oferită de IBKR pentru a prelua datele automat fără software instalat.

## 🟢 Pasul 2: Creare Flex Query (Raportul de Poziții)
1. Din meniul principal, mergi la **Performance & Reports** > **Flex Queries**.
2. Apasă pe iconița **+** (Create a new Flex Query).
3. **Query Name**: Introdu `Portfolio_Sync`.
4. La secțiunea **Sections**, apasă pe **Open Positions**.
5. Se va deschide o fereastră cu coloane disponibile. Bifează **Select All** (pentru siguranță) sau asigură-te că ai minim:
   - `Symbol`
   - `Position` (Quantity)
   - `Mark Price`
   - `Cost Basis Price` (sau Avg Price)
   - `Unrealized P&L`
   - `Market Value`
6. Apasă **Save** la fereastra de coloane.
7. La opțiunile de jos (Delivery Configuration):
   - **Format**: `XML` (Foarte important! Nu CSV).
8. Apasă **Next / Create**.
9. După creare, vei vedea în listă noul query și un **Query ID** (un număr scurt, ex: `987654`). Notează-l.

## 🟢 Pasul 3: Configurare în Aplicație
1. Deschide folderul proiectului (`antigravity`).
2. Creează un fișier nou numit `ibkr_config.txt`.
3. Adaugă pe prima linie Token-ul și pe a doua Query ID-ul:
   ```text
   1234567890abcdef1234567890... (Token-ul tău lung)
   987654 (Query ID-ul tău)
   ```
4. Salvează fișierul.

## ✅ Testare
Rulează scriptul:
```bash
python3 market_scanner.py
```
Dacă totul e corect, vei vedea mesajul:
`=== Sincronizare IBKR (Flex Web Service) ===`
`Raport generat. Descărcat X poziții...`

### Notă pentru GitHub Actions (Automated Cloud Updates)
Dacă dorești ca actualizarea să meargă și automat pe GitHub (fără PC-ul tău pornit):
1. Mergi la Repository-ul tău pe GitHub > **Settings** > **Secrets and variables** > **Actions**.
2. Adaugă 2 secrete noi:
   - `IBKR_TOKEN`: (lipește token-ul lung)
   - `IBKR_QUERY_ID`: (lipește ID-ul numeric)
3. Scriptul va citi automat aceste valori când rulează în cloud.
