"""Tkinter front end for the STM32 timer parameter calculator."""

from decimal import Decimal

from tk_setup import configure_tk

configure_tk()

import tkinter as tk
from tkinter import ttk

from calculator import decimal_input, register_input, solve, solve_arr_psc


TIME_UNITS = {"s": Decimal(1), "ms": Decimal("0.001"), "µs": Decimal("0.000001"), "ns": Decimal("0.000000001")}
FREQUENCY_UNITS = {"Hz": Decimal(1), "kHz": Decimal(1000), "MHz": Decimal(1000000)}
CLOCK_UNITS = FREQUENCY_UNITS


def display(value: Decimal) -> str:
    if value == value.to_integral_value() and abs(value) < Decimal("1e12"):
        return format(value, "f")
    return format(value, ".12g")


class TimerCalculator(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("STM32 Timer Calculator")
        self.resizable(False, False)

        frame = ttk.Frame(self, padding=18)
        frame.grid(sticky="nsew")
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="Calculate").grid(row=0, column=0, sticky="w", pady=(0, 12))
        self.target = tk.StringVar(value="T")
        selector = ttk.Combobox(frame, textvariable=self.target, values=("T", "Output frequency", "ARR", "PSC", "Clock", "ARR + PSC"), state="readonly", width=17)
        selector.grid(row=0, column=1, sticky="w", pady=(0, 12))
        selector.bind("<<ComboboxSelected>>", self.on_target_change)

        ttk.Label(frame, text="Timing value").grid(row=1, column=0, sticky="w", pady=5)
        self.timing_mode = tk.StringVar(value="T")
        self.timing_selector = ttk.Combobox(frame, textvariable=self.timing_mode, values=("T", "Output frequency"), state="readonly", width=17)
        self.timing_selector.grid(row=1, column=1, sticky="w", pady=5)
        self.timing_selector.bind("<<ComboboxSelected>>", self.on_timing_change)

        self.values = {
            "T": tk.StringVar(value="1"),
            "Output frequency": tk.StringVar(value="1000"),
            "ARR": tk.StringVar(value="999"),
            "PSC": tk.StringVar(value="79"),
            "Clock": tk.StringVar(value="80"),
        }
        self.entries: dict[str, ttk.Entry] = {}
        labels = {"T": "Period (T)", "ARR": "Auto-reload (ARR)", "PSC": "Prescaler (PSC)", "Clock": "Timer input clock"}
        for row, key in enumerate(("T", "ARR", "PSC", "Clock"), start=2):
            label = ttk.Label(frame, text=labels[key])
            label.grid(row=row, column=0, sticky="w", padx=(0, 16), pady=5)
            if key == "T":
                self.timing_label = label
            entry = ttk.Entry(frame, textvariable=self.values[key], width=20)
            entry.grid(row=row, column=1, sticky="ew", pady=5)
            self.entries[key] = entry

        self.time_unit = tk.StringVar(value="ms")
        self.frequency_unit = tk.StringVar(value="Hz")
        self.timing_unit_selector = ttk.Combobox(frame, textvariable=self.time_unit, values=tuple(TIME_UNITS), state="readonly", width=7)
        self.timing_unit_selector.grid(row=2, column=2, padx=(8, 0))
        self.clock_unit = tk.StringVar(value="MHz")
        ttk.Combobox(frame, textvariable=self.clock_unit, values=tuple(CLOCK_UNITS), state="readonly", width=7).grid(row=5, column=2, padx=(8, 0))

        ttk.Label(frame, text="ARR register width").grid(row=6, column=0, sticky="w", pady=(12, 5))
        self.arr_bits = tk.StringVar(value="16")
        ttk.Combobox(frame, textvariable=self.arr_bits, values=("16", "32"), state="readonly", width=7).grid(row=6, column=1, sticky="w", pady=(12, 5))
        ttk.Label(frame, text="bits").grid(row=6, column=2, sticky="w", padx=(8, 0), pady=(12, 5))

        ttk.Button(frame, text="Calculate", command=self.calculate).grid(row=7, column=0, columnspan=3, sticky="ew", pady=(14, 12))
        self.result = tk.StringVar(value="Enter the known values, then click Calculate.")
        ttk.Label(frame, textvariable=self.result, justify="left", wraplength=430).grid(row=8, column=0, columnspan=3, sticky="w")
        ttk.Separator(frame).grid(row=9, column=0, columnspan=3, sticky="ew", pady=12)
        ttk.Label(frame, text="Edge aligned: T = (PSC + 1) × (ARR + 1) / timer clock; output frequency = 1 / T", wraplength=430).grid(row=10, column=0, columnspan=3, sticky="w")
        ttk.Label(frame, text="Timer clock means the clock at the timer input, after any MCU clock-tree multiplication.", wraplength=430).grid(row=11, column=0, columnspan=3, sticky="w", pady=(5, 0))

        self.on_target_change()
        self.bind("<Return>", lambda _event: self.calculate())

    def on_target_change(self, _event: object = None) -> None:
        target = self.target.get()
        if target in ("T", "Output frequency"):
            self.timing_mode.set(target)
        self.timing_selector.configure(state="disabled" if target in ("T", "Output frequency") else "readonly")
        self.on_timing_change()
        for key, entry in self.entries.items():
            disabled = (key == "T" and target in ("T", "Output frequency")) or key == target or (target == "ARR + PSC" and key in ("ARR", "PSC"))
            entry.configure(state="disabled" if disabled else "normal")
        self.result.set("Enter the known values, then click Calculate.")

    def on_timing_change(self, _event: object = None) -> None:
        frequency = self.timing_mode.get() == "Output frequency"
        self.timing_label.configure(text="Output frequency" if frequency else "Period (T)")
        self.entries["T"].configure(textvariable=self.values["Output frequency" if frequency else "T"])
        self.timing_unit_selector.configure(
            textvariable=self.frequency_unit if frequency else self.time_unit,
            values=tuple(FREQUENCY_UNITS if frequency else TIME_UNITS),
        )
        self.result.set("Enter the known values, then click Calculate.")

    def input_period_s(self) -> Decimal:
        if self.timing_mode.get() == "T":
            return decimal_input(self.values["T"].get(), "T") * TIME_UNITS[self.time_unit.get()]
        frequency_hz = decimal_input(self.values["Output frequency"].get(), "Output frequency") * FREQUENCY_UNITS[self.frequency_unit.get()]
        if frequency_hz <= 0:
            raise ValueError("Output frequency must be positive.")
        return 1 / frequency_hz

    def timing_summary(self, period_s: Decimal) -> str:
        return (
            f"Achieved T = {display(period_s / TIME_UNITS[self.time_unit.get()])} {self.time_unit.get()}\n"
            f"Output frequency = {display((1 / period_s) / FREQUENCY_UNITS[self.frequency_unit.get()])} {self.frequency_unit.get()}"
        )

    def calculate(self) -> None:
        target = self.target.get()
        bits = int(self.arr_bits.get())
        try:
            if target == "ARR + PSC":
                period_s = self.input_period_s()
                clock_hz = decimal_input(self.values["Clock"].get(), "Timer clock") * CLOCK_UNITS[self.clock_unit.get()]
                answer = solve_arr_psc(period_s, clock_hz, bits)
                self.result.set(
                    f"ARR = {answer.arr:,}\n"
                    f"PSC = {answer.psc:,}\n"
                    f"{self.timing_summary(answer.achieved_period_s)}\n"
                    f"Period error = {display(answer.error_percent)} %"
                )
                return
            kwargs = {"arr_bits": bits}
            if target not in ("T", "Output frequency"):
                kwargs["period_s"] = self.input_period_s()
            if target != "ARR":
                kwargs["arr"] = register_input(self.values["ARR"].get(), "ARR", (1 << bits) - 1)
            if target != "PSC":
                kwargs["psc"] = register_input(self.values["PSC"].get(), "PSC", 65535)
            if target != "Clock":
                kwargs["clock_hz"] = decimal_input(self.values["Clock"].get(), "Timer clock") * CLOCK_UNITS[self.clock_unit.get()]
            answer = solve(target, **kwargs)
        except ValueError as error:
            self.result.set(f"Input error: {error}")
            return

        if target == "T":
            self.result.set(self.timing_summary(answer.value).replace("Achieved T", "Period T"))
        elif target == "Output frequency":
            unit = self.frequency_unit.get()
            self.result.set(
                f"Output frequency = {display(answer.value / FREQUENCY_UNITS[unit])} {unit}\n"
                f"Period T = {display((1 / answer.value) / TIME_UNITS[self.time_unit.get()])} {self.time_unit.get()}"
            )
        elif target == "Clock":
            unit = self.clock_unit.get()
            self.result.set(f"Timer input clock = {display(answer.value / CLOCK_UNITS[unit])} {unit}")
        else:
            maximum = (1 << bits) - 1 if target == "ARR" else 65535
            range_note = "\nRequested period is outside the range of this register." if answer.value < 0 or answer.value > maximum else ""
            self.result.set(
                f"{target} = {answer.register:,} (nearest usable register value)\n"
                f"Ideal {target} = {display(answer.value)}\n"
                f"{self.timing_summary(answer.achieved_period_s)}\n"
                f"Period error = {display(answer.error_percent)} %{range_note}"
            )


if __name__ == "__main__":
    TimerCalculator().mainloop()
