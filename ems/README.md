# EMS Configuration & Control

This section documents how the EMS is configured, how decisions are made during day and night, and which helpers are typically adjusted on a new installation.

The EMS is designed to be **deterministic, tariff-agnostic, and portable**, relying only on local state and explicitly configured parameters.

---

## EMS Helper Cheat Sheet

Each helper has a **single responsibility**. Helpers are grouped by function to make the system easy to reason about.

> **Design principle:**  
> Tariff sensors decide *when* EMS logic applies, SoC thresholds decide *whether* it applies, and power limits decide *how hard* it acts.

### Global EMS Control

- **`input_boolean.cap_enabled`**  
  Master switch that enables or disables all EMS logic without changing configuration.

- **`input_boolean.cap_manual_override`**  
  Temporarily disables EMS cap behavior regardless of battery state or tariff conditions.

---

### Tariff Configuration (GUI-controlled)

- **`input_datetime.tariff_day_start`**  
  Time of day when dayprice begins.

- **`input_datetime.tariff_day_end`**  
  Time of day when dayprice ends.

- **`input_select.tariff_mode`**  
  Selects how tariff state is determined: automatic schedule, forced dayprice, or forced nightprice.

---

### Tariff State (Derived Sensors)

- **`binary_sensor.electricity_dayprice_active`**  
  Indicates whether the system is currently in dayprice based on tariff configuration and overrides.

- **`binary_sensor.electricity_nightprice_active`**  
  Indicates whether the system is currently in nightprice (logical inverse of dayprice).

---

### Daytime Grid Cap Mode

- **`input_number.cap_soc_start_pct`**  
  Battery SoC below which grid cap mode becomes active during dayprice.

- **`input_number.cap_soc_stop_reset_pct`**  
  Battery SoC above which grid cap mode is released again, providing hysteresis.

- **`input_number.cap_import_target_w`**  
  Desired maximum grid import power that cap mode attempts to maintain during dayprice.

- **`input_boolean.grid_cap_mode`**  
  Indicates that EMS is actively regulating battery power to cap grid import.

---

### Night Charging Eligibility & Behavior

- **`input_number.cap_night_soc_start_pct`**  
  Battery SoC threshold evaluated at the moment nightprice starts to decide whether this night should include charging at all.

- **`input_number.cap_night_soc_target_pct`**  
  Battery SoC target that night charging aims to reach if charging is enabled.

- **`input_number.cap_night_charge_power_w`**  
  Maximum power allowed for battery charging during nightprice.

- **`input_boolean.cap_night_never_charge`**  
  Hard override that forbids all night charging, typically used as a “summer mode”.

- **`input_boolean.cap_night_charge_active`**  
  Latched EMS decision indicating whether night charging is active for the current night.

---

### Night Safety Limits (Fuse & Grid Protection)

- **`input_number.cap_night_max_power_w`**  
  Maximum allowed total grid import during nightprice before charging is reduced or stopped.

- **`input_number.cap_night_max_phase_a`**  
  Maximum allowed current per phase during nightprice to protect fuses.

---

### Sensor Health & Safety Indicators

- **`binary_sensor.ems_phase_sensors_ok`**  
  Indicates that all phase current sensors are valid and within expected limits.

---

## Which Helpers You Normally Tune (New Install Guide)

On a fresh installation, **most helpers can be left at their defaults**.

### Always tune
- **`tariff_day_start` / `tariff_day_end`**
- **`cap_import_target_w`**
- **`cap_soc_start_pct` / `cap_soc_stop_reset_pct`**

### Tune once per season
- **`cap_night_soc_start_pct`**
- **`cap_night_soc_target_pct`**
- **`cap_night_charge_power_w`**
- **`cap_night_never_charge`**

### Rarely change
- **`cap_night_max_power_w`**
- **`cap_night_max_phase_a`**

---

## Day / Night Behavior Timeline

```
DAYPRICE
│  Normal operation or grid cap mode
│
└── Nightprice starts
    │  Evaluate cap_night_soc_start_pct ONCE
    │
    ├─ SoC < threshold → Night charging enabled
    └─ SoC ≥ threshold → Night charging skipped
│
└── Dayprice starts
    → Battery reset to automatic
    → Cap mode may resume
```

---

### Why `cap_night_soc_start_pct` Exists

This threshold allows the EMS to infer seasonal behavior without weather or solar forecasts, using only battery state at night start.

---

**Mental model:**  
*Tariff decides when EMS acts. SoC decides whether EMS acts. Power limits decide how hard EMS acts.*
