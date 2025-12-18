# Esempi d'Uso - Call Blocker

## Scenario 1: Blocco Call-Center Milano

\`\`\`bash
sudo blacklist-cli add-prefix 02
sudo blacklist-cli list
\`\`\`

## Scenario 2: Blocco Numero Specifico

\`\`\`bash
sudo blacklist-cli add 0291234567
sudo blacklist-cli log
\`\`\`

## Scenario 3: Blocco Chiamate Anonime

\`\`\`bash
sudo blacklist-cli block-anonymous
sudo blacklist-cli list
\`\`\`

## Scenario 4: Monitoraggio Real-Time

\`\`\`bash
# Terminale 1: Log
sudo journalctl -u callblocker -f

# Terminale 2: Statistiche
watch -n 1 'sudo blacklist-cli stats'
\`\`\`

## Scenario 5: Analisi Chiamate Bloccate

\`\`\`bash
sudo blacklist-cli log --blocked -n 50
sudo blacklist-cli stats
\`\`\`

## Scenario 6: Backup Black-List

\`\`\`bash
sudo cp /var/lib/callblocker/blacklist.json ~/blacklist_backup.json
\`\`\`

Vedi documentazione completa per 14 scenari dettagliati!
