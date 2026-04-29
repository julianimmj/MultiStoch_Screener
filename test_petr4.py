import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

sys.path.append(r"C:\Users\julia\OneDrive\Documentos\gravity\MultiStoch_Screener")

from utils.indicators import compute_stoch320, compute_theo_park, compute_fmfi

start_date = (datetime.today() - timedelta(days=730)).strftime('%Y-%m-%d')
df = yf.download("PETR4.SA", start=start_date, progress=False)

# Garantir que é um DataFrame plano se vier com multiindex
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.droplevel(1)

df = df.dropna()

stoch_320 = compute_stoch320(df)
k3, d3 = compute_theo_park(df, length=80, smoothK=20, smoothD=40)
fmfi = compute_fmfi(df)

curr_fmfi = fmfi.iloc[-1]
prev_fmfi = fmfi.iloc[-2]
prev2_fmfi = fmfi.iloc[-3]

curr_stoch320 = stoch_320.iloc[-1]
curr_k3 = k3.iloc[-1]
prev_k3 = k3.iloc[-2]
curr_d3 = d3.iloc[-1]

fmfi_crossover = (prev_fmfi <= prev2_fmfi) and (curr_fmfi > prev_fmfi)

buy_A_1 = (curr_k3 > curr_stoch320)
buy_A_2 = (curr_fmfi < 50) and fmfi_crossover
buy_A = buy_A_1 and buy_A_2

buy_B_1 = curr_stoch320 > 85
buy_B_2 = (curr_fmfi < 20) and fmfi_crossover
buy_B = buy_B_1 and buy_B_2

is_buy = buy_A or buy_B

print("--- PETR4.SA DATA ---")
print(f"Stoch 320: {curr_stoch320:.2f}")
print(f"FMFI (D): {curr_fmfi:.2f}")
print(f"FMFI (D-1): {prev_fmfi:.2f}")
print(f"FMFI (D-2): {prev2_fmfi:.2f}")
print(f"FMFI Crossover (Bolinha): {fmfi_crossover}")
print(f"Stoch 80 D (Current): {curr_k3:.4f}")
print(f"Stoch 80 D-1 (Prev): {prev_k3:.4f}")
print(f"is_buy: {is_buy}")
print(f"Buy A: {buy_A} | Buy B: {buy_B}")

if is_buy:
    k3_c = round(curr_k3, 2)
    k3_p = round(prev_k3, 2)
    print(f"Arredondado -> D: {k3_c} | D-1: {k3_p}")
    if k3_c > k3_p:
        print("Risco Calculado: Baixo")
    elif k3_c == k3_p:
        print("Risco Calculado: Médio")
    elif k3_c < k3_p:
        print("Risco Calculado: Alto")
