"""Azioni sulle chiamate."""
import time
import logging

logger = logging.getLogger(__name__)

class CallAction:
    def __init__(self, serial_handler, block_wait_time=1.5):
        self.serial = serial_handler
        self.block_wait_time = block_wait_time
        
    def block_call(self, number=None, reason="blacklist"):
        logger.info(f"Blocco chiamata da {number or 'UNKNOWN'} (motivo: {reason})")
        try:
            resp = self.serial.send_ata()
            if not resp or 'OK' not in resp:
                logger.warning("ATA non ha risposto OK")
            logger.debug(f"Attesa {self.block_wait_time}s prima di riagganciare")
            time.sleep(self.block_wait_time)
            resp = self.serial.send_ath()
            if not resp or 'OK' not in resp:
                logger.warning("ATH non ha risposto OK")
            logger.info("Chiamata bloccata con successo")
            return True
        except Exception as e:
            logger.error(f"Errore durante blocco chiamata: {e}")
            return False
            
    def ignore_call(self, number=None):
        logger.info(f"Chiamata ignorata da {number or 'UNKNOWN'}")
