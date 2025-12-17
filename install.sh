#!/bin/bash
# Script di installazione per Call Blocker
# Per Ubuntu Linux

set -e

echo "=== Installazione Call Blocker ==="
echo ""

# Verifica se eseguito come root
if [ "$EUID" -ne 0 ]; then 
    echo "Errore: questo script deve essere eseguito come root (usa sudo)"
    exit 1
fi

# Installa dipendenze Python
echo "1. Installazione dipendenze Python..."
pip3 install -r requirements.txt

# Installa il pacchetto
echo "2. Installazione pacchetto Call Blocker..."
pip3 install .

# Crea utente callblocker se non esiste
if ! id -u callblocker > /dev/null 2>&1; then
    echo "3. Creazione utente callblocker..."
    useradd -r -s /bin/false callblocker
else
    echo "3. Utente callblocker già esistente"
fi

# Aggiungi utente al gruppo dialout per accesso seriale
echo "4. Configurazione permessi porta seriale..."
usermod -a -G dialout callblocker

# Crea directory necessarie
echo "5. Creazione directory..."
mkdir -p /var/lib/callblocker
mkdir -p /var/log/callblocker
chown callblocker:callblocker /var/lib/callblocker
chown callblocker:callblocker /var/log/callblocker
chmod 755 /var/lib/callblocker
chmod 755 /var/log/callblocker

# Copia file di servizio systemd
echo "6. Installazione servizio systemd..."
cp callblocker.service /etc/systemd/system/
systemctl daemon-reload

# Chiedi se abilitare il servizio all'avvio
read -p "Abilitare Call Blocker all'avvio? (s/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[SsYy]$ ]]; then
    systemctl enable callblocker
    echo "✓ Servizio abilitato all'avvio"
fi

# Chiedi porta del modem
read -p "Porta del modem USB [/dev/ttyUSB0]: " MODEM_PORT
MODEM_PORT=${MODEM_PORT:-/dev/ttyUSB0}

# Verifica che la porta esista
if [ -e "$MODEM_PORT" ]; then
    echo "✓ Porta $MODEM_PORT trovata"
    
    # Aggiorna il file di servizio con la porta corretta
    sed -i "s|/dev/ttyUSB0|$MODEM_PORT|g" /etc/systemd/system/callblocker.service
    systemctl daemon-reload
else
    echo "⚠ Attenzione: porta $MODEM_PORT non trovata"
    echo "  Assicurati che il modem sia collegato prima di avviare il servizio"
fi

echo ""
echo "=== Installazione completata ==="
echo ""
echo "Comandi utili:"
echo "  sudo systemctl start callblocker    - Avvia il servizio"
echo "  sudo systemctl stop callblocker     - Ferma il servizio"
echo "  sudo systemctl status callblocker   - Verifica stato"
echo "  callblocker-cli add <numero>        - Aggiungi numero alla blacklist"
echo "  callblocker-cli list                - Elenca numeri bloccati"
echo "  callblocker-cli logs                - Visualizza log chiamate"
echo ""
echo "Per maggiori informazioni, consultare README.md"
