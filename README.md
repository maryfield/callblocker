# Call Blocker

Sistema di blocco chiamate telefoniche indesiderate su linee PSTN analogiche tramite modem USB.

## Descrizione

Call Blocker è un demone headless in Python che monitora le chiamate in arrivo su linee telefoniche analogiche PSTN attraverso un modem USB. Il sistema blocca automaticamente le chiamate provenienti da numeri presenti in una blacklist dinamica e registra tutte le chiamate in un database SQLite.

### Caratteristiche

- 🚫 **Blocco automatico** di chiamate indesiderate
- 📋 **Blacklist dinamica** gestibile tramite CLI
- 📊 **Logging SQLite** di tutte le chiamate
- 🔧 **CLI tool** per gestione e monitoraggio
- 🐧 **Ottimizzato per Ubuntu Linux**
- 📞 **Supporto Caller ID** (se disponibile sul modem)
- 🔄 **Demone headless** eseguibile come servizio systemd

## Requisiti

### Hardware
- Modem USB compatibile con comandi AT (es. modem V.92)
- Linea telefonica PSTN analogica
- Computer con porta USB (testato su Ubuntu Linux)

### Software
- Python 3.8 o superiore
- Ubuntu Linux (o altra distribuzione Linux compatibile)
- Accesso root per installazione come servizio

## Installazione

### 1. Clonare il repository

```bash
git clone https://github.com/maryfield/callblocker.git
cd callblocker
```

### 2. Installare le dipendenze

```bash
pip install -r requirements.txt
```

oppure installare il pacchetto:

```bash
sudo pip install .
```

### 3. Configurare il modem

Identificare la porta del modem USB (solitamente `/dev/ttyUSB0` o `/dev/ttyACM0`):

```bash
ls -l /dev/ttyUSB*
```

### 4. Creare utente e directory (opzionale, per servizio systemd)

```bash
sudo useradd -r -s /bin/false callblocker
sudo usermod -a -G dialout callblocker
sudo mkdir -p /var/lib/callblocker
sudo mkdir -p /var/log/callblocker
sudo chown callblocker:callblocker /var/lib/callblocker
sudo chown callblocker:callblocker /var/log/callblocker
```

### 5. Installare come servizio systemd (opzionale)

```bash
sudo cp callblocker.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable callblocker
sudo systemctl start callblocker
```

## Utilizzo

### Gestione Blacklist

#### Aggiungere un numero alla blacklist

```bash
callblocker-cli add 1234567890 --description "Spam telefonico"
```

#### Rimuovere un numero dalla blacklist

```bash
callblocker-cli remove 1234567890
```

#### Elencare tutti i numeri bloccati

```bash
callblocker-cli list
```

#### Verificare se un numero è bloccato

```bash
callblocker-cli check 1234567890
```

### Visualizzazione Log

#### Visualizzare gli ultimi 20 log

```bash
callblocker-cli logs
```

#### Visualizzare più log

```bash
callblocker-cli logs --limit 50
```

#### Visualizzare solo chiamate bloccate

```bash
callblocker-cli logs --blocked
```

### Statistiche

```bash
callblocker-cli stats
```

### Avviare il demone manualmente

```bash
callblockerd --port /dev/ttyUSB0
```

Con debug abilitato:

```bash
callblockerd --port /dev/ttyUSB0 --debug
```

### Gestione servizio systemd

```bash
# Avviare il servizio
sudo systemctl start callblocker

# Fermare il servizio
sudo systemctl stop callblocker

# Riavviare il servizio
sudo systemctl restart callblocker

# Verificare stato
sudo systemctl status callblocker

# Visualizzare log
sudo journalctl -u callblocker -f
```

## Configurazione

### Porta del modem

Per configurare una porta diversa, modificare il file del servizio o usare l'opzione `--port`:

```bash
callblockerd --port /dev/ttyACM0
```

### Database

Il database SQLite viene creato automaticamente in `/var/lib/callblocker/callblocker.db`.

Per usare un percorso diverso:

```bash
callblockerd --db /path/to/database.db
callblocker-cli --db /path/to/database.db list
```

### Struttura Database

Il database contiene due tabelle:

#### blacklist
- `id`: ID univoco
- `phone_number`: Numero di telefono (univoco)
- `description`: Descrizione opzionale
- `added_date`: Data di aggiunta

#### call_logs
- `id`: ID univoco
- `phone_number`: Numero chiamante
- `call_date`: Data e ora della chiamata
- `blocked`: Flag booleano (chiamata bloccata?)
- `caller_id`: Nome chiamante (se disponibile)

## Funzionamento

1. Il demone si connette al modem USB tramite porta seriale
2. Invia comandi AT per configurare il modem e abilitare il Caller ID
3. Rimane in ascolto per chiamate in arrivo (segnale RING)
4. Quando arriva una chiamata:
   - Estrae il numero chiamante dai dati del modem
   - Verifica se il numero è nella blacklist
   - Se bloccato: risponde e riaggancia immediatamente
   - Se permesso: lascia squillare normalmente
5. Registra tutte le chiamate nel database SQLite

## Risoluzione Problemi

### Il modem non viene rilevato

```bash
# Verificare connessione USB
lsusb

# Verificare porte seriali disponibili
ls -l /dev/ttyUSB* /dev/ttyACM*

# Verificare permessi
sudo usermod -a -G dialout $USER
```

### Errori di connessione al modem

- Verificare che il modem supporti comandi AT
- Provare velocità di connessione diverse (9600, 19200, 38400, 115200)
- Controllare i log: `sudo journalctl -u callblocker -f`

### Il Caller ID non funziona

Il Caller ID richiede:
- Supporto del modem (comando AT+VCID=1 o AT+CLIP=1)
- Servizio attivo sulla linea telefonica
- Alcuni modem potrebbero non supportare questa funzionalità

### Permessi database

```bash
sudo chown callblocker:callblocker /var/lib/callblocker/callblocker.db
sudo chmod 644 /var/lib/callblocker/callblocker.db
```

## Test

Per testare il sistema senza hardware:

```bash
# Testare la CLI
callblocker-cli --db /tmp/test.db add 1234567890
callblocker-cli --db /tmp/test.db list
callblocker-cli --db /tmp/test.db check 1234567890
```

## Licenza

MIT License - vedere il file [LICENSE](LICENSE) per dettagli.

## Autore

maryfield - https://github.com/maryfield

## Contributi

Contributi, issues e richieste di funzionalità sono benvenute!

## Note di Sicurezza

- Il sistema deve avere accesso alla porta seriale del modem
- I log potrebbero contenere numeri di telefono sensibili
- Configurare appropriati permessi per il database e i log
- Non esporre il database pubblicamente

## Disclaimer

Questo software è fornito "così com'è" senza garanzie. Verificare le leggi locali relative al blocco chiamate e alla privacy prima dell'uso.
