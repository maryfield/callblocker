# Quick Reference - Call Blocker

## Installazione Rapida

```bash
git clone https://github.com/maryfield/callblocker.git
cd callblocker
sudo ./install.sh
```

## Comandi Essenziali

### Gestione Blacklist

```bash
# Aggiungere numero
callblocker-cli add <numero> --description "<descrizione>"

# Rimuovere numero
callblocker-cli remove <numero>

# Elencare numeri bloccati
callblocker-cli list

# Verificare numero
callblocker-cli check <numero>
```

### Visualizzazione Log

```bash
# Ultimi 20 log
callblocker-cli logs

# Ultimi 50 log
callblocker-cli logs --limit 50

# Solo chiamate bloccate
callblocker-cli logs --blocked

# Statistiche
callblocker-cli stats
```

### Gestione Servizio

```bash
# Avviare
sudo systemctl start callblocker

# Fermare
sudo systemctl stop callblocker

# Riavviare
sudo systemctl restart callblocker

# Stato
sudo systemctl status callblocker

# Log in tempo reale
sudo journalctl -u callblocker -f
```

## Percorsi Importanti

- **Database**: `/var/lib/callblocker/callblocker.db`
- **Log**: `/var/log/callblocker/callblocker.log`
- **Servizio**: `/etc/systemd/system/callblocker.service`
- **Porta modem**: `/dev/ttyUSB0` (predefinito)

## Troubleshooting Veloce

### Modem non rilevato
```bash
ls -l /dev/ttyUSB*
sudo usermod -a -G dialout $USER
```

### Verificare log errori
```bash
sudo journalctl -u callblocker -n 50
```

### Testare connessione modem
```bash
sudo screen /dev/ttyUSB0 115200
# Digitare: AT
# Dovrebbe rispondere: OK
```

## Requisiti Minimi

- Python 3.8+
- pyserial
- Modem USB con supporto AT commands
- Ubuntu Linux (o compatibile)
- Permessi gruppo `dialout` per accesso seriale

## Supporto

- README.md: Documentazione completa
- EXAMPLES.md: Esempi di utilizzo dettagliati
- test.py: Test di verifica funzionamento
