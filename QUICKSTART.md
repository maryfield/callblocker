# Quick Start - Call Blocker

Guida rapida per installare e configurare Call Blocker in 5 minuti.

## Installazione

\`\`\`bash
# 1. Clone
git clone https://github.com/maryfield/callblocker.git
cd callblocker

# 2. Test hardware
sudo python3 test_modem.py
# Fai squillare il telefono quando richiesto

# 3. Installazione
sudo ./install.sh

# 4. Avvio
sudo systemctl start callblocker
sudo systemctl enable callblocker
\`\`\`

## Primi Passi

\`\`\`bash
# Aggiungi numeri
sudo blacklist-cli add 0291234567
sudo blacklist-cli add-prefix 02

# Visualizza
sudo blacklist-cli list
sudo blacklist-cli log
sudo blacklist-cli stats
\`\`\`

## Test

\`\`\`bash
# 1. Aggiungi il tuo cellulare
sudo blacklist-cli add +393401234567

# 2. Monitora log
sudo journalctl -u callblocker -f

# 3. Chiama la linea dal cellulare
# Risultato: 1-2 squilli poi chiamata rifiutata

# 4. Rimuovi numero test
sudo blacklist-cli remove +393401234567
\`\`\`

## Comandi Essenziali

\`\`\`bash
sudo systemctl start/stop/restart callblocker
sudo blacklist-cli add/remove NUMERO
sudo blacklist-cli log
sudo journalctl -u callblocker -f
\`\`\`

Vedi \`README.md\` per documentazione completa!
