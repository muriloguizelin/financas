import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import investpy

# Configuração da página
st.set_page_config(
    page_title="Dashboard B3 - Maiores Altas e Baixas do Dia",
    page_icon="🇧🇷",
    layout="wide"
)

# --- FUNÇÕES DE BUSCA DE DADOS ---

@st.cache_data(ttl=300)  # Cache de 5 minutos
def buscar_dados_ativo(ticker):
    """Busca dados detalhados de um ativo com cache."""
    try:
        if not ticker.endswith('.SA'):
            ticker = f"{ticker}.SA"
            
        ativo = yf.Ticker(ticker)
        info = ativo.info

        hist = ativo.history(period="1y")
        if hist.empty or len(hist) < 2:
            return None

        preco_atual = hist['Close'].iloc[-1]
        preco_anterior = hist['Close'].iloc[-2]
        variacao_diaria = ((preco_atual - preco_anterior) / preco_anterior) * 100 if preco_anterior else 0
        
        return {
            'ticker': ticker.replace('.SA', ''),
            'nome': info.get('longName', ticker),
            'preco': preco_atual,
            'variacao_diaria': variacao_diaria,
            'pvp': info.get('priceToBook'),
            'volume': info.get('volume'),
            'beta': info.get('beta')
        }
    except Exception:
        return None

@st.cache_data(ttl=360) # Cache um pouco maior para a lista de movers
def buscar_maiores_altas_e_baixas():
    """
    Busca os tickers das maiores altas e baixas do dia na B3 usando a investpy.
    Retorna uma lista única de tickers a serem detalhados.
    """
    try:
        # Busca top 10 de cada para garantir que tenhamos 5 válidos após o filtro
        df_altas = investpy.stocks.get_stock_gainers(country='brazil')
        df_baixas = investpy.stocks.get_stock_losers(country='brazil')

        # Extrai os símbolos (tickers) e adiciona '.SA' para compatibilidade com yfinance
        tickers_altas = [f"{row['symbol']}.SA" for _, row in df_altas.head(10).iterrows()]
        tickers_baixas = [f"{row['symbol']}.SA" for _, row in df_baixas.head(10).iterrows()]
        
        # Junta as listas e remove duplicados
        todos_tickers = list(set(tickers_altas + tickers_baixas))
        return todos_tickers
    except Exception as e:
        st.error(f"Não foi possível buscar a lista de maiores altas e baixas. O serviço pode estar temporariamente indisponível. Erro: {e}")
        return []

def buscar_detalhes_em_paralelo(tickers):
    """Busca os detalhes de uma lista de tickers em paralelo."""
    dados = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        resultados = executor.map(buscar_dados_ativo, tickers)
        for resultado in resultados:
            if resultado:
                dados.append(resultado)
    return dados

# --- FUNÇÕES DE EXIBIÇÃO (UI) ---

def formatar_numero(valor, prefixo="", sufixo="", casas_decimais=2):
    """Formata um número, retornando 'N/A' se for nulo."""
    if valor is None or pd.isna(valor):
        return "N/A"
    return f"{prefixo}{valor:,.{casas_decimais}f}{sufixo}"

def exibir_cartao_ativo(row):
    """Exibe um cartão com informações de um ativo."""
    col_info, col_graf = st.columns([3, 1])
    with col_info:
        nome_curto = row['nome'][:30] + '...' if len(row['nome']) > 30 else row['nome']
        st.markdown(f"**{row['ticker']} - {nome_curto}**")
        st.markdown(f"Preço: **{formatar_numero(row['preco'], 'R$ ')}** | Variação: **{formatar_numero(row['variacao_diaria'], sufixo='%')}**")
        st.markdown(f"P/VP: **{formatar_numero(row['pvp'])}** | Beta: **{formatar_numero(row['beta'])}**")
        
        cor_barra = "green" if row['variacao_diaria'] > 0 else "red"
        st.progress(min(abs(row['variacao_diaria']) / 10, 1.0))

    with col_graf:
        try:
            ativo_graf = yf.Ticker(f"{row['ticker']}.SA")
            hist = ativo_graf.history(period="5d", interval="15m")
            if not hist.empty:
                st.line_chart(hist['Close'], use_container_width=True, height=100)
        except Exception:
            st.empty() # Não mostra nada se o gráfico falhar
    st.markdown("---")


# --- LAYOUT PRINCIPAL DA APLICAÇÃO ---

st.title("📈 Dashboard B3 - Maiores Altas e Baixas do Dia")
st.markdown(f"*Dados atualizados pela última vez em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}*")
st.markdown("---")

# Buscar a lista de ativos do dia (altas e baixas)
tickers_do_dia = buscar_maiores_altas_e_baixas()

if not tickers_do_dia:
    st.warning("Não foi possível carregar os dados das maiores altas e baixas. Tente atualizar em alguns minutos.")
    st.stop()

# Buscar os dados detalhados para esses ativos
with st.spinner("Buscando dados detalhados dos ativos do dia..."):
    dados_detalhados = buscar_detalhes_em_paralelo(tickers_do_dia)

if not dados_detalhados:
    st.error("Falha ao buscar os detalhes dos ativos. A API pode estar indisponível.")
    st.stop()

# Criar DataFrame e ordenar
df = pd.DataFrame(dados_detalhados)
df = df.sort_values(by='variacao_diaria', ascending=False).dropna(subset=['variacao_diaria'])

# Separar em top 5 de altas e baixas
df_altas = df.head(5)
df_baixas = df.tail(5).sort_values(by='variacao_diaria', ascending=True)

# Layout em duas colunas
col1, col2 = st.columns(2)

with col1:
    st.subheader("🚀 Top 5 Maiores Altas do Dia")
    if not df_altas.empty:
        for _, row in df_altas.iterrows():
            exibir_cartao_ativo(row)
    else:
        st.info("Não foi possível carregar as maiores altas.")

with col2:
    st.subheader("📉 Top 5 Maiores Baixas do Dia")
    if not df_baixas.empty:
        for _, row in df_baixas.iterrows():
            exibir_cartao_ativo(row)
    else:
        st.info("Não foi possível carregar as maiores baixas.")

# Tabela completa com todos os dados do dia
st.subheader("📊 Resumo dos Ativos em Destaque Hoje")
df_display = df.rename(columns={
    'ticker': 'Ticker', 'nome': 'Nome', 'preco': 'Preço', 'variacao_diaria': 'Var. Diária (%)',
    'beta': 'Beta', 'pvp': 'P/VP', 'volume': 'Volume'
})
colunas_para_exibir = ['Ticker', 'Nome', 'Preço', 'Var. Diária (%)', 'P/VP', 'Beta', 'Volume']
st.dataframe(df_display[colunas_para_exibir], use_container_width=True,
             column_config={
                 "Preço": st.column_config.NumberColumn(format="R$ %.2f"),
                 "Var. Diária (%)": st.column_config.ProgressColumn(
                     label="Variação Diária",
                     format="%.2f%%",
                     min_val=df['variacao_diaria'].min(),
                     max_val=df['variacao_diaria'].max(),
                 ),
                 "P/VP": st.column_config.NumberColumn(format="%.2f"),
                 "Beta": st.column_config.NumberColumn(format="%.2f"),
                 "Volume": st.column_config.NumberColumn(format="%d")
             })

# Botão de atualização manual
if st.button("🔄 Atualizar Dados Agora"):
    st.cache_data.clear()
    st.rerun()