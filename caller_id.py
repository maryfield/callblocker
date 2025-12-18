"""Parsing Caller ID (CLIP)."""
import re
import logging

logger = logging.getLogger(__name__)

class CallerIDParser:
    def __init__(self):
        self.patterns = [
            re.compile(r'NMBR\s*=\s*([0-9+]+)'),
            re.compile(r'\+CLIP:\s*"([0-9+]+)"'),
            re.compile(r'CALLER\s+NUMBER:\s*([0-9+]+)'),
            re.compile(r'([0-9+]{6,})'),
        ]
        self.current_number = None
        
    def parse_line(self, line):
        if not line:
            return None
        for pattern in self.patterns:
            match = pattern.search(line)
            if match:
                number = match.group(1)
                self.current_number = self.normalize_number(number)
                logger.info(f"Caller ID rilevato: {self.current_number}")
                return self.current_number
        return None
        
    def normalize_number(self, number):
        number = number.replace(' ', '').replace('-', '')
        if number.startswith('00'):
            number = '+' + number[2:]
        return number
        
    def is_anonymous(self, number):
        if not number:
            return True
        anonymous_markers = ['ANONYMOUS', 'PRIVATE', 'WITHHELD', 'UNAVAILABLE', 'P', 'O', '']
        return number.upper() in anonymous_markers
        
    def get_current_number(self):
        return self.current_number
        
    def reset(self):
        self.current_number = None
