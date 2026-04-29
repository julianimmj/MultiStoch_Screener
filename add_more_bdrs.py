import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import ast

MORE_BDRS = [
    "COCA34.SA", "JNJB34.SA", "VISA34.SA", "WALM34.SA", "PGCO34.SA", "NIKE34.SA",
    "MCDC34.SA", "BBDC34.SA", "HOME34.SA", "BERK34.SA", "JPMC34.SA", "MSBR34.SA",
    "BBOV11.SA", "EXXO34.SA", "CHVX34.SA", "ABUD34.SA", "PFIZ34.SA", "MRCK34.SA",
    "FDXB34.SA", "AALL34.SA", "SBUB34.SA", "GOGL35.SA", "BOEI34.SA", "CMCS34.SA",
    "CSCO34.SA", "INTC34.SA", "QCOM34.SA", "TXSA34.SA", "UBER34.SA", "SNOW34.SA",
    "CRWD34.SA", "SQQU34.SA", "PYPL34.SA", "ZMBI34.SA", "ROKU34.SA", "SPOT34.SA",
    "AIRB34.SA", "TMOS34.SA", "HOND34.SA", "SONY34.SA", "SSFO34.SA"
]

def add_more_bdrs():
    print(f"Testando {len(MORE_BDRS)} novos BDRs...")
    start_date = (datetime.today() - timedelta(days=730)).strftime('%Y-%m-%d')
    df_raw = yf.download(MORE_BDRS, start=start_date, group_by='ticker', threads=True, progress=False)
    
    valid_bdrs = []
    
    for ticker in MORE_BDRS:
        if ticker in df_raw.columns.levels[0] if isinstance(df_raw.columns, pd.MultiIndex) else [ticker]:
            df = df_raw[ticker] if isinstance(df_raw.columns, pd.MultiIndex) else df_raw
            df = df.dropna(subset=['Close', 'Volume'])
            
            if len(df) >= 400:
                avg_vol = df['Volume'].tail(30).mean() * df['Close'].tail(30).mean()
                if avg_vol > 100000: # Liquidez diária maior que 100k BRL para BDRs (menos líquidos que ações)
                    valid_bdrs.append(ticker)
    
    print(f"Encontrados {len(valid_bdrs)} BDRs liquidos e validos.")
    
    # Atualizar tickers.py
    with open(r"C:\Users\julia\OneDrive\Documentos\gravity\MultiStoch_Screener\data\tickers.py", "r", encoding="utf-8") as f:
        content = f.read()
        
    # Extrair lista atual
    import re
    match = re.search(r'B3_BDRS = \[(.*?)\]', content, re.DOTALL)
    if match:
        current_bdrs_str = match.group(1)
        current_bdrs = [t.strip().strip('"').strip("'") for t in current_bdrs_str.split(',') if t.strip()]
        
        all_bdrs = sorted(list(set(current_bdrs + valid_bdrs)))
        
        new_bdrs_str = "B3_BDRS = [\n    " + ', '.join([f'"{t}"' for t in all_bdrs]) + "\n]"
        new_content = content.replace(match.group(0), new_bdrs_str)
        
        with open(r"C:\Users\julia\OneDrive\Documentos\gravity\MultiStoch_Screener\data\tickers.py", "w", encoding="utf-8") as f:
            f.write(new_content)
            print("tickers.py atualizado com sucesso!")

if __name__ == "__main__":
    add_more_bdrs()
