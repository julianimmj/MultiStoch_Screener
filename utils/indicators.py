import pandas as pd
import numpy as np

# ---------------------------------------------------------
# STOCHASTIC 320 — Instância 1 do TradingView
# "4 Multi-Timeframe Stochastic-Theo Park"
# %K1 = 320, %D1 = 40 (smoothK), Smooth1 = 3 (smoothD)
# ---------------------------------------------------------
def compute_stoch320(df: pd.DataFrame, length=320, smoothK=40, smoothD=3):
    """
    Stochastic 320 — Instância 1 (Theo Park).
    %K1 = SMA(Stoch(320), 40)
    %D1 = SMA(%K1, 3)
    Requires at least ~400 periods of data.
    """
    high = df['High']
    low = df['Low']
    close = df['Close']
    
    highest_high = high.rolling(window=length).max()
    lowest_low = low.rolling(window=length).min()
    
    # Raw Stochastic
    stoch_raw = 100 * (close - lowest_low) / (highest_high - lowest_low)
    
    # %K1 — Smoothed Stochastic (SMA)
    k1 = stoch_raw.rolling(window=smoothK).mean()
    
    # %D1 — Signal line (SMA of K1)
    d1 = k1.rolling(window=smoothD).mean()
    
    return k1, d1

# ---------------------------------------------------------
# STOCHASTIC 80 — Instância 2 do TradingView
# "4 Multi-Timeframe Stochastic-Theo Park"
# %K2 = 80, %D2 = 40 (smoothK), Smooth2 = 3 (smoothD)
# ---------------------------------------------------------
def compute_theo_park(df: pd.DataFrame, length=80, smoothK=40, smoothD=3):
    """
    Theo Park Stoch Instance 2:
    %K2 = SMA(Stoch(80), 40)
    %D2 = SMA(%K2, 3)
    Matches TradingView '4 Multi-Timeframe Stochastic-Theo Park' Instance 2.
    """
    high = df['High']
    low = df['Low']
    close = df['Close']
    
    highest_high = high.rolling(window=length).max()
    lowest_low = low.rolling(window=length).min()
    
    stoch_raw = 100 * (close - lowest_low) / (highest_high - lowest_low)
    
    k2 = stoch_raw.rolling(window=smoothK).mean()
    d2 = k2.rolling(window=smoothD).mean()
    
    return k2, d2

# ---------------------------------------------------------
# STOCHASTIC 40 — Instância 3 do TradingView
# "4 Multi-Timeframe Stochastic-Theo Park"
# %K3 = 40, %D3 = 8 (smoothK), Smooth3 = 4 (smoothD)
# ---------------------------------------------------------
def compute_stoch40(df: pd.DataFrame, length=40, smoothK=8, smoothD=4):
    """
    Theo Park Stoch Instance 3:
    %K3 = SMA(Stoch(40), 8)
    %D3 = SMA(%K3, 4)
    Matches TradingView '4 Multi-Timeframe Stochastic-Theo Park' Instance 3.
    """
    high = df['High']
    low = df['Low']
    close = df['Close']
    
    highest_high = high.rolling(window=length).max()
    lowest_low = low.rolling(window=length).min()
    
    stoch_raw = 100 * (close - lowest_low) / (highest_high - lowest_low)
    
    k3 = stoch_raw.rolling(window=smoothK).mean()
    d3 = k3.rolling(window=smoothD).mean()
    
    return k3, d3

# ---------------------------------------------------------
# FOURIER TRANSFORMED MONEY FLOW INDEX (FMFI)
# ---------------------------------------------------------
def _hlc3(high, low, close):
    return (high + low + close) / 3.0

def _raw_mfi(typical_price, volume, length):
    money_flow = typical_price * volume
    
    positive_mf = money_flow.where(typical_price > typical_price.shift(1), 0.0)
    negative_mf = money_flow.where(typical_price <= typical_price.shift(1), 0.0)
    
    pmf = positive_mf.rolling(window=length).sum()
    nmf = negative_mf.rolling(window=length).sum()
    
    # Avoid division by zero
    nmf = nmf.replace(0, np.nan)
    mfi = 100.0 - (100.0 / (1.0 + pmf / nmf))
    return mfi.fillna(50.0)

def _ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def compute_fmfi(df: pd.DataFrame, fourier_period=4, mfi_length=6, mfi_smooth=3):
    """
    Discrete Fourier Transformed Money Flow Index (FMFI).
    Fourier smoothed HLC3 -> MFI -> EMA smoothed.
    Parameters: fourier_period=4, mfi_length=6, mfi_smooth=3.
    """
    high = df['High']
    low = df['Low']
    close = df['Close']
    volume = df['Volume']
    
    fourier_src = _hlc3(high, low, close)
    
    # Emulando o filtro passa-baixa básico da DFT com uma SMA 
    # (No código original, a DFT_re_im acaba atuando primariamente como um filtro de média / passa-baixa)
    ft = fourier_src.rolling(window=fourier_period).mean()
    
    raw_mfi = _raw_mfi(ft, volume, mfi_length)
    fmfi = _ema(raw_mfi, mfi_smooth)
    
    return fmfi
