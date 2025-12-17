"""
Database module for Call Blocker.

Gestisce il database SQLite per blacklist e logging delle chiamate.
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Tuple, Optional


class CallBlockerDB:
    """Gestisce il database SQLite per blacklist e call logs."""
    
    def __init__(self, db_path: str = "/var/lib/callblocker/callblocker.db"):
        """
        Inizializza il database.
        
        Args:
            db_path: Percorso del file database SQLite
        """
        self.db_path = db_path
        
        # Crea la directory se non esiste
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self._init_database()
    
    def _init_database(self):
        """Inizializza le tabelle del database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabella blacklist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS blacklist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone_number TEXT UNIQUE NOT NULL,
                description TEXT,
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabella call logs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS call_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone_number TEXT NOT NULL,
                call_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                blocked BOOLEAN NOT NULL,
                caller_id TEXT
            )
        """)
        
        # Indici per performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_blacklist_phone 
            ON blacklist(phone_number)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_call_logs_date 
            ON call_logs(call_date)
        """)
        
        conn.commit()
        conn.close()
    
    def add_to_blacklist(self, phone_number: str, description: str = "") -> bool:
        """
        Aggiunge un numero alla blacklist.
        
        Args:
            phone_number: Numero di telefono da bloccare
            description: Descrizione opzionale
            
        Returns:
            True se aggiunto con successo, False se già presente
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO blacklist (phone_number, description) VALUES (?, ?)",
                (phone_number, description)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            if conn:
                conn.close()
    
    def remove_from_blacklist(self, phone_number: str) -> bool:
        """
        Rimuove un numero dalla blacklist.
        
        Args:
            phone_number: Numero di telefono da rimuovere
            
        Returns:
            True se rimosso con successo, False se non presente
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM blacklist WHERE phone_number = ?",
                (phone_number,)
            )
            affected = cursor.rowcount
            conn.commit()
            return affected > 0
        finally:
            if conn:
                conn.close()
    
    def is_blacklisted(self, phone_number: str) -> bool:
        """
        Verifica se un numero è nella blacklist.
        
        Args:
            phone_number: Numero di telefono da verificare
            
        Returns:
            True se il numero è blacklisted, False altrimenti
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM blacklist WHERE phone_number = ?",
                (phone_number,)
            )
            count = cursor.fetchone()[0]
            return count > 0
        finally:
            if conn:
                conn.close()
    
    def get_blacklist(self) -> List[Tuple[str, str, str]]:
        """
        Recupera tutti i numeri nella blacklist.
        
        Returns:
            Lista di tuple (phone_number, description, added_date)
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT phone_number, description, added_date FROM blacklist ORDER BY added_date DESC"
            )
            results = cursor.fetchall()
            return results
        finally:
            if conn:
                conn.close()
    
    def log_call(self, phone_number: str, blocked: bool, caller_id: str = "") -> None:
        """
        Registra una chiamata nel log.
        
        Args:
            phone_number: Numero chiamante
            blocked: True se la chiamata è stata bloccata
            caller_id: Identificativo chiamante (se disponibile)
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO call_logs (phone_number, blocked, caller_id) VALUES (?, ?, ?)",
                (phone_number, blocked, caller_id)
            )
            conn.commit()
        finally:
            if conn:
                conn.close()
    
    def get_call_logs(self, limit: int = 100, blocked_only: bool = False) -> List[Tuple]:
        """
        Recupera i log delle chiamate.
        
        Args:
            limit: Numero massimo di record da recuperare
            blocked_only: Se True, mostra solo chiamate bloccate
            
        Returns:
            Lista di tuple (phone_number, call_date, blocked, caller_id)
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT phone_number, call_date, blocked, caller_id FROM call_logs"
            if blocked_only:
                query += " WHERE blocked = 1"
            query += " ORDER BY call_date DESC LIMIT ?"
            
            cursor.execute(query, (limit,))
            results = cursor.fetchall()
            return results
        finally:
            if conn:
                conn.close()
    
    def get_statistics(self) -> dict:
        """
        Recupera statistiche sulle chiamate.
        
        Returns:
            Dizionario con statistiche
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Totale chiamate
            cursor.execute("SELECT COUNT(*) FROM call_logs")
            total_calls = cursor.fetchone()[0]
            
            # Chiamate bloccate
            cursor.execute("SELECT COUNT(*) FROM call_logs WHERE blocked = 1")
            blocked_calls = cursor.fetchone()[0]
            
            # Numeri in blacklist
            cursor.execute("SELECT COUNT(*) FROM blacklist")
            blacklist_count = cursor.fetchone()[0]
            
            return {
                "total_calls": total_calls,
                "blocked_calls": blocked_calls,
                "allowed_calls": total_calls - blocked_calls,
                "blacklist_count": blacklist_count
            }
        finally:
            if conn:
                conn.close()
