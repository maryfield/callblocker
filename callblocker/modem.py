"""
Modem module for Call Blocker.

Gestisce la comunicazione con il modem USB tramite comandi AT.
"""

import serial
import time
import re
import logging
from typing import Optional, Tuple

# Costanti
MODEM_BUFFER_MAX_SIZE = 1000  # Dimensione massima buffer dati modem


class ModemError(Exception):
    """Eccezione per errori del modem."""
    pass


class Modem:
    """Gestisce la comunicazione con il modem USB."""
    
    def __init__(self, port: str = "/dev/ttyUSB0", baudrate: int = 115200, timeout: int = 1):
        """
        Inizializza la connessione al modem.
        
        Args:
            port: Porta seriale del modem (es. /dev/ttyUSB0)
            baudrate: Velocità di comunicazione
            timeout: Timeout in secondi per le operazioni
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_conn = None
        self.logger = logging.getLogger(__name__)
    
    def connect(self) -> bool:
        """
        Connette al modem e lo inizializza.
        
        Returns:
            True se la connessione è riuscita
            
        Raises:
            ModemError: Se la connessione fallisce
        """
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            
            # Attendi che il modem sia pronto
            time.sleep(2)
            
            # Reset del modem
            if not self._send_command("ATZ"):
                raise ModemError("Impossibile resettare il modem")
            
            # Disabilita echo
            if not self._send_command("ATE0"):
                raise ModemError("Impossibile disabilitare echo")
            
            # Abilita Caller ID
            if not self._send_command("AT+VCID=1"):
                self.logger.warning("Caller ID potrebbe non essere supportato")
            
            # Configura per rilevare chiamate
            self._send_command("AT+CLIP=1")
            
            self.logger.info(f"Modem connesso su {self.port}")
            return True
            
        except serial.SerialException as e:
            raise ModemError(f"Errore connessione al modem: {e}")
    
    def disconnect(self):
        """Disconnette dal modem."""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            self.logger.info("Modem disconnesso")
    
    def _send_command(self, command: str, wait_response: float = 1.0) -> bool:
        """
        Invia un comando AT al modem.
        
        Args:
            command: Comando AT da inviare
            wait_response: Tempo di attesa per la risposta
            
        Returns:
            True se il comando è riuscito (risposta OK)
        """
        if not self.serial_conn or not self.serial_conn.is_open:
            return False
        
        try:
            # Svuota buffer
            self.serial_conn.reset_input_buffer()
            
            # Invia comando
            self.serial_conn.write(f"{command}\r\n".encode())
            time.sleep(wait_response)
            
            # Leggi risposta
            response = ""
            while self.serial_conn.in_waiting:
                response += self.serial_conn.read(self.serial_conn.in_waiting).decode(errors='ignore')
                time.sleep(0.1)
            
            self.logger.debug(f"Comando: {command}, Risposta: {response.strip()}")
            
            return "OK" in response
            
        except Exception as e:
            self.logger.error(f"Errore invio comando {command}: {e}")
            return False
    
    def wait_for_call(self, timeout: Optional[int] = None) -> Optional[Tuple[str, str]]:
        """
        Attende una chiamata in arrivo.
        
        Args:
            timeout: Timeout in secondi (None = infinito)
            
        Returns:
            Tupla (numero_telefono, caller_id) se chiamata rilevata, None altrimenti
        """
        if not self.serial_conn or not self.serial_conn.is_open:
            return None
        
        start_time = time.time()
        buffer = ""
        
        while True:
            if timeout and (time.time() - start_time) > timeout:
                return None
            
            if self.serial_conn.in_waiting:
                try:
                    data = self.serial_conn.read(self.serial_conn.in_waiting).decode(errors='ignore')
                    buffer += data
                    
                    # Cerca segnale di chiamata (RING)
                    if "RING" in buffer:
                        self.logger.debug(f"Chiamata rilevata: {buffer}")
                        
                        # Estrai numero chiamante
                        phone_number = self._extract_phone_number(buffer)
                        caller_id = self._extract_caller_id(buffer)
                        
                        # Pulisci buffer
                        buffer = ""
                        
                        if phone_number:
                            return (phone_number, caller_id)
                    
                    # Mantieni solo gli ultimi caratteri nel buffer
                    if len(buffer) > MODEM_BUFFER_MAX_SIZE:
                        buffer = buffer[-MODEM_BUFFER_MAX_SIZE:]
                        
                except Exception as e:
                    self.logger.error(f"Errore lettura chiamata: {e}")
            
            time.sleep(0.1)
    
    def _extract_phone_number(self, data: str) -> Optional[str]:
        """
        Estrae il numero di telefono dai dati del modem.
        
        Args:
            data: Dati ricevuti dal modem
            
        Returns:
            Numero di telefono estratto o None
        """
        # Pattern per CLIP (Calling Line Identification Presentation)
        patterns = [
            r'\+CLIP:\s*"([^"]+)"',  # +CLIP: "1234567890"
            r'NMBR\s*=\s*([0-9]+)',   # NMBR = 1234567890
            r'CALLER NUMBER:\s*([0-9]+)',  # CALLER NUMBER: 1234567890
        ]
        
        for pattern in patterns:
            match = re.search(pattern, data)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_caller_id(self, data: str) -> str:
        """
        Estrae il Caller ID (nome) dai dati del modem.
        
        Args:
            data: Dati ricevuti dal modem
            
        Returns:
            Caller ID o stringa vuota
        """
        # Pattern per nome chiamante
        patterns = [
            r'NAME\s*=\s*([^\r\n]+)',  # NAME = John Doe
            r'\+CLIP:\s*"[^"]+",\d+,"([^"]+)"',  # +CLIP: "123",129,"John Doe"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, data)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def hang_up(self) -> bool:
        """
        Rifiuta/termina una chiamata.
        
        Returns:
            True se il comando è riuscito
        """
        # ATH - Hang up
        return self._send_command("ATH")
    
    def answer_and_hangup(self) -> bool:
        """
        Risponde alla chiamata e riaggancia immediatamente (per blocco efficace).
        
        Returns:
            True se il comando è riuscito
        """
        # Risponde
        if self._send_command("ATA", wait_response=0.5):
            time.sleep(0.2)
            # Riaggancia
            return self.hang_up()
        return False
    
    def get_modem_info(self) -> dict:
        """
        Recupera informazioni sul modem.
        
        Returns:
            Dizionario con informazioni sul modem
        """
        info = {
            "port": self.port,
            "baudrate": self.baudrate,
            "connected": self.serial_conn.is_open if self.serial_conn else False
        }
        
        if self.serial_conn and self.serial_conn.is_open:
            # ATI - Manufacturer information
            self._send_command("ATI")
        
        return info
