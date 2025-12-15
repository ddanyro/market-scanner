# Cum să activezi Ordinele (Stop Loss/Trail) în Market Scanner

Pentru ca scannerul să vadă ordinele tale active (ex: Trailing Stop) și să le afișeze în dashboard, trebuie să incluzi secțiunea **Orders** în raportul Flex din IBKR.

### Pasul 1: Mergi la Flex Queries
1. Loghează-te în **Interactive Brokers Portal**.
2. Mergi la **Performance & Reports** -> **Flex Queries**.
3. Găsește Query-ul pe care l-ai creat pentru acest proiect și apasă pe iconița de **Edit** (creion).

### Pasul 2: Adaugă Secțiunea "Orders"
1. În lista de secțiuni (unde ai selectat deja "Open Positions"), apasă pe **Orders** (în partea de jos, la "Select Sections").
2. Se va deschide o fereastră de configurare pentru Ordine.

### Pasul 3: Configurează coloanele
Asigură-te că selectezi următoarele opțiuni:
- **Orders to Include:** `Active Orders` (foarte important, să nu luăm doar cele executate).
- **Selectați toate coloanele** sau cel puțin:
  - `Symbol`
  - `Order Type`
  - `Aux Price`
  - `Stop Price` (Trig Price)
  - `Trailing Percent`
  - `Total Quantity`

### Pasul 4: Salvează
1. Apasă **Save** la fereastra Orders.
2. Apasă **Save Changes** la tot Query-ul.

### Gata!
La următoarea rulare (automată sau manuală), scriptul va primi XML-ul care conține și `<Order>`. 
Codul meu este deja pregătit să citească `stopPrice` și `trailingPercent` din aceste etichete și să le afișeze în coloana "Stop Loss" din Dashboard.
