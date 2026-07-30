# Sincronizare read-only prin Client Portal Web API

Aceasta este sursa preferată local pentru solduri, cash pe valute și istoricul
NAV PortfolioAnalyst. Nu expune funcții de plasare sau modificare a ordinelor.

## Cerințe

- cont IBKR Pro activ și finanțat;
- Java instalat;
- Client Portal Gateway descărcat de la IBKR;
- autentificare în browser cel puțin o dată după miezul nopții, conform
  limitărilor IBKR pentru conturile individuale.

## Pornire pe macOS

1. Dezarhivează Client Portal Gateway într-un director local.
2. Din directorul Gateway rulează:

   ```bash
   bin/run.sh root/conf.yaml
   ```

3. Deschide în browser `https://localhost:5000` și autentifică-te în IBKR.
4. Rulează normal:

   ```bash
   python3 market_scanner.py --mode portfolio
   ```

Scannerul verifică automat Gateway pe `https://localhost:5000/v1/api`. Dacă
sesiunea este validă, preia conturile, sumarul, ledgerul pe valute, pozițiile și
istoricul NAV de până la un an. Dacă Gateway nu este disponibil, păstrează
fallbackurile TWS, Flex și ultimul cache valid.

Configurare opțională:

- `IBKR_WEB_API_ENABLED=0` dezactivează încercarea locală;
- `IBKR_WEB_API_URL=https://localhost:5001/v1/api` schimbă portul/adresa locală.

Clientul refuză dezactivarea verificării TLS pentru adrese care nu sunt loopback.
Snapshotul exact este păstrat în fișierul criptat existent; varianta publică de
risc nu conține soldurile brute.

# Istoric automat prin Flex (compatibil cu iPhone)

Tokenul și Query ID-ul Flex deja configurate continuă să fie folosite de GitHub
Actions. Nu este necesar un token nou. Pentru ca același raport să furnizeze și
istoricul zilnic folosit de grafic, editează Activity Flex Query existent și
adaugă următoarele secțiuni/câmpuri:

- **Account Information**: Account ID și Base Currency;
- **Net Asset Value (NAV) Summary In Base**: Report Date, Cash și Total;
- **Change in NAV**: Starting Value și Ending Value;
- **Cash Report**: Currency, Ending Cash și Ending Settled Cash.

Păstrează formatul XML și selectează o perioadă de până la un an. Poți edita
query-ul existent și păstra același token. După salvare, verifică din iconița
**Info** că Query ID-ul a rămas cel configurat; dacă IBKR afișează alt ID,
actualizează numai secretul `IBKR_QUERY_ID`. Scannerul:

- importă punctele istorice NAV și cash deja prezente în raport;
- actualizează o singură observație pentru fiecare dată;
- păstrează până la 366 de observații în dashboard;
- nu reconstruiește NAV sau cash din poziții când câmpurile lipsesc.

Flex Activity este actualizat de IBKR după închiderea zilei, deci istoricul este
zilnic, nu intraday. Client Portal Web API rămâne un supliment local opțional.

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
