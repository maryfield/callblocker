# Esempi di Utilizzo di Call Blocker

## Scenario 1: Primo avvio e configurazione base

```bash
# 1. Installare il sistema
sudo ./install.sh

# 2. Aggiungere alcuni numeri alla blacklist
callblocker-cli add 0123456789 --description "Telemarketing XYZ"
callblocker-cli add 9876543210 --description "Spam"
callblocker-cli add 5555555555 --description "Numero sospetto"

# 3. Verificare la blacklist
callblocker-cli list

# 4. Avviare il servizio
sudo systemctl start callblocker

# 5. Monitorare i log in tempo reale
sudo journalctl -u callblocker -f
```

## Scenario 2: Gestione quotidiana

```bash
# Controllare se un numero è bloccato
callblocker-cli check 0123456789

# Vedere gli ultimi 50 log
callblocker-cli logs --limit 50

# Vedere solo le chiamate bloccate
callblocker-cli logs --blocked

# Vedere le statistiche
callblocker-cli stats

# Rimuovere un numero dalla blacklist (sbloccare)
callblocker-cli remove 0123456789
```

## Scenario 3: Avvio manuale per test

```bash
# Avviare il daemon manualmente con debug
callblockerd --port /dev/ttyUSB0 --debug

# In un altro terminale, monitorare cosa succede
# Quando arriva una chiamata, il daemon:
# - Rileva il numero
# - Verifica la blacklist
# - Blocca o permette la chiamata
# - Registra nel database
```

## Scenario 4: Importazione blacklist da file

```bash
# Creare un file con numeri da bloccare (uno per riga)
cat > blacklist.txt << EOF
0123456789 Telemarketing
9876543210 Spam call
5555555555 Numero sospetto
1111111111 Truffa
EOF

# Importare i numeri
while IFS=' ' read -r numero descrizione resto; do
    callblocker-cli add "$numero" --description "$descrizione $resto"
done < blacklist.txt

# Verificare
callblocker-cli list
```

## Scenario 5: Backup del database

```bash
# Fermare il servizio
sudo systemctl stop callblocker

# Fare backup
sudo cp /var/lib/callblocker/callblocker.db /backup/callblocker-$(date +%Y%m%d).db

# Riavviare il servizio
sudo systemctl start callblocker
```

## Scenario 6: Analisi delle chiamate ricevute

```bash
# Vedere tutte le chiamate dell'ultimo periodo
callblocker-cli logs --limit 100

# Vedere solo chiamate bloccate
callblocker-cli logs --blocked --limit 100

# Statistiche generali
callblocker-cli stats
```

## Scenario 7: Reset completo

```bash
# Fermare il servizio
sudo systemctl stop callblocker

# Eliminare il database (ATTENZIONE: perdi tutti i dati!)
sudo rm /var/lib/callblocker/callblocker.db

# Riavviare il servizio (verrà creato un nuovo database vuoto)
sudo systemctl start callblocker
```

## Scenario 8: Cambio porta del modem

```bash
# 1. Fermare il servizio
sudo systemctl stop callblocker

# 2. Modificare il file di servizio
sudo nano /etc/systemd/system/callblocker.service
# Cambiare --port /dev/ttyUSB0 con la porta corretta

# 3. Ricaricare systemd
sudo systemctl daemon-reload

# 4. Riavviare il servizio
sudo systemctl start callblocker
```

## Scenario 9: Debug problemi

```bash
# Vedere i log del servizio
sudo journalctl -u callblocker -n 100

# Vedere i log in tempo reale
sudo journalctl -u callblocker -f

# Verificare lo stato del servizio
sudo systemctl status callblocker

# Testare la connessione al modem manualmente
sudo screen /dev/ttyUSB0 115200
# Poi digitare: AT
# Dovrebbe rispondere: OK
# Per uscire: Ctrl+A poi K

# Verificare permessi
ls -l /dev/ttyUSB0
groups callblocker  # Dovrebbe includere 'dialout'
```

## Scenario 10: Uso con database personalizzato

```bash
# Creare una directory personale
mkdir -p ~/callblocker-data

# Usare un database personalizzato
callblockerd --port /dev/ttyUSB0 --db ~/callblocker-data/mydb.db

# Usare la CLI con lo stesso database
callblocker-cli --db ~/callblocker-data/mydb.db list
```
