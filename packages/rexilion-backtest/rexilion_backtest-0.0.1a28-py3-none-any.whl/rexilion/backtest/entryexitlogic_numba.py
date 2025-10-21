from numba import njit
import numpy as np
from rexilion.backtest.formula_numba import (
    rolling_mean,
    rolling_ema,
    rolling_wma,
    rolling_std,
    rolling_min,
    rolling_max
)

# Mode IDs
MODE_MR = 0
MODE_MR_0 = 1
MODE_0_SIDELINE = 2
MODE_MOMENTUM = 3
MODE_MOMENTUM_SIDELINE = 4
MODE_MOMENTUM_0 = 5
MODE_MR_SMAMA = 6
MODE_MR_EMAMA = 7
MODE_MR_WMAMA = 8
MODE_MOMENTUM_SMAMA = 9
MODE_MOMENTUM_EMAMA = 10
MODE_MOMENTUM_WMAMA = 11
MODE_MR_SMA = 12
MODE_MR_EMA = 13
MODE_MR_WMA = 14
MODE_MOMENTUM_SMA = 15
MODE_MOMENTUM_EMA = 16
MODE_MOMENTUM_WMA = 17
MODE_MOM_SMA_SIDELINE = 18
MODE_MOM_EMA_SIDELINE = 19
MODE_MOM_WMA_SIDELINE = 20
MODE_MM_MR = 21
MODE_MM_MR_0 = 22
MODE_MM_MOMENTUM = 23
MODE_MM_MOMENTUM_0 = 24
MODE_MM_MR_SMA = 25
MODE_MM_MR_EMA = 26
MODE_MM_MR_WMA = 27
MODE_MM_MOMENTUM_SMA = 28
MODE_MM_MOMENTUM_EMA = 29
MODE_MM_MOMENTUM_WMA = 30


# ──────────────────────────────────────────────────────────────────────────────
# Helpers: deterministic tie-break for dual-side entries
# ──────────────────────────────────────────────────────────────────────────────
@njit(cache=True)
def _entry_from_dual_mom(xL: float, xS: float, thr_long: float, thr_short: float, prev: int) -> int:
    # Momentum entries: long if xL > thr_long, short if xS < thr_short
    long_hit = xL > thr_long
    short_hit = xS < thr_short
    if long_hit and not short_hit:
        return 1
    if short_hit and not long_hit:
        return -1
    if not long_hit and not short_hit:
        return 2  # carry
    # both hit -> pick stronger
    ls = xL - thr_long
    ss = thr_short - xS
    if ls > ss:
        return 1
    elif ss > ls:
        return -1
    return prev if (prev == 1 or prev == -1) else 0

@njit(cache=True)
def _entry_from_dual_mr(xL: float, xS: float, thr_long: float, thr_short: float, prev: int) -> int:
    # Mean-reversion entries: long if xL < -thr_long, short if xS > thr_short
    long_hit = xL < -thr_long
    short_hit = xS >  thr_short
    if long_hit and not short_hit:
        return 1
    if short_hit and not long_hit:
        return -1
    if not long_hit and not short_hit:
        return 2  # carry
    # both hit -> pick stronger (distance beyond barrier)
    ls = (-thr_long) - xL
    ss = xS - thr_short
    if ls > ss:
        return 1
    elif ss > ls:
        return -1
    return prev if (prev == 1 or prev == -1) else 0


# ──────────────────────────────────────────────────────────────────────────────
# THRESHOLD FAMILY
# Uses TWO processed streams and TWO rolling windows (side-specific).
# - processed_long / rolling_window_long  : long-side series & baselines
# - processed_short / rolling_window_short: short-side series & baselines
# Entries use side-specific series; exits compare against the same side’s baselines.
# ──────────────────────────────────────────────────────────────────────────────
@njit(cache=True)
def entry_exit_threshold(
    processed_long: np.ndarray,
    processed_short: np.ndarray,
    rolling_window_long: int,
    rolling_window_short: int,
    thr_long: float,
    thr_short: float,
    mode_id: int,
    weightage: float = 1.0  # NEW (optional)
) -> np.ndarray:
    n = processed_long.shape[0]  # assume both arrays same length
    warmup = rolling_window_long if rolling_window_long > rolling_window_short else rolling_window_short

    pos = np.empty(n, np.int8)
    for i in range(warmup):
        pos[i] = 0

    # feature flags
    use_sma = (mode_id == MODE_MR_SMAMA or mode_id == MODE_MOMENTUM_SMAMA
               or mode_id == MODE_MR_SMA or mode_id == MODE_MOMENTUM_SMA
               or mode_id == MODE_MM_MOMENTUM_SMA or mode_id == MODE_MM_MR_SMA
               or mode_id == MODE_MOM_SMA_SIDELINE)
    use_ema = (mode_id == MODE_MR_EMAMA or mode_id == MODE_MOMENTUM_EMAMA
               or mode_id == MODE_MR_EMA or mode_id == MODE_MOMENTUM_EMA
               or mode_id == MODE_MM_MOMENTUM_EMA or mode_id == MODE_MM_MR_EMA
               or mode_id == MODE_MOM_EMA_SIDELINE)
    use_wma = (mode_id == MODE_MR_WMAMA or mode_id == MODE_MOMENTUM_WMAMA
               or mode_id == MODE_MR_WMA or mode_id == MODE_MOMENTUM_WMA
               or mode_id == MODE_MM_MOMENTUM_WMA or mode_id == MODE_MM_MR_WMA
               or mode_id == MODE_MOM_WMA_SIDELINE)
    use_minmax = (mode_id == MODE_MM_MOMENTUM or mode_id == MODE_MM_MOMENTUM_0
                  or mode_id == MODE_MM_MOMENTUM_EMA or mode_id == MODE_MM_MOMENTUM_SMA
                  or mode_id == MODE_MM_MOMENTUM_WMA or mode_id == MODE_MM_MR
                  or mode_id == MODE_MM_MR_EMA or mode_id == MODE_MM_MR_SMA
                  or mode_id == MODE_MM_MR_WMA)

    # side-specific baselines with side-specific windows
    if use_sma:
        smaL = rolling_mean(processed_long,  rolling_window_long)
        smaS = rolling_mean(processed_short, rolling_window_short)
    else:
        smaL = smaS = np.empty(1, np.float64)

    if use_ema:
        emaL = rolling_ema(processed_long,  rolling_window_long)
        emaS = rolling_ema(processed_short, rolling_window_short)
    else:
        emaL = emaS = np.empty(1, np.float64)

    if use_wma:
        wmaL = rolling_wma(processed_long,  rolling_window_long)
        wmaS = rolling_wma(processed_short, rolling_window_short)
    else:
        wmaL = wmaS = np.empty(1, np.float64)

    if use_minmax:
        mnL = rolling_min(processed_long,  rolling_window_long)
        mxL = rolling_max(processed_long,  rolling_window_long)
        mnS = rolling_min(processed_short, rolling_window_short)
        mxS = rolling_max(processed_short, rolling_window_short)
    else:
        mnL = mxL = mnS = mxS = np.empty(1, np.float64)

    # main loop
    for i in range(warmup, n):
        xL = processed_long[i]
        xS = processed_short[i]
        prev = pos[i - 1]

        # ── MR family (dual-stream entries + side exits)
        if mode_id == MODE_MR:
            d = _entry_from_dual_mr(xL, xS, thr_long, thr_short, prev)
            pos[i] = (1 if d == 1 else (-1 if d == -1 else (prev if d == 2 else 0)))

        elif mode_id == MODE_MR_0:
            d = _entry_from_dual_mr(xL, xS, thr_long, thr_short, prev)
            if d == 1:
                pos[i] = 1
            elif d == -1:
                pos[i] = -1
            else:
                if   (prev == 1 and xL >= 0.0) or (prev == -1 and xS <= 0.0):
                    pos[i] = 0
                else:
                    pos[i] = prev if d == 2 else 0

        elif mode_id == MODE_MR_SMA:
            d = _entry_from_dual_mr(xL, xS, thr_long, thr_short, prev)
            if d == 1:
                pos[i] = 1
            elif d == -1:
                pos[i] = -1
            else:
                if   (prev == 1 and xL >= smaL[i]) or (prev == -1 and xS <= smaS[i]):
                    pos[i] = 0
                else:
                    pos[i] = prev if d == 2 else 0

        elif mode_id == MODE_MR_EMA:
            d = _entry_from_dual_mr(xL, xS, thr_long, thr_short, prev)
            if d == 1:
                pos[i] = 1
            elif d == -1:
                pos[i] = -1
            else:
                if   (prev == 1 and xL >= emaL[i]) or (prev == -1 and xS <= emaS[i]):
                    pos[i] = 0
                else:
                    pos[i] = prev if d == 2 else 0

        elif mode_id == MODE_MR_WMA:
            d = _entry_from_dual_mr(xL, xS, thr_long, thr_short, prev)
            if d == 1:
                pos[i] = 1
            elif d == -1:
                pos[i] = -1
            else:
                if   (prev == 1 and xL >= wmaL[i]) or (prev == -1 and xS <= wmaS[i]):
                    pos[i] = 0
                else:
                    pos[i] = prev if d == 2 else 0

        # 0_sideline (side-specific version)
        elif mode_id == MODE_0_SIDELINE:
            if   (xL > 0.0) and (xL <  thr_long):
                pos[i] = 1
            elif (xS < 0.0) and (xS > -thr_short):
                pos[i] = -1
            elif (prev == 1 and xL >= thr_short) or (prev == -1 and xS <= -thr_long):
                pos[i] = 0
            else:
                pos[i] = prev

        # ── Momentum family (dual-stream entries + side exits)
        elif mode_id == MODE_MOMENTUM:
            d = _entry_from_dual_mom(xL, xS, thr_long, thr_short, prev)
            pos[i] = (1 if d == 1 else (-1 if d == -1 else (prev if d == 2 else 0)))

        elif mode_id == MODE_MOMENTUM_0:
            d = _entry_from_dual_mom(xL, xS, thr_long, thr_short, prev)
            if d == 1:
                pos[i] = 1
            elif d == -1:
                pos[i] = -1
            else:
                if   (prev == 1 and xL <= 0.0) or (prev == -1 and xS >= 0.0):
                    pos[i] = 0
                else:
                    pos[i] = prev if d == 2 else 0

        elif mode_id == MODE_MOMENTUM_SIDELINE:
            d = _entry_from_dual_mom(xL, xS, thr_long, thr_short, prev)
            if d == 1:
                pos[i] = 1
            elif d == -1:
                pos[i] = -1
            else:
                if   (prev == 1 and xL <= thr_long) or (prev == -1 and xS >= thr_short):
                    pos[i] = 0
                else:
                    pos[i] = prev if d == 2 else 0

        elif mode_id == MODE_MOMENTUM_SMA:
            d = _entry_from_dual_mom(xL, xS, thr_long, thr_short, prev)
            if d == 1:
                pos[i] = 1
            elif d == -1:
                pos[i] = -1
            else:
                if   (prev == 1 and xL <= smaL[i]) or (prev == -1 and xS >= smaS[i]):
                    pos[i] = 0
                else:
                    pos[i] = prev if d == 2 else 0

        elif mode_id == MODE_MOMENTUM_EMA:
            d = _entry_from_dual_mom(xL, xS, thr_long, thr_short, prev)
            if d == 1:
                pos[i] = 1
            elif d == -1:
                pos[i] = -1
            else:
                if   (prev == 1 and xL <= emaL[i]) or (prev == -1 and xS >= emaS[i]):
                    pos[i] = 0
                else:
                    pos[i] = prev if d == 2 else 0

        elif mode_id == MODE_MOMENTUM_WMA:
            d = _entry_from_dual_mom(xL, xS, thr_long, thr_short, prev)
            if d == 1:
                pos[i] = 1
            elif d == -1:
                pos[i] = -1
            else:
                if   (prev == 1 and xL <= wmaL[i]) or (prev == -1 and xS >= wmaS[i]):
                    pos[i] = 0
                else:
                    pos[i] = prev if d == 2 else 0

        # ── % around mean (side-specific)
        elif mode_id == MODE_MR_SMAMA:
            mL = smaL[i]; mS = smaS[i]
            upS = mS * (1.0 + thr_short) if mS > 0 else mS * (1.0 - thr_short)
            loL = mL * (1.0 - thr_long)  if mL > 0 else mL * (1.0 + thr_long)
            if xS > upS:
                pos[i] = -1
            elif xL < loL:
                pos[i] = 1
            else:
                pos[i] = prev

        elif mode_id == MODE_MOMENTUM_SMAMA:
            mL = smaL[i]; mS = smaS[i]
            upL = mL * (1.0 + thr_long)  if mL > 0 else mL * (1.0 - thr_long)
            loS = mS * (1.0 - thr_short) if mS > 0 else mS * (1.0 + thr_short)
            if xL > upL:
                pos[i] = 1
            elif xS < loS:
                pos[i] = -1
            else:
                pos[i] = prev

        elif mode_id == MODE_MR_EMAMA:
            mL = emaL[i]; mS = emaS[i]
            upS = mS * (1.0 + thr_short) if mS > 0 else mS * (1.0 - thr_short)
            loL = mL * (1.0 - thr_long)  if mL > 0 else mL * (1.0 + thr_long)
            if xS > upS:
                pos[i] = -1
            elif xL < loL:
                pos[i] = 1
            else:
                pos[i] = prev

        elif mode_id == MODE_MOMENTUM_EMAMA:
            mL = emaL[i]; mS = emaS[i]
            upL = mL * (1.0 + thr_long)  if mL > 0 else mL * (1.0 - thr_long)
            loS = mS * (1.0 - thr_short) if mS > 0 else mS * (1.0 + thr_short)
            if xL > upL:
                pos[i] = 1
            elif xS < loS:
                pos[i] = -1
            else:
                pos[i] = prev

        elif mode_id == MODE_MR_WMAMA:
            mL = wmaL[i]; mS = wmaS[i]
            upS = mS * (1.0 + thr_short) if mS > 0 else mS * (1.0 - thr_short)
            loL = mL * (1.0 - thr_long)  if mL > 0 else mL * (1.0 + thr_long)
            if xS > upS:
                pos[i] = -1
            elif xL < loL:
                pos[i] = 1
            else:
                pos[i] = prev

        elif mode_id == MODE_MOMENTUM_WMAMA:
            mL = wmaL[i]; mS = wmaS[i]
            upL = mL * (1.0 + thr_long)  if mL > 0 else mL * (1.0 - thr_long)
            loS = mS * (1.0 - thr_short) if mS > 0 else mS * (1.0 + thr_short)
            if xL > upL:
                pos[i] = 1
            elif xS < loS:
                pos[i] = -1
            else:
                pos[i] = prev

        # ── Min/Max families (side-specific)
        elif mode_id == MODE_MM_MR:
            if xL < mnL[i] * thr_long:
                pos[i] = 1
            elif xS > mxS[i] * thr_short:
                pos[i] = -1
            else:
                pos[i] = prev

        elif mode_id == MODE_MM_MR_0:
            if xL < mnL[i] * thr_long:
                pos[i] = 1
            elif xS > mxS[i] * thr_short:
                pos[i] = -1
            elif (prev == 1 and xL >= 0.0) or (prev == -1 and xS <= 0.0):
                pos[i] = 0
            else:
                pos[i] = prev

        elif mode_id == MODE_MM_MR_SMA:
            if xL < mnL[i] * thr_long:
                pos[i] = 1
            elif xS > mxS[i] * thr_short:
                pos[i] = -1
            elif (prev == 1 and xL >= smaL[i]) or (prev == -1 and xS <= smaS[i]):
                pos[i] = 0
            else:
                pos[i] = prev

        elif mode_id == MODE_MM_MR_EMA:
            if xL < mnL[i] * thr_long:
                pos[i] = 1
            elif xS > mxS[i] * thr_short:
                pos[i] = -1
            elif (prev == 1 and xL >= emaL[i]) or (prev == -1 and xS <= emaS[i]):
                pos[i] = 0
            else:
                pos[i] = prev

        elif mode_id == MODE_MM_MR_WMA:
            if xL < mnL[i] * thr_long:
                pos[i] = 1
            elif xS > mxS[i] * thr_short:
                pos[i] = -1
            elif (prev == 1 and xL >= wmaL[i]) or (prev == -1 and xS <= wmaS[i]):
                pos[i] = 0
            else:
                pos[i] = prev

        elif mode_id == MODE_MM_MOMENTUM:
            if xL > mxL[i] * thr_long:
                pos[i] = 1
            elif xS < mnS[i] * thr_short:
                pos[i] = -1
            else:
                pos[i] = prev

        elif mode_id == MODE_MM_MOMENTUM_0:
            if xL > mxL[i] * thr_long:
                pos[i] = 1
            elif xS < mnS[i] * thr_short:
                pos[i] = -1
            elif (prev == 1 and xL <= 0.0) or (prev == -1 and xS >= 0.0):
                pos[i] = 0
            else:
                pos[i] = prev

        elif mode_id == MODE_MM_MOMENTUM_SMA:
            if xL > mxL[i] * thr_long:
                pos[i] = 1
            elif xS < mnS[i] * thr_short:
                pos[i] = -1
            elif (prev == 1 and xL <= smaL[i]) or (prev == -1 and xS >= smaS[i]):
                pos[i] = 0
            else:
                pos[i] = prev

        elif mode_id == MODE_MM_MOMENTUM_EMA:
            if xL > mxL[i] * thr_long:
                pos[i] = 1
            elif xS < mnS[i] * thr_short:
                pos[i] = -1
            elif (prev == 1 and xL <= emaL[i]) or (prev == -1 and xS >= emaS[i]):
                pos[i] = 0
            else:
                pos[i] = prev

        elif mode_id == MODE_MM_MOMENTUM_WMA:
            if xL > mxL[i] * thr_long:
                pos[i] = 1
            elif xS < mnS[i] * thr_short:
                pos[i] = -1
            elif (prev == 1 and xL <= wmaL[i]) or (prev == -1 and xS >= wmaS[i]):
                pos[i] = 0
            else:
                pos[i] = prev

        else:
            pos[i] = prev

    # scale to float64 with weightage
    out = np.empty(n, np.float64)
    for i in range(n):
        out[i] = pos[i] * weightage
    return out


# ──────────────────────────────────────────────────────────────────────────────
# BAND FAMILY (unchanged logic; weightage output)
# ──────────────────────────────────────────────────────────────────────────────
@njit(cache=True)
def entry_exit_band(
    data: np.ndarray,
    rolling_window: int,
    mult_long: float,   # lower band distance (long-side)
    mult_short: float,  # upper band distance (short-side)
    mode_id: int,
    weightage: float = 1.0  # NEW (optional)
) -> np.ndarray:
    n = data.shape[0]

    sma = rolling_mean(data, rolling_window)
    std = rolling_std(data, rolling_window)
    need_ema = (mode_id == MODE_MR_EMA or mode_id == MODE_MOMENTUM_EMA
                or mode_id == MODE_MOM_EMA_SIDELINE)
    need_wma = (mode_id == MODE_MR_WMA or mode_id == MODE_MOMENTUM_WMA
                or mode_id == MODE_MOM_WMA_SIDELINE)
    ema = rolling_ema(data, rolling_window) if need_ema else np.empty(n, np.float64)
    wma = rolling_wma(data, rolling_window) if need_wma else np.empty(n, np.float64)

    upper = np.empty(n, np.float64)
    lower = np.empty(n, np.float64)
    for i in range(n):
        upper[i] = sma[i] + mult_short * std[i]
        lower[i] = sma[i] - mult_long  * std[i]

    pos = np.empty(n, np.int8)
    for i in range(rolling_window):
        pos[i] = 0

    for i in range(rolling_window, n):
        x = data[i]
        prev = pos[i - 1]
        up = upper[i]
        lo = lower[i]
        m_sma = sma[i]
        m_ema = ema[i] if need_ema else 0.0
        m_wma = wma[i] if need_wma else 0.0

        if mode_id == MODE_MR:
            if x < lo:
                pos[i] = 1
            elif x > up:
                pos[i] = -1
            else:
                pos[i] = prev

        elif mode_id == MODE_MR_SMA:
            if x < lo:
                pos[i] = 1
            elif x > up:
                pos[i] = -1
            elif ((x >= m_sma and prev == 1) or (x <= m_sma and prev == -1)):
                pos[i] = 0
            else:
                pos[i] = prev

        elif mode_id == MODE_MR_EMA:
            if x < lo:
                pos[i] = 1
            elif x > up:
                pos[i] = -1
            elif ((x >= m_ema and prev == 1) or (x <= m_ema and prev == -1)):
                pos[i] = 0
            else:
                pos[i] = prev

        elif mode_id == MODE_MR_WMA:
            if x < lo:
                pos[i] = 1
            elif x > up:
                pos[i] = -1
            elif ((x >= m_wma and prev == 1) or (x <= m_wma and prev == -1)):
                pos[i] = 0
            else:
                pos[i] = prev

        elif mode_id == MODE_MR_0:
            if x < lo:
                pos[i] = 1
            elif x > up:
                pos[i] = -1
            elif ((x >= 0.0 and prev == 1) or (x <= 0.0 and prev == -1)):
                pos[i] = 0
            else:
                pos[i] = prev

        elif mode_id == MODE_0_SIDELINE:
            if x > 0.0 and x < up:
                pos[i] = 1
            elif x < 0.0 and x > lo:
                pos[i] = -1
            elif ((x >= up and prev == 1) or (x <= lo and prev == -1)):
                pos[i] = 0
            else:
                pos[i] = prev

        elif mode_id == MODE_MOM_SMA_SIDELINE:
            if x > m_sma and x < up:
                pos[i] = 1
            elif x < m_sma and x > lo:
                pos[i] = -1
            elif ((x >= up and prev == 1) or (x <= lo and prev == -1)):
                pos[i] = 0
            else:
                pos[i] = prev

        elif mode_id == MODE_MOM_EMA_SIDELINE:
            if x > m_ema and x < up:
                pos[i] = 1
            elif x < m_ema and x > lo:
                pos[i] = -1
            elif ((x >= up and prev == 1) or (x <= lo and prev == -1)):
                pos[i] = 0
            else:
                pos[i] = prev

        elif mode_id == MODE_MOM_WMA_SIDELINE:
            if x > m_wma and x < up:
                pos[i] = 1
            elif x < m_wma and x > lo:
                pos[i] = -1
            elif ((x >= up and prev == 1) or (x <= lo and prev == -1)):
                pos[i] = 0
            else:
                pos[i] = prev

        elif mode_id == MODE_MOMENTUM:
            if x > up:
                pos[i] = 1
            elif x < lo:
                pos[i] = -1
            else:
                pos[i] = prev

        elif mode_id == MODE_MOMENTUM_SIDELINE:
            if x > up:
                pos[i] = 1
            elif x < lo:
                pos[i] = -1
            elif ((x <= up and prev == 1) or (x >= lo and prev == -1)):
                pos[i] = 0
            else:
                pos[i] = prev

        elif mode_id == MODE_MOMENTUM_0:
            if x > up:
                pos[i] = 1
            elif x < lo:
                pos[i] = -1
            elif ((x <= 0.0 and prev == 1) or (x >= 0.0 and prev == -1)):
                pos[i] = 0
            else:
                pos[i] = prev

        elif mode_id == MODE_MOMENTUM_SMA:
            if x > up:
                pos[i] = 1
            elif x < lo:
                pos[i] = -1
            elif ((x <= m_sma and prev == 1) or (x >= m_sma and prev == -1)):
                pos[i] = 0
            else:
                pos[i] = prev

        elif mode_id == MODE_MOMENTUM_EMA:
            if x > up:
                pos[i] = 1
            elif x < lo:
                pos[i] = -1
            elif ((x <= m_ema and prev == 1) or (x >= m_ema and prev == -1)):
                pos[i] = 0
            else:
                pos[i] = prev

        elif mode_id == MODE_MOMENTUM_WMA:
            if x > up:
                pos[i] = 1
            elif x < lo:
                pos[i] = -1
            elif ((x <= m_wma and prev == 1) or (x >= m_wma and prev == -1)):
                pos[i] = 0
            else:
                pos[i] = prev

        else:
            continue

    # scale to float64 with weightage
    out = np.empty(n, np.float64)
    for i in range(n):
        out[i] = pos[i] * weightage
    return out


# ──────────────────────────────────────────────────────────────────────────────
# MACD FAMILY (unchanged logic; weightage output)
# ──────────────────────────────────────────────────────────────────────────────
@njit(cache=True)
def entry_exit_macd(
    macd: np.ndarray,
    signal: np.ndarray,
    rolling_window: int,
    weightage: float = 1.0  # NEW (optional)
) -> np.ndarray:
    n = macd.shape[0]
    pos = np.empty(n, np.int8)
    for i in range(rolling_window):
        pos[i] = 0
    for i in range(rolling_window, n):
        if macd[i] >= signal[i]:
            pos[i] = 1
        elif macd[i] <= signal[i]:
            pos[i] = -1
        else:
            pos[i] = pos[i-1]

    out = np.empty(n, np.float64)
    for i in range(n):
        out[i] = pos[i] * weightage
    return out
