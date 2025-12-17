"""
Daemon module for Call Blocker.

Demone headless che monitora chiamate in arrivo e blocca quelle in blacklist.
"""

import sys
import signal
import time
import logging
import argparse
import os
from typing import Optional
from pathlib import Path

from .modem import Modem, ModemError
from .database import CallBlockerDB


class CallBlockerDaemon:
    """Demone principale per il blocco chiamate."""
    
    def __init__(self, port: str = "/dev/ttyUSB0", db_path: str = "/var/lib/callblocker/callblocker.db"):
        """
        Inizializza il daemon.
        
        Args:
            port: Porta seriale del modem
            db_path: Percorso del database SQLite
        """
        self.port = port
        self.db_path = db_path
        self.modem = None
        self.db = None
        self.running = False
        
        # Setup logging
        self._setup_logging()
        
        # Signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _setup_logging(self):
        """Configura il logging."""
        log_dir = "/var/log/callblocker"
        
        # Crea directory log se non esiste (gestisce permessi)
        try:
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, "callblocker.log")
        except PermissionError:
            # Fallback a home directory se non abbiamo permessi
            log_dir = os.path.expanduser("~/.callblocker")
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, "callblocker.log")
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def _signal_handler(self, signum, frame):
        """Gestisce i segnali di terminazione."""
        self.logger.info(f"Ricevuto segnale {signum}, arresto in corso...")
        self.stop()
    
    def start(self):
        """Avvia il daemon."""
        self.logger.info("Avvio Call Blocker Daemon...")
        
        try:
            # Inizializza database
            self.db = CallBlockerDB(self.db_path)
            self.logger.info(f"Database inizializzato: {self.db_path}")
            
            # Connetti al modem
            self.modem = Modem(self.port)
            self.modem.connect()
            self.logger.info(f"Modem connesso su {self.port}")
            
            # Avvia loop principale
            self.running = True
            self._main_loop()
            
        except ModemError as e:
            self.logger.error(f"Errore modem: {e}")
            sys.exit(1)
        except Exception as e:
            self.logger.error(f"Errore avvio daemon: {e}", exc_info=True)
            sys.exit(1)
    
    def stop(self):
        """Ferma il daemon."""
        self.running = False
        if self.modem:
            self.modem.disconnect()
        self.logger.info("Call Blocker Daemon arrestato")
    
    def _main_loop(self):
        """Loop principale del daemon."""
        self.logger.info("Monitoraggio chiamate in corso...")
        
        while self.running:
            try:
                # Attendi chiamata in arrivo
                call_info = self.modem.wait_for_call(timeout=1)
                
                if call_info:
                    phone_number, caller_id = call_info
                    self._handle_call(phone_number, caller_id)
                    
            except Exception as e:
                self.logger.error(f"Errore nel loop principale: {e}", exc_info=True)
                time.sleep(1)
    
    def _handle_call(self, phone_number: str, caller_id: str):
        """
        Gestisce una chiamata in arrivo.
        
        Args:
            phone_number: Numero chiamante
            caller_id: Identificativo chiamante
        """
        self.logger.info(f"Chiamata in arrivo: {phone_number} ({caller_id})")
        
        # Verifica blacklist
        is_blocked = self.db.is_blacklisted(phone_number)
        
        if is_blocked:
            self.logger.info(f"BLOCCO: {phone_number} è nella blacklist")
            
            # Blocca la chiamata
            if self.modem.answer_and_hangup():
                self.logger.info(f"Chiamata bloccata con successo: {phone_number}")
            else:
                self.logger.warning(f"Errore nel blocco della chiamata: {phone_number}")
        else:
            self.logger.info(f"PERMESSO: {phone_number} non è nella blacklist")
        
        # Registra nel log
        self.db.log_call(phone_number, is_blocked, caller_id)


def main():
    """Entry point per il daemon."""
    parser = argparse.ArgumentParser(
        description="Call Blocker Daemon - Blocca chiamate indesiderate su linee PSTN analogiche"
    )
    parser.add_argument(
        "--port",
        default="/dev/ttyUSB0",
        help="Porta seriale del modem (default: /dev/ttyUSB0)"
    )
    parser.add_argument(
        "--db",
        default="/var/lib/callblocker/callblocker.db",
        help="Percorso del database SQLite (default: /var/lib/callblocker/callblocker.db)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Abilita logging debug"
    )
    
    args = parser.parse_args()
    
    # Imposta livello debug se richiesto
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Avvia daemon
    daemon = CallBlockerDaemon(port=args.port, db_path=args.db)
    daemon.start()


if __name__ == "__main__":
    main()
