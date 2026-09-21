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
După trecerea la versiunea 1.3.4, reîncarcă și fila Tradeville pentru a elimina
bucla veche a extensiei. Joburile expirate sunt acum eliberate automat; un
răspuns întârziat al unui job vechi nu poate bloca sau înlocui jobul nou.
Mesajul „extensia a preluat jobul” confirmă numai legătura locală, nu loginul
Tradeville. Timeoutul precizează dacă jobul a fost preluat sau nu.

La fiecare rulare, `tradeville_bridge.py` ascultă temporar numai pe
`127.0.0.1:43129`. Extensia preia jobul, citește prin WebSocket ambele persoane
Tradeville și trimite înapoi datele de portofoliu, ordine, cont și istoricul
`graf_pers_brut`. Istoricul este filtrat automat de la prima dată NAV
disponibilă în IBKR și păstrează separat NAV, cash, NAV ajustat cu transferuri
și performanța rezultată.

În caz de browser închis sau sesiune expirată, fișierele existente nu sunt
șterse și `tradeville_sync_status.json` este marcat cu eroarea curentă.
Dacă endpointul istoric `graf_pers_brut` nu răspunde, pozițiile și ordinele
curente sunt sincronizate în continuare, iar bridge-ul reutilizează numai
ultimul istoric grafic valid din snapshotul local criptat.
