# Market Scanner Tradeville Bridge

Extensie Chrome read-only care folosește sesiunea deja autentificată din
`portal.tradeville.ro` și livrează local snapshoturi pentru Market Scanner.
Nu conține comenzi de creare, modificare sau anulare a ordinelor.

## Instalare (o singură dată)

1. Deschide `chrome://extensions`.
2. Activează **Developer mode**.
3. Apasă **Load unpacked** și selectează directorul `tradeville_bridge`.
4. Deschide și autentifică `https://portal.tradeville.ro/portal/app/portfolio`.
5. Păstrează cel puțin o filă Tradeville deschisă când rulezi
   `./update_portfolio.sh`.

După instalare sau după modificarea extensiei, apasă **Reload** pe cardul ei.
Insigna extensiei devine `ON` când bridge-ul este activ în fila Tradeville.

La fiecare rulare, `tradeville_bridge.py` ascultă temporar numai pe
`127.0.0.1:43129`. Extensia preia jobul, citește prin WebSocket ambele persoane
Tradeville și trimite înapoi numai datele de portofoliu, ordine și cont.

În caz de browser închis sau sesiune expirată, fișierele existente nu sunt
șterse și `tradeville_sync_status.json` este marcat cu eroarea curentă.
