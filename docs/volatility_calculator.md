# Volatilitate și trailing stop

Calculatorul folosește ATR Finviz când este disponibil. Dacă lipsește, folosește
`ATR_Native`, calculat din istoricul de prețuri la scanare. Pentru snapshoturile
mai vechi, recuperează `ATR_14` sau media ultimelor 14 true ranges din 15 bare
`Chart_OHLC`. Aceste două câmpuri vechi sunt în EUR și sunt convertite în moneda
instrumentului folosind raportul dintre prețul nativ și prețul EUR.

ATR și prețul utilizat pentru procent trebuie să fie în aceeași monedă.
Valorile lipsă, negative, `NaN` sau infinite nu sunt indicatori utilizabili.
Istoricul insuficient este afișat ca „Indisponibil”, nu ca volatilitate zero.

Volatilitatea săptămânală/lunară Finviz nu este inventată când lipsește.
Calculatorul afișează sursa ATR și folosește numai indicatorii disponibili:

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
