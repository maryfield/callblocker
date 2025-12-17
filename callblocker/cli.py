"""
CLI module for Call Blocker.

Strumento a riga di comando per gestire la blacklist e visualizzare i log.
"""

import sys
import argparse
from datetime import datetime
from typing import Optional

from .database import CallBlockerDB


class CallBlockerCLI:
    """Interfaccia a riga di comando per Call Blocker."""
    
    def __init__(self, db_path: str = "/var/lib/callblocker/callblocker.db"):
        """
        Inizializza la CLI.
        
        Args:
            db_path: Percorso del database SQLite
        """
        self.db = CallBlockerDB(db_path)
    
    def add_number(self, phone_number: str, description: str = ""):
        """
        Aggiunge un numero alla blacklist.
        
        Args:
            phone_number: Numero da bloccare
            description: Descrizione opzionale
        """
        if self.db.add_to_blacklist(phone_number, description):
            print(f"✓ Numero {phone_number} aggiunto alla blacklist")
            if description:
                print(f"  Descrizione: {description}")
        else:
            print(f"✗ Numero {phone_number} già presente nella blacklist", file=sys.stderr)
            sys.exit(1)
    
    def remove_number(self, phone_number: str):
        """
        Rimuove un numero dalla blacklist.
        
        Args:
            phone_number: Numero da sbloccare
        """
        if self.db.remove_from_blacklist(phone_number):
            print(f"✓ Numero {phone_number} rimosso dalla blacklist")
        else:
            print(f"✗ Numero {phone_number} non trovato nella blacklist", file=sys.stderr)
            sys.exit(1)
    
    def list_blacklist(self):
        """Elenca tutti i numeri nella blacklist."""
        blacklist = self.db.get_blacklist()
        
        if not blacklist:
            print("Blacklist vuota")
            return
        
        print(f"\n{'Numero':<20} {'Descrizione':<30} {'Data aggiunta'}")
        print("-" * 75)
        
        for phone_number, description, added_date in blacklist:
            desc_short = (description[:27] + "...") if len(description) > 30 else description
            print(f"{phone_number:<20} {desc_short:<30} {added_date}")
        
        print(f"\nTotale numeri bloccati: {len(blacklist)}")
    
    def check_number(self, phone_number: str):
        """
        Verifica se un numero è nella blacklist.
        
        Args:
            phone_number: Numero da verificare
        """
        if self.db.is_blacklisted(phone_number):
            print(f"✓ Il numero {phone_number} è nella blacklist")
        else:
            print(f"✗ Il numero {phone_number} NON è nella blacklist")
    
    def show_logs(self, limit: int = 20, blocked_only: bool = False):
        """
        Visualizza i log delle chiamate.
        
        Args:
            limit: Numero massimo di log da visualizzare
            blocked_only: Mostra solo chiamate bloccate
        """
        logs = self.db.get_call_logs(limit=limit, blocked_only=blocked_only)
        
        if not logs:
            print("Nessuna chiamata registrata")
            return
        
        print(f"\n{'Data e Ora':<20} {'Numero':<20} {'Stato':<10} {'Caller ID'}")
        print("-" * 75)
        
        for phone_number, call_date, blocked, caller_id in logs:
            stato = "BLOCCATO" if blocked else "Permesso"
            caller_id_short = (caller_id[:20] + "...") if len(caller_id) > 23 else caller_id
            print(f"{call_date:<20} {phone_number:<20} {stato:<10} {caller_id_short}")
        
        print(f"\nMostrati {len(logs)} log")
    
    def show_statistics(self):
        """Visualizza statistiche sulle chiamate."""
        stats = self.db.get_statistics()
        
        print("\n=== Statistiche Call Blocker ===")
        print(f"Numeri in blacklist:  {stats['blacklist_count']}")
        print(f"Totale chiamate:      {stats['total_calls']}")
        print(f"Chiamate bloccate:    {stats['blocked_calls']}")
        print(f"Chiamate permesse:    {stats['allowed_calls']}")
        
        if stats['total_calls'] > 0:
            block_rate = (stats['blocked_calls'] / stats['total_calls']) * 100
            print(f"Percentuale blocco:   {block_rate:.1f}%")


def main():
    """Entry point per la CLI."""
    parser = argparse.ArgumentParser(
        description="Call Blocker CLI - Gestione blacklist e visualizzazione log",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Esempi:
  callblocker-cli add 1234567890 --description "Spam"
  callblocker-cli remove 1234567890
  callblocker-cli list
  callblocker-cli check 1234567890
  callblocker-cli logs --limit 50
  callblocker-cli logs --blocked
  callblocker-cli stats
        """
    )
    
    parser.add_argument(
        "--db",
        default="/var/lib/callblocker/callblocker.db",
        help="Percorso del database SQLite"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Comandi disponibili")
    
    # Comando: add
    add_parser = subparsers.add_parser("add", help="Aggiunge un numero alla blacklist")
    add_parser.add_argument("phone_number", help="Numero di telefono da bloccare")
    add_parser.add_argument(
        "-d", "--description",
        default="",
        help="Descrizione opzionale"
    )
    
    # Comando: remove
    remove_parser = subparsers.add_parser("remove", help="Rimuove un numero dalla blacklist")
    remove_parser.add_argument("phone_number", help="Numero di telefono da sbloccare")
    
    # Comando: list
    list_parser = subparsers.add_parser("list", help="Elenca tutti i numeri nella blacklist")
    
    # Comando: check
    check_parser = subparsers.add_parser("check", help="Verifica se un numero è nella blacklist")
    check_parser.add_argument("phone_number", help="Numero di telefono da verificare")
    
    # Comando: logs
    logs_parser = subparsers.add_parser("logs", help="Visualizza i log delle chiamate")
    logs_parser.add_argument(
        "-l", "--limit",
        type=int,
        default=20,
        help="Numero massimo di log da visualizzare (default: 20)"
    )
    logs_parser.add_argument(
        "-b", "--blocked",
        action="store_true",
        help="Mostra solo chiamate bloccate"
    )
    
    # Comando: stats
    stats_parser = subparsers.add_parser("stats", help="Visualizza statistiche")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Esegui comando
    cli = CallBlockerCLI(db_path=args.db)
    
    if args.command == "add":
        cli.add_number(args.phone_number, args.description)
    elif args.command == "remove":
        cli.remove_number(args.phone_number)
    elif args.command == "list":
        cli.list_blacklist()
    elif args.command == "check":
        cli.check_number(args.phone_number)
    elif args.command == "logs":
        cli.show_logs(limit=args.limit, blocked_only=args.blocked)
    elif args.command == "stats":
        cli.show_statistics()


if __name__ == "__main__":
    main()
