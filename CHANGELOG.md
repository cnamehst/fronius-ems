# Changelog — fronius-ems

All notable changes to this project are documented here.

The format is based on *Keep a Changelog*, and this project adheres to *Semantic Versioning*.

---

## [1.0.0] — 2026-01-09

### Added
- First stable EMS package for Fronius GEN24
- Optional Wattpilot EV control module (opt‑in)
- EMS health binary sensor
- Phase sensor validation and clamping
- Dashboards:
  - EMS configuration
  - EMS sensors
  - EMS overview tile
- EV binding diagram
- WordPress project page (HTML)

### Changed
- Battery SoC source standardized to Modbus register `40351`
- Battery minimum SoC standardized to `40350`
- Battery power calculation standardized to `(raw4 - raw3)`
- Phase current scale factor range expanded to `-4..0`
- All automations updated to treat unavailable sensors as unknown
- Recorder configuration formalized to exclude raw Modbus sensors
- Canonical `ems_*` entity naming enforced across dashboards and automations

### Removed
- Incorrect / misleading battery SoC register `40310`
- Hard‑coded Wattpilot dependencies
- Direct automation use of raw Modbus sensors
- High‑frequency statistics on volatile raw sensors

### Fixed
- False fuse‑trip behavior caused by transient Modbus glitches
- Phase current spikes caused by invalid scale factors
- Inconsistent naming between dashboards and logic
- Night charging edge cases when sensors go unavailable

---

## [Unreleased]
- Adaptive EV throttling
- Export‑aware night charging
- Multi‑inverter support
- Custom Lovelace cards
