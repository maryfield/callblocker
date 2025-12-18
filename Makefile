.PHONY: help install uninstall test start stop restart status logs enable disable clean

help:
	@echo "Call Blocker - Comandi disponibili:"
	@echo ""
	@echo "  make install     - Installa il sistema"
	@echo "  make uninstall   - Disinstalla il sistema"
	@echo "  make test        - Testa il modem"
	@echo ""
	@echo "  make start       - Avvia il demone"
	@echo "  make stop        - Ferma il demone"
	@echo "  make restart     - Riavvia il demone"
	@echo "  make status      - Stato del servizio"
	@echo "  make logs        - Visualizza log in tempo reale"
	@echo ""
	@echo "  make enable      - Abilita avvio automatico"
	@echo "  make disable     - Disabilita avvio automatico"

install:
	sudo ./install.sh

uninstall:
	sudo ./uninstall.sh

test:
	sudo python3 test_modem.py

start:
	sudo systemctl start callblocker

stop:
	sudo systemctl stop callblocker

restart:
	sudo systemctl restart callblocker

status:
	sudo systemctl status callblocker

logs:
	sudo journalctl -u callblocker -f

enable:
	sudo systemctl enable callblocker

disable:
	sudo systemctl disable callblocker

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
