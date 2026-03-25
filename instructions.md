# Complete Guide: Using the Keithley DMM7510 + Running Code (Current Repo, 4-Wire Mode)

## 1. What the Keithley DMM7510 Does (in this project)

Measures electrical resistance very accurately.

In this project:
- Uses 4-wire resistance mode (`FRES`)
- Controlled using Python + PyVISA + SCPI
- Can output:
- Resistance (ohms)
- Conductivity if sample geometry is provided

## 2. Physical Setup (Very Important)

### 4-Wire Connection (Correct Wiring)

You should use 4 leads:

| Connection | Purpose |
| --- | --- |
| INPUT HI | Current |
| INPUT LO | Current |
| SENSE HI | Voltage |
| SENSE LO | Voltage |

Steps:
1. Connect 2 wires for current.
2. Connect 2 wires for voltage sensing.
3. Attach them to the sample securely.

This setup helps remove error caused by the test leads and contact resistance.

## 3. Using the Instrument (Front Panel Setup)

Basic setup on the instrument:
1. Power on the DMM7510.
2. Select 4-wire resistance / 4W ohm mode.
3. In settings, keep these enabled if available:
- Auto Range
- Auto Zero
4. Return to the home screen.

Note:
- Your Python code also sends setup commands, so the remote code configuration is the main thing that matters.

## 4. Important Settings (Simple Explanation)

### NPLC

- Low (0.1) = faster, more noise
- Medium (1) = balanced
- High (10) = slower, more stable

In this repo:
- Default examples mostly use `10.0`
- You can change it with `--nplc`

### Averaging

Your code takes multiple readings and averages them to reduce fluctuations.

In this repo:
- `measure-once` averages multiple samples
- `resistance-loop` averages samples for each displayed reading

### Delay Between Samples

Your code also waits a short amount of time between readings when averaging.

## 5. Connecting to Your Laptop

Step 1: Install the needed software
- NI-VISA
- Python dependencies for the project

Step 2: Verify the instrument is detected

You should see a VISA resource like:

```text
USB0::0x05E6::7510::XXXX::INSTR
```

Step 3: Use the repo config
- You can put the VISA name in `.env`
- Variable used by this repo:

```text
VISA_RESOURCE=USB0::...::INSTR
```

If `VISA_RESOURCE` is not set, the code tries to open the first available VISA instrument.

## 6. SCPI Commands (What This Code Actually Sends)

This repo currently uses these core commands:

```text
*RST
:SENS:FUNC "FRES"
:SENS:FRES:RANG:AUTO ON
:SENS:FRES:NPLC 10.0
:SENS:FRES:AZER ON
*CLS
:MEAS:FRES?
```

What they mean:
- `FRES` = 4-wire resistance mode
- `RANG:AUTO ON` = auto range
- `NPLC` = integration time / noise filtering
- `AZER ON` = auto zero
- `:MEAS:FRES?` = take one 4-wire resistance reading

Important repo note:
- The current code uses `:MEAS:FRES?`
- It does not currently send `:SENS:FRES:OCOM ON`
- It also does not use `:READ?` in the measurement helper

## 7. Running Your Code (Actual Workflow for This Repo)

Step-by-step

### a. Connect everything

- Sample mounted
- 4 wires connected
- USB connected to laptop

### b. Open terminal in the project folder

```bash
cd dmm7510-python-interface
```

### c. Run a single measurement

```bash
measure-once --count 50 --delay-s 0.05 --nplc 10
```

Optional additions:

```bash
measure-once --count 50 --delay-s 0.05 --nplc 10 --visa-resource "USB0::..." --log-file run.log
```

If you want conductivity too:

```bash
measure-once --count 50 --delay-s 0.05 --nplc 10 --length-m 0.01 --area-m2 1e-6
```

### d. Run continuous measurements

```bash
resistance-loop --count 20 --delay-s 0.1 --interval-s 1 --out-csv runs/run.csv
```

Optional additions:

```bash
resistance-loop --count 20 --delay-s 0.1 --interval-s 1 --out-csv runs/run.csv --nplc 10 --log-file loop.log
```

If you want conductivity during the loop:

```bash
resistance-loop --count 20 --delay-s 0.1 --interval-s 1 --out-csv runs/run.csv --length-m 0.01 --area-m2 1e-6
```

Dry run mode:

```bash
measure-once --dry-run
resistance-loop --dry-run
```

Important flag note for this repo:
- It uses `--delay-s`
- It uses `--interval-s`
- Not `--interval`

## 8. What Happens Internally (Simple)

When you run the code:

### a. Python connects to the DMM7510 through VISA.

### b. The code sets the meter to 4-wire resistance mode.

### c. It takes one or more readings.

### d. It averages the readings.

### e. It prints:

- Resistance
- Conductivity, if geometry values were given

### f. In loop mode, it can also save results to CSV.

## 9. Common Problems + Simple Fixes

| Problem | Cause | Fix |
| --- | --- | --- |
| No connection | VISA not set up or device not detected | Check NI MAX and USB connection |
| Wrong device opened | `VISA_RESOURCE` not set and first device was not the DMM | Set `VISA_RESOURCE` in `.env` or use `--visa-resource` |
| Timeout / open failure | Instrument communication issue | Check cable, power, and VISA installation |
| Noisy readings | Electrical noise or unstable contact | Increase `--count`, increase `--nplc`, stabilize probes |
| Bad readings | Poor contact on sample | Re-seat probes and check holder alignment |
| Conductivity not shown | Missing geometry values | Provide both `--length-m` and `--area-m2` |

## 10. Why 4-Wire is Important

4-wire resistance is better for accurate low-resistance measurements because it reduces error from the wires and contacts.

In simple terms:
- 2-wire includes extra resistance from leads/contact points
- 4-wire is much closer to the true sample resistance

That is why this repo was changed to use 4-wire mode by default.

## 11. Best Practices for This Project

- Use 4-wire mode for accurate measurements
- Keep probe contact stable
- Use averaging with `--count`
- Use a suitable `--nplc` value
- Save long runs with `--out-csv`
- Provide `--length-m` and `--area-m2` if conductivity is needed
- Set `VISA_RESOURCE` if more than one instrument may be connected

## 12. Repo-Specific Notes

This repo currently has:
- A `measure-once` command for single measurements
- A `resistance-loop` command for continuous measurements
- CSV export in loop mode
- Optional logging with `--log-file`
- Optional dry-run mode
- Optional conductivity calculation when geometry is supplied

It also has a small backward-compatibility helper in the code, but the active measurement path is now 4-wire.

The current codebase controls the Keithley DMM7510 in 4-wire resistance mode using Python and SCPI, averages readings for stability, and can also calculate conductivity when sample geometry is provided.

## Useful References

Official Manuals
- https://www.tek.com/en/support
- DMM7510 user guide (Section 6: 4-wire measurement)

Python + Instrument Control
- https://pyvisa.readthedocs.io/

SCPI Basics
- https://en.wikipedia.org/wiki/Standard_Commands_for_Programmable_Instruments

---

# Keithley DMM7510 - Full Configuration Guide (Machine-Specific)

## 1. Understanding the Interface (Front Panel)

The DMM7510 is controlled mainly through:
- Touchscreen UI
- Measure button (quick access)
- Menu -> Settings

## 2. Selecting Measurement Modes (Most Important)

Step-by-step on the machine:
1. Press HOME.
2. Tap Measure.
3. Choose a mode.

Common modes:

| Mode | What it does | Use in your project |
| --- | --- | --- |
| DC Voltage | Measures voltage | No |
| DC Current | Measures current | No |
| 2W Resistance (ohm) | Simple resistance | Less accurate |
| 4W Resistance (FRES) | High-precision resistance | Required |
| Continuity | Checks connection | Optional |
| Diode | Tests diodes | No |

For this project:
- Always select 4W Resistance (`FRES`)

## 3. Configuring 4-Wire Resistance Mode

After selecting 4W resistance, configure:

Open settings:
1. Tap MENU.
2. Go to Measure -> Settings.

Key parameters:

### 1. Range

- Auto Range -> ON
- Or set manually if needed

### 2. NPLC (Noise filtering)

| Value | Meaning |
| --- | --- |
| 0.1 | Fast, noisy |
| 1 | Balanced |
| 10 | Very accurate, slow |

Use for this repo:
- `NPLC = 10` is the current code default/example value

### 3. Offset Compensation (OCOM)

- On the instrument, set ON if you want extra thermal-voltage correction
- Important for precision work

Repo note:
- The current code does not send `:SENS:FRES:OCOM ON`, so this is not currently enabled by the Python helper

### 4. Auto Zero

- Set ON
- Improves stability

### 5. Filter / Averaging

- The instrument may support internal averaging
- This project already performs averaging in Python, which gives more direct control

## 4. Switching Between Modes (Quick Method)

Fast switching:
1. Press Measure.
2. Tap the desired mode.

For advanced control:
1. MENU -> Measure -> Function
2. Select the new function

## 5. Input Terminal Configuration (Very Important)

For 4-wire, use:

| Terminal | Use |
| --- | --- |
| INPUT HI | Current |
| INPUT LO | Current |
| SENSE HI | Voltage |
| SENSE LO | Voltage |

If you use only 2 leads, then you are not doing a proper 4-wire measurement.

## 6. Remote Configuration (What This Repo's Python Code Does)

Instead of touchscreen setup, the current code does:

```python
write(inst, "*RST")
write(inst, ':SENS:FUNC "FRES"')
write(inst, ":SENS:FRES:RANG:AUTO ON")
write(inst, f":SENS:FRES:NPLC {nplc}")
write(inst, ":SENS:FRES:AZER ON")
write(inst, "*CLS")
response = query(inst, ":MEAS:FRES?")
```

This is the remote equivalent of configuring the meter for 4-wire resistance and then taking a reading.

## 7. Changing Modes via Code

Example: switch to 2-wire

```python
write(inst, ':SENS:FUNC "RES"')
```

Switch back to 4-wire

```python
write(inst, ':SENS:FUNC "FRES"')
```

Note:
- The current repo measurement path is already set to 4-wire by default

## 8. Resetting the Instrument

If something goes wrong:

On the machine:
- Use the reset option from the menu if needed

Or via code:

```python
write(inst, "*RST")
```

## 9. Verifying Current Mode

On screen:
- `4W ohm` = correct
- `ohm` = 2-wire mode

Via Python:

```python
print(query(inst, ":SENS:FUNC?"))
```

## 10. Saving Configuration (Optional)

You can save settings on the instrument as a preset if you run the same setup often.

## 11. Best Configuration for This Project

Recommended setup:
- Mode -> 4W Resistance (`FRES`)
- Range -> Auto
- NPLC -> 10 for stable measurements in the current repo examples
- Auto Zero -> ON
- Averaging -> handled in Python using `--count`

Optional:
- Offset Compensation can be enabled on the instrument, but it is not currently enabled by the Python helper

## 12. Common Mistakes

| Mistake | Result |
| --- | --- |
| Using 2-wire instead of 4-wire | Wrong resistance |
| Wrong terminals | No measurement or incorrect reading |
| NPLC too low | Noisy data |
| No averaging | Unstable readings |
| Loose probes | Fluctuating values |
