# Tradeville: stopuri condiționate și data deținerii

Extensia 1.4.0 citește, separat pentru fiecare persoană/cont:

- `ordineActive`: ordinele curente;
- `ordine` cu `prm.idord`: detaliile ordinelor condiționate;
- `activit` cu `prm.vlr`, `d1`, `d2`, `opt: "toate"`: activitatea executată în intervalul istoricului configurat.

Sunt doar interogări de citire, identice cu cele folosite de paginile Orders/Transactions ale portalului. Nu se adaugă comenzi pentru plasarea, modificarea sau anularea ordinelor.

Condiția este primul segment al `obs`, de exemplu `P<51.56; `. Prețul de execuție `pret=0` înseamnă execuție la piață și nu înlocuiește pragul condiției. Sunt acceptate ca stop-loss doar condițiile simple de preț/bid/ask în jos ale ordinelor SELL active. Condițiile de dată, de execuție a altui ordin, cele ascendente, suspendate, procesate, anulate sau neinterpretabile nu sunt prezentate drept protecție.

Asocierea folosește contul, simbolul și ID-ul ordinului. Cantitatea rămasă este pozitivă și ține cont de detaliile mai recente. Un stop apare pe poziție numai dacă un ordin confirmat acoperă întreaga cantitate. Ordinele parțiale rămân vizibile în lista de ordine. Dacă există mai multe ordine eligibile, se folosește pragul minim, conservator. Un stop fix nu inventează un procent de trailing.

`Entry_Date` reprezintă începutul deținerii curente neîntrerupte. Este reconstruită înapoi din cumpărări/vânzări executate, pornind de la cantitatea curentă, până la sold zero. Nu este data ordinului de vânzare sau a ultimei sincronizări. Istoricul insuficient, transferurile neinterpretate, datele invalide sau nereconcilierea cantității lasă data necunoscută. Datele vechi din `portfolio.csv` nu au prioritate peste snapshotul Tradeville.

Interogările suplimentare au bugete limitate (4 secunde pentru detalii și 4 pentru activitate, pe cont). Eșecul lor nu șterge pozițiile; lipsa datelor nu produce un stop sau o dată inventate. CLI și `tradeville_sync_status.json` raportează câte poziții au dată/stop și eventualele avertismente. Detaliile brute și activitatea se păstrează numai în snapshotul criptat.

După actualizarea extensiei: Reload în `chrome://extensions`, apoi reîncărcarea tuturor filelor Tradeville autentificate. Rularea normală `update_portfolio.sh` actualizează portofoliul și dashboardul. Pe GitHub sunt folosite snapshoturile deja sincronizate, fără browser local.

Protocol verificat pe 2026-10-08 atât în modulele publice ale portalului (`index.CuTWZtRV.js`, `Orders.D-uebNuU.js`, `Transactions.y3H6GrV6.js`), cât și cu două conturi reale. Testele nu conțin identificatori sau tranzacții private.
