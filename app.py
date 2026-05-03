import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import base64
from pathlib import Path
from datetime import datetime, timedelta

# Local modules
from data.tickers import get_all_tickers
from utils.indicators import compute_stoch320, compute_theo_park, compute_fmfi

# ---------------------------------------------------------
# SETUP DA PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="MultiStoch & FMFI Confluence",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Ocultar elementos do Streamlit Cloud (sem afetar sidebar) ──
st.markdown("""
<style>
    .stAppDeployButton {display: none !important;}
    .stMainMenu {display: none !important;}
    [data-testid="manage-app-button"] {display: none !important;}
    #GithubIcon {display: none !important;}
    .viewerBadge_container__1QSob {display: none !important;}
    .viewerBadge_link__qRIco {display: none !important;}
    [data-testid="stStatusWidget"] {display: none !important;}
</style>
""", unsafe_allow_html=True)

# ==========================================================
# DESIGN SYSTEM: Darklight Premium + Glassmorphism + Mobile
# ==========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Base ────────────────────────────────────── */
html, body, .stApp {
    font-family: 'Inter', sans-serif;
}
.stApp {
    background: linear-gradient(160deg, #0a0f1a 0%, #111827 40%, #1e1b4b 100%);
    color: #e2e8f0;
}

/* ── Sidebar ─────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1a1040 100%) !important;
    border-right: 1px solid rgba(99, 102, 241, 0.15);
}
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 {
    color: #a5b4fc !important;
}

/* ── Botões ───────────────────────────────────── */
div.stButton > button {
    background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.75rem 1.6rem !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    letter-spacing: 0.02em !important;
    transition: all 0.3s cubic-bezier(.4,0,.2,1) !important;
    box-shadow: 0 2px 8px rgba(79, 70, 229, 0.3) !important;
}
div.stButton > button:hover {
    background: linear-gradient(135deg, #6366f1 0%, #818cf8 100%) !important;
    box-shadow: 0 6px 20px rgba(99, 102, 241, 0.45) !important;
    transform: translateY(-1px) !important;
}

/* ── Tabela / DataFrame ──────────────────────── */
.stDataFrame {
    border-radius: 12px;
    overflow: hidden;
}
.stDataFrame [data-testid="stDataFrameResizable"] {
    border: 1px solid rgba(99, 102, 241, 0.15) !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}

/* ── Cards glassmorphism ─────────────────────── */
.glass-card {
    background: rgba(255, 255, 255, 0.04);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 1.6rem 2rem;
    margin-bottom: 1.2rem;
}
.glass-card h3 {
    margin-top: 0;
    color: #a5b4fc;
    font-weight: 600;
    font-size: 1.1rem;
}
.glass-card p {
    color: #94a3b8;
    font-size: 0.95rem;
    line-height: 1.7;
}

/* ── Streamlit branding — gerenciado pelo bloco hide_streamlit_style ── */

/* ── Hero section ──────────────────────────────── */
.hero-container {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 0.2rem;
}
.hero-logo {
    height: 4.2rem;
    object-fit: contain;
    flex-shrink: 0;
}
.hero-title {
    font-size: 3.2rem !important;
    font-weight: 700 !important;
    background: linear-gradient(90deg, #c7d2fe, #818cf8, #6366f1) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    margin: 0 !important;
    line-height: 1.1 !important;
    padding-top: 0.2rem;
    letter-spacing: -0.02em;
}
.hero-subtitle {
    color: #64748b;
    font-size: 1.05rem;
    font-weight: 400;
    margin-bottom: 1.5rem;
}

/* ── Disclaimer ──────────────────────────────── */
.disclaimer {
    background: rgba(245, 158, 11, 0.06);
    border-left: 4px solid #f59e0b;
    border-radius: 8px;
    padding: 1.1rem 1.4rem;
    font-size: 0.85rem;
    color: #94a3b8;
    line-height: 1.7;
    margin-top: 2rem;
}
.disclaimer strong { color: #fbbf24; }

/* ── Responsividade Mobile ───────────────────── */
@media (max-width: 768px) {
    .hero-container {
        flex-direction: column;
        align-items: center;
        text-align: center;
        gap: 0.5rem;
    }
    .hero-logo { 
        height: 3.2rem; 
        margin-top: 0;
    }
    .hero-title { 
        font-size: 1.8rem !important; 
        line-height: 1.25 !important;
        text-align: center;
        padding-top: 0;
    }
    .hero-subtitle { 
        font-size: 0.9rem; 
        text-align: center;
    }
    .glass-card { padding: 1rem 1.2rem; }
    div.stButton > button {
        width: 100% !important;
        font-size: 14px !important;
        padding: 0.65rem 1rem !important;
    }
}
</style>
""", unsafe_allow_html=True)

# ==========================================================
# HERO SECTION
# ==========================================================
logo_path = Path(__file__).parent / "assets" / "logo.png"
if logo_path.exists():
    logo_b64 = base64.b64encode(logo_path.read_bytes()).decode()
    logo_html = f'<img class="hero-logo" src="data:image/png;base64,{logo_b64}"/>'
else:
    logo_html = ""

st.markdown(f'''
<div class="hero-container">
    {logo_html}
    <h1 class="hero-title">MultiStoch Fourier Transformed Money Flow Confluence</h1>
</div>
''', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">Screener quantitativo de alta precisão para o mercado brasileiro</p>', unsafe_allow_html=True)

st.markdown("""
<div class="glass-card">
    <h3>⚡ Como funciona o Motor de Busca</h3>
    <p>
        Este algoritmo avançado monitora a <strong>confluência de múltiplos tempos gráficos</strong> 
        e analisa o fluxo financeiro institucional através da <strong>Transformada Discreta de Fourier</strong>. 
        O motor varre centenas de ativos em tempo real para identificar <strong>anomalias estatísticas</strong> 
        que sugerem exaustão de ciclos de mercado, permitindo o rastreamento preciso de oportunidades 
        de reversão de tendência com classificação de risco integrada.
    </p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# FUNÇÃO DE CAPTURA DE DADOS (COM CACHE)
# ---------------------------------------------------------
@st.cache_data(ttl="24h")
def fetch_and_process_data(tickers):
    results_today = []
    results_history = []
    
    # Data de corte para o histórico (15 dias corridos)
    cutoff_date = datetime.today() - timedelta(days=15)
    
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
            
            # Iterar sobre os dias recentes (últimos 15 dias)
            recent_dates = df[df.index >= pd.Timestamp(cutoff_date)].index
            
            for date_idx in recent_dates:
                i = df.index.get_loc(date_idx)
                if i < 3: # Precisamos de pelo menos 3 dias de histórico anterior
                    continue
                    
                curr_fmfi = fmfi.iloc[i]
                prev_fmfi = fmfi.iloc[i-1]
                prev2_fmfi = fmfi.iloc[i-2]
                
                curr_stoch320 = stoch_320.iloc[i]
                curr_k3 = k3.iloc[i]
                prev_k3 = k3.iloc[i-1]
                curr_d3 = d3.iloc[i]
                
                price = df['Close'].iloc[i]
                
                # Condições de Direção do FMFI (Inflection Point / Bolinha do TradingView)
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
                
                # Condição BUY C
                buy_C_1 = (curr_stoch320 > 50) and (curr_stoch320 < 85)
                buy_C_2 = (curr_fmfi < 50) and fmfi_crossover
                buy_C_3 = (curr_k3 >= prev_k3)
                buy_C = buy_C_1 and buy_C_2 and buy_C_3
                
                is_buy = buy_A or buy_B or buy_C
                
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
                    if buy_C and not (buy_A or buy_B):
                        risco = "Alto"
                    else:
                        if k3_c > k3_p:
                            risco = "Baixo"
                        elif k3_c == k3_p:
                            risco = "Médio"
                        elif k3_c < k3_p:
                            risco = "Alto"
                elif is_sell:
                    signal = "🔴 SELL"
                    if k3_c < k3_p:
                        risco = "Baixo"
                    elif k3_c == k3_p:
                        risco = "Médio"
                    elif k3_c > k3_p:
                        risco = "Alto"
                    
                if signal != "-":
                    # Adicionar ao histórico
                    results_history.append({
                        "Data (Raw)": date_idx, # Para ordenação depois
                        "Data": date_idx.strftime('%d/%m/%Y'),
                        "Ativo": ticker.replace(".SA", ""),
                        "Sinal": signal,
                        "Preço": f"R$ {price:.2f}",
                        "Risco": risco,
                        "Stoch 80": f"{curr_k3:.2f}%"
                    })
                    
                    # Se for o último dia (Hoje), adicionar à tabela principal
                    if i == len(df) - 1:
                        results_today.append({
                            "Data": date_idx.strftime('%d/%m/%Y'),
                            "Ativo": ticker.replace(".SA", ""),
                            "Sinal": signal,
                            "Preço": f"R$ {price:.2f}",
                            "Risco": risco,
                            "Stoch 80": f"{curr_k3:.2f}%"
                        })
                
        except Exception as e:
            continue
            
    df_today = pd.DataFrame(results_today)
    
    df_hist = pd.DataFrame(results_history)
    if not df_hist.empty:
        # Ordenar da data mais recente para a mais antiga
        df_hist = df_hist.sort_values(by="Data (Raw)", ascending=False).drop(columns=["Data (Raw)"])
        
    return df_today, df_hist

# ==========================================================
# SIDEBAR (Painel de Controle – recolhível no mobile)
# ==========================================================
with st.sidebar:
    st.markdown('<p style="color:#a5b4fc; font-size:1.15rem; font-weight:600;">⚙️ Painel de Controle</p>', unsafe_allow_html=True)
    st.markdown('---')

    st.markdown('<p style="color:#94a3b8; font-size:0.85rem; margin-bottom:4px;">Universo de Ativos</p>', unsafe_allow_html=True)
    inc_stocks = st.checkbox("Ações B3", value=True)
    inc_etfs   = st.checkbox("ETFs", value=True)
    inc_bdrs   = st.checkbox("BDRs", value=True)

    st.markdown('---')
    if st.button("🔄  Executar Varredura", type="primary", use_container_width=True):
        st.cache_data.clear()

    st.markdown('---')
    st.markdown(
        '<p style="color:#475569; font-size:0.75rem; text-align:center;">'
        'Cache atualizado a cada 24 h.<br>Clique acima para forçar refresh.</p>',
        unsafe_allow_html=True
    )

# ==========================================================
# CORPO PRINCIPAL
# ==========================================================
tickers_to_scan = get_all_tickers(inc_stocks, inc_etfs, inc_bdrs)

if not tickers_to_scan:
    st.warning("Selecione pelo menos uma categoria de ativos no painel lateral.")
else:
    with st.spinner(f"Processando {len(tickers_to_scan)} ativos — aguarde a primeira execução…"):
        df_today, df_hist = fetch_and_process_data(tickers_to_scan)

    if df_today.empty:
        st.markdown("""
        <div class="glass-card" style="text-align:center; padding:2rem;">
            <p style="font-size:1.1rem; color:#94a3b8;">Nenhum ativo disparou sinal de <strong>Compra</strong> ou <strong>Venda</strong> hoje sob estas condições.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        col_l, col_r = st.columns([3, 1])
        with col_l:
            st.markdown(
                f'<p style="color:#a5b4fc; font-weight:600; font-size:1rem;">'
                f'✅ Sinais de Hoje — <span style="color:#34d399;">{len(df_today)}</span> oportunidade(s) encontrada(s)</p>',
                unsafe_allow_html=True
            )
        st.dataframe(
            df_today,
            use_container_width=True,
            hide_index=True
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f'<p style="color:#94a3b8; font-weight:600; font-size:1rem;">'
        f'📜 Histórico de Sinais (Últimos 15 dias)</p>',
        unsafe_allow_html=True
    )
    
    if df_hist.empty:
        st.info("Nenhum sinal registrado nos últimos 15 dias.")
    else:
        st.dataframe(
            df_hist,
            use_container_width=True,
            hide_index=True
        )

# ==========================================================
# DISCLAIMER
# ==========================================================
st.markdown("""
<div class="disclaimer">
    <strong>⚠️ AVISO LEGAL (DISCLAIMER):</strong> Esta aplicação possui finalidade puramente 
    educacional e de estudo quantitativo. Os sinais gerados por este motor (BUY / SELL) 
    baseiam-se estritamente em modelos estatísticos e matemáticos aplicados a dados históricos. 
    <strong>Eles NÃO configuram, sob nenhuma hipótese, recomendação, indicação ou 
    aconselhamento de compra ou venda de valores mobiliários.</strong> 
    O mercado de capitais envolve riscos. O uso desta ferramenta para tomada de decisões 
    financeiras é de inteira responsabilidade do usuário.
</div>
""", unsafe_allow_html=True)
