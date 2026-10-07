# Cozile de actualizare și publicare

`update_dashboard.yml:build` și `update_ro.yml:update-ro` folosesc aceeași
blocare de job, `market-dashboard-writes`. Ea protejează citirea/modificarea/
salvarea snapshoturilor R2 și commiturile Git. Nu se anulează un writer activ;
`queue: max` păstrează până la 100 de joburi în așteptare, inclusiv BVB.
Checkout-ul citește `main` după obținerea blocării, nu un snapshot vechi din
momentul declanșării. Joburile active au o limită de 120 de minute.

`deploy-pages` are blocarea separată `market-dashboard-pages`. Dacă mediul
`github-pages` așteaptă, scanările și actualizările R2 pot continua. Nu se
întrerupe o publicare activă; dintre candidații în așteptare rămâne cel mai
recent. Protecțiile mediului nu sunt eliminate sau aprobate automat.

Înaintea publicării comparăm commitul artefactului (capturat după commitul
scannerului) cu `main`. Artefactele depășite sunt omise, iar o eroare API oprește
jobul fără publicare. Dacă main avansează după verificare, publicările rămân
serializate: succesorul nu poate fi suprascris de deploymentul deja activ.

Un push cu `GITHUB_TOKEN` nu declanșează alt workflow `on: push`. De aceea,
workflow-ul BVB solicită explicit `update_dashboard.yml` cu `publish_only=true`.
Acest mod nu instalează Python, nu rulează scannerul, nu retrimite alerte și
nu scrie R2; construiește/publică numai Pages din main. Permisiunea `actions:
write` a jobului BVB permite acest dispatch, fără credențiale personale noi.

Limita Pages de 15 minute se aplică jobului pornit, **nu** timpului petrecut
în așteptarea mediului. Un asemenea blocaj poate necesita anularea/reluarea
deploymentului, dar nu mai reține blocarea datelor de piață. La remedierea
unui blocaj existent trebuie încheiată rularea veche: schimbarea YAML nu
modifică workflow-urile care au fost deja pornite.
