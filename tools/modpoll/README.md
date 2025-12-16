# Modbus verification (House bring-up)

This folder contains a register verification plan used when onboarding a new GEN24 inverter.

- `modpoll_verify_gen24.csv` is the source of truth (registers + expectations)
- `run_verify.py` reads the CSV and runs checks (via modpoll config file or native pymodbus)

Usage examples:
- python3 run_verify.py --host 192.168.x.y --port 502 --backend pymodbus
- python3 run_verify.py --host 192.168.x.y --port 502 --backend modpoll --modpoll /usr/bin/modpoll


