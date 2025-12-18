#!/usr/bin/env python3
"""Script di test per verificare il funzionamento del modem."""
import serial
import time
import sys

DEVICE = '/dev/ttyACM0'
BAUDRATE = 9600

def test_serial_open():
    print(f"[TEST] Apertura {DEVICE}...")
    try:
        ser = serial.Serial(port=DEVICE, baudrate=BAUDRATE, bytesize=serial.EIGHTBITS,
                          parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                          timeout=1.0, xonxoff=False, rtscts=False, dsrdtr=False)
        print(f"✓ Porta aperta con successo")
        print(f"  Baudrate: {ser.baudrate}")
        print(f"  Bytesize: {ser.bytesize}")
        print(f"  Parity: {ser.parity}")
        return ser
    except Exception as e:
        print(f"✗ ERRORE apertura: {e}")
        return None

def test_at_commands(ser):
    print("\n[TEST] Comandi AT...")
    commands = [('ATZ', 'Reset modem'), ('ATE0', 'Echo off'), ('ATV1', 'Verbose on'), ('AT+VCID=1', 'Abilita Caller ID')]
    for cmd, desc in commands:
        print(f"\nInvio: {cmd} ({desc})")
        ser.write((cmd + '\r').encode('ascii'))
        time.sleep(0.5)
        response = []
        while ser.in_waiting > 0:
            line = ser.readline().decode('ascii', errors='ignore').strip()
            if line:
                response.append(line)
                print(f"  RX: {line}")
        if 'OK' in response:
            print(f"  ✓ {desc} OK")
        else:
            print(f"  ⚠ {desc} - risposta inattesa")

def test_ring_detection(ser):
    print("\n[TEST] Rilevamento RING...")
    print("\n" + "="*60)
    print("FAI SQUILLARE IL TELEFONO ORA!")
    print("Premi Ctrl+C per terminare il test")
    print("="*60 + "\n")
    ring_count = 0
    try:
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('ascii', errors='ignore').strip()
                if line:
                    print(f"RX: {line}")
                    if line.upper().startswith('RING'):
                        ring_count += 1
                        print(f"  >>> RING #{ring_count} rilevato!")
                    if 'NMBR' in line.upper() or 'CLIP' in line.upper():
                        print(f"  >>> Caller ID rilevato!")
            time.sleep(0.1)
    except KeyboardInterrupt:
        print(f"\n\nTest terminato.")
        print(f"RING rilevati: {ring_count}")
        if ring_count > 0:
            print("✓ Modem funziona correttamente!")
        else:
            print("⚠ Nessun RING rilevato. Hai fatto squillare il telefono?")

def main():
    print("="*60)
    print("CALL BLOCKER - TEST MODEM")
    print("="*60)
    ser = test_serial_open()
    if not ser:
        print(f"\n✗ ERRORE: Impossibile aprire la porta seriale")
        print(f"\nVerifica:")
        print(f"  1. Il modem è collegato? ls -l {DEVICE}")
        print(f"  2. Hai i permessi? groups | grep dialout")
        print(f"  3. Device corretto? dmesg | grep tty")
        sys.exit(1)
    test_at_commands(ser)
    test_ring_detection(ser)
    ser.close()
    print("\nPorta seriale chiusa.")

if __name__ == '__main__':
    main()
