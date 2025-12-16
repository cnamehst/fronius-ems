# Modbus registers used by this EMS

This file is **auto-generated** from `ems/modbus_gen24.yaml`.

## Notes

- Tables below list **read/telemetry** registers configured as sensors.
- Battery **control writes** are documented in the main `README.md` (40348/40355/40356), because they are written via scripts and not defined as sensors here.

## Battery SoC & limits (slave 1)

| Slave | Address | Name | Input | Data type | Scan (s) | Notes |
|---:|---:|---|---|---|---:|---|
| 1 | 40310 | `gen24_soc_raw` | holding | uint16 | 30 | Battery state of charge (SoC) raw |
| 1 | 40350 | `gen24_battery_soc_min_raw` | holding | uint16 | 60 | Battery minimum SoC setting (raw) |
| 1 | 40351 | `gen24_battery_soc_raw` | holding | uint16 | 30 | Battery SoC (alternate/raw) |

## Battery power telemetry (slave 1)

| Slave | Address | Name | Input | Data type | Scan (s) | Notes |
|---:|---:|---|---|---|---:|---|
| 1 | 40314 | `gen24_storage_module3_dcw_raw` | holding | uint16 | 2 | Battery DC power / module 3 (raw) |
| 1 | 40334 | `gen24_storage_module4_dcw_raw` | holding | uint16 | 2 | Battery DC power / module 4 (raw) |

## DC scale & misc (slave 1)

| Slave | Address | Name | Input | Data type | Scan (s) | Notes |
|---:|---:|---|---|---|---:|---|
| 1 | 40257 | `gen24_dc_power_sf` | holding | int16 | 5 | Scale factor for DC power |

## Energy & counters (slave 1)

| Slave | Address | Name | Input | Data type | Scan (s) | Notes |
|---:|---:|---|---|---|---:|---|
| 1 | 40188 | `gen24_ac_lifetime_energy_raw` | holding | custom | 60 | Lifetime AC energy (raw, custom 32-bit); count=2; struct=>L |

## Inverter AC telemetry (slave 1)

| Slave | Address | Name | Input | Data type | Scan (s) | Notes |
|---:|---:|---|---|---|---:|---|
| 1 | 30072 | `inv_ac_power_raw` | input | int16 |  | AC inverter power (raw) |
| 1 | 30081 | `inv_ac_power_sf` | input | int16 |  | Scale factor for AC power |

## PV telemetry (slave 1)

| Slave | Address | Name | Input | Data type | Scan (s) | Notes |
|---:|---:|---|---|---|---:|---|
| 1 | 30201 | `inv_pv_power_raw` | input | int16 |  | PV power (raw) |
| 1 | 30247 | `inv_pv_power_sf` | input | int16 |  | Scale factor for PV power |

## Smart meter telemetry (slave 200)

| Slave | Address | Name | Input | Data type | Scan (s) | Notes |
|---:|---:|---|---|---|---:|---|
| 200 | 40072 | `sm_current_l1_raw` | holding | int16 | 1 | Phase L1 current (raw) |
| 200 | 40073 | `sm_current_l2_raw` | holding | int16 | 1 | Phase L2 current (raw) |
| 200 | 40074 | `sm_current_l3_raw` | holding | int16 | 1 | Phase L3 current (raw) |
| 200 | 40075 | `sm_current_sf` | holding | int16 | 30 | Scale factor for phase currents |
| 200 | 40087 | `sm_power_raw` | holding | int16 | 1 | Grid power (raw) |
| 200 | 40091 | `sm_power_sf` | holding | int16 | 1 | Scale factor for grid power |
| 200 | 40115 | `sm_totwhimp_raw` | holding | uint32 | 30 | Total imported energy (raw) |
| 200 | 40123 | `sm_totwhimp_sf` | holding | int16 | 600 | Scale factor for imported energy |
