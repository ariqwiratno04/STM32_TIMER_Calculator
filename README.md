# STM32 Timer Calculator

A desktop calculator for STM32 timer update timing. Enter the values you know, choose what to calculate, and get a period, frequency, timer clock, ARR, PSC, or an ARR/PSC pair. The app uses Python's built-in Tkinter GUI and needs no third-party packages.

## Codex contribution

Codex assisted with the implementation of this project, including the timer calculation logic, the Tkinter interface, the Windows launcher, and the unit tests. The calculator supports solving for period, output frequency, timer clock, ARR, PSC, or an ARR/PSC pair, with register limits and timing error reported where applicable.

## Requirements

- Python 3.10 or newer
- Tkinter (included with most desktop Python installations)

To check Tkinter, run `python -m tkinter` on Windows or `python3 -m tkinter` on macOS/Linux. A small test window should open.

## Get started

Download this repository as a ZIP from GitHub and extract it, or clone it. Open a terminal in the extracted project folder.

**Windows:** Double-click `run.cmd`, or run one of these commands in PowerShell:

```powershell
py -3 app.py
# If the Python launcher is unavailable:
python app.py
```

**macOS/Linux:**

```sh
python3 app.py
```

If the `python` command opens the Microsoft Store on Windows, install Python from [python.org](https://www.python.org/downloads/) and enable **Add Python to PATH** during setup. Alternatively, use `py -3 app.py` if the Python launcher is available.

## Use the calculator

1. In **Calculate**, select the value you want to find.
2. Enter the enabled values. Choose units for the timing value and timer clock.
3. Set **ARR register width** to match your STM32 timer (16 or 32 bits).
4. Click **Calculate**.

| Calculate | Values to enter |
| --- | --- |
| T or Output frequency | ARR, PSC, timer input clock |
| ARR | T or output frequency, PSC, timer input clock |
| PSC | T or output frequency, ARR, timer input clock |
| Clock | T or output frequency, ARR, PSC |
| ARR + PSC | Desired T or output frequency, timer input clock |

For the last four choices, use **Timing value** to switch between entering T and output frequency. When solving for ARR or PSC, the app shows the ideal value, nearest valid integer register value, achieved timing, and period error. When solving for both, it searches for the ARR/PSC pair with the smallest period error. Ties favor the smaller PSC to retain more ARR resolution.

**Example:** Select **ARR + PSC**, enter **T = 1 ms** and **timer input clock = 80 MHz**, and leave ARR width at 16 bits. The result is **ARR = 39,999** and **PSC = 1**, giving **1 ms** or **1,000 Hz**.

## How the calculation works

For a generic edge aligned STM32 timer update event:

```text
T = (PSC + 1) × (ARR + 1) / timer_input_clock
output_frequency = 1 / T
```

ARR and PSC are register values, so each contributes one more count than its displayed value. PSC is limited to 16 bits; ARR can be 16 or 32 bits depending on the timer.

Enter the clock **actually supplied to the timer**, after any clock-tree multiplication. The output frequency shown is the update frequency; it is also the PWM cycle frequency for typical edge aligned PWM. Center aligned modes and some other timer configurations have different timing rules, so check the reference manual for your MCU and timer.

## Run tests

```sh
python -m unittest discover
```

On macOS/Linux, use `python3` if that is your Python command.
