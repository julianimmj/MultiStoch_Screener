# Arquivo gerado automaticamente filtrando ativos válidos (> 400 pregões) e alta liquidez

B3_STOCKS = [
    "PETR4.SA", "VALE3.SA", "ITUB4.SA", "PRIO3.SA", "PETR3.SA", "B3SA3.SA", "BBDC4.SA", "SBSP3.SA", "BBAS3.SA", "BPAC11.SA", "ENEV3.SA", "ITSA4.SA", "RENT3.SA", "ABEV3.SA", "SUZB3.SA", "WEGE3.SA", "RDOR3.SA", "EQTL3.SA", "VBBR3.SA", "LREN3.SA", "RADL3.SA", "CMIG4.SA", "GGBR4.SA", "CSMG3.SA", "RAIL3.SA", "BBSE3.SA", "VIVT3.SA", "ENGI11.SA", "CYRE3.SA", "UGPA3.SA", "CSAN3.SA", "HAPV3.SA", "BBDC3.SA", "MGLU3.SA", "TOTS3.SA", "TIMS3.SA", "ASAI3.SA", "CPFE3.SA", "DIRR3.SA", "MULT3.SA", "CEAB3.SA", "PSSA3.SA", "KLBN11.SA", "TAEE11.SA", "USIM5.SA", "CSNA3.SA", "COGN3.SA", "CXSE3.SA", "SANB11.SA", "MOVI3.SA", "NEOE3.SA", "ECOR3.SA", "VIVA3.SA", "TEND3.SA", "VAMO3.SA", "EGIE3.SA", "GOAU4.SA", "HYPE3.SA", "MRVE3.SA", "BEEF3.SA", "POMO4.SA", "JHSF3.SA", "ODPV3.SA", "BRKM5.SA", "PLPL3.SA", "SLCE3.SA", "SMTO3.SA", "IGTI11.SA", "BRAP4.SA", "AURE3.SA", "YDUQ3.SA", "GGPS3.SA", "SIMH3.SA", "FLRY3.SA", "MDNE3.SA", "IRBR3.SA", "CMIN3.SA", "INTB3.SA", "ALUP11.SA", "PGMN3.SA", "EZTC3.SA", "CBAV3.SA", "BRSR6.SA", "ALPA4.SA", "ANIM3.SA", "CVCB3.SA", "RAPT4.SA", "VULC3.SA", "SBFG3.SA", "TUPY3.SA", "UNIP6.SA", "PCAR3.SA", "GRND3.SA", "ONCO3.SA", "KEPL3.SA", "ABCB4.SA", "LWSA3.SA", "PINE4.SA", "BMOB3.SA", "RAIZ4.SA", "DXCO3.SA", "MYPK3.SA", "TGMA3.SA", "PNVL3.SA", "LAVV3.SA", "SOJA3.SA", "MDIA3.SA", "QUAL3.SA", "LOGG3.SA", "RANI3.SA", "HBSA3.SA", "VLID3.SA", "CASH3.SA", "BMGB4.SA", "FRAS3.SA", "FESA4.SA", "ARML3.SA", "EVEN3.SA", "POSI3.SA", "WIZC3.SA", "AGRO3.SA", "JALL3.SA", "CSED3.SA", "HBOR3.SA", "SYNE3.SA", "TRIS3.SA", "ROMI3.SA", "GFSA3.SA", "TASA4.SA", "MTRE3.SA", "AMBP3.SA", "VITT3.SA", "PTBL3.SA", "ESPA3.SA", "SEQL3.SA", "MATD3.SA", "NGRD3.SA"
]

B3_ETFS = [
    "BOVA11.SA", "SMAL11.SA", "IVVB11.SA", "HASH11.SA", "NASD11.SA", "DIVO11.SA"
]

B3_BDRS = [
    "AAPL34.SA", "MSFT34.SA", "AMZO34.SA", "GOGL34.SA", "TSLA34.SA", "META34.SA", "NVDC34.SA", "DISB34.SA", "MELI34.SA", "NFLX34.SA"
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
