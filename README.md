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
| t or Output frequency | ARR, PSC, timer input clock |
| ARR | t or output frequency, PSC, timer input clock |
| PSC | t or output frequency, ARR, timer input clock |
| Clock | t or output frequency, ARR, PSC |
| ARR + PSC | Desired t or output frequency, timer input clock |

For the last four choices, use **Timing value** to switch between entering t and output frequency. When solving for ARR or PSC, the app shows the ideal value, nearest valid integer register value, achieved timing, and duration error. When solving for both, it searches for the ARR/PSC pair with the smallest duration error. Ties favor the smaller PSC to retain more ARR resolution.

**Example:** Select **ARR + PSC**, enter **t = 1 ms** and **timer input clock = 80 MHz**, and leave ARR width at 16 bits. The result is **ARR = 39,999** and **PSC = 1**, giving **1 ms** per output level, a full cycle of **T = 2 ms**, and a **500 Hz** square wave.

### Optional PWM calculation

Fill **PWM compare (CCR)** or **PWM duty cycle** to add an edge-aligned PWM calculation. Enter duty cycle as a fraction from **0 to 1** (for example, `0.25` for 25%). Leave both blank for the original toggle calculation. If both are filled, CCR must match the register value obtained by rounding the requested duty cycle.

This PWM calculation applies only when the timer uses **PWM1 mode with high OC polarity**: the output is HIGH while `CNT < CCR`. For that configuration:

```text
PWM cycle T = (PSC + 1) × (ARR + 1) / timer_input_clock
PWM frequency = 1 / T
CCR = duty_cycle × (ARR + 1)
duty_cycle = CCR / (ARR + 1)
HIGH time t = T × duty_cycle
```

The app uses the entered or calculated ARR to determine CCR or the achieved duty cycle. Requested duty cycles are rounded to the nearest timer count; the result shows the achieved value. CCR may range from 0 to the smaller of ARR + 1 and the register maximum for the selected ARR width. At the maximum ARR value, 100% duty cannot be represented by a larger CCR and the app shows the closest achievable duty.

**Output frequency** in the main calculator continues to mean the toggle-output frequency. When CCR or duty cycle is entered, the result also shows the PWM frequency, which is twice the toggle-output frequency for the same ARR, PSC, and clock.

## How the calculation works

For an output that toggles at each edge aligned STM32 timer update event, t is the duration of one HIGH or LOW level. A full square wave is HIGH plus LOW, so its period is T = 2t:

```text
t = (PSC + 1) × (ARR + 1) / timer_input_clock
T = 2 * t
output_frequency = 1 / T
```

ARR and PSC are register values, so each contributes one more count than its displayed value. PSC is limited to 16 bits; ARR can be 16 or 32 bits depending on the timer.

Enter the clock **actually supplied to the timer**, after any clock-tree multiplication. The timer update rate is 1/t, or twice the square-wave frequency. This calculation assumes the output toggles once at each update. PWM and other timer modes may use a different relationship; check the reference manual for your MCU and timer.

## Run tests

```sh
python -m unittest discover
```

On macOS/Linux, use `python3` if that is your Python command.
