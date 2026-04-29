import pandas as pd
import numpy as np

# ---------------------------------------------------------
# STOCHASTIC 320 (AGU+MultiStoch_FINAL)
# ---------------------------------------------------------
def compute_stoch320(df: pd.DataFrame, length=320, smooth=80) -> pd.Series:
    """
    Stochastic 320 smoothed by SMA 80.
    Requires at least ~400 periods of data.
    """
    high = df['High']
    low = df['Low']
    close = df['Close']
    
    highest_high = high.rolling(window=length).max()
    lowest_low = low.rolling(window=length).min()
    
    # Raw Stochastic
    stoch_raw = 100 * (close - lowest_low) / (highest_high - lowest_low)
    
    # Smoothed Stochastic (SMA)
    stoch_smoothed = stoch_raw.rolling(window=smooth).mean()
    
    return stoch_smoothed

# ---------------------------------------------------------
# 4 Multi-Timeframe Stochastic - Theo Park (80)
# ---------------------------------------------------------
def compute_theo_park(df: pd.DataFrame, length=80, smoothK=20, smoothD=40):
    """
    Theo Park Stoch Instance 3:
    %K3 = SMA(Stoch(80), 20)
    %D3 = SMA(%K3, 40)
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

def compute_fmfi(df: pd.DataFrame, fourier_period=5, mfi_length=9, mfi_smooth=4):
    """
    Discrete Fourier Transformed Money Flow Index (FMFI).
    Fourier smoothed HLC3 -> MFI -> EMA smoothed.
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
