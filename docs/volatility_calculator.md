# Volatilitate și trailing stop

Calculatorul folosește ATR Finviz când este disponibil. Dacă lipsește, folosește
`ATR_Native`, calculat din istoricul de prețuri la scanare. Pentru snapshoturile
mai vechi, recuperează `ATR_14` sau media ultimelor 14 true ranges din 15 bare
`Chart_OHLC`. Aceste două câmpuri vechi sunt în EUR și sunt convertite în moneda
instrumentului folosind raportul dintre prețul nativ și prețul EUR.

ATR și prețul utilizat pentru procent trebuie să fie în aceeași monedă.
Valorile lipsă, negative, `NaN` sau infinite nu sunt indicatori utilizabili.
Istoricul insuficient este afișat ca „Indisponibil”, nu ca volatilitate zero.

## Alternativa fără Finviz

Folosim `Chart_OHLC`, deja descărcat de scanner (Yahoo Finance, IBKR sau
sursa BVB indicată de `Market_Data_Source`). Nu sunt necesare Elite, browser,
chei API noi sau cereri suplimentare. Calculul este identic local și în GitHub
Actions și funcționează inclusiv la regenerarea HTML din snapshot.

- Zi: amplitudinea ultimei bare, `(High - Low) / Low × 100`.
- Săptămână: media amplitudinilor ultimelor **5 ședințe**.
- Lună: media amplitudinilor ultimelor **21 de ședințe**.

Aceste valori descriu amplitudinea zilnică medie, nu randamentul perioadei,
deviația standard sau volatilitatea anualizată. Nu pretind reproducerea exactă
a metodologiei Finviz. Raportul este independent de moneda OHLC.
Se afișează data ultimei bare; în timpul ședinței aceasta poate fi incompletă.
Un snapshot vechi produce valori istorice cu data sa, nu valori live.

Finviz rămâne prioritar pentru ATR și mediile săptămânală/lunară valide ale
instrumentelor SUA; fiecare metrică lipsă folosește separat alternativa.
Pentru monede explicit diferite de USD nu folosim indicatorii Finviz, pentru a
evita asocierea unui simbol străin cu o listare SUA omonimă. Ziua este calculată
din OHLC. Sursele fiecărei valori sunt afișate separat, ca `Calculat OHLC` și
furnizorul istoricului, fără a le prezenta ca date Finviz.

O fereastră incompletă sau cu High/Low invalide rămâne indisponibilă: nu sărim
peste o bară invalidă prezentă în snapshot ca să completăm cele 5/21 de ședințe.
Numărăm barele disponibile în `Chart_OHLC`; sesiuni omise deja de furnizor sau
de colector nu pot fi reconstruite aici. Close nu intră în formula amplitudinii.
Datele duplicate
sau neordonate invalidează calculul. O amplitudine măsurată de zero este afișată
ca `0.00%`, distinct de lipsa datelor.

Calculatorul folosește ATR%, săptămâna și luna pentru trailing stop (nu adaugă
ziua ca al patrulea indicator) și numai indicatorii disponibili, pozitivi:

- Larg: maximul indicatorilor × 3.
- Mediu: media indicatorilor × 2.
- Strâns: minimul indicatorilor × 1,5.

Cu ATR drept singurul indicator, multiplicatorii se aplică procentului ATR.
Schimbarea simbolului golește rezultatele precedente, inclusiv când noul simbol
nu are date suficiente. Calculele nu trimit și nu modifică ordine la broker.

Răspunsurile HTTP nereușite Finviz și paginile fără indicatori recunoscuți produc
avertismente explicite în log. Rezultatul gol este reutilizat numai în cache-ul
procesului curent, pentru a nu repeta cererile blocate. Următoarea rulare poate
încerca din nou; nu se ocolește protecția anti-bot.
