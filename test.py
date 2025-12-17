#!/usr/bin/env python3
"""
Test script per Call Blocker.

Testa le funzionalità di base senza necessità di hardware.
"""

import os
import tempfile
import sys
from pathlib import Path

# Aggiungi il path del modulo
sys.path.insert(0, str(Path(__file__).parent))

from callblocker.database import CallBlockerDB


def test_database():
    """Test delle funzionalità del database."""
    print("=== Test Database ===\n")
    
    # Usa database temporaneo
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        db = CallBlockerDB(db_path)
        
        print("✓ Database creato")
        
        # Test aggiunta alla blacklist
        assert db.add_to_blacklist("1234567890", "Test numero 1")
        print("✓ Numero aggiunto alla blacklist")
        
        # Test aggiunta duplicata
        assert not db.add_to_blacklist("1234567890", "Duplicato")
        print("✓ Aggiunta duplicata rifiutata correttamente")
        
        # Test verifica blacklist
        assert db.is_blacklisted("1234567890")
        assert not db.is_blacklisted("9999999999")
        print("✓ Verifica blacklist funzionante")
        
        # Test aggiunta multipla
        db.add_to_blacklist("0987654321", "Test numero 2")
        db.add_to_blacklist("5555555555", "Test numero 3")
        
        # Test lista blacklist
        blacklist = db.get_blacklist()
        assert len(blacklist) == 3
        print(f"✓ Blacklist contiene {len(blacklist)} numeri")
        
        # Test logging chiamate
        db.log_call("1234567890", True, "Spam Caller")
        db.log_call("9999999999", False, "Amico")
        db.log_call("1234567890", True, "Spam Caller")
        print("✓ Chiamate registrate")
        
        # Test recupero log
        logs = db.get_call_logs(limit=10)
        assert len(logs) == 3
        print(f"✓ Log contiene {len(logs)} chiamate")
        
        # Test log solo bloccate
        blocked_logs = db.get_call_logs(limit=10, blocked_only=True)
        assert len(blocked_logs) == 2
        print(f"✓ Log chiamate bloccate: {len(blocked_logs)}")
        
        # Test statistiche
        stats = db.get_statistics()
        assert stats['total_calls'] == 3
        assert stats['blocked_calls'] == 2
        assert stats['allowed_calls'] == 1
        assert stats['blacklist_count'] == 3
        print("✓ Statistiche corrette:")
        print(f"  - Totale chiamate: {stats['total_calls']}")
        print(f"  - Chiamate bloccate: {stats['blocked_calls']}")
        print(f"  - Chiamate permesse: {stats['allowed_calls']}")
        print(f"  - Numeri in blacklist: {stats['blacklist_count']}")
        
        # Test rimozione dalla blacklist
        assert db.remove_from_blacklist("1234567890")
        assert not db.is_blacklisted("1234567890")
        print("✓ Numero rimosso dalla blacklist")
        
        # Test rimozione numero non esistente
        assert not db.remove_from_blacklist("8888888888")
        print("✓ Rimozione numero inesistente gestita correttamente")
        
        print("\n=== Tutti i test del database passati! ===\n")


def test_cli_help():
    """Test del CLI help."""
    print("=== Test CLI ===\n")
    
    from callblocker.cli import main
    
    print("Testando CLI help...")
    print("(Questo dovrebbe mostrare l'help della CLI)\n")
    
    # Simula --help
    sys.argv = ['callblocker-cli', '--help']
    try:
        main()
    except SystemExit:
        pass
    
    print("\n✓ CLI funzionante\n")


if __name__ == "__main__":
    print("\n" + "="*50)
    print("Call Blocker - Test Suite")
    print("="*50 + "\n")
    
    try:
        test_database()
        # test_cli_help()  # Commentato perché stampa help
        
        print("="*50)
        print("Tutti i test completati con successo!")
        print("="*50 + "\n")
        
    except AssertionError as e:
        print(f"\n✗ Test fallito: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Errore durante i test: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
