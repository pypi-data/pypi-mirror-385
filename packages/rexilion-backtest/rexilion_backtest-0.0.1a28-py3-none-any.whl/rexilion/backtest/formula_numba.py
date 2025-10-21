# -*- coding: utf-8 -*-
import numpy as np
from numba import njit, prange
from math import isnan, sqrt, log, atan

# ──────────────────────────────────────────────────────────────────────────────
# Helpers (Numba-friendly)
# ──────────────────────────────────────────────────────────────────────────────

@njit(cache=False, nogil=True)   # cache=False to force rebuild
def _as_f64(a):
    b = np.asarray(a, np.float64)   # cast
    return np.ascontiguousarray(b)  # then contiguous

@njit(cache=True, nogil=True)
def _isfinite(x):
    return np.isfinite(x)

# ──────────────────────────────────────────────────────────────────────────────
# Diff helpers
# ──────────────────────────────────────────────────────────────────────────────

@njit(cache=True, nogil=True)
def diff(arr, periods=1):
    a = _as_f64(arr)
    if periods < 1:
        raise ValueError("`periods` must be a positive integer")
    n = a.size
    out = np.empty(n, np.float64)
    for i in range(min(periods, n)):
        out[i] = np.nan
    for i in range(periods, n):
        out[i] = a[i] - a[i - periods]
    return out

@njit(cache=True, nogil=True)
def diff_n(arr, n_diffs=1) -> np.ndarray:
    d = _as_f64(arr)
    for _ in range(n_diffs):
        d = diff(d, 1)
    return d

# ──────────────────────────────────────────────────────────────────────────────
# Rolling aggregates (Numba)
# ──────────────────────────────────────────────────────────────────────────────

@njit(cache=True, nogil=True)
def rolling_sum(x: np.ndarray, window: int, min_periods: int = -1, fill_value: float = np.nan) -> np.ndarray:
    x = _as_f64(x)
    n = x.size
    if window < 1:
        raise ValueError("`window` must be an integer ≥ 1")
    if min_periods == -1:
        min_periods = window
    if min_periods < 1:
        raise ValueError("`min_periods` must be an integer ≥ 1")

    out = np.empty(n, np.float64)
    # maintain rolling sum and count of finite values
    roll_sum = 0.0
    roll_cnt = 0

    for i in range(n):
        xi = x[i]
        if _isfinite(xi):
            roll_sum += xi
            roll_cnt += 1
        if i >= window:
            x_old = x[i - window]
            if _isfinite(x_old):
                roll_sum -= x_old
                roll_cnt -= 1

        if i >= window - 1:
            out[i] = roll_sum if roll_cnt >= min_periods else fill_value
        else:
            out[i] = fill_value
    return out

@njit(cache=True, nogil=True)
def rolling_mean(array, rolling_window):
    a = _as_f64(array)
    n = a.size
    out = np.empty(n, np.float64)
    if rolling_window < 1:
        for i in range(n):
            out[i] = np.nan
        return out

    s = 0.0
    cnt = 0
    for i in range(n):
        ai = a[i]
        if np.isfinite(ai):
            s += ai
            cnt += 1
        if i >= rolling_window:
            ao = a[i - rolling_window]
            if np.isfinite(ao):
                s -= ao
                cnt -= 1
        if i >= rolling_window - 1:
            out[i] = (s / cnt) if cnt > 0 else np.nan
        else:
            out[i] = np.nan
    return out

@njit(cache=True, nogil=True)
def rolling_ema(data, window):
    d = _as_f64(data)
    n = d.size
    out = np.empty(n, np.float64)
    if window > n:
        for i in range(n):
            out[i] = np.nan
        return out

    alpha = 2.0 / (window + 1.0)
    # initial SMA
    s = 0.0
    for i in range(window):
        s += d[i]
    out[window - 1] = s / window
    for i in range(window, n):
        out[i] = (d[i] - out[i - 1]) * alpha + out[i - 1]
    for i in range(window - 1):
        out[i] = np.nan
    return out

@njit(cache=True, nogil=True)
def rolling_wma(data, window):
    d = _as_f64(data)
    n = d.size
    out = np.empty(n, np.float64)
    if window > n:
        for i in range(n):
            out[i] = np.nan
        return out
    weight_sum = window * (window + 1) * 0.5
    for i in range(window - 1):
        out[i] = np.nan
    for i in range(window - 1, n):
        s = 0.0
        w = 1
        # weights: 1..window aligned to most recent being weight=window
        for k in range(i - window + 1, i + 1):
            s += d[k] * w
            w += 1
        out[i] = s / weight_sum
    return out

@njit(cache=True, nogil=True)
def rolling_min(array, rolling_window):
    a = _as_f64(array)
    n = a.size
    out = np.empty(n, np.float64)
    if rolling_window > n:
        for i in range(n):
            out[i] = np.nan
        return out
    for i in range(rolling_window - 1):
        out[i] = np.nan
    for i in range(rolling_window - 1, n):
        m = a[i - rolling_window + 1]
        for j in range(i - rolling_window + 2, i + 1):
            if a[j] < m:
                m = a[j]
        out[i] = m
    return out

@njit(cache=True, nogil=True)
def rolling_max(array, rolling_window):
    a = _as_f64(array)
    n = a.size
    out = np.empty(n, np.float64)
    if rolling_window > n:
        for i in range(n):
            out[i] = np.nan
        return out
    for i in range(rolling_window - 1):
        out[i] = np.nan
    for i in range(rolling_window - 1, n):
        m = a[i - rolling_window + 1]
        for j in range(i - rolling_window + 2, i + 1):
            if a[j] > m:
                m = a[j]
        out[i] = m
    return out

@njit(cache=True, nogil=True)
def rolling_std(array, window):
    a = _as_f64(array)
    n = a.size
    out = np.empty(n, np.float64)
    if window > n:
        for i in range(n):
            out[i] = np.nan
        return out

    s = 0.0
    ss = 0.0
    cnt = 0

    for i in range(n):
        ai = a[i]
        if np.isfinite(ai):
            s += ai
            ss += ai * ai
            cnt += 1

        if i >= window:
            ao = a[i - window]
            if np.isfinite(ao):
                s -= ao
                ss -= ao * ao
                cnt -= 1

        if i >= window - 1:
            if cnt > 1:
                var = (ss - (s * s) / cnt) / (cnt - 1)
                out[i] = sqrt(var) if var > 0.0 else 0.0
            else:
                out[i] = np.nan
        else:
            out[i] = np.nan
    return out

# ──────────────────────────────────────────────────────────────────────────────
# Transforms built on rolling primitives
# ──────────────────────────────────────────────────────────────────────────────

@njit(cache=True, nogil=True)
def rolling_mean_normalize(array, rolling_window):
    a = _as_f64(array)
    sma = rolling_mean(a, rolling_window)
    mn = rolling_min(a, rolling_window)
    mx = rolling_max(a, rolling_window)
    n = a.size
    out = np.empty(n, np.float64)
    for i in range(n):
        out[i] = (a[i] - sma[i]) / (mx[i] - mn[i] + 1e-9)
    return out

@njit(cache=True, nogil=True)
def rolling_zscore_mean(array, rolling_window):
    a = _as_f64(array)
    sma = rolling_mean(a, rolling_window)
    stddev = rolling_std(a, rolling_window)
    n = a.size
    z = np.empty(n, np.float64)
    for i in range(n):
        z[i] = (a[i] - sma[i]) / (stddev[i] + 1e-9)
    # remove local mean
    zm = rolling_mean(z, rolling_window)
    out = np.empty(n, np.float64)
    for i in range(n):
        out[i] = z[i] - zm[i]
    return out

@njit(cache=True, nogil=True)
def rolling_zscore(array, rolling_window):
    a = _as_f64(array)
    sma = rolling_mean(a, rolling_window)
    stddev = rolling_std(a, rolling_window)
    n = a.size
    out = np.empty(n, np.float64)
    for i in range(n):
        out[i] = (a[i] - sma[i]) / (stddev[i] + 1e-9)
    return out

@njit(cache=True, nogil=True)
def rolling_sigmoid_zscore(arr: np.ndarray, window: int) -> np.ndarray:
    z = rolling_zscore(arr, window)
    n = z.size
    out = np.empty(n, np.float64)
    for i in range(n):
        out[i] = np.tanh(z[i] / 2.0)
    return out

@njit(cache=True, nogil=True)
def rolling_minmax_original(array, rolling_window):
    a = _as_f64(array)
    mn = rolling_min(a, rolling_window)
    mx = rolling_max(a, rolling_window)
    n = a.size
    out = np.empty(n, np.float64)
    for i in range(n):
        out[i] = (a[i] - mn[i]) / (mx[i] - mn[i] + 1e-9)
    return out

@njit(cache=True, nogil=True)
def rolling_minmax_normalize(array, rolling_window):
    a = _as_f64(array)
    mn = rolling_min(a, rolling_window)
    mx = rolling_max(a, rolling_window)
    n = a.size
    out = np.empty(n, np.float64)
    for i in range(n):
        out[i] = 2.0 * (a[i] - mn[i]) / (mx[i] - mn[i] + 1e-9) - 1.0
    return out

@njit(cache=True, nogil=True)
def rolling_skew(arr, window):
    x = _as_f64(arr)
    n = x.size
    out = np.empty(n, np.float64)
    if n < window:
        for i in range(n):
            out[i] = np.nan
        return out
    for i in range(window - 1):
        out[i] = np.nan
    for i in range(window - 1, n):
        # compute sample skewness over window
        m = 0.0
        for k in range(i - window + 1, i + 1):
            m += x[k]
        m /= window
        s2 = 0.0
        s3 = 0.0
        for k in range(i - window + 1, i + 1):
            d = x[k] - m
            s2 += d * d
            s3 += d * d * d
        if window > 2 and s2 > 0.0:
            s2 /= (window - 1)
            std = sqrt(s2)
            out[i] = (window / ((window - 1.0) * (window - 2.0))) * (s3 / (std * std * std))
        else:
            out[i] = np.nan
    return out

@njit(cache=True, nogil=True)
def rolling_var(arr, window):
    x = _as_f64(arr)
    n = x.size
    out = np.empty(n, np.float64)
    if n < window:
        for i in range(n):
            out[i] = np.nan
        return out
    for i in range(window - 1):
        out[i] = np.nan
    for i in range(window - 1, n):
        m = 0.0
        for k in range(i - window + 1, i + 1):
            m += x[k]
        m /= window
        v = 0.0
        for k in range(i - window + 1, i + 1):
            d = x[k] - m
            v += d * d
        out[i] = v / (window - 1.0) if window > 1 else np.nan
    return out

@njit(cache=True, nogil=True)
def rolling_kurt(arr, window):
    x = _as_f64(arr)
    n = x.size
    out = np.empty(n, np.float64)
    if n < window:
        for i in range(n):
            out[i] = np.nan
        return out
    for i in range(window - 1):
        out[i] = np.nan
    for i in range(window - 1, n):
        m = 0.0
        for k in range(i - window + 1, i + 1):
            m += x[k]
        m /= window
        s = 0.0
        m4 = 0.0
        for k in range(i - window + 1, i + 1):
            d = x[k] - m
            s += d * d
            m4 += d * d * d * d
        s /= window
        if s > 0.0:
            m4 /= window
            out[i] = m4 / (s * s) - 3.0
        else:
            out[i] = np.nan
    return out

@njit(cache=True, nogil=True)
def rolling_tanh_estimator(arr, rolling_window):
    a = _as_f64(arr)
    sma = rolling_mean(a, rolling_window)
    std = rolling_std(a, rolling_window)
    n = a.size
    out = np.empty(n, np.float64)
    for i in range(n):
        out[i] = np.tanh(0.01 * (a[i] - sma[i]) / (std[i] + 1e-9))
    return out

@njit(cache=True, nogil=True)
def sigmoid(arr):
    a = _as_f64(arr)
    n = a.size
    out = np.empty(n, np.float64)
    for i in range(n):
        out[i] = 2.0 * (1.0 / (1.0 + np.exp(-a[i]))) - 1.0
    return out

@njit(cache=True, nogil=True)
def rolling_softmax(arr, window):
    x = _as_f64(arr)
    n = x.size
    out = np.empty(n, np.float64)
    if window > n:
        for i in range(n):
            out[i] = np.nan
        return out
    for i in range(window - 1):
        out[i] = np.nan
    for i in range(window - 1, n):
        # softmax over the window, return value for last element
        m = x[i - window + 1]
        for k in range(i - window + 2, i + 1):
            if x[k] > m:
                m = x[k]
        s = 0.0
        last_exp = 0.0
        for k in range(i - window + 1, i + 1):
            e = np.exp(x[k] - m)
            s += e
            if k == i:
                last_exp = e
        sm_last = last_exp / s
        out[i] = 2.0 * sm_last - 1.0
    return out

@njit(cache=True, nogil=True)
def rolling_l1_normalization(arr, rolling_window):
    x = _as_f64(arr)
    n = x.size
    abs_arr = np.empty(n, np.float64)
    for i in range(n):
        abs_arr[i] = abs(x[i])
    abs_sum = rolling_sum(abs_arr, rolling_window, -1, np.nan)
    out = np.empty(n, np.float64)
    for i in range(n):
        out[i] = 2.0 * (x[i] / (abs_sum[i] + 1e-9)) - 1.0
    return out

# NOTE: These two keep Python signatures that accept DataFrame; Numba does not support pandas.
# They remain non-JIT but are fast enough for typical window sizes. You can pass numpy arrays
# to the inner computations for speed elsewhere.
def rolling_rsi(df, rolling_window):
    data = np.asarray(df["data"], dtype=float)

    # compute delta
    n = data.size
    delta = np.empty(n, np.float64)
    delta[0] = np.nan
    for i in range(1, n):
        delta[i] = data[i] - data[i - 1]

    # gains and losses (non-negative)
    gain = np.empty(n, np.float64)
    loss = np.empty(n, np.float64)
    for i in range(n):
        di = delta[i]
        gain[i] = di if (not np.isnan(di) and di > 0.0) else 0.0
        loss[i] = -di if (not np.isnan(di) and di < 0.0) else 0.0

    gain_ma = rolling_mean(gain, rolling_window)
    loss_ma = rolling_mean(loss, rolling_window)

    rs = gain_ma / (loss_ma + 1e-9)
    rsi = 100.0 - (100.0 / (1.0 + rs))

    df["rsi"] = rsi
    df["sma"] = rolling_mean(rsi, rolling_window)
    df["ema"] = rolling_ema(rsi, rolling_window)
    df["wma"] = rolling_wma(rsi, rolling_window)
    df["processed_data"] = (df["rsi"] - 50.0) / 50.0
    return df

def calculate_macd(df, short_window, long_window, signal_window=9):
    data = np.asarray(df["data"], dtype=float)
    ema_s = rolling_ema(data, short_window)
    ema_l = rolling_ema(data, long_window)
    macd = ema_s - ema_l
    signal = rolling_ema(macd, signal_window)
    hist = macd - signal
    df["EMA_short"] = ema_s
    df["EMA_long"]  = ema_l
    df["MACD"]      = macd
    df["Signal"]    = signal
    df["Histogram"] = hist
    return df

@njit(cache=True, nogil=True)
def rolling_median(array, rolling_window):
    a = _as_f64(array)
    n = a.size
    out = np.empty(n, np.float64)
    if rolling_window > n:
        for i in range(n):
            out[i] = np.nan
        return out
    for i in range(rolling_window - 1):
        out[i] = np.nan
    buf = np.empty(rolling_window, np.float64)
    for i in range(rolling_window - 1, n):
        # copy & sort
        for k in range(rolling_window):
            buf[k] = a[i - rolling_window + 1 + k]
        buf.sort()
        if rolling_window % 2 == 1:
            out[i] = buf[rolling_window // 2]
        else:
            j = rolling_window // 2
            out[i] = 0.5 * (buf[j - 1] + buf[j])
    return out

@njit(cache=True, nogil=True)
def signed_log1p(x: np.ndarray) -> np.ndarray:
    a = _as_f64(x)
    n = a.size
    out = np.empty(n, np.float64)
    for i in range(n):
        v = a[i]
        if v >= 0.0:
            out[i] = log(1.0 + v)
        else:
            out[i] = -log(1.0 + (-v))
    return out

@njit(cache=True, nogil=True)
def rolling_cvs(array: np.ndarray, rolling_window: int) -> np.ndarray:
    a = _as_f64(array)
    std = rolling_std(a, rolling_window)
    mean = rolling_mean(a, rolling_window)
    n = a.size
    out = np.empty(n, np.float64)
    for i in range(n):
        out[i] = std[i] / (mean[i] + 1e-9)
    return out

@njit(cache=True, nogil=True)
def rolling_range(array, rolling_window):
    a = _as_f64(array)
    return rolling_max(a, rolling_window) - rolling_min(a, rolling_window)

@njit(cache=True, nogil=True)
def rolling_moment(array: np.ndarray, rolling_window: int, moment: int) -> np.ndarray:
    a = _as_f64(array)
    mu = rolling_mean(a, rolling_window)
    sigma = rolling_std(a, rolling_window)
    n = a.size
    out = np.empty(n, np.float64)
    # compute E[(x-mu)^moment] / sigma^moment
    for i in range(n):
        # local mean over window i handled via separate pass to keep speed:
        # we just reuse mu and compute numerator with an extra inner loop
        if i < rolling_window - 1:
            out[i] = np.nan
        else:
            s = 0.0
            for k in range(i - rolling_window + 1, i + 1):
                d = a[k] - mu[i]
                # power
                p = 1.0
                for _ in range(moment):
                    p *= d
                s += p
            num = s / rolling_window
            denom = 1.0
            if moment > 0:
                pow_sigma = sigma[i]
                for _ in range(moment - 1):
                    pow_sigma *= sigma[i]
                denom = pow_sigma + 1e-9
            out[i] = num / denom
    return out

@njit(cache=True, nogil=True)
def pct_change(arr):
    a = _as_f64(arr)
    n = a.size
    out = np.empty(n, np.float64)
    out[0] = np.nan
    for i in range(1, n):
        denom = a[i - 1]
        out[i] = (a[i] - denom) / (denom + 1e-9)
    return out

@njit(cache=True, nogil=True)
def log_diff_n(arr, n_diffs=1) -> np.ndarray:
    d = diff_n(arr, n_diffs)
    return signed_log1p(d)

@njit(cache=True, nogil=True)
def rolling_iqr(array: np.ndarray, rolling_window: int) -> np.ndarray:
    a = _as_f64(array)
    n = a.size
    out = np.empty(n, np.float64)
    if rolling_window > n:
        for i in range(n):
            out[i] = np.nan
        return out
    for i in range(rolling_window - 1):
        out[i] = np.nan
    buf = np.empty(rolling_window, np.float64)
    for i in range(rolling_window - 1, n):
        for k in range(rolling_window):
            buf[k] = a[i - rolling_window + 1 + k]
        buf.sort()
        # 25th and 75th percentiles (simple nearest-rank interpolation)
        q25_idx = 0.25 * (rolling_window - 1)
        q75_idx = 0.75 * (rolling_window - 1)
        lo = int(q25_idx)
        hi = int(q25_idx + 1.0)
        w = q25_idx - lo
        q25 = buf[lo] * (1.0 - w) + buf[hi] * w if hi < rolling_window else buf[lo]

        lo2 = int(q75_idx)
        hi2 = int(q75_idx + 1.0)
        w2 = q75_idx - lo2
        q75 = buf[lo2] * (1.0 - w2) + buf[hi2] * w2 if hi2 < rolling_window else buf[lo2]

        out[i] = q75 - q25
    return out

@njit(cache=True, nogil=True)
def rolling_mad(array: np.ndarray, rolling_window: int) -> np.ndarray:
    a = _as_f64(array)
    n = a.size
    out = np.empty(n, np.float64)
    if rolling_window > n:
        for i in range(n):
            out[i] = np.nan
        return out
    for i in range(rolling_window - 1):
        out[i] = np.nan
    win = np.empty(rolling_window, np.float64)
    dev = np.empty(rolling_window, np.float64)
    for i in range(rolling_window - 1, n):
        # median
        for k in range(rolling_window):
            win[k] = a[i - rolling_window + 1 + k]
        win.sort()
        med = win[rolling_window // 2] if (rolling_window % 2 == 1) else 0.5 * (win[rolling_window // 2 - 1] + win[rolling_window // 2])
        # deviations
        for k in range(rolling_window):
            dev[k] = abs(a[i - rolling_window + 1 + k] - med)
        dev.sort()
        mad = dev[rolling_window // 2] if (rolling_window % 2 == 1) else 0.5 * (dev[rolling_window // 2 - 1] + dev[rolling_window // 2])
        out[i] = mad
    return out

@njit(cache=True, nogil=True)
def rolling_robust_z(array, rolling_window):
    x = _as_f64(array)
    med = rolling_median(x, rolling_window)
    mad = rolling_mad(x, rolling_window)
    n = x.size
    out = np.empty(n, np.float64)
    for i in range(n):
        out[i] = (x[i] - med[i]) / (mad[i] + 1e-9)
    return out

@njit(cache=True, nogil=True)
def rolling_max_drawdown(array, rolling_window):
    x = _as_f64(array)
    rm = rolling_max(x, rolling_window)
    n = x.size
    out = np.empty(n, np.float64)
    for i in range(n):
        out[i] = (rm[i] - x[i]) / (rm[i] + 1e-9)
    return out

@njit(cache=True, nogil=True)
def rolling_trend_slope(array: np.ndarray, window: int) -> np.ndarray:
    y = _as_f64(array)
    n = y.size
    out = np.empty(n, np.float64)
    if window > n:
        for i in range(n):
            out[i] = np.nan
        return out
    for i in range(window - 1):
        out[i] = np.nan
    # precompute x demean denom for 0..window-1
    x_mean = (window - 1) * 0.5
    denom = 0.0
    for i in range(window):
        d = i - x_mean
        denom += d * d
    for t in range(window - 1, n):
        # compute y_mean
        y_mean = 0.0
        for k in range(t - window + 1, t + 1):
            y_mean += y[k]
        y_mean /= window
        # slope = sum( (x-xbar)*(y-ybar) ) / sum((x-xbar)^2)
        num = 0.0
        idx = 0
        for k in range(t - window + 1, t + 1):
            num += (idx - x_mean) * (y[k] - y_mean)
            idx += 1
        out[t] = num / denom
    return out

@njit(cache=True, nogil=True)
def rolling_entropy(array, window):
    a = _as_f64(array)
    n = a.size
    out = np.empty(n, np.float64)
    if window > n:
        for i in range(n):
            out[i] = np.nan
        return out
    for i in range(window - 1):
        out[i] = np.nan
    buf = np.empty(window, np.float64)
    for i in range(window - 1, n):
        # copy window and sort to count runs (unique frequencies)
        for k in range(window):
            buf[k] = a[i - window + 1 + k]
        buf.sort()
        # count frequencies
        ent = 0.0
        run_val = buf[0]
        run_cnt = 1
        for k in range(1, window):
            if buf[k] == run_val:
                run_cnt += 1
            else:
                p = run_cnt / window
                ent -= p * log(p)
                run_val = buf[k]
                run_cnt = 1
        p = run_cnt / window
        ent -= p * log(p)
        out[i] = ent
    return out

@njit(cache=True, nogil=True)
def rolling_positive_ratio(array, rolling_window):
    x = _as_f64(array)
    n = x.size
    # 1-lag diff
    d = np.empty(n, np.float64)
    d[0] = np.nan
    for i in range(1, n):
        d[i] = x[i] - x[i - 1]
    # positive mask as float
    pos = np.empty(n, np.float64)
    pos[0] = np.nan
    for i in range(1, n):
        pos[i] = 1.0 if (not np.isnan(d[i]) and d[i] > 0.0) else 0.0
    return rolling_mean(pos, rolling_window)

@njit(cache=True, nogil=True)
def count_direction_changes(x):
    a = _as_f64(x)
    n = a.size
    if n < 3:
        return 0.0
    # dx = diff(sign(diff(x)))
    flips = 0
    prev = a[1] - a[0]
    for i in range(2, n):
        cur = a[i] - a[i - 1]
        s_prev = 0.0
        if prev > 0: s_prev = 1.0
        elif prev < 0: s_prev = -1.0
        s_cur = 0.0
        if cur > 0: s_cur = 1.0
        elif cur < 0: s_cur = -1.0
        if s_cur != s_prev and s_prev != 0.0 and s_cur != 0.0:
            flips += 1
        prev = cur
    return float(flips)

@njit(cache=True, nogil=True)
def rolling_direction_changes(array, window):
    a = _as_f64(array)
    n = a.size
    out = np.empty(n, np.float64)
    if window > n:
        for i in range(n):
            out[i] = np.nan
        return out
    for i in range(window - 1):
        out[i] = np.nan
    buf = np.empty(window, np.float64)
    for i in range(window - 1, n):
        for k in range(window):
            buf[k] = a[i - window + 1 + k]
        out[i] = count_direction_changes(buf)
    return out

@njit(cache=True, nogil=True)
def rolling_autocorr(array, window, lag=1):
    x = _as_f64(array)
    n = x.size
    out = np.empty(n, np.float64)
    if window > n or lag < 1 or lag >= window:
        for i in range(n):
            out[i] = np.nan
        return out
    for i in range(window - 1):
        out[i] = np.nan
    for t in range(window - 1, n):
        # window [t-window+1 .. t]
        # y1: first window-lag, y2: last window-lag, both length window-lag
        m1 = 0.0
        m2 = 0.0
        L = window - lag
        for k in range(L):
            y1 = x[t - window + 1 + k]
            y2 = x[t - window + 1 + lag + k]
            m1 += y1
            m2 += y2
        m1 /= L
        m2 /= L
        num = 0.0
        s1 = 0.0
        s2 = 0.0
        for k in range(L):
            y1 = x[t - window + 1 + k] - m1
            y2 = x[t - window + 1 + lag + k] - m2
            num += y1 * y2
            s1 += y1 * y1
            s2 += y2 * y2
        den = sqrt(s1 * s2)
        out[t] = num / den if den != 0.0 else np.nan
    return out

@njit(cache=True, nogil=True)
def rolling_sharpe_like(array, rolling_window):
    x = _as_f64(array)
    mu = rolling_mean(x, rolling_window)
    sigma = rolling_std(x, rolling_window)
    n = x.size
    out = np.empty(n, np.float64)
    for i in range(n):
        out[i] = (mu[i] / (sigma[i] + 1e-9)) * np.sqrt(365.0)
    return out

@njit(cache=True, nogil=True)
def rolling_zscore_jump(array, window):
    x = _as_f64(array)
    n = x.size
    out = np.empty(n, np.float64)
    if window > n:
        for i in range(n):
            out[i] = np.nan
        return out
    for i in range(window - 1):
        out[i] = np.nan
    for i in range(window - 1, n):
        # stats for this window
        m = 0.0
        for k in range(i - window + 1, i + 1):
            m += x[k]
        m /= window
        s2 = 0.0
        for k in range(i - window + 1, i + 1):
            d = x[k] - m
            s2 += d * d
        s = sqrt(s2 / window)
        cnt = 0.0
        for k in range(i - window + 1, i + 1):
            z = abs((x[k] - m) / (s + 1e-9))
            if z > 2.0:
                cnt += 1.0
        out[i] = cnt
    return out

# Approximate rolling Yeo-Johnson:
# We use λ=0 per-window (log1p on x>=0, -log1p on -x for x<0) for speed and JIT-compatibility.
@njit(cache=True, nogil=True)
def rolling_yeojohnson(array: np.ndarray, window: int) -> np.ndarray:
    x = _as_f64(array)
    n = x.size
    out = np.empty(n, np.float64)
    if window > n:
        for i in range(n):
            out[i] = np.nan
        return out
    for i in range(window - 1):
        out[i] = np.nan
    for i in range(window - 1, n):
        v = x[i]
        if v >= 0.0:
            out[i] = log(1.0 + v)
        else:
            out[i] = -log(1.0 - v)
    return out

@njit(cache=True, nogil=True)
def log_returns(arr) -> np.ndarray:
    a = _as_f64(arr)
    n = a.size
    out = np.empty(n, np.float64)
    out[0] = np.nan
    for i in range(1, n):
        prev = a[i - 1]
        # Guard against non-positive or zero prev (rare if prices, but safe)
        r = a[i] / (prev + 1e-12)
        if r <= 0.0 or np.isnan(r):
            out[i] = np.nan
        else:
            out[i] = np.log(r)
    return out

@njit(cache=True, nogil=True)
def rolling_trend_angle(arr: np.ndarray, window: int, to_degrees: bool = False) -> np.ndarray:
    slopes = rolling_trend_slope(arr, window)
    n = slopes.size
    out = np.empty(n, np.float64)
    k = 180.0 / np.pi
    for i in range(n):
        s = slopes[i]
        if np.isnan(s):
            out[i] = np.nan
        else:
            ang = np.arctan(s)
            out[i] = ang * k if to_degrees else ang
    return out


@njit(cache=True, nogil=True)
def rolling_volatility_adjusted_return(arr: np.ndarray, window: int) -> np.ndarray:
    ret = pct_change(arr)
    std = rolling_std(ret, window)
    n = ret.size
    out = np.empty(n, np.float64)
    for i in range(n):
        out[i] = ret[i] / (std[i] + 1e-9)
    return out

@njit(cache=True, nogil=True)
def rolling_slope_acceleration(array: np.ndarray, window: int) -> np.ndarray:
    slopes = rolling_trend_slope(array, window)
    n = slopes.size
    out = np.empty(n, np.float64)
    for i in range(n):
        out[i] = np.nan
    for i in range(window, n):
        prev = slopes[i - 1]
        cur = slopes[i]
        out[i] = cur - prev
    return out
