import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Local modules
from data.tickers import get_all_tickers
from utils.indicators import compute_stoch320, compute_theo_park, compute_fmfi

# ---------------------------------------------------------
# SETUP DA PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="MultiStoch & FMFI Screener",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark Mode custom CSS
st.markdown("""
    <style>
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📈 MultiStoch Fourier Transformed Money Flow Confluence")
st.markdown("Screener quantitativo operando na confluência de múltiplos timeframes e ciclos de fluxo de dinheiro.")

# ---------------------------------------------------------
# FUNÇÃO DE CAPTURA DE DADOS (COM CACHE)
# ---------------------------------------------------------
@st.cache_data(ttl="24h")
def fetch_and_process_data(tickers):
    results = []
    
    # Precisamos de um histórico longo para o Stoch 320 (cerca de 400 pregões)
    # Vamos puxar 2 anos de dados
    start_date = (datetime.today() - timedelta(days=730)).strftime('%Y-%m-%d')
    
    # Download em batch é mais rápido no yfinance
    df_raw = yf.download(tickers, start=start_date, group_by='ticker', threads=True, progress=False)
    
    if len(tickers) == 1:
        # Quando tem só 1 ticker, o yfinance não usa MultiIndex no columns
        dict_dfs = {tickers[0]: df_raw}
    else:
        dict_dfs = {ticker: df_raw[ticker] for ticker in tickers}
        
    for ticker, df in dict_dfs.items():
        try:
            df = df.dropna()
            if len(df) < 400:
                continue # Dados insuficientes
                
            # Calcular indicadores
            stoch_320 = compute_stoch320(df)
            k3, d3 = compute_theo_park(df, length=80, smoothK=20, smoothD=40)
            fmfi = compute_fmfi(df)
            
            # Pegar últimos três dias para verificação de cruzamento exato (bolinha do TradingView = inversão)
            curr_fmfi = fmfi.iloc[-1]
            prev_fmfi = fmfi.iloc[-2]
            prev2_fmfi = fmfi.iloc[-3]
            
            curr_stoch320 = stoch_320.iloc[-1]
            curr_k3 = k3.iloc[-1]
            curr_d3 = d3.iloc[-1]
            
            price = df['Close'].iloc[-1]
            
            # Condições de Direção do FMFI (Inflection Point / Bolinha do TradingView)
            # ta.crossover(mf, mf[1]) significa mf[1] <= mf[2] and mf > mf[1]
            fmfi_crossover = (prev_fmfi <= prev2_fmfi) and (curr_fmfi > prev_fmfi)
            fmfi_crossunder = (prev_fmfi >= prev2_fmfi) and (curr_fmfi < prev_fmfi)
            
            # Condição BUY A
            buy_A_1 = (curr_k3 > curr_stoch320)
            buy_A_2 = (curr_fmfi < 50) and fmfi_crossover
            buy_A = buy_A_1 and buy_A_2
            
            # Condição BUY B
            buy_B_1 = curr_stoch320 > 85
            buy_B_2 = (curr_fmfi < 20) and fmfi_crossover
            buy_B = buy_B_1 and buy_B_2
            
            is_buy = buy_A or buy_B
            
            # Condição SELL
            sell_1 = curr_stoch320 < 85
            sell_2 = (curr_k3 < curr_stoch320)
            sell_3 = (curr_fmfi > 80) and fmfi_crossunder
            is_sell = sell_1 and sell_2 and sell_3
            
            signal = "-"
            color = ""
            if is_buy:
                signal = "🟢 BUY"
            elif is_sell:
                signal = "🔴 SELL"
                
            if signal != "-":
                results.append({
                    "Ativo": ticker.replace(".SA", ""),
                    "Preço Atual": f"R$ {price:.2f}",
                    "Sinal": signal,
                    "Stoch 320": round(curr_stoch320, 2),
                    "Theo Park %K3": round(curr_k3, 2),
                    "FMFI": round(curr_fmfi, 2)
                })
                
        except Exception as e:
            continue
            
    return pd.DataFrame(results)

# ---------------------------------------------------------
# INTERFACE DO USUÁRIO
# ---------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Configurações")
    inc_stocks = st.checkbox("Ações B3", value=True)
    inc_etfs = st.checkbox("ETFs", value=True)
    inc_bdrs = st.checkbox("BDRs", value=True)
    
    st.markdown("---")
    if st.button("🔄 Executar Varredura", type="primary"):
        st.cache_data.clear() # Limpa o cache para forçar atualização ao clicar no botão
        
tickers_to_scan = get_all_tickers(inc_stocks, inc_etfs, inc_bdrs)

if not tickers_to_scan:
    st.warning("Selecione pelo menos uma categoria de ativos na barra lateral.")
else:
    with st.spinner(f"Avaliando {len(tickers_to_scan)} ativos... (Pode demorar um pouco na primeira execução)"):
        df_results = fetch_and_process_data(tickers_to_scan)
        
    if df_results.empty:
        st.info("Nenhum ativo disparou sinal de Compra ou Venda hoje sob estas condições específicas.")
    else:
        st.success(f"Busca concluída! {len(df_results)} oportunidades encontradas.")
        st.dataframe(
            df_results,
            use_container_width=True,
            hide_index=True
        )

st.markdown("---")
st.caption("Desenvolvido para o portfólio de julianimmj. Os cálculos matemáticos exigem no mínimo 400 pregões de histórico por ativo.")
