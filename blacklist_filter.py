"""Gestione black-list con ricarica runtime."""
import json
import os
import logging

logger = logging.getLogger(__name__)

class BlacklistFilter:
    def __init__(self, blacklist_file):
        self.blacklist_file = blacklist_file
        self.enabled = True
        self.numbers = set()
        self.prefixes = []
        self.block_anonymous = False
        self.last_mtime = 0
        self.load()
        
    def load(self):
        try:
            if not os.path.exists(self.blacklist_file):
                self._create_empty_blacklist()
            with open(self.blacklist_file, 'r') as f:
                data = json.load(f)
            self.enabled = data.get('enabled', True)
            self.numbers = set(data.get('numbers', []))
            self.prefixes = data.get('prefixes', [])
            self.block_anonymous = data.get('block_anonymous', False)
            self.last_mtime = os.path.getmtime(self.blacklist_file)
            logger.info(f"Black-list caricata: {len(self.numbers)} numeri, {len(self.prefixes)} prefissi")
        except Exception as e:
            logger.error(f"Errore caricamento black-list: {e}")
            
    def _create_empty_blacklist(self):
        default_data = {"enabled": True, "block_anonymous": False, "numbers": [], "prefixes": []}
        os.makedirs(os.path.dirname(self.blacklist_file), exist_ok=True)
        with open(self.blacklist_file, 'w') as f:
            json.dump(default_data, f, indent=2)
        logger.info(f"Creato file black-list vuoto: {self.blacklist_file}")
        
    def check_reload(self):
        try:
            if not os.path.exists(self.blacklist_file):
                return
            mtime = os.path.getmtime(self.blacklist_file)
            if mtime > self.last_mtime:
                logger.info("Rilevata modifica black-list, ricarico...")
                self.load()
        except Exception as e:
            logger.error(f"Errore check reload: {e}")
            
    def is_blocked(self, number):
        if not self.enabled:
            return False, "filter_disabled"
        if not number or number.upper() in ['ANONYMOUS', 'PRIVATE', 'WITHHELD', 'UNAVAILABLE']:
            if self.block_anonymous:
                return True, "anonymous"
            return False, "anonymous_allowed"
        if number in self.numbers:
            return True, f"exact_match:{number}"
        for prefix in self.prefixes:
            if number.startswith(prefix):
                return True, f"prefix_match:{prefix}"
        return False, "not_in_blacklist"
