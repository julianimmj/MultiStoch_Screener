import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# Uma lista massiva de tickers da B3 (inclui possíveis delistados para filtragem)
RAW_TICKERS = [
    "RRRP3", "ALPA4", "ABEV3", "AMBP3", "ARZZ3", "ASAI3", "AZUL4", "B3SA3", 
    "BBSE3", "BBDC3", "BBDC4", "BRAP4", "BBAS3", "BRKM5", "BRFS3", "BPAC11", 
    "CRFB3", "CCRO3", "CMIG4", "CIEL3", "COGN3", "CPLE6", "CSAN3", "CPFE3", 
    "CMIN3", "CVCB3", "CYRE3", "DXCO3", "ELET3", "ELET6", "EMBR3", "ENGI11", 
    "ENEV3", "EGIE3", "EQTL3", "EZTC3", "FLRY3", "GGBR4", "GOAU4", "GOLL4", 
    "NTCO3", "SOMA3", "HAPV3", "HYPE3", "IGTI11", "IRBR3", "ITSA4", "ITUB4", 
    "JBSS3", "JHSF3", "KLBN11", "RENT3", "LWSA3", "LREN3", "MGLU3", "MRFG3", 
    "CASH3", "BEEF3", "MRVE3", "MULT3", "PCAR3", "PETR3", "PETR4", "PRIO3", 
    "PETZ3", "RADL3", "RAIZ4", "RDOR3", "RAIL3", "SBSP3", "SANB11", "SMTO3", 
    "CSNA3", "SLCE3", "SUZB3", "TAEE11", "VIVT3", "TIMS3", "TOTS3", "UGPA3", 
    "USIM5", "VALE3", "VIIA3", "VBBR3", "WEGE3", "YDUQ3", "AERI3", "AESB3", 
    "ALUP11", "ANIM3", "ARML3", "BMOB3", "BRSR6", "CBAV3", "CEAB3", "CLSA3", 
    "CSMG3", "CSED3", "DIRR3", "ECOR3", "ENAT3", "ESPA3", "EVEN3", "FESA4", 
    "GFSA3", "GGPS3", "GRND3", "GUAR3", "HBOR3", "HBSA3", "INTB3", "ISIS3", 
    "JALL3", "KEPL3", "LAVV3", "LOGG3", "LOGN3", "LUPA3", "MATD3", "MDIA3", 
    "MEAL3", "MOVI3", "MTRE3", "MYPK3", "NEOE3", "NGRD3", "ODPV3", "ONCO3", 
    "PARD3", "PGMN3", "PLPL3", "PNVL3", "POMO4", "PORP4", "POSI3", "PTBL3", 
    "QUAL3", "RANI3", "RAPT4", "RCSL3", "ROMI3", "SBFG3", "SEQL3", "SIMH3", 
    "SQIA3", "STBP3", "SYNE3", "TCSA3", "TEND3", "TGMA3", "TRIS3", "TRPL4", 
    "TUPY3", "UNIP6", "VAMO3", "VIVA3", "VULC3", "WIZC3", "ZAMP3", "CXSE3",
    "PSSA3", "BRIT3", "AGRO3", "SOJA3", "VITT3", "TASA4", "RNEW11", "AURE3",
    "MDNE3", "VLID3", "FHER3", "FRAS3", "BMGB4", "PINE4", "ABCB4", "BPAN4"
]

def generate_valid_tickers():
    print(f"Buscando histórico de {len(RAW_TICKERS)} ativos. Isso pode demorar...")
    tickers_sa = [t + ".SA" for t in set(RAW_TICKERS)]
    start_date = (datetime.today() - timedelta(days=730)).strftime('%Y-%m-%d')
    
    # Download batch
    df_raw = yf.download(tickers_sa, start=start_date, group_by='ticker', threads=True, progress=False)
    
    valid_stocks = []
    
    for ticker in tickers_sa:
        if ticker in df_raw.columns.levels[0] if isinstance(df_raw.columns, pd.MultiIndex) else [ticker]:
            df = df_raw[ticker] if isinstance(df_raw.columns, pd.MultiIndex) else df_raw
            df = df.dropna(subset=['Close', 'Volume'])
            
            # Precisamos de 400 dias mínimos para o Stoch 320 + SMA 80
            if len(df) >= 400:
                avg_vol = df['Volume'].tail(30).mean() * df['Close'].tail(30).mean() # Financeiro
                if avg_vol > 500000: # Liquidez diária maior que 500k BRL
                    valid_stocks.append((ticker, avg_vol))
    
    # Sort by liquidity descending
    valid_stocks.sort(key=lambda x: x[1], reverse=True)
    
    # Take top 150
    top_150 = [x[0] for x in valid_stocks[:150]]
    
    # Keep the same ETFs and BDRs from before
    etfs = ["BOVA11.SA", "SMAL11.SA", "IVVB11.SA", "HASH11.SA", "NASD11.SA", "DIVO11.SA"]
    bdrs = ["AAPL34.SA", "MSFT34.SA", "AMZO34.SA", "GOGL34.SA", "TSLA34.SA", "META34.SA",
            "NVDC34.SA", "DISB34.SA", "MELI34.SA", "NFLX34.SA"]
            
    code = f'''# Arquivo gerado automaticamente filtrando ativos válidos (> 400 pregões) e alta liquidez

B3_STOCKS = [
    {', '.join([f'"{t}"' for t in top_150])}
]

B3_ETFS = [
    {', '.join([f'"{t}"' for t in etfs])}
]

B3_BDRS = [
    {', '.join([f'"{t}"' for t in bdrs])}
]

def get_all_tickers(include_stocks=True, include_etfs=True, include_bdrs=True):
    tickers = []
    if include_stocks:
        tickers.extend(B3_STOCKS)
    if include_etfs:
        tickers.extend(B3_ETFS)
    if include_bdrs:
        tickers.extend(B3_BDRS)
    return sorted(list(set(tickers)))
'''
    with open(r"C:\Users\julia\OneDrive\Documentos\gravity\MultiStoch_Screener\data\tickers.py", "w", encoding="utf-8") as f:
        f.write(code)
    
    print(f"Salvos {len(top_150)} ativos em tickers.py")

if __name__ == "__main__":
    generate_valid_tickers()
