#!/bin/bash
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
echo_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

if [ "$EUID" -ne 0 ]; then 
    echo_error "Questo script deve essere eseguito come root"
    exit 1
fi

echo_warn "=== Disinstallazione Call Blocker ==="
read -p "Continuare? (s/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo_info "Disinstallazione annullata"
    exit 0
fi

echo_info "Fermo servizio..."
systemctl stop callblocker 2>/dev/null || true
systemctl disable callblocker 2>/dev/null || true

echo_info "Rimozione servizio systemd..."
rm -f /etc/systemd/system/callblocker.service
systemctl daemon-reload

echo_info "Rimozione symlink..."
rm -f /usr/local/bin/callblocker-daemon
rm -f /usr/local/bin/blacklist-cli

echo_info "Rimozione file programma..."
rm -rf /opt/callblocker

echo_info "Rimozione utente callblocker..."
if id -u callblocker >/dev/null 2>&1; then
    userdel callblocker
    echo_info "Utente callblocker rimosso"
fi

echo ""
read -p "Rimuovere anche i dati in /var/lib/callblocker? (s/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    echo_warn "Rimozione dati..."
    rm -rf /var/lib/callblocker
    echo_info "Dati rimossi"
else
    echo_info "Dati conservati in /var/lib/callblocker"
fi

echo ""
echo_info "=== Disinstallazione completata ==="
