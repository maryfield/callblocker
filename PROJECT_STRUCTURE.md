# Struttura Progetto Call Blocker

## Repository

\`\`\`
callblocker/
├── callblocker_daemon.py      # Demone principale
├── serial_handler.py          # Gestione seriale
├── ring_detector.py           # Rilevamento RING
├── caller_id.py              # Parsing Caller ID
├── blacklist_filter.py        # Filtro black-list
├── call_action.py            # Azioni blocco
├── call_logger.py            # Logging SQLite
├── blacklist_cli.py          # CLI tool
├── test_modem.py             # Test hardware
├── install.sh                # Installazione
├── uninstall.sh              # Disinstallazione
├── callblocker.service       # Systemd unit
├── requirements.txt          # Dipendenze
├── Makefile                  # Comandi rapidi
└── docs/                     # Documentazione
\`\`\`

## Post-Installazione

\`\`\`
/opt/callblocker/          # Programmi
/var/lib/callblocker/      # Dati
/usr/local/bin/            # Comandi
\`\`\`
