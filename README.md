# EMS for Fronius GEN24 (Home Assistant)

This repository implements a **deterministic, battery-aware Energy Management System (EMS)** for a **single Fronius GEN24 inverter** using **Modbus TCP**.

House **#1** is the playground.  
House **#2 / #3** reuse the same logic with different parameters.

## What this EMS is trying to accomplish

### Dayprice: self-consumption & peak shaving (“cap mode”)
During **dayprice**, we prefer to run the house on battery as much as possible. When battery SoC drops below a threshold, we enter **cap mode** and dynamically set a battery power target to keep grid import near a configured target (e.g. 3 kW). Cap mode exits via hysteresis once SoC recovers.

### Nightprice: controlled charging (optional)
During **nightprice**, the EMS may charge the battery from the grid if it started the night sufficiently low. Charging is season-aware, capped by power limits, and phase-safe.

### Night safety: protect fuses and phases
At night, EMS continuously monitors total import and per-phase currents. If limits are exceeded, forced charging is reduced/stopped and battery discharge/export can be disabled **via Modbus control registers** instead of using `power_w: 0`.

## Core design principles

1. **EMS owns the battery explicitly** when active (no hidden defaults).
2. **Never use `power_w: 0` as neutral** in this system: it can hand control back to inverter EMS and cause unintended battery export.
3. **GEN24 “allows”, battery decides**: the BYD BMS enforces real physical limits (model, modules, temp, SoC).

## Battery control registers (EMS-owned writes)

These are the only registers the EMS should write to for hard battery behavior control:

| Address | Name (EMS) | Unit | Purpose |
|---:|---|---|---|
| 40348 | Battery operation mode | enum | Selects inverter vs EMS limit modes |
| 40355 | OutWRte | W | Max discharge power (0 disables discharge/export) |
| 40356 | InWRte | W | Max charge power |

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
```

**Discharge disabled (allow charge, no export)**
```text
40348 = 3
40355 = 0
40356 = 10000
```

> **Battery-pack nuance (informational):** GEN24 can allow 10 kW, but the BYD pack may cap below that depending on model and module count. No EMS config changes are required — the BMS enforces physical limits.

## Modbus register tables

- Auto-generated register tables are in **`docs/registers.md`**.

## Repo layout

```
ems/
  modbus_gen24.yaml
  template_sensors.yaml
  scripts.yaml
  automations/
dashboards/
  ...
docs/
  registers.md
```

## Philosophy (tl;dr)

- Registers over magic
- EMS stays in control when active
- Battery BMS is the final authority
- Document everything (house #1 is the lab)
