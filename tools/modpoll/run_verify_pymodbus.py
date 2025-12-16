#!/usr/bin/env python3
"""
Modbus register verification runner for Fronius GEN24 EMS.

- Reads a CSV "plan" (default: modpoll_verif_gen24y.csv) with columns:
  group,name,slave,fc,address,qty,type,description,expected

- Connects via Modbus TCP using pymodbus and reads each register (or block),
  printing values + short expectations.

This is designed for "house bring-up": verify that the inverter + smart meter
respond and that values look sane.

Examples:
  python3 run_verify.py --host 192.168.199.72 --port 502
  python3 run_verify.py --host 192.168.199.72 --csv tools/modpoll/modpoll_verify_gen24.csv
  python3 run_verify.py --host 192.168.199.72 --endian big --wordorder big --json out.json

Notes:
- Fronius registers are typically big-endian words. Defaults are big/big.
- This script does NOT write anything. Read-only verification.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from pymodbus.client import ModbusTcpClient


@dataclass
class PlanRow:
    group: str
    name: str
    slave: int
    fc: int
    address: int
    qty: int
    typ: str
    description: str
    expected: str


def _to_int(s: str, default: int) -> int:
    try:
        return int(str(s).strip())
    except Exception:
        return default


def load_plan(csv_path: str) -> List[PlanRow]:
    rows: List[PlanRow] = []
    with open(csv_path, "r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for line in r:
            rows.append(
                PlanRow(
                    group=(line.get("group") or "").strip(),
                    name=(line.get("name") or "").strip(),
                    slave=_to_int(line.get("slave") or "", 1),
                    fc=_to_int(line.get("fc") or "", 3),
                    address=_to_int(line.get("address") or "", 0),
                    qty=_to_int(line.get("qty") or "", 1),
                    typ=(line.get("type") or "int").strip(),
                    description=(line.get("description") or "").strip(),
                    expected=(line.get("expected") or "").strip(),
                )
            )
    # stable sort
    rows.sort(key=lambda x: (x.slave, x.address, x.name))
    return rows


def decode_int16(v: int) -> int:
    v &= 0xFFFF
    return v - 0x10000 if v & 0x8000 else v


def decode_uint16(v: int) -> int:
    return v & 0xFFFF


def decode_uint32(regs: List[int], wordorder: str, endian: str) -> int:
    """
    regs: list of 2 16-bit registers.
    wordorder: 'big' means regs[0] is high word, 'little' means regs[0] is low word.
    endian: byte endian within each 16-bit word: usually 'big' for Modbus.
    """
    if len(regs) != 2:
        raise ValueError("uint32 requires exactly 2 registers")

    w0 = regs[0] & 0xFFFF
    w1 = regs[1] & 0xFFFF

    # byte swap inside words if endian is little
    if endian == "little":
        w0 = ((w0 & 0xFF) << 8) | ((w0 >> 8) & 0xFF)
        w1 = ((w1 & 0xFF) << 8) | ((w1 >> 8) & 0xFF)

    if wordorder == "big":
        return (w0 << 16) | w1
    else:
        return (w1 << 16) | w0


def read_registers(
    client: ModbusTcpClient,
    slave: int,
    fc: int,
    address: int,
    qty: int,
    retries: int,
    retry_delay: float,
) -> Tuple[Optional[List[int]], Optional[str]]:
    for attempt in range(retries + 1):
        try:
            if fc == 3:
                rr = client.read_holding_registers(address=address, count=qty, slave=slave)
            elif fc == 4:
                rr = client.read_input_registers(address=address, count=qty, slave=slave)
            else:
                return None, f"Unsupported function code fc={fc}"

            if rr.isError():
                err = getattr(rr, "message", None) or str(rr)
                raise RuntimeError(err)

            regs = list(rr.registers or [])
            if len(regs) != qty:
                return regs, f"Short read: expected {qty}, got {len(regs)}"
            return regs, None
        except Exception as e:
            if attempt >= retries:
                return None, f"{type(e).__name__}: {e}"
            time.sleep(retry_delay)
    return None, "Unknown error"


def format_value(row: PlanRow, regs: List[int], endian: str, wordorder: str) -> Tuple[str, Any]:
    """
    Returns (pretty_string, raw_value_obj)
    """
    typ = row.typ.lower()

    if typ in ("int", "int16"):
        val = decode_int16(regs[0])
        return str(val), val

    if typ in ("uint", "uint16"):
        val = decode_uint16(regs[0])
        return str(val), val

    if typ in ("uint32",) or (typ.startswith("custom_") and row.qty == 2):
        val = decode_uint32(regs[:2], wordorder=wordorder, endian=endian)
        return str(val), val

    # Fallback: show registers
    pretty = "[" + ", ".join(str(decode_uint16(x)) for x in regs) + "]"
    raw = [decode_uint16(x) for x in regs]
    return pretty, raw


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", required=True, help="Modbus TCP host/IP (GEN24)")
    ap.add_argument("--port", type=int, default=502, help="Modbus TCP port (default: 502)")
    ap.add_argument("--csv", default="modpoll_verify_gen24.csv", help="CSV plan file (default: modpoll_verify_gen24.csv)")
    ap.add_argument("--timeout", type=float, default=3.0, help="Socket timeout seconds")
    ap.add_argument("--retries", type=int, default=1, help="Retries per read on error")
    ap.add_argument("--retry-delay", type=float, default=0.3, help="Delay between retries (seconds)")
    ap.add_argument("--endian", choices=["big", "little"], default="big", help="Byte order within 16-bit words (default: big)")
    ap.add_argument("--wordorder", choices=["big", "little"], default="big", help="Word order for 32-bit values (default: big)")
    ap.add_argument("--json", default="", help="Write results to JSON file")
    ap.add_argument("--only-slave", type=int, default=0, help="Only read this slave id (0 = all)")
    ap.add_argument("--only-group", default="", help="Only read rows matching group (substring match)")
    args = ap.parse_args()

    plan = load_plan(args.csv)

    client = ModbusTcpClient(host=args.host, port=args.port, timeout=args.timeout)
    if not client.connect():
        print(f"ERROR: could not connect to {args.host}:{args.port}", file=sys.stderr)
        return 2

    results: List[Dict[str, Any]] = []
    ok = 0
    fail = 0
    warn = 0

    try:
        for row in plan:
            if args.only_slave and row.slave != args.only_slave:
                continue
            if args.only_group and (args.only_group.lower() not in row.group.lower()):
                continue

            regs, err = read_registers(
                client=client,
                slave=row.slave,
                fc=row.fc,
                address=row.address,
                qty=row.qty,
                retries=args.retries,
                retry_delay=args.retry_delay,
            )

            status = "OK"
            value_pretty = ""
            raw_value: Any = None

            if regs is None:
                status = "FAIL"
                fail += 1
                value_pretty = ""
            else:
                value_pretty, raw_value = format_value(row, regs, endian=args.endian, wordorder=args.wordorder)
                if err:
                    status = "WARN"
                    warn += 1
                else:
                    ok += 1

            line = {
                "group": row.group,
                "name": row.name,
                "slave": row.slave,
                "fc": row.fc,
                "address": row.address,
                "qty": row.qty,
                "type": row.typ,
                "value": raw_value,
                "value_pretty": value_pretty,
                "description": row.description,
                "expected": row.expected,
                "status": status,
                "error": err or "",
            }
            results.append(line)

            # Human-friendly output
            addr = f"{row.address}".rjust(6)
            slv = f"{row.slave}".rjust(3)
            st = status.ljust(4)
            nm = (row.name[:36] + "…") if len(row.name) > 37 else row.name
            print(f"{st}  slave={slv}  fc={row.fc}  addr={addr}  qty={row.qty:<3}  {nm:<38}  -> {value_pretty}")
            if row.description or row.expected:
                if row.description:
                    print(f"      {row.description}")
                if row.expected:
                    print(f"      expect: {row.expected}")
            if err:
                print(f"      note: {err}")

    finally:
        client.close()

    print("")
    print(f"Summary: OK={ok}  WARN={warn}  FAIL={fail}")

    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "target": {"host": args.host, "port": args.port},
                    "endian": args.endian,
                    "wordorder": args.wordorder,
                    "summary": {"ok": ok, "warn": warn, "fail": fail},
                    "results": results,
                },
                f,
                ensure_ascii=False,
                indent=2,
            )
        print(f"Wrote JSON report: {args.json}")

    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
