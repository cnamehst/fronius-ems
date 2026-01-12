# Fronius GEN24 – Registers used by fronius-ems

This document lists **all Modbus registers actively used by fronius-ems**, what they represent, and **how EMS uses them**.

The goal is transparency:
- You should be able to verify every value in Fronius SolarWeb / HA
- No “mystery registers”
- Easy troubleshooting when something looks wrong

---

## 🧠 Design principles

- **Only registers that have been verified in real installations are used**
- Raw Modbus sensors are *never* used directly in automations
- All logic uses validated `ems_*` template sensors
- Registers are shared between House A / House B (HVS & HVM)

---

## 🔋 Battery / Storage (GEN24)

### Battery State of Charge (SoC)

| Register | Name | Unit | Used by EMS |
|--------|------|------|-------------|
| `40351` | Battery SoC | 0.01 % | ✅ **Primary SoC** |

**Notes**
- Value example: `3150` → `31.50 %`
- This is the *only* SoC register used by EMS
- Replaces earlier incorrect assumptions about `40310`

---

### Battery Minimum SoC (reserve)

| Register | Name | Unit | Used by EMS |
|--------|------|------|-------------|
| `40350` | Minimum allowed SoC | 0.01 % | ✅ |

**Usage**
- EMS reads this value for informational purposes
- EMS can reset this register during dayprice start (battery reset)

---

### Battery Power (charge / discharge)

Battery power is derived from **two DC power registers**.

| Register | Name | Unit | Notes |
|--------|------|------|------|
| `40314` | Storage module 3 DC power | W (raw) | Signed via SF |
| `40334` | Storage module 4 DC power | W (raw) | Signed via SF |
| `40257` | DC power scale factor | 10^x | Range -4…0 |

**EMS calculation**
```
battery_power_w =
  (storage_module4_dcw_raw - storage_module3_dcw_raw)
  * (10 ** dc_power_sf)
```

**Sign convention**
- `+` → battery discharging
- `-` → battery charging

This formula has been verified on:
- BYD HVS
- BYD HVM

---

## ⚡ Grid / Smart Meter (Slave 200)

### Grid Power (import / export)

| Register | Name | Unit | Used by EMS |
|--------|------|------|-------------|
| `40087` | Total real power | W (raw) | ✅ |
| `40091` | Power scale factor | 10^x | ✅ |

**EMS calculation**
```
grid_power_w = raw * (10 ** sf)
```

Typical convention:
- `+` import
- `-` export  
(depends on meter configuration)

---

### Phase Currents (L1 / L2 / L3)

| Register | Phase | Unit |
|--------|-------|------|
| `40072` | L1 current raw | A (raw) |
| `40073` | L2 current raw | A (raw) |
| `40074` | L3 current raw | A (raw) |
| `40075` | Current scale factor | 10^x |

**Validation rules**
- Scale factor range: **-4 … 0**
- Absolute current clamp: **≤ 40 A**
- Must be updated recently (< 5s)

Only validated values are exposed as:
- `sensor.ems_grid_current_l1`
- `sensor.ems_grid_current_l2`
- `sensor.ems_grid_current_l3`

---

### Grid Import Energy (total)

| Register | Name | Unit |
|--------|------|------|
| `40115` | Imported energy | Wh (raw) |
| `40123` | Energy scale factor | 10^x |

Used for:
- Energy dashboard
- Utility meters

---

## ☀️ Solar / PV (GEN24)

### PV Power

| Register | Name | Unit |
|--------|------|------|
| `30201` | PV power raw | W |
| `30247` | PV power scale factor | 10^x |

Used for:
- Informational dashboards
- PV vs battery intuition

---

### PV / AC Energy (lifetime)

| Register | Name | Unit |
|--------|------|------|
| `40188–40189` | AC lifetime energy | Wh |

Used for:
- EMS PV energy total
- Energy dashboard

---

## 🧯 Control / Write Registers

These registers are **written by EMS scripts**.

| Register | Purpose |
|--------|---------|
| `40348` | Battery control mode |
| `40355` | Charge / discharge power limit |
| `40356` | Maximum discharge |
| `40361` | Battery enable / mode |

**Important**
- These are never written directly by automations
- Only via controlled scripts (`battery_set_power_target`, `battery_reset_*`)

---

## 🚫 Registers intentionally NOT used

| Register | Reason |
|--------|--------|
| `40310` | Unreliable / misleading SoC |
| High-frequency debug regs | Recorder & performance protection |
| Vendor-specific diagnostics | Non-portable |

---

## ✅ Summary

If a register is not listed here:
- It is **not required**
- It is **not used**
- EMS will function without it

This keeps the system:
- Predictable
- Portable
- Auditable

If Fronius firmware changes a register meaning, this file is the **single source of truth** to update.
