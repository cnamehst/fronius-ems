EMS Helper Cheat Sheet

This section documents all Home Assistant helpers used by the EMS package.
Each helper has one clear responsibility, and helpers are grouped by function.

Design principle:
Tariff sensors decide when EMS logic applies, SoC thresholds decide whether it applies, and power limits decide how hard it acts.

⸻

Global EMS Control
	•	input_boolean.cap_enabled
Master switch that enables or disables all EMS logic without changing any configuration.
	•	input_boolean.cap_manual_override
Temporarily disables EMS cap behavior regardless of battery state or tariff conditions.

⸻

Tariff Configuration (GUI-controlled)
	•	input_datetime.tariff_day_start
Time of day when dayprice begins.
	•	input_datetime.tariff_day_end
Time of day when dayprice ends.
	•	input_select.tariff_mode
Selects how tariff state is determined: automatic schedule, forced dayprice, or forced nightprice.

⸻

Tariff State (Derived Sensors)
	•	binary_sensor.electricity_dayprice_active
Indicates whether the system is currently in dayprice based on tariff configuration and overrides.
	•	binary_sensor.electricity_nightprice_active
Indicates whether the system is currently in nightprice (logical inverse of dayprice).

⸻

Daytime Grid Cap Mode
	•	input_number.cap_soc_start_pct
Battery SoC below which grid cap mode becomes active during dayprice.
	•	input_number.cap_soc_stop_reset_pct
Battery SoC above which grid cap mode is released again, providing hysteresis.
	•	input_number.cap_import_target_w
Desired maximum grid import power that cap mode attempts to maintain during dayprice.
	•	input_boolean.grid_cap_mode
Indicates that EMS is actively regulating battery power to cap grid import.

⸻

Night Charging Eligibility & Behavior
	•	input_number.cap_night_soc_start_pct
Battery SoC threshold evaluated at the moment nightprice starts to decide whether this night should include charging at all.
	•	input_number.cap_night_soc_target_pct
Battery SoC target that night charging aims to reach if charging is enabled.
	•	input_number.cap_night_charge_power_w
Maximum power allowed for battery charging during nightprice.
	•	input_boolean.cap_night_never_charge
Hard override that forbids all night charging, typically used as a “summer mode”.
	•	input_boolean.cap_night_charge_active
Latched EMS decision indicating whether night charging is active for the current night.

⸻

Night Safety Limits (Fuse & Grid Protection)
	•	input_number.cap_night_max_power_w
Maximum allowed total grid import during nightprice before charging is reduced or stopped.
	•	input_number.cap_night_max_phase_a
Maximum allowed current per phase during nightprice to protect fuses.

⸻

Sensor Health & Safety Indicators
	•	binary_sensor.ems_phase_sensors_ok
Indicates that all phase current sensors are valid and within expected limits.

⸻

Battery Control Scripts (Operational)
	•	script.battery_set_power_target
Low-level EMS control that sets a signed battery power target via Fronius Modbus registers.
	•	script.battery_reset_charging_5_int
Resets the battery to Fronius automatic control when EMS releases ownership.

⸻

Conceptual Summary
	•	Tariff helpers decide when EMS logic applies
	•	SoC helpers decide whether EMS acts
	•	Power/current helpers decide how hard EMS acts
	•	State booleans show what EMS has decided, not user intent

This separation keeps the EMS deterministic, debuggable, and portable across installations.

⸻

If you want next, I can:
	•	Integrate this seamlessly into your existing README structure
	•	Add a short “Which helpers you normally tune” section for new installs
	•	Add a diagram-style markdown timeline for day/night behavior