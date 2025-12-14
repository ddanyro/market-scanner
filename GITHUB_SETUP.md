# Cum să configurezi actualizarea automată pe GitHub

Pentru ca Market Scanner să se actualizeze singur în fiecare oră (inclusiv AI și IBKR), trebuie să adaugi cheile secrete în setările proiectului pe GitHub.

### Pasul 1: Deschide Setările
1. Mergi la pagina proiectului tău pe GitHub: https://github.com/ddanyro/market-scanner
2. Click pe tab-ul **Settings** (sus dreapta).

### Pasul 2: Accesează Secretele
1. În meniul din stânga, dă click pe **Secrets and variables**.
2. Selectează **Actions**.

### Pasul 3: Adaugă Cheile
Apasă pe butonul verde **New repository secret** și adaugă următoarele 3 secrete (numele trebuie să fie exact):

1. **Nume:** `GOOGLE_API_KEY`
   **Valoare:** Cheia ta Gemini (`AIzaSyBVcvEkLS9CqPDlJIEpmz4Mr4yblfodC34`)

2. **Nume:** `IBKR_TOKEN`
   **Valoare:** Token-ul lung generat din IBKR Portal (dacă îl ai).

3. **Nume:** `IBKR_QUERY_ID`
   **Valoare:** ID-ul scurt al raportului Flex (ex: `1349493` sau similar).

### Gata!
După ce le adaugi, GitHub va avea acces la ele și va putea rula scriptul automat la fiecare oră, generând analiza AI și portofoliul actualizat.
