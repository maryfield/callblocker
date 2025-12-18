# 📞 Call Blocker

**Sistema professionale di blocco chiamate indesiderate per linee PSTN analogiche**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![Ubuntu](https://img.shields.io/badge/ubuntu-20.04+-orange.svg)](https://ubuntu.com/)

Sistema robusto e minimale per bloccare automaticamente chiamate telefoniche indesiderate su linee PSTN tradizionali tramite modem USB analogico.

---

## 🎯 Cosa Fa

- ✅ **Blocca automaticamente** chiamate da numeri in black-list
- ✅ **Monitora 24/7** la linea telefonica senza intervento umano
- ✅ **Registra tutto** in database SQLite con statistiche
- ✅ **Si aggiorna in tempo reale** senza mai richiedere riavvii
- ✅ **Funziona headless** su server, Raspberry Pi, o desktop

## 🚀 Quick Start (5 minuti)

\`\`\`bash
# 1. Clone repository
git clone https://github.com/maryfield/callblocker.git
cd callblocker

# 2. Test modem (IMPORTANTE!)
sudo python3 test_modem.py
# Fai squillare quando richiesto per verificare il funzionamento

# 3. Installazione automatica
sudo ./install.sh

# 4. Avvio e attivazione
sudo systemctl start callblocker
sudo systemctl enable callblocker

# 5. Configurazione black-list
sudo blacklist-cli add-prefix 02        # Blocca prefisso Milano
sudo blacklist-cli add 0291234567       # Blocca numero specifico
sudo blacklist-cli block-anonymous      # Blocca anonimi
sudo blacklist-cli list                 # Verifica configurazione
\`\`\`

**FATTO!** Il sistema è attivo e protegge la tua linea! 🎉

## 📋 Requisiti

**Hardware:**
- Modem USB analogico compatibile Linux
- Linea telefonica PSTN tradizionale
- Computer con Ubuntu/Debian (o Raspberry Pi)

**Software:**
- Ubuntu 20.04+ o Debian-based
- Python 3.8+
- 50MB spazio disco
- Accesso sudo

## 🎮 Comandi Principali

### Gestione Black-List
\`\`\`bash
sudo blacklist-cli add NUMERO           # Aggiungi numero completo
sudo blacklist-cli add-prefix PREFISSO  # Aggiungi prefisso (blocca tutti)
sudo blacklist-cli remove NUMERO        # Rimuovi numero
sudo blacklist-cli list                 # Visualizza black-list completa
sudo blacklist-cli enable               # Abilita filtro
sudo blacklist-cli disable              # Disabilita filtro temporaneamente
sudo blacklist-cli block-anonymous      # Blocca chiamate anonime
sudo blacklist-cli allow-anonymous      # Permetti chiamate anonime
\`\`\`

### Monitoraggio e Log
\`\`\`bash
sudo blacklist-cli log                  # Ultime 20 chiamate
sudo blacklist-cli log -n 50            # Ultime 50 chiamate
sudo blacklist-cli log --blocked        # Solo chiamate bloccate
sudo blacklist-cli stats                # Statistiche complete
sudo journalctl -u callblocker -f       # Log in tempo reale
\`\`\`

### Gestione Servizio
\`\`\`bash
sudo systemctl start callblocker        # Avvia demone
sudo systemctl stop callblocker         # Ferma demone
sudo systemctl restart callblocker      # Riavvia demone
sudo systemctl status callblocker       # Verifica stato
sudo systemctl enable callblocker       # Avvio automatico ON
sudo systemctl disable callblocker      # Avvio automatico OFF
\`\`\`

## 💡 Esempi Pratici

### Blocco Call-Center per Città
\`\`\`bash
sudo blacklist-cli add-prefix 02        # Milano
sudo blacklist-cli add-prefix 06        # Roma
sudo blacklist-cli add-prefix 011       # Torino
sudo blacklist-cli add-prefix 051       # Bologna
\`\`\`

### Monitoraggio Attività
\`\`\`bash
# Terminale 1: Log in tempo reale
sudo journalctl -u callblocker -f

# Terminale 2: Statistiche aggiornate
watch -n 2 'sudo blacklist-cli stats'
\`\`\`

### Backup Configurazione
\`\`\`bash
sudo cp /var/lib/callblocker/blacklist.json ~/blacklist_backup_$(date +%Y%m%d).json
\`\`\`

## 🏗️ Architettura Sistema

\`\`\`
┌──────────────────┐
│   Linea PSTN     │  ← Chiamata in arrivo
└────────┬─────────┘
         │
┌────────▼──────────┐
│   Modem USB       │  ← Hardware fisico
└────────┬──────────┘
         │ /dev/ttyACM0
┌────────▼────────────────────────────┐
│  Call Blocker Daemon (Python)       │
│  ┌──────────────────────────────┐   │
│  │ 1. Rileva RING               │   │
│  │ 2. Legge Caller ID (se disp.)│   │
│  │ 3. Verifica Black-List       │   │
│  │ 4. Azione: ATA → wait → ATH  │   │
│  └──────────────────────────────┘   │
└────────┬────────────────────────────┘
         │
┌────────▼────────────────────────────┐
│  Storage Layer                      │
│  ├─ blacklist.json  (configurazione)│
│  └─ calls.db        (log SQLite)    │
└─────────────────────────────────────┘
         ▲
         │
┌────────┴────────────────────────────┐
│  CLI Management Tool                │
│  (blacklist-cli)                    │
└─────────────────────────────────────┘
\`\`\`

## 📊 Caratteristiche Tecniche

| Caratteristica | Dettaglio |
|---------------|-----------|
| **Protocollo** | Seriale raw 9600 baud, 8N1 |
| **Caller ID** | Supporto multipli formati CLIP |
| **Black-List** | JSON con hot-reload ogni 2s |
| **Database** | SQLite per storico completo |
| **Logging** | journald + file + SQLite |
| **Sicurezza** | Utente dedicato, protezioni systemd |
| **Performance** | ~20MB RAM, <1% CPU |
| **Affidabilità** | Restart automatico, watchdog systemd |

## 📚 Documentazione Completa

| Documento | Descrizione |
|-----------|-------------|
| [QUICKSTART.md](QUICKSTART.md) | Guida installazione rapida 5 minuti |
| [FAQ.md](FAQ.md) | Risposte a domande frequenti |
| [EXAMPLES.md](EXAMPLES.md) | Scenari pratici step-by-step |
| [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) | Architettura e struttura file |
| [CHANGELOG.md](CHANGELOG.md) | Storico versioni e modifiche |

## 🔧 Risoluzione Problemi

### Servizio non parte
\`\`\`bash
sudo journalctl -u callblocker -n 100 --no-pager
\`\`\`

### Permission denied su device
\`\`\`bash
sudo usermod -a -G dialout callblocker
sudo systemctl restart callblocker
\`\`\`

### Device seriale non trovato
\`\`\`bash
ls -l /dev/tty*          # Lista device disponibili
dmesg | grep tty         # Verifica riconoscimento kernel
\`\`\`

### Caller ID non funziona
Alcuni modem richiedono comandi AT specifici. Modifica \`serial_handler.py\` → \`initialize_modem()\` con i comandi del tuo modem.

**Vedi [FAQ.md](FAQ.md) per soluzioni complete!**

## 🧪 Test Funzionamento

\`\`\`bash
# 1. Test hardware
sudo python3 test_modem.py

# 2. Test blocco completo
sudo blacklist-cli add +393401234567    # Aggiungi tuo cellulare
sudo journalctl -u callblocker -f       # Monitora in tempo reale
# Chiama dal cellulare → Vedrai blocco nei log
sudo blacklist-cli remove +393401234567 # Rimuovi dopo test
\`\`\`

## 📦 Struttura File Installati

\`\`\`
/opt/callblocker/                  # Programmi Python
  ├── callblocker_daemon.py        # Demone principale
  ├── serial_handler.py            # Gestione seriale
  ├── ring_detector.py             # Rilevamento RING
  ├── caller_id.py                 # Parser Caller ID
  ├── blacklist_filter.py          # Filtro black-list
  ├── call_action.py               # Azioni blocco
  ├── call_logger.py               # Logging SQLite
  └── blacklist_cli.py             # CLI tool

/var/lib/callblocker/              # Dati persistenti
  ├── blacklist.json               # Black-list configurazione
  └── calls.db                     # Database log chiamate

/usr/local/bin/                    # Comandi globali
  ├── callblocker-daemon           # Avvio demone
  └── blacklist-cli                # Gestione CLI

/etc/systemd/system/               # Servizio
  └── callblocker.service          # Unit systemd
\`\`\`

## 🚧 Roadmap Sviluppo Futuro

- [ ] **GUI Desktop** (GTK/Qt) per gestione visuale
- [ ] **Web UI** (localhost:8080) con dashboard
- [ ] **Whitelist** per numeri sempre permessi
- [ ] **Filtri Orari** (blocca solo in fasce orarie)
- [ ] **Notifiche** via Telegram, email, webhook
- [ ] **Home Assistant** integration
- [ ] **Docker Container** per deploy facile
- [ ] **Multi-modem** support per più linee
- [ ] **Pattern Recognition** ML per identificare spam

## 🤝 Contribuire al Progetto

Contributi benvenuti! Per contribuire:

1. **Fork** il repository
2. **Crea branch** feature: \`git checkout -b feature/nuova-funzione\`
3. **Commit** modifiche: \`git commit -m 'Aggiunta nuova funzione'\`
4. **Push** al branch: \`git push origin feature/nuova-funzione\`
5. **Apri Pull Request** su GitHub

### Linee Guida
- Segui PEP 8 per codice Python
- Aggiungi test per nuove funzionalità
- Aggiorna documentazione se necessario
- Descrivi chiaramente le modifiche nel PR

## 📝 Licenza

Questo progetto è rilasciato sotto licenza **MIT License**.  
Vedi file [LICENSE](LICENSE) per dettagli completi.

In sintesi: puoi usare, modificare, distribuire il codice liberamente, anche per scopi commerciali, mantenendo l'attribuzione originale.

## 🆘 Supporto e Community

- 📖 **Documentazione**: Tutti i file \`.md\` nel repository
- 🐛 **Bug Report**: [GitHub Issues](https://github.com/maryfield/callblocker/issues)
- 💬 **Discussioni**: [GitHub Discussions](https://github.com/maryfield/callblocker/discussions)
- 📧 **Email**: [Apri Issue su GitHub]

## 🌟 Ringraziamenti

Sviluppato per proteggere la privacy e la tranquillità domestica dalle chiamate indesiderate.

Un ringraziamento speciale a tutti coloro che hanno contribuito con suggerimenti, bug report e miglioramenti.

---

## 📊 Statistiche Progetto

- **Linguaggio**: Python 3.8+
- **Licenza**: MIT
- **Stato**: Production Ready
- **Piattaforma**: Linux (Ubuntu/Debian)
- **Architettura**: Modulare, estendibile

---

**Made with ❤️ for privacy and peace of mind**

Se questo progetto ti è utile, lascia una ⭐ su GitHub!
