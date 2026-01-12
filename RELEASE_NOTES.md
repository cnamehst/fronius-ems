# fronius-ems v1.0.0 — Release Notes

**Release date:** 2026-01-09  
**Status:** First stable release for new installations

This is the first *stable* release of **fronius-ems**, designed to be installed on a clean Home Assistant system and used as the primary Energy Management System (EMS) for Fronius GEN24–based homes.

---

## 🎯 What this release is about

Version **1.0.0** marks the point where the system is:

- Predictable
- Portable between houses
- Safe for fuses and batteries
- Documented well enough for others to adopt

It is explicitly optimized for **GEN24 + BYD (HVS/HVM)** installations and Swedish/Nordic grid constraints.

---

## ✅ Highlights

### Battery & Modbus correctness
- **Battery SoC standardized to register `40351`**
- Battery minimum SoC standardized to `40350`
- Removed incorrect / misleading `40310` usage
- Battery power calculation standardized to:
  ```
  (storage_module4_dcw_raw - storage_module3_dcw_raw) * (10 ** sf)
  ```

### Robust phase & power handling
- Phase current scale factor range fixed to **-4..0**
- Phase currents clamped to sane residential limits
- All automations now use:
  ```
  | float(none) + is not none
  ```
  to avoid false trips on sensor glitches

### Clean EMS control model
- Clear separation between:
  - **Dayprice (automatic / battery-driven)**
  - **Nightprice (controlled charging + safety caps)**
- Deterministic “winter vs summer” logic based on battery SoC at night start
- Manual overrides available via helpers

### Optional Wattpilot EV control (opt‑in)
- EV logic moved into a **fully optional module**
- Gated by `input_boolean.ems_ev_enabled`
- Safe binding via helper:
  - `input_number.ems_ev_max_charging_current`
- Automatic fuse protection by temporarily reducing EV current
- No hard dependency on Wattpilot integration

### Recorder & performance
- Formalized **“do not record raw modbus sensors”** policy
- Template sensors run at lower frequency for statistics
- Reduced HA load and database churn

### Documentation & UX
- Clear README with:
  - install checklist
  - helper cheat sheet
  - day/night timeline
- Diagrams:
  - EMS flow
  - EV/Wattpilot binding
- Updated dashboards using canonical `ems_*` entities
- WordPress page included for public presentation

---

## 🧱 Intended use

This release is intended for:
- New house installs (House B / C / future)
- Clean HA instances
- Users who want *predictable energy behavior* rather than price speculation

Not included (by design):
- Nordpool
- Solcast
- Weather‑based heuristics

---

## 🔜 What’s next (not in this release)

- Adaptive charge power based on headroom
- Multi‑EV coordination
- Export‑aware strategies
- UI polish / custom cards

---

Thanks to everyone involved in testing, cross‑checking registers, and sanity‑checking assumptions.  
This release is the foundation everything else will build on.
