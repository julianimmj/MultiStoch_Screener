# Lista de ativos comuns da B3 com boa liquidez
# Pode ser expandida futuramente

B3_STOCKS = [
    "PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA", "B3SA3.SA", "BBAS3.SA",
    "ABEV3.SA", "WEGE3.SA", "RENT3.SA", "SUZB3.SA", "EQTL3.SA", "RADL3.SA",
    "VIVT3.SA", "LREN3.SA", "JBSS3.SA", "HAPV3.SA", "GGBR4.SA", "PRIO3.SA",
    "SBSP3.SA", "CMIG4.SA", "BBSE3.SA", "CPLE6.SA", "CSAN3.SA", "TOTS3.SA",
    "KLBN11.SA", "EGIE3.SA", "ENEV3.SA", "TIMS3.SA", "CCRO3.SA", "ALOS3.SA",
    "BRFS3.SA", "ASAI3.SA", "UGPA3.SA", "CSNA3.SA", "GOAU4.SA", "MULT3.SA",
    "EMBR3.SA", "CPFE3.SA", "YDUQ3.SA", "NTCO3.SA", "MGLU3.SA", "MRVE3.SA",
    "CYRE3.SA", "EZTC3.SA", "TAEE11.SA", "TRPL4.SA", "BRAP4.SA", "FLRY3.SA",
    "POMO4.SA", "CXSE3.SA"
]

B3_ETFS = [
    "BOVA11.SA", "SMAL11.SA", "IVVB11.SA", "HASH11.SA", "NASD11.SA", "DIVO11.SA"
]

B3_BDRS = [
    "AAPL34.SA", "MSFT34.SA", "AMZO34.SA", "GOGL34.SA", "TSLA34.SA", "META34.SA",
    "NVDC34.SA", "DISB34.SA", "MELI34.SA", "NFLX34.SA"
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
