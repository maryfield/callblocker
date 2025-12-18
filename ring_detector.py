"""Rilevamento eventi RING dalla seriale."""
import time
import logging

logger = logging.getLogger(__name__)

class RingDetector:
    def __init__(self, ring_timeout=8.0):
        self.ring_timeout = ring_timeout
        self.ring_count = 0
        self.last_ring_time = None
        self.in_call_state = False
        
    def reset(self):
        if self.ring_count > 0:
            logger.debug(f"Reset ring counter (era {self.ring_count})")
        self.ring_count = 0
        self.last_ring_time = None
        self.in_call_state = False
        
    def process_line(self, line):
        current_time = time.time()
        if self.last_ring_time and (current_time - self.last_ring_time) > self.ring_timeout:
            self.reset()
            return {'type': 'timeout'}
        if line.upper().startswith('RING'):
            self.ring_count += 1
            self.last_ring_time = current_time
            self.in_call_state = True
            logger.info(f"RING rilevato (count: {self.ring_count})")
            return {'type': 'ring', 'count': self.ring_count, 'timestamp': current_time}
        return None
        
    def get_ring_count(self):
        return self.ring_count
        
    def is_ringing(self):
        if not self.in_call_state:
            return False
        current_time = time.time()
        if self.last_ring_time and (current_time - self.last_ring_time) > self.ring_timeout:
            self.reset()
            return False
        return True
