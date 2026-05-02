"""
Teste de Validação Completa do Screener
Simula exatamente o que o app.py faz, mas com output detalhado de debug.
"""
import sys
sys.path.append(r"C:\Users\julia\OneDrive\Documentos\gravity\MultiStoch_Screener")

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from data.tickers import get_all_tickers
from utils.indicators import compute_stoch320, compute_theo_park, compute_fmfi

start_date = (datetime.today() - timedelta(days=730)).strftime('%Y-%m-%d')

tickers = get_all_tickers(include_stocks=True, include_etfs=True, include_bdrs=True)
print(f"Total de ativos na lista: {len(tickers)}")

print("Baixando dados do Yahoo Finance (batch)...")
df_raw = yf.download(tickers, start=start_date, group_by='ticker', threads=True, progress=False)

dict_dfs = {ticker: df_raw[ticker] for ticker in tickers}

total_ok = 0
total_skip = 0
total_err = 0
buys = []
sells = []

for ticker, df in dict_dfs.items():
    try:
        df = df.dropna()
        if len(df) < 400:
            total_skip += 1
            continue

        stoch_320 = compute_stoch320(df)
        k3, d3 = compute_theo_park(df, length=80, smoothK=20, smoothD=40)
        fmfi = compute_fmfi(df)

        curr_fmfi = fmfi.iloc[-1]
        prev_fmfi = fmfi.iloc[-2]
        prev2_fmfi = fmfi.iloc[-3]
        curr_stoch320 = stoch_320.iloc[-1]
        curr_k3 = k3.iloc[-1]
        prev_k3 = k3.iloc[-2]
        price = df['Close'].iloc[-1]

        fmfi_crossover = (prev_fmfi <= prev2_fmfi) and (curr_fmfi > prev_fmfi)
        fmfi_crossunder = (prev_fmfi >= prev2_fmfi) and (curr_fmfi < prev_fmfi)

        buy_A = (curr_k3 > curr_stoch320) and (curr_fmfi < 50) and fmfi_crossover
        buy_B = (curr_stoch320 > 85) and (curr_fmfi < 20) and fmfi_crossover
        buy_C = (curr_stoch320 > 50) and (curr_stoch320 < 85) and (curr_fmfi < 50) and fmfi_crossover and (curr_k3 >= prev_k3)
        is_buy = buy_A or buy_B or buy_C

        sell_1 = curr_stoch320 < 85
        sell_2 = curr_k3 < curr_stoch320
        sell_3 = (curr_fmfi > 80) and fmfi_crossunder
        is_sell = sell_1 and sell_2 and sell_3

        k3_c = round(curr_k3, 2)
        k3_p = round(prev_k3, 2)

        if is_buy:
            if buy_C and not (buy_A or buy_B):
                risco = "Alto"
            else:
                if k3_c > k3_p:
                    risco = "Baixo"
                elif k3_c == k3_p:
                    risco = "Médio"
                elif k3_c < k3_p:
                    risco = "Alto"
            buys.append(f"  BUY  {ticker.replace('.SA',''):>8}  R${price:>8.2f}  Stoch80={k3_c:>6.2f}%  Risco={risco}")

        if is_sell:
            if k3_c < k3_p:
                risco = "Baixo"
            elif k3_c == k3_p:
                risco = "Médio"
            elif k3_c > k3_p:
                risco = "Alto"
            sells.append(f"  SELL {ticker.replace('.SA',''):>8}  R${price:>8.2f}  Stoch80={k3_c:>6.2f}%  Risco={risco}")

        total_ok += 1

    except Exception as e:
        total_err += 1

print(f"\n{'='*60}")
print(f"RESULTADOS DA VARREDURA")
print(f"{'='*60}")
print(f"Ativos processados com sucesso: {total_ok}")
print(f"Ativos pulados (< 400 pregões): {total_skip}")
print(f"Ativos com erro:                {total_err}")
print(f"{'='*60}")

if buys:
    print(f"\n[BUY] SINAIS DE COMPRA ({len(buys)}):")
    for b in buys:
        print(b)
else:
    print("\n[BUY] Nenhum sinal de COMPRA disparado hoje.")

if sells:
    print(f"\n[SELL] SINAIS DE VENDA ({len(sells)}):")
    for s in sells:
        print(s)
else:
    print("\n[SELL] Nenhum sinal de VENDA disparado hoje.")

print(f"\n[OK] Teste concluido com sucesso!")
