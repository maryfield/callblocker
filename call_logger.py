"""Logging chiamate su SQLite."""
import sqlite3
import logging
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class CallLogger:
    def __init__(self, db_file):
        self.db_file = db_file
        self._init_database()
        
    def _init_database(self):
        try:
            os.makedirs(os.path.dirname(self.db_file), exist_ok=True)
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS calls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    number TEXT,
                    action TEXT NOT NULL,
                    reason TEXT,
                    ring_count INTEGER,
                    notes TEXT
                )
            ''')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON calls(timestamp DESC)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_number ON calls(number)')
            conn.commit()
            conn.close()
            logger.info(f"Database inizializzato: {self.db_file}")
        except Exception as e:
            logger.error(f"Errore inizializzazione database: {e}")
            
    def log_call(self, number=None, action='unknown', reason=None, ring_count=0, notes=None):
        try:
            timestamp = datetime.now().isoformat()
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO calls (timestamp, number, action, reason, ring_count, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (timestamp, number, action, reason, ring_count, notes))
            conn.commit()
            conn.close()
            logger.info(f"Chiamata registrata: {number or 'UNKNOWN'} - {action} - {reason}")
            return True
        except Exception as e:
            logger.error(f"Errore registrazione chiamata: {e}")
            return False
            
    def get_recent_calls(self, limit=50):
        try:
            conn = sqlite3.connect(self.db_file)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM calls ORDER BY timestamp DESC LIMIT ?', (limit,))
            rows = cursor.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Errore recupero chiamate: {e}")
            return []
            
    def get_stats(self):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM calls')
            total = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM calls WHERE action = 'blocked'")
            blocked = cursor.fetchone()[0]
            today = datetime.now().date().isoformat()
            cursor.execute('SELECT COUNT(*) FROM calls WHERE date(timestamp) = ?', (today,))
            today_count = cursor.fetchone()[0]
            conn.close()
            return {'total_calls': total, 'blocked_calls': blocked, 'allowed_calls': total - blocked, 'today_calls': today_count}
        except Exception as e:
            logger.error(f"Errore calcolo statistiche: {e}")
            return {}
            
    def search_by_number(self, number):
        try:
            conn = sqlite3.connect(self.db_file)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM calls WHERE number = ? ORDER BY timestamp DESC', (number,))
            rows = cursor.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Errore ricerca numero: {e}")
            return []
