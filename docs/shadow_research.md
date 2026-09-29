# Cercetare shadow separată de actualizarea dashboardului

Actualizările `portfolio`, `all`, `international` și workflow-ul dashboardului
colectează în continuare snapshoturi. Nu pornesc evaluările forward și nu așteaptă
cercetarea înainte de sincronizare/publicare, inclusiv la reunirea ledgerelor Git.

## Pornire manuală

Din directorul proiectului:

```bash
bash run_shadow_research.sh --only technical
bash run_shadow_research.sh --only enhanced
```

Fără `--only`, sunt verificate ambele evaluări. Cadența existentă rămâne: Technical
Events la 168 de ore, Enhanced la 24 de ore, raportat la ultima reușită. Acesta
este un filtru la pornirea manuală, **nu un programator instalat în fundal**.

```bash
# Ignoră cadența; Technical Events reîmprospătează și prețurile.
bash run_shadow_research.sh --only technical --force

# Buget de 10 minute în locul valorii implicite de 60 minute per evaluare.
bash run_shadow_research.sh --only technical --timeout-seconds 600
```

Limita implicită este 3600 secunde **per evaluare** (ambele pot însuma 120 minute).
La expirare, noul proces și descendenții săi sunt opriți; există maximum 5 secunde
de grație înainte de oprirea forțată. Timeout-ul nu este marcat drept succes.
O pornire în timpul unei alte mentenanțe iese imediat fără s-o întrerupă.
După o rulare online reușită, wrapperul face commit/push doar pentru rapoartele
cercetării și pornește `update_dashboard.yml` în modul `portfolio`. Necesită
ramura `main` și `gh` autentificat. Nu include modificările locale ale
portofoliului, dataseturile private sau cache-ul și nu face pull/push runtime R2.
Modificările deja staged blochează sincronizarea pentru a evita includerea lor.
La timeout, eroare, lock ocupat, cadență neîmplinită sau rulare `--offline`, nu
sincronizează. Dacă rapoartele nu s-au schimbat, nu pornește nici workflow-ul.
Erorile Git/workflow sunt raportate; rezultatele rămân local.
Utilizează ledgerul local și citirea R2 existentă, cu credentialele încărcate
prin mecanismul proiectului.

## Checkpointuri și corectitudine

- `.shadow_research_cache/` este privat și ignorat de Git. Conține SQLite cu
  JSON comprimat și checksum; nu conține pickle sau cod executabil.
- Obiectele istorice R2, imuabile prin contractul ledgerului, sunt descărcate o
  singură dată. Lista remote este recitită, astfel încât obiectele noi/deleted
  sunt reflectate; namespace-ul include endpointul și bucketul.
- Technical Events salvează istoricele prețurilor pe intervale orare și rezultate
  pentru combinații unice simbol/zi/preț de intrare. Observațiile repetate nu sunt
  eliminate din statistici. Cache-ul orar poate întârzia o corecție a furnizorului
  cu până la o oră; `--force` ocolește cache-ul de prețuri.
- Ferestrele mature se reutilizează numai dacă datele folosite de formulă sunt
  identice. Schimbarea intrării, istoricului/spliturilor sau maturizarea unei noi
  ferestre invalidează rezultatul relevant. Lipsa istoricului este reîncercată.
- Checkpointurile sunt confirmate în loturi mici și la final de simbol/snapshot.
  O oprire forțată poate pierde lotul curent, nu progresul confirmat anterior.
- Starea cadenței se păstrează local în
  `.shadow_research_cache/maintenance-state.json`; vechiul fișier sincronizat R2
  este folosit doar la migrarea inițială.

La reluare se repetă încă citirea/validarea ledgerului, construirea observațiilor
și agregarea/exportul rapoartelor. Nu este reluare de la instrucțiunea exactă și
nu garantează finalizarea întregului istoric în prima fereastră de 60 minute.
Enhanced reutilizează snapshoturile R2, dar calculul său de rezultate forward
nu este încă incremental. Formulele și deciziile de tranzacționare nu se schimbă.

## Rapoarte și rulări existente

Ambele evaluări pregătesc rezultatele într-un director temporar privat. Dacă
pregătirea este întreruptă, rapoartele finalizate anterior rămân. După succes,
fișierele sunt înlocuite individual atomic, iar markerul de finalizare este
ultimul. Publicarea întregului set nu este o tranzacție multi-fișier.

`--offline` scrie diagnostice separate în subdirectorul `offline/`, fără să
înlocuiască rapoartele online sau să avanseze cadența acestora.

Aceste schimbări se aplică **pornirilor noi**. Procesul vechi deja pornit nu
primește retroactiv timeout/checkpointuri și nu este oprit de implementare.

Verificare: `python -m pytest tests/test_shadow_maintenance.py
tests/test_shadow_update_separation.py tests/test_shadow_research_cache.py
tests/test_shadow_parquet_store.py tests/test_technical_events_validation.py
--no-cov -p no:cacheprovider` (pe o singură linie).
