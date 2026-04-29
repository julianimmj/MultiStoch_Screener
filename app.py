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
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #F8FAFC;
    }
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        background-color: rgba(15, 23, 42, 0.6);
    }
    div.stButton > button:first-child {
        background-color: #3b82f6;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.3s ease;
    }
    div.stButton > button:first-child:hover {
        background-color: #2563eb;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);
    }
    </style>
""", unsafe_allow_html=True)

st.title("📈 Screener Quantitativo Institucional")
st.markdown("""
**Motor de Busca Multi-Timeframe:**  
Este algoritmo avançado monitora a confluência de múltiplos tempos gráficos e analisa o fluxo financeiro através da Transformada Discreta de Fourier. O motor varre centenas de ativos do mercado para identificar anomalias estatísticas que sugerem exaustão de ciclos, permitindo o rastreamento preciso de oportunidades de reversão de tendência.
""")

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
            prev_k3 = k3.iloc[-2]
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
            risco = "-"
            
            # Arredondar para 2 casas decimais para permitir D == D-1
            k3_c = round(curr_k3, 2)
            k3_p = round(prev_k3, 2)
            
            if is_buy:
                signal = "🟢 BUY"
                if k3_c > k3_p:
                    risco = "Baixo"
                elif k3_c == k3_p:
                    risco = "Médio"
                elif k3_c < k3_p:
                    # Se estiver caindo e estiver entre 20 e 50 (conforme regra restrita) é Alto.
                    # Se cair fora dessa faixa, assumimos Alto por ser um movimento adverso (queda no Buy).
                    risco = "Alto"
            elif is_sell:
                signal = "🔴 SELL"
                if k3_c < k3_p:
                    risco = "Baixo"
                elif k3_c == k3_p:
                    risco = "Médio"
                elif k3_c > k3_p:
                    # Se estiver subindo e estiver entre 50 e 80 é Alto.
                    # Se cair fora da faixa, assumimos Alto por ser movimento adverso (alta no Sell).
                    risco = "Alto"
                
            if signal != "-":
                results.append({
                    "Ativo": ticker.replace(".SA", ""),
                    "Preço Atual": f"R$ {price:.2f}",
                    "Sinal": signal,
                    "Risco": risco,
                    "Stoch 80": f"{curr_k3:.2f}%"
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
st.markdown("""
<div style='background-color: rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 8px; border-left: 4px solid #f59e0b; font-size: 14px; color: #cbd5e1;'>
<strong>⚠️ AVISO LEGAL (DISCLAIMER):</strong> Esta aplicação possui finalidade puramente educacional e de estudo quantitativo. 
Os sinais gerados por este motor (BUY/SELL) baseiam-se estritamente em modelos estatísticos e matemáticos aplicados a dados históricos. 
<strong>Eles NÃO configuram, sob nenhuma hipótese, recomendação, indicação ou aconselhamento de compra ou venda de valores mobiliários.</strong> 
O mercado de capitais envolve riscos. O uso desta ferramenta para tomada de decisões financeiras é de inteira responsabilidade do usuário.
</div>
""", unsafe_allow_html=True)
