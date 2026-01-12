# fronius-ems – Version 1.0.0

## Summary
First stable release intended for clean installs in a new house.

## Major changes since previous iteration
- Battery SoC standardized to Modbus register **40351**; removed incorrect **40310** usage.
- Battery SoC minimum standardized to **40350**.
- Battery power standardized to **(storage_module4 - storage_module3) * (10 ** sf)**.
- Phase current scale factor range fixed to **-4..0** and currents clamped to sane values.
- Automations updated to treat invalid/unavailable phase values as unknown (use `float(none)` guards).
- Wattpilot EV control moved to an **optional module** and is gated by `input_boolean.ems_ev_enabled` and entity availability.
- Added portable EV binding helper: `input_number.ems_ev_max_charging_current` (A).
- Docs: added EV binding diagram and instructions for renaming Wattpilot entities.
