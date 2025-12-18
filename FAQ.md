# FAQ - Call Blocker

## Installazione

**Q: Su quali versioni di Ubuntu funziona?**  
A: Testato su Ubuntu 20.04 e 22.04, ma funziona su qualsiasi distribuzione con systemd e Python 3.8+.

**Q: Come verifico che il modem funziona?**  
A: Esegui \`sudo python3 test_modem.py\` e fai squillare il telefono.

## Funzionamento

**Q: Come funziona il blocco?**  
A: Rileva RING, legge Caller ID, verifica black-list. Se bloccato: risponde (ATA), attende 1-2s, riattacca (ATH).

**Q: Devo riavviare dopo aver modificato la black-list?**  
A: No! Il demone ricarica automaticamente ogni 2 secondi.

**Q: Posso bloccare numeri anonimi?**  
A: Sì, usa \`sudo blacklist-cli block-anonymous\`

## Problemi Comuni

**Q: "Permission denied" su /dev/ttyACM0**  
A: \`sudo usermod -a -G dialout callblocker && sudo systemctl restart callblocker\`

**Q: Device non trovato**  
A: Verifica con \`ls -l /dev/tty*\` e modifica config se necessario.

**Q: Non ricevo Caller ID**  
A: Alcuni modem richiedono comandi AT specifici. Verifica il manuale del modem.

Vedi documentazione completa per altre FAQ!
