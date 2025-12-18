#!/usr/bin/env python3
"""CLI Tool per gestione black-list."""
import json
import sys
import argparse
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

BLACKLIST_FILE = '/var/lib/callblocker/blacklist.json'
LOG_DB = '/var/lib/callblocker/calls.db'

def load_blacklist():
    try:
        with open(BLACKLIST_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {'enabled': True, 'block_anonymous': False, 'numbers': [], 'prefixes': []}
    except Exception as e:
        print(f"Errore caricamento: {e}", file=sys.stderr)
        sys.exit(1)

def save_blacklist(data):
    try:
        Path(BLACKLIST_FILE).parent.mkdir(parents=True, exist_ok=True)
        with open(BLACKLIST_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        print("✓ Black-list salvata")
    except Exception as e:
        print(f"Errore salvataggio: {e}", file=sys.stderr)
        sys.exit(1)

def add_number(number):
    bl = load_blacklist()
    if number in bl['numbers']:
        print(f"Numero {number} già presente")
        return
    bl['numbers'].append(number)
    save_blacklist(bl)
    print(f"✓ Aggiunto: {number}")

def remove_number(number):
    bl = load_blacklist()
    if number not in bl['numbers']:
        print(f"Numero {number} non trovato")
        return
    bl['numbers'].remove(number)
    save_blacklist(bl)
    print(f"✓ Rimosso: {number}")

def add_prefix(prefix):
    bl = load_blacklist()
    if prefix in bl['prefixes']:
        print(f"Prefisso {prefix} già presente")
        return
    bl['prefixes'].append(prefix)
    save_blacklist(bl)
    print(f"✓ Aggiunto prefisso: {prefix}")

def remove_prefix(prefix):
    bl = load_blacklist()
    if prefix not in bl['prefixes']:
        print(f"Prefisso {prefix} non trovato")
        return
    bl['prefixes'].remove(prefix)
    save_blacklist(bl)
    print(f"✓ Rimosso prefisso: {prefix}")

def list_blacklist():
    bl = load_blacklist()
    print("\n=== BLACK-LIST ===")
    print(f"Stato: {'ATTIVA' if bl['enabled'] else 'DISATTIVA'}")
    print(f"Blocco anonimi: {'SÌ' if bl['block_anonymous'] else 'NO'}")
    print(f"\nNumeri bloccati ({len(bl['numbers'])}):")
    for num in sorted(bl['numbers']):
        print(f"  - {num}")
    print(f"\nPrefissi bloccati ({len(bl['prefixes'])}):")
    for pref in sorted(bl['prefixes']):
        print(f"  - {pref}")

def enable_filter(enable=True):
    bl = load_blacklist()
    bl['enabled'] = enable
    save_blacklist(bl)
    print(f"✓ Filtro {'abilitato' if enable else 'disabilitato'}")

def toggle_anonymous(block=True):
    bl = load_blacklist()
    bl['block_anonymous'] = block
    save_blacklist(bl)
    print(f"✓ Chiamate anonime: {'bloccate' if block else 'permesse'}")

def show_log(limit=20, blocked_only=False):
    try:
        conn = sqlite3.connect(LOG_DB)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        query = 'SELECT * FROM calls'
        if blocked_only:
            query += " WHERE action = 'blocked'"
        query += ' ORDER BY timestamp DESC LIMIT ?'
        cursor.execute(query, (limit,))
        rows = cursor.fetchall()
        conn.close()
        if not rows:
            print("Nessuna chiamata registrata")
            return
        print(f"\n=== ULTIME {len(rows)} CHIAMATE ===\n")
        for row in rows:
            ts = datetime.fromisoformat(row['timestamp'])
            number = row['number'] or 'ANONIMO'
            action = row['action'].upper()
            reason = row['reason'] or '-'
            symbol = '🚫' if action == 'BLOCKED' else '✓'
            print(f"{symbol} {ts.strftime('%Y-%m-%d %H:%M:%S')} | {number:20} | {action:10} | {reason}")
    except Exception as e:
        print(f"Errore lettura log: {e}", file=sys.stderr)

def show_stats():
    try:
        conn = sqlite3.connect(LOG_DB)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM calls')
        total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM calls WHERE action = 'blocked'")
        blocked = cursor.fetchone()[0]
        today = datetime.now().date().isoformat()
        cursor.execute('SELECT COUNT(*) FROM calls WHERE date(timestamp) = ?', (today,))
        today_total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM calls WHERE date(timestamp) = ? AND action = 'blocked'", (today,))
        today_blocked = cursor.fetchone()[0]
        week_ago = (datetime.now() - timedelta(days=7)).date().isoformat()
        cursor.execute('SELECT COUNT(*) FROM calls WHERE date(timestamp) >= ?', (week_ago,))
        week_total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM calls WHERE date(timestamp) >= ? AND action = 'blocked'", (week_ago,))
        week_blocked = cursor.fetchone()[0]
        cursor.execute('''SELECT number, COUNT(*) as count FROM calls 
                         WHERE action = 'blocked' AND number IS NOT NULL
                         GROUP BY number ORDER BY count DESC LIMIT 5''')
        top_blocked = cursor.fetchall()
        conn.close()
        print("\n=== STATISTICHE ===\n")
        print(f"Totale chiamate:     {total}")
        print(f"  - Bloccate:        {blocked} ({blocked/total*100 if total > 0 else 0:.1f}%)")
        print(f"  - Permesse:        {total - blocked}")
        print(f"\nOggi:")
        print(f"  - Totale:          {today_total}")
        print(f"  - Bloccate:        {today_blocked}")
        print(f"\nUltimi 7 giorni:")
        print(f"  - Totale:          {week_total}")
        print(f"  - Bloccate:        {week_blocked}")
        if top_blocked:
            print(f"\nTop 5 numeri bloccati:")
            for num, count in top_blocked:
                print(f"  - {num:20} ({count} volte)")
    except Exception as e:
        print(f"Errore calcolo statistiche: {e}", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(description='Gestione black-list Call Blocker')
    subparsers = parser.add_subparsers(dest='command', help='Comando')
    add_parser = subparsers.add_parser('add', help='Aggiungi numero')
    add_parser.add_argument('number', help='Numero da aggiungere')
    remove_parser = subparsers.add_parser('remove', help='Rimuovi numero')
    remove_parser.add_argument('number', help='Numero da rimuovere')
    add_prefix_parser = subparsers.add_parser('add-prefix', help='Aggiungi prefisso')
    add_prefix_parser.add_argument('prefix', help='Prefisso da aggiungere')
    remove_prefix_parser = subparsers.add_parser('remove-prefix', help='Rimuovi prefisso')
    remove_prefix_parser.add_argument('prefix', help='Prefisso da rimuovere')
    subparsers.add_parser('list', help='Mostra black-list')
    subparsers.add_parser('enable', help='Abilita filtro')
    subparsers.add_parser('disable', help='Disabilita filtro')
    subparsers.add_parser('block-anonymous', help='Blocca chiamate anonime')
    subparsers.add_parser('allow-anonymous', help='Permetti chiamate anonime')
    log_parser = subparsers.add_parser('log', help='Mostra log chiamate')
    log_parser.add_argument('-n', '--limit', type=int, default=20, help='Numero chiamate da mostrare')
    log_parser.add_argument('--blocked', action='store_true', help='Solo chiamate bloccate')
    subparsers.add_parser('stats', help='Mostra statistiche')
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    if args.command == 'add':
        add_number(args.number)
    elif args.command == 'remove':
        remove_number(args.number)
    elif args.command == 'add-prefix':
        add_prefix(args.prefix)
    elif args.command == 'remove-prefix':
        remove_prefix(args.prefix)
    elif args.command == 'list':
        list_blacklist()
    elif args.command == 'enable':
        enable_filter(True)
    elif args.command == 'disable':
        enable_filter(False)
    elif args.command == 'block-anonymous':
        toggle_anonymous(True)
    elif args.command == 'allow-anonymous':
        toggle_anonymous(False)
    elif args.command == 'log':
        show_log(args.limit, args.blocked)
    elif args.command == 'stats':
        show_stats()

if __name__ == '__main__':
    main()
