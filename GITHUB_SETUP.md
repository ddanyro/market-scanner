# Cum să configurezi actualizarea automată pe GitHub

Pentru ca Market Scanner să se actualizeze singur în fiecare oră (inclusiv AI și IBKR), trebuie să adaugi cheile secrete în setările proiectului pe GitHub.

### Pasul 1: Deschide Setările
1. Mergi la pagina proiectului tău pe GitHub: https://github.com/ddanyro/market-scanner
2. Click pe tab-ul **Settings** (sus dreapta).

### Pasul 2: Accesează Secretele
1. În meniul din stânga, dă click pe **Secrets and variables**.
2. Selectează **Actions**.

### Pasul 3: Adaugă Cheile
3. Apasă pe **New repository secret**.
4. Adaugă următoarele secrete (pe rând):

   - **Name**: `OPENAI_API_KEY`
     - **Value**: Cheia ta OpenAI (începe cu `sk-...`).
   
   - **Name**: `IBKR_TOKEN`
     - **Value**: Token-ul generat din IBKR Portal (pentru Flex Query).

   - **Name**: `IBKR_QUERY_ID`
     - **Value**: Query ID-ul raportului Flex.

   *(Opțional: `GOOGLE_API_KEY` nu mai este necesar dacă folosești OpenAI)* (ex: `1349493` sau similar).

### Gata!
După ce le adaugi, GitHub va avea acces la ele și va putea rula scriptul automat la fiecare oră, generând analiza AI și portofoliul actualizat.
