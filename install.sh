#!/bin/bash
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
echo_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
echo_error() { echo -e "${RED}[ERROR]${NC} $1"; }

if [ "$EUID" -ne 0 ]; then 
    echo_error "Questo script deve essere eseguito come root"
    exit 1
fi

echo_info "=== Installazione Call Blocker ==="

echo_info "Installazione dipendenze..."
apt-get update
apt-get install -y python3 python3-pip python3-serial
pip3 install pyserial 2>/dev/null || true

echo_info "Creazione utente callblocker..."
if ! id -u callblocker >/dev/null 2>&1; then
    useradd -r -s /bin/false -G dialout callblocker
    echo_info "Utente callblocker creato e aggiunto al gruppo dialout"
else
    echo_warn "Utente callblocker già esistente"
    usermod -a -G dialout callblocker
fi

echo_info "Creazione directory..."
mkdir -p /opt/callblocker
mkdir -p /var/lib/callblocker
mkdir -p /var/log
mkdir -p /etc/callblocker

echo_info "Copia file programma..."
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cp "$SCRIPT_DIR/callblocker_daemon.py" /opt/callblocker/
cp "$SCRIPT_DIR/serial_handler.py" /opt/callblocker/
cp "$SCRIPT_DIR/ring_detector.py" /opt/callblocker/
cp "$SCRIPT_DIR/caller_id.py" /opt/callblocker/
cp "$SCRIPT_DIR/blacklist_filter.py" /opt/callblocker/
cp "$SCRIPT_DIR/call_action.py" /opt/callblocker/
cp "$SCRIPT_DIR/call_logger.py" /opt/callblocker/
cp "$SCRIPT_DIR/blacklist_cli.py" /opt/callblocker/

chmod +x /opt/callblocker/callblocker_daemon.py
chmod +x /opt/callblocker/blacklist_cli.py

ln -sf /opt/callblocker/callblocker_daemon.py /usr/local/bin/callblocker-daemon
ln -sf /opt/callblocker/blacklist_cli.py /usr/local/bin/blacklist-cli

echo_info "Programmi installati in /opt/callblocker"

echo_info "Configurazione permessi..."
chown -R callblocker:dialout /opt/callblocker
chown -R callblocker:callblocker /var/lib/callblocker
chmod 755 /opt/callblocker
chmod 755 /var/lib/callblocker

if [ ! -f /var/lib/callblocker/blacklist.json ]; then
    echo_info "Creazione blacklist.json iniziale..."
    cat > /var/lib/callblocker/blacklist.json <<EOJ
{
  "enabled": true,
  "block_anonymous": false,
  "numbers": [],
  "prefixes": []
}
EOJ
    chown callblocker:callblocker /var/lib/callblocker/blacklist.json
    chmod 644 /var/lib/callblocker/blacklist.json
fi

echo_info "Installazione servizio systemd..."
cp "$SCRIPT_DIR/callblocker.service" /etc/systemd/system/
systemctl daemon-reload

echo_info "Servizio systemd installato"

echo_info "Verifica device seriale..."
if [ -e /dev/ttyACM0 ]; then
    echo_info "Device /dev/ttyACM0 trovato"
    ls -l /dev/ttyACM0
else
    echo_warn "Device /dev/ttyACM0 non trovato!"
    echo_warn "Assicurati che il modem USB sia collegato"
fi

echo_info "Verifica permessi utente callblocker..."
groups callblocker

echo ""
echo_info "=== Installazione completata! ==="
echo ""
echo "Per avviare il servizio:"
echo "  sudo systemctl start callblocker"
echo ""
echo "Per abilitare avvio automatico:"
echo "  sudo systemctl enable callblocker"
echo ""
echo "Per vedere lo stato:"
echo "  sudo systemctl status callblocker"
echo ""
echo "Per vedere i log:"
echo "  sudo journalctl -u callblocker -f"
echo ""
echo "Per gestire la black-list:"
echo "  sudo blacklist-cli list"
echo "  sudo blacklist-cli add 0291234567"
echo "  sudo blacklist-cli log"
echo "  sudo blacklist-cli stats"
echo ""
