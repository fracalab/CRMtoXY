# 📄 CRM Transaction Parser

Questo progetto contiene uno script Python per convertire file CSV esportati da CRM in un formato standardizzato, utile per integrazione XY.

---

## 📆 Cosa fa questo script?

- Legge un file `fileinput.csv` esportato da un CRM
- Estrae e trasforma i dati secondo specifiche aziendali
- Genera un file `Result.csv` con:
  - `orderId` ripulito dalla posizione
  - `lineNumber` calcolato
  - `itemId` pulito da eventuali `.0`
  - `itemSKU` e `barcode` da `itemInstanceId`

---

## 🛠️ Come usare questo progetto

### 1. Opzione A: Eseguire da Python (consigliato per utenti tecnici)

#### a) Installa Python

Scarica Python da:
https://www.python.org/downloads/

Assicurati di selezionare la casella **"Add Python to PATH"** durante l'installazione.

Verifica:
```bash
python --version
```

#### b) Clona o scarica questo progetto

```bash
git clone https://github.com/tuo-utente/tuo-repo.git
cd tuo-repo
```

#### c) Installa le librerie necessarie

```bash
pip install -r requirements.txt
```

#### d) Esegui lo script

```bash
python crmtoxy.py
```

---

### 2. Opzione B: Generare un eseguibile (.exe) per Windows

Se vuoi distribuire il programma senza dover installare Python:

#### a) Installa PyInstaller
```bash
pip install pyinstaller
```

#### b) Genera l'eseguibile
```bash
pyinstaller --onefile --name converti_crm crmtoxy.py
```

L'eseguibile si troverà in:
```
dist/converti_crm.exe
```

#### c) Esegui il file su qualsiasi PC Windows

Basta fare doppio clic oppure:
```bash
converti_crm.exe
```

---

## 🧪 Esempio di input/output

Input `fileinput.csv`:
```
BOUTIQUE_CODE;TRANSACTION_DATE;RECEIPT_CODE;POSITION;...;PRODUCT_CODE;QTY;...
B001;20240330;1234567890;1;...;20072392;1;...
```

Output `Result.csv`:
```
storeId;orderDate;orderId;lineNumber;...;itemId;...;itemSKU;...
B001;1711770000;RPB0011234567890;1;...;20072392;...;20072392;...
```

---

## 📌 Note tecniche

- `orderId` viene convertito da notazione scientifica ed esclusa la posizione
- `lineNumber` è estratto dalla colonna POSITION
- `itemId` viene trattato come stringa per evitare problemi con `.0`
- `itemSKU` e `barcode` sono derivati dall'`itemInstanceId`

---

## 📢 Contatti

Per suggerimenti o segnalazioni, crea una issue nel repository oppure contattami direttamente.

---

🛠 Creato da Francesco Calabrese
