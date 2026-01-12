# EMS for Fronius GEN24 (Home Assistant)

**An open, deterministic Energy Management System for Fronius GEN24 – built by CNAME AB, with help from ChatGPT and Claude.ai.**

---

## What this is

This project is a **practical, production‑tested EMS** for homes using:

- Fronius **GEN24** inverters  
- BYD **HVS / HVM** batteries  
- Home Assistant as the orchestration layer  

It was built because existing “smart” solutions often suffer from one or more of these problems:

- opaque logic (“why did it do that?”)
- cloud dependency
- over‑optimization based on forecasts
- poor fuse protection
- high database load from raw sensors

This EMS takes a different approach.

---

## Design philosophy

**Predictability beats cleverness.**

The system is intentionally built around:
- deterministic rules
- explicit thresholds
- local control only
- clear separation between *measurement*, *decision*, and *action*

No Nordpool.  
No Solcast.  
No weather guesses.

Just **measured reality**, tariffs, and safety limits.

---

## What EMS does

### 1. Dayprice (normal operation)
- Battery runs the house automatically
- Grid import is allowed
- Battery is protected by a minimum SoC
- No artificial limits unless needed

At dayprice start, EMS:
- resets battery control back to Fronius “automatic”
- clears any night charging state
- prepares for cap mode if needed later

---

### 2. Cap mode (daytime fuse protection)
When battery SoC drops below a configured threshold:
- EMS enables *grid cap mode*
- Grid import is limited (e.g. 3 kW)
- Battery is trickle‑charged just enough to avoid collapse
- Fuse limits are respected at all times

When SoC recovers:
- Cap mode disengages automatically
- Battery returns to normal operation

This avoids:
- peak‑tariff penalties
- main fuse trips
- oscillating charge/discharge behavior

---

### 3. Nightprice charging (optional, controlled)
At nightprice start:
- EMS decides if charging is needed based on **actual battery SoC**
- This doubles as a **winter/summer heuristic**
  - Low SoC → winter → charge
  - High SoC → summer → skip charging

Charging:
- happens at a fixed, user‑defined power
- stops at a target SoC
- is guarded by grid import and phase current limits

A manual “never night charge” (summer mode) override is always available.

---

### 4. Optional EV (Wattpilot) control
If enabled:
- EMS can bind to a Fronius Wattpilot charger
- EV charging is allowed during nightprice
- Phase currents and import limits are enforced
- EMS can temporarily reduce EV current to protect fuses

If not enabled:
- EMS does **nothing** with EVs

---

## What EMS deliberately does NOT do

- No price prediction
- No solar forecast dependency
- No battery cycling for “optimization”
- No cloud services
- No writing Modbus registers from automations directly

Everything is:
- local
- auditable
- reversible

---

## Architecture overview

```
Modbus (raw, fast, noisy)
        ↓
Template sensors (ems_*)
        ↓
Decision automations
        ↓
Scripted register writes
```

Raw Modbus sensors:
- are *never* used directly in logic
- are excluded from long‑term statistics

---

## Supported hardware

- Fronius GEN24 (tested on 8.0 / 10.0)
- BYD Battery‑Box Premium HVS & HVM
- Fronius Smart Meter (Modbus TCP)
- Fronius Wattpilot (optional)

---

## Installation model

This repository is designed to be:

- cloned into a **clean Home Assistant install**
- included using **native HA includes**
- configured mostly via **helpers in the UI**

EMS assumes it is the *first* system you install.
Anything added later is outside its scope.

---

## Documentation

- `docs/registers.md` — all Modbus registers used and why
- `VERSION.md` — current version
- `CHANGELOG.md` — historical changes
- Dashboards — EMS status, configuration, sensors

---

## Credits

This system was designed and implemented by **CNAME AB**  
with iterative reasoning and validation assisted by:

- **ChatGPT** (architecture, automation structure, documentation)
- **Claude.ai** (cross‑checking assumptions, alternative perspectives)

The final decisions, testing, and responsibility remain human.

---

## License & intent

This project is published openly to:
- help other Fronius GEN24 owners
- encourage transparent energy control
- avoid vendor lock‑in

Use it, adapt it, learn from it.

If you improve it — please share back.

---

*“Simple systems fail less often — and are easier to fix when they do.”*
