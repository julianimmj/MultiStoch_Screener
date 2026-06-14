import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Dynamically append current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.indicators import compute_stoch320, compute_theo_park, compute_stoch40, compute_fmfi

start_date = (datetime.today() - timedelta(days=730)).strftime('%Y-%m-%d')
df = yf.download("PETR4.SA", start=start_date, progress=False)

# Garantir que é um DataFrame plano se vier com multiindex
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.droplevel(1)

df = df.dropna()

k1, d1 = compute_stoch320(df)
k2, d2 = compute_theo_park(df)
k3, d3 = compute_stoch40(df)
fmfi = compute_fmfi(df)

curr_fmfi = fmfi.iloc[-1]
prev_fmfi = fmfi.iloc[-2]
prev2_fmfi = fmfi.iloc[-3]

curr_k1 = k1.iloc[-1]
curr_k2 = k2.iloc[-1]
prev_k2 = k2.iloc[-2]
curr_k3 = k3.iloc[-1]
prev_k3 = k3.iloc[-2]

fmfi_crossover = (prev_fmfi <= prev2_fmfi) and (curr_fmfi > prev_fmfi)

buy_A = (
    (curr_k2 >= curr_k1) and
    (curr_k2 >= prev_k2) and
    (curr_k3 >= 20) and
    (curr_fmfi <= 50) and
    fmfi_crossover
)

buy_B = (
    (curr_k1 >= 85) and
    (curr_k2 >= prev_k2) and
    (curr_k3 >= 20) and
    (curr_fmfi <= 50) and
    fmfi_crossover
)

buy_C = (
    (curr_k2 <= curr_k1) and
    (curr_k2 >= prev_k2) and
    (curr_k3 >= curr_k2) and
    (curr_k3 >= 20) and
    (curr_fmfi <= 50) and
    fmfi_crossover
)

is_buy = buy_A or buy_B or buy_C

print("--- PETR4.SA DATA ---")
print(f"Stoch 320 (%K1): {curr_k1:.2f}")
print(f"Stoch 80 (%K2): {curr_k2:.2f} (prev: {prev_k2:.2f})")
print(f"Stoch 40 (%K3): {curr_k3:.2f} (prev: {prev_k3:.2f})")
print(f"FMFI (D): {curr_fmfi:.2f}")
print(f"FMFI (D-1): {prev_fmfi:.2f}")
print(f"FMFI (D-2): {prev2_fmfi:.2f}")
print(f"FMFI Crossover (Bolinha): {fmfi_crossover}")
print(f"is_buy: {is_buy}")
print(f"Buy A: {buy_A} | Buy B: {buy_B} | Buy C: {buy_C}")

if is_buy:
    k3_c = round(curr_k3, 2)
    k3_p = round(prev_k3, 2)
    print(f"Arredondado -> D: {k3_c} | D-1: {k3_p}")
    if buy_C and not (buy_A or buy_B):
        risco = "Alto"
    else:
        if k3_c > k3_p:
            risco = "Baixo"
        elif k3_c == k3_p:
            risco = "Médio"
        elif k3_c < k3_p:
            risco = "Alto"
    print(f"Risco Calculado: {risco}")
