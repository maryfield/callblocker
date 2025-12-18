"""Gestione della porta seriale in modalità raw bidirezionale."""
import serial
import time
import logging

logger = logging.getLogger(__name__)

class SerialHandler:
    def __init__(self, device='/dev/ttyACM0', baudrate=9600, timeout=0.1):
        self.device = device
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None
        
    def open(self):
        try:
            self.ser = serial.Serial(
                port=self.device, baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE, timeout=self.timeout,
                xonxoff=False, rtscts=False, dsrdtr=False
            )
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            logger.info(f"Porta seriale aperta: {self.device} @ {self.baudrate} baud")
            return True
        except serial.SerialException as e:
            logger.error(f"Errore apertura seriale: {e}")
            return False
            
    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            logger.info("Porta seriale chiusa")
            
    def read_line(self, timeout_override=None):
        if not self.ser or not self.ser.is_open:
            return None
        old_timeout = None
        if timeout_override is not None:
            old_timeout = self.ser.timeout
            self.ser.timeout = timeout_override
        try:
            line = self.ser.readline()
            if line:
                decoded = line.decode('ascii', errors='ignore').strip()
                if decoded:
                    logger.debug(f"RX: {decoded}")
                    return decoded
        except Exception as e:
            logger.error(f"Errore lettura seriale: {e}")
        finally:
            if old_timeout is not None:
                self.ser.timeout = old_timeout
        return None
        
    def read_available(self):
        lines = []
        while self.ser and self.ser.is_open and self.ser.in_waiting > 0:
            line = self.read_line()
            if line:
                lines.append(line)
        return lines
        
    def write_command(self, command, wait_response=True, response_timeout=2.0):
        if not self.ser or not self.ser.is_open:
            logger.error("Seriale non aperta")
            return []
        cmd_bytes = (command + '\r').encode('ascii')
        self.ser.write(cmd_bytes)
        logger.debug(f"TX: {command}")
        if not wait_response:
            return []
        response = []
        start_time = time.time()
        while (time.time() - start_time) < response_timeout:
            line = self.read_line(timeout_override=0.1)
            if line:
                response.append(line)
                if line in ['OK', 'ERROR']:
                    break
        return response
        
    def send_ata(self):
        logger.info("Invio ATA (risposta)")
        return self.write_command('ATA', wait_response=True, response_timeout=5.0)
        
    def send_ath(self):
        logger.info("Invio ATH (riattacco)")
        return self.write_command('ATH', wait_response=True, response_timeout=2.0)
        
    def initialize_modem(self):
        logger.info("Inizializzazione modem...")
        resp = self.write_command('ATZ')
        if 'OK' not in resp:
            logger.warning("ATZ non ha risposto OK")
        time.sleep(0.5)
        resp = self.write_command('ATE0')
        if 'OK' not in resp:
            logger.warning("ATE0 non ha risposto OK")
        self.write_command('ATV1')
        self.write_command('AT+VCID=1')
        logger.info("Modem inizializzato")
        return True
        
    def is_open(self):
        return self.ser and self.ser.is_open
