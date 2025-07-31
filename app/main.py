import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pika
import json

# Configuração da página
st.set_page_config(
    page_title="Dashboard B3 - Top Altas e Baixas",
    page_icon="📈",
    layout="wide"
)

# Cache para dados
@st.cache_data(ttl=300)  # Cache por 5 minutos
def buscar_dados_ativo(ticker):
    """Busca dados de um ativo com cache"""
    try:
        ativo = yf.Ticker(ticker)
        info = ativo.info
        
        # Dados de cotação
        hist = ativo.history(period="1y")
        if hist.empty:
            return None
            
        preco_atual = hist['Close'].iloc[-1]
        preco_anterior = hist['Close'].iloc[-2] if len(hist) > 1 else preco_atual
        
        variacao_diaria = ((preco_atual - preco_anterior) / preco_anterior) * 100
        
        # Variações
        variacao_semanal = ((preco_atual - hist['Close'].iloc[-6]) / hist['Close'].iloc[-6]) * 100 if len(hist) >= 6 else 0
        variacao_mensal = ((preco_atual - hist['Close'].iloc[-21]) / hist['Close'].iloc[-21]) * 100 if len(hist) >= 21 else 0
        variacao_anual = ((preco_atual - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100 if len(hist) > 0 else 0
        
        return {
            'ticker': ticker.replace('.SA', ''),
            'nome': info.get('longName', ticker),
            'preco': preco_atual,
            'variacao_diaria': variacao_diaria,
            'variacao_semanal': variacao_semanal,
            'variacao_mensal': variacao_mensal,
            'variacao_anual': variacao_anual,
            'dy': info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0,
            'pvp': info.get('priceToBook', 0),
            'ebitda': info.get('ebitda', 0),
            'volume': info.get('volume', 0)
        }
    except Exception as e:
        return None

@st.cache_data(ttl=300)
def buscar_todos_dados():
    """Busca dados de todos os ativos com cache"""
    # Lista de ações e FIIs para monitorar
    acoes_monitoradas = [
        'PETR4.SA', 'VALE3.SA', 'ITUB4.SA', 'BBDC4.SA', 'ABEV3.SA',
        'WEGE3.SA', 'RENT3.SA', 'BBAS3.SA', 'B3SA3.SA', 'SUZB3.SA',
        'RAIL3.SA', 'UGPA3.SA', 'LREN3.SA', 'MGLU3.SA',
        'JBSS3.SA', 'EMBR3.SA', 'GGBR4.SA', 'CSAN3.SA', 'VIVT3.SA'
    ]

    # FIIs populares
    fiis_monitorados = [
        'HGLG11.SA', 'XPML11.SA', 'HABT11.SA', 'IRDM11.SA', 'BTLG11.SA',
        'XPIN11.SA', 'HGRU11.SA', 'KNRI11.SA', 'RBRF11.SA', 'VGHF11.SA'
    ]
    
    todos_ativos = acoes_monitoradas + fiis_monitorados
    dados = []
    
    for ativo in todos_ativos:
        dados_ativo = buscar_dados_ativo(ativo)
        if dados_ativo:
            dados.append(dados_ativo)
    
    return dados

def mostrar_dados_ativo(ticker):
    """Mostra dados de um ativo específico"""
    if not ticker:
        return
    
    # Adicionar .SA se não estiver presente
    if not ticker.endswith('.SA'):
        ticker = f"{ticker}.SA"
    
    dados = buscar_dados_ativo(ticker)
    if dados:
        st.subheader(f"📊 Dados de {dados['ticker']}")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Preço", f"R$ {dados['preco']:.2f}")
            st.metric("Variação Diária", f"{dados['variacao_diaria']:.2f}%")
        
        with col2:
            st.metric("DY", f"{dados['dy']:.2f}%")
            st.metric("P/VP", f"{dados['pvp']:.2f}")
        
        with col3:
            st.metric("Variação Semanal", f"{dados['variacao_semanal']:.2f}%")
            st.metric("Variação Mensal", f"{dados['variacao_mensal']:.2f}%")
        
        # Gráfico de histórico
        try:
            ativo = yf.Ticker(ticker)
            hist = ativo.history(period="1mo")
            if not hist.empty:
                st.line_chart(hist['Close'])
        except:
            pass
    else:
        st.error(f"Não foi possível encontrar dados para {ticker}")

def send_notification(ticker, target_price, current_price):
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue='stock_alerts')
    message = {
        'ticker': ticker,
        'target_price': target_price,
        'current_price': current_price
    }
    channel.basic_publish(exchange='', routing_key='stock_alerts', body=json.dumps(message))
    connection.close()

# Exemplo de uso:
if __name__ == "__main__":
    # Simule que PETR4.SA atingiu o preço alvo de 40.00
    send_notification('PETR4.SA', 40.00, 40.05)

# Título principal
st.title("📈 Dashboard B3 - Top Altas e Baixas do Dia")
st.markdown("---")

# Sidebar para pesquisa
st.sidebar.title("🔍 Pesquisar Ativo")
ticker_pesquisa = st.sidebar.text_input("Digite o ticker (ex: PETR4)", "").upper()

if ticker_pesquisa:
    mostrar_dados_ativo(ticker_pesquisa)
    st.markdown("---")

# Sidebar para configurações
st.sidebar.title("⚙️ Configurações")
auto_refresh = st.sidebar.checkbox("Atualização automática", value=True)
refresh_interval = st.sidebar.slider("Intervalo (segundos)", 30, 300, 60)

if auto_refresh:
    st.sidebar.info(f"Atualiza a cada {refresh_interval} segundos")

# Buscar dados
with st.spinner("Buscando dados dos ativos..."):
    todos_dados = buscar_todos_dados()

if not todos_dados:
    st.error("Não foi possível buscar dados dos ativos.")
    st.stop()

# Criar DataFrame
df = pd.DataFrame(todos_dados)

# Ordenar por variação diária
df_altas = df[df['variacao_diaria'] > 0].nlargest(5, 'variacao_diaria')
df_baixas = df[df['variacao_diaria'] < 0].nsmallest(5, 'variacao_diaria')

# Layout em duas colunas
col1, col2 = st.columns(2)

with col1:
    st.subheader("🚀 Top 5 Maiores Altas")
    if not df_altas.empty:
        for _, row in df_altas.iterrows():
            with st.container():
                st.markdown(f"""
                **{row['ticker']} - {row['nome'][:30]}...**
                - Preço: R$ {row['preco']:.2f}
                - Variação: {row['variacao_diaria']:.2f}%
                - DY: {row['dy']:.2f}%
                - P/VP: {row['pvp']:.2f}
                """)
                st.progress(min(abs(row['variacao_diaria']) / 10, 1.0))
                st.markdown("---")
    else:
        st.info("Nenhuma alta significativa hoje.")

with col2:
    st.subheader("📉 Top 5 Maiores Baixas")
    if not df_baixas.empty:
        for _, row in df_baixas.iterrows():
            with st.container():
                st.markdown(f"""
                **{row['ticker']} - {row['nome'][:30]}...**
                - Preço: R$ {row['preco']:.2f}
                - Variação: {row['variacao_diaria']:.2f}%
                - DY: {row['dy']:.2f}%
                - P/VP: {row['pvp']:.2f}
                """)
                st.progress(min(abs(row['variacao_diaria']) / 10, 1.0))
                st.markdown("---")
    else:
        st.info("Nenhuma baixa significativa hoje.")

# Tabela completa com todos os dados
st.subheader("📊 Dados Completos")

# Formatar DataFrame para exibição
df_display = df.copy()
df_display['preco'] = df_display['preco'].apply(lambda x: f"R$ {x:.2f}")
df_display['variacao_diaria'] = df_display['variacao_diaria'].apply(lambda x: f"{x:.2f}%")
df_display['variacao_semanal'] = df_display['variacao_semanal'].apply(lambda x: f"{x:.2f}%")
df_display['variacao_mensal'] = df_display['variacao_mensal'].apply(lambda x: f"{x:.2f}%")
df_display['variacao_anual'] = df_display['variacao_anual'].apply(lambda x: f"{x:.2f}%")
df_display['dy'] = df_display['dy'].apply(lambda x: f"{x:.2f}%")
df_display['pvp'] = df_display['pvp'].apply(lambda x: f"{x:.2f}")

# Renomear colunas
df_display = df_display.rename(columns={
    'ticker': 'Ticker',
    'nome': 'Nome',
    'preco': 'Preço',
    'variacao_diaria': 'Var. Diária',
    'variacao_semanal': 'Var. Semanal',
    'variacao_mensal': 'Var. Mensal',
    'variacao_anual': 'Var. Anual',
    'dy': 'DY',
    'pvp': 'P/VP'
})

# Selecionar colunas para exibir
colunas_exibir = ['Ticker', 'Nome', 'Preço', 'Var. Diária', 'Var. Semanal', 'Var. Mensal', 'Var. Anual', 'DY', 'P/VP']
df_exibir = df_display[colunas_exibir]

st.dataframe(df_exibir, use_container_width=True)

# Informações adicionais
st.markdown("---")
st.markdown(f"**Última atualização:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
st.markdown(f"**Total de ativos monitorados:** {len(todos_dados)}")

# Auto-refresh
if st.button("🔄 Atualizar Dados"):
    st.cache_data.clear()
    st.rerun() 