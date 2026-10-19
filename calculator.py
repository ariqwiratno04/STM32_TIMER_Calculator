"""Math for a generic, edge-aligned STM32 timer update event."""

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, localcontext


@dataclass(frozen=True)
class Result:
    value: Decimal
    register: int | None = None
    achieved_period_s: Decimal | None = None
    error_percent: Decimal | None = None


@dataclass(frozen=True)
class PairResult:
    arr: int
    psc: int
    achieved_period_s: Decimal
    error_percent: Decimal


def decimal_input(text: str, name: str) -> Decimal:
    try:
        value = Decimal(text.strip())
    except (InvalidOperation, AttributeError):
        raise ValueError(f"{name} must be a number.") from None
    if not value.is_finite():
        raise ValueError(f"{name} must be finite.")
    return value


def register_input(text: str, name: str, maximum: int) -> int:
    value = decimal_input(text, name)
    if value != value.to_integral_value() or not 0 <= value <= maximum:
        raise ValueError(f"{name} must be an integer from 0 to {maximum:,}.")
    return int(value)


def solve(
    target: str,
    *,
    period_s: Decimal | None = None,
    arr: int | None = None,
    psc: int | None = None,
    clock_hz: Decimal | None = None,
    arr_bits: int = 16,
) -> Result:
    """Solve one variable, given the other three.

    T = (PSC + 1) * (ARR + 1) / timer_input_clock.
    ARR and PSC outputs include the closest feasible register value.
    """
    if target not in {"T", "Output frequency", "ARR", "PSC", "Clock"}:
        raise ValueError("Choose T, output frequency, ARR, PSC, or Clock.")
    if arr_bits not in (16, 32):
        raise ValueError("ARR width must be 16 or 32 bits.")

    arr_max = (1 << arr_bits) - 1
    psc_max = 65535
    if target not in {"T", "Output frequency"}:
        if period_s is None or not period_s.is_finite() or period_s <= 0:
            raise ValueError("T must be a positive, finite period.")
    if target != "Clock":
        if clock_hz is None or not clock_hz.is_finite() or clock_hz <= 0:
            raise ValueError("Timer clock must be a positive, finite frequency.")
    if target != "ARR":
        if type(arr) is not int or not 0 <= arr <= arr_max:
            raise ValueError(f"ARR must be an integer from 0 to {arr_max:,}.")
    if target != "PSC":
        if type(psc) is not int or not 0 <= psc <= psc_max:
            raise ValueError("PSC must be an integer from 0 to 65,535.")

    with localcontext() as context:
        context.prec = 50
        if target == "T":
            return Result(Decimal((psc + 1) * (arr + 1)) / clock_hz)
        if target == "Output frequency":
            return Result(clock_hz / Decimal((psc + 1) * (arr + 1)))
        if target == "Clock":
            return Result(Decimal((psc + 1) * (arr + 1)) / period_s)

        if target == "ARR":
            ideal = period_s * clock_hz / Decimal(psc + 1) - 1
            maximum = arr_max
            divisor = psc + 1
        else:
            ideal = period_s * clock_hz / Decimal(arr + 1) - 1
            maximum = psc_max
            divisor = arr + 1

        nearest = int(ideal.to_integral_value(rounding=ROUND_HALF_UP))
        nearest = max(0, min(maximum, nearest))
        achieved = Decimal((nearest + 1) * divisor) / clock_hz
        error = (achieved - period_s) / period_s * 100
        return Result(ideal, nearest, achieved, error)


def solve_arr_psc(period_s: Decimal, clock_hz: Decimal, arr_bits: int = 16) -> PairResult:
    """Find the ARR/PSC pair with the smallest absolute period error.

    In a tie, prefer the smaller PSC to retain more ARR resolution.
    """
    if arr_bits not in (16, 32):
        raise ValueError("ARR width must be 16 or 32 bits.")
    if not period_s.is_finite() or period_s <= 0:
        raise ValueError("T must be a positive, finite period.")
    if not clock_hz.is_finite() or clock_hz <= 0:
        raise ValueError("Timer clock must be a positive, finite frequency.")

    with localcontext() as context:
        context.prec = 50
        target_ticks = period_s * clock_hz
        arr_count_max = 1 << arr_bits
        best_error = None
        best_arr = 0
        best_psc = 0
        best_ticks = 1

        for psc_count in range(1, 65537):
            arr_count = int((target_ticks / psc_count).to_integral_value(rounding=ROUND_HALF_UP))
            arr_count = max(1, min(arr_count_max, arr_count))
            ticks = psc_count * arr_count
            error = abs(Decimal(ticks) - target_ticks)
            if best_error is None or error < best_error:
                best_error = error
                best_arr = arr_count - 1
                best_psc = psc_count - 1
                best_ticks = ticks
                if error == 0:
                    break

        achieved = Decimal(best_ticks) / clock_hz
        error_percent = (achieved - period_s) / period_s * 100
        return PairResult(best_arr, best_psc, achieved, error_percent)
