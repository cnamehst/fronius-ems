# EMS for Fronius GEN24 (Home Assistant)

This repository implements a **deterministic, battery-aware Energy Management System (EMS)** for a **single Fronius GEN24 inverter** using **Modbus TCP**.

House **#1** is the playground.  
House **#2 / #3** reuse the same logic with different parameters.

---

## What this EMS is trying to accomplish

### Dayprice: self-consumption & peak shaving (“cap mode”)
During **dayprice**, we prefer to run the house on battery as much as possible. When battery SoC drops below a threshold, we enter **cap mode** and dynamically set a battery power target to keep grid import near a configured target (e.g. 3 kW). Cap mode exits via hysteresis once SoC recovers.

### Nightprice: controlled charging (optional)
During **nightprice**, the EMS may charge the battery from the grid if it started the night sufficiently low. Charging is season-aware (“winter logic”), capped by power limits, and phase-safe.

### Night safety: protect fuses and phases
At night, EMS continuously monitors **total import** and **per-phase currents**. If limits are exceeded, forced charging is reduced/stopped and battery discharge/export can be disabled **via Modbus control registers**.

---

## Core design principles

1. **Raw Modbus = plumbing.** Not for dashboards. Not for statistics. Not for Energy.
2. **EMS sensors = products.** Validated, stable, suitable for dashboards and Energy.
3. **EMS owns the battery explicitly** when active (no hidden defaults).
4. **Avoid handing control back implicitly.** When the EMS is responsible, it should stay responsible.
5. **BYD BMS is final authority.** The inverter can “allow”, but the battery decides actual limits.

---

## Performance & stability (IMPORTANT)

Home Assistant can become slow if you:
- poll lots of Modbus sensors at 1s
- record raw sensors in the database
- produce long-term statistics from noisy/raw sensors

### The EMS approach
- Raw Modbus sensors are polled at a reasonable cadence (typically **5s**; slower where appropriate).
- Raw sensors are excluded from recorder.
- EMS template sensors are **time-triggered** to reduce CPU churn and database writes.

### Update cadence used by EMS template sensors
| Category | Examples | Cadence |
|---|---|---|
| Power + phase currents | EMS Grid Power, EMS PV Power, EMS Battery Power, EMS Grid Current L1/L2/L3 | Every **5s** |
| Battery SoC | EMS Battery SoC, EMS Battery SoC Minimum | Every **30s** |
| Energy totals | EMS Grid Import Energy Total, EMS PV Energy Total | Every **60s** |

> Tip: Use only `sensor.ems_*` in dashboards and automations. Keep raw sensors as internal plumbing.

---

## Battery control registers (EMS-owned writes)

These are the only registers the EMS should write to for hard battery behavior control:

| Address | Name (EMS) | Unit | Purpose |
|---:|---|---|---|
| 40348 | Battery operation mode | enum | Selects inverter vs EMS limit modes |
| 40355 | OutWRte | reg | Max discharge power limit (register encoding) |
| 40356 | InWRte | reg | Max charge power limit (register encoding) |

### 40348 operation mode semantics
| Value | Meaning |
|---:|---|
| 0 | Normal/default: inverter manages charging/discharging automatically |
| 1 | Activates discharge limit using OutWRte (40355) |
| 2 | Charge only (typically paired with OutWRte=0) |
| 3 | Activates **both** charge and discharge limits using InWRte (40356) and OutWRte (40355) |

### Mode patterns used by this EMS

**Normal operation (“let GEN24 handle it”)**
```text
40348 = 0
40355 = 10000
40356 = 10000