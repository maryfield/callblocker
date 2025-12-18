#!/usr/bin/env python3
"""Call Blocker Daemon - Sistema di blocco chiamate analogiche."""
import sys
import signal
import time
import logging
import argparse
import os
from pathlib import Path

from serial_handler import SerialHandler
from ring_detector import RingDetector
from caller_id import CallerIDParser
from blacklist_filter import BlacklistFilter
from call_action import CallAction
from call_logger import CallLogger

class CallBlockerDaemon:
    def __init__(self, config):
        self.config = config
        self.running = False
        self.serial = SerialHandler(device=config['device'], baudrate=config['baudrate'])
        self.ring_detector = RingDetector(ring_timeout=config['ring_timeout'])
        self.caller_id = CallerIDParser()
        self.blacklist = BlacklistFilter(config['blacklist_file'])
        self.action = CallAction(self.serial, block_wait_time=config['block_wait_time'])
        self.logger = CallLogger(config['log_db'])
        self.current_call = {'number': None, 'ring_count': 0, 'caller_id_received': False, 'action_taken': False}
        self._setup_logging(config['log_level'])
        
    def _setup_logging(self, level_str):
        level = getattr(logging, level_str.upper(), logging.INFO)
        logging.basicConfig(level=level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                          handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler('/var/log/callblocker.log')])
        
    def start(self):
        logging.info("=== Call Blocker Daemon avvio ===")
        logging.info(f"Dispositivo: {self.config['device']}")
        logging.info(f"Black-list: {self.config['blacklist_file']}")
        if not self.serial.open():
            logging.error("Impossibile aprire la porta seriale")
            return False
        if not self.serial.initialize_modem():
            logging.error("Impossibile inizializzare il modem")
            return False
        self.running = True
        logging.info("Demone pronto, in ascolto...")
        return True
        
    def stop(self):
        logging.info("Arresto demone...")
        self.running = False
        self.serial.close()
        logging.info("Demone fermato")
        
    def reset_call_state(self):
        self.current_call = {'number': None, 'ring_count': 0, 'caller_id_received': False, 'action_taken': False}
        self.ring_detector.reset()
        self.caller_id.reset()
        
    def process_call(self):
        if self.current_call['action_taken']:
            return
        number = self.current_call['number']
        ring_count = self.current_call['ring_count']
        is_blocked, reason = self.blacklist.is_blocked(number)
        if is_blocked:
            logging.info(f"Chiamata BLOCCATA: {number or 'ANONYMOUS'} ({reason})")
            self.action.block_call(number, reason)
            self.logger.log_call(number=number, action='blocked', reason=reason, ring_count=ring_count)
            self.current_call['action_taken'] = True
        else:
            logging.info(f"Chiamata PERMESSA: {number or 'UNKNOWN'} ({reason})")
            self.logger.log_call(number=number, action='allowed', reason=reason, ring_count=ring_count)
            self.current_call['action_taken'] = True
            
    def main_loop(self):
        last_blacklist_check = time.time()
        while self.running:
            try:
                if time.time() - last_blacklist_check > 2.0:
                    self.blacklist.check_reload()
                    last_blacklist_check = time.time()
                lines = self.serial.read_available()
                for line in lines:
                    ring_event = self.ring_detector.process_line(line)
                    if ring_event:
                        if ring_event['type'] == 'ring':
                            self.current_call['ring_count'] = ring_event['count']
                            if ring_event['count'] == 1:
                                logging.info("Prima squillo, attesa Caller ID...")
                        elif ring_event['type'] == 'timeout':
                            if self.current_call['ring_count'] > 0:
                                logging.info("Timeout RING, reset stato")
                                self.reset_call_state()
                    number = self.caller_id.parse_line(line)
                    if number:
                        self.current_call['number'] = number
                        self.current_call['caller_id_received'] = True
                        self.process_call()
                if (self.ring_detector.is_ringing() and not self.current_call['caller_id_received'] and
                    not self.current_call['action_taken'] and self.current_call['ring_count'] >= 2):
                    logging.info("Caller ID non ricevuto, processo chiamata come anonima")
                    self.current_call['number'] = None
                    self.current_call['caller_id_received'] = True
                    self.process_call()
                time.sleep(0.05)
            except KeyboardInterrupt:
                logging.info("Ricevuto SIGINT")
                break
            except Exception as e:
                logging.error(f"Errore nel main loop: {e}", exc_info=True)
                time.sleep(1)
        self.stop()

def load_config(config_file):
    return {
        'device': '/dev/ttyACM0', 'baudrate': 9600, 'ring_timeout': 8.0,
        'clip_wait_timeout': 3.0, 'block_wait_time': 1.5,
        'blacklist_file': '/var/lib/callblocker/blacklist.json',
        'log_db': '/var/lib/callblocker/calls.db', 'log_level': 'INFO'
    }

def main():
    parser = argparse.ArgumentParser(description='Call Blocker Daemon')
    parser.add_argument('-c', '--config', help='File configurazione', default='/etc/callblocker/daemon.conf')
    parser.add_argument('-d', '--device', help='Device seriale', default='/dev/ttyACM0')
    parser.add_argument('-v', '--verbose', action='store_true', help='Modalità verbose (DEBUG)')
    args = parser.parse_args()
    config = load_config(args.config)
    if args.device:
        config['device'] = args.device
    if args.verbose:
        config['log_level'] = 'DEBUG'
    daemon = CallBlockerDaemon(config)
    def signal_handler(signum, frame):
        logging.info(f"Ricevuto segnale {signum}")
        daemon.stop()
        sys.exit(0)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    if daemon.start():
        daemon.main_loop()
    else:
        logging.error("Impossibile avviare il demone")
        sys.exit(1)

if __name__ == '__main__':
    main()
