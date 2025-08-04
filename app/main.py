import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import time
import psycopg2
import os

# Configuração do banco de dados via variáveis de ambiente
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'postgres'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'financas'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres')
}

def get_db_connection():
    """Cria conexão com o banco de dados"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        st.error(f"Erro ao conectar ao banco: {e}")
        return None

def init_database():
    """Inicializa as tabelas do banco de dados"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Tabela de ativos favoritos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ativos_favoritos (
                    id SERIAL PRIMARY KEY,
                    ticker VARCHAR(20) NOT NULL UNIQUE,
                    nome VARCHAR(255),
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabela de histórico de consultas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS historico_consultas (
                    id SERIAL PRIMARY KEY,
                    ticker VARCHAR(20) NOT NULL,
                    data_consulta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabela de configurações do usuário
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS configuracoes_usuario (
                    id SERIAL PRIMARY KEY,
                    chave VARCHAR(50) NOT NULL UNIQUE,
                    valor TEXT,
                    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            st.success("✅ Banco de dados conectado e tabelas criadas!")
        except Exception as e:
            st.error(f"Erro ao criar tabelas: {e}")
        finally:
            conn.close()

def salvar_favorito(ticker, nome):
    """Salva um ativo como favorito"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO ativos_favoritos (ticker, nome) VALUES (%s, %s) ON CONFLICT (ticker) DO NOTHING',
                (ticker, nome)
            )
            conn.commit()
            return True
        except Exception as e:
            st.error(f"Erro ao salvar favorito: {e}")
            return False
        finally:
            conn.close()
    return False

def remover_favorito(ticker):
    """Remove um ativo dos favoritos"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM ativos_favoritos WHERE ticker = %s', (ticker,))
            conn.commit()
            return True
        except Exception as e:
            st.error(f"Erro ao remover favorito: {e}")
            return False
        finally:
            conn.close()
    return False

def get_favoritos():
    """Retorna lista de favoritos"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT ticker, nome FROM ativos_favoritos ORDER BY data_criacao DESC')
            return cursor.fetchall()
        except Exception as e:
            st.error(f"Erro ao buscar favoritos: {e}")
            return []
        finally:
            conn.close()
    return []

def salvar_consulta(ticker):
    """Registra uma consulta no histórico"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO historico_consultas (ticker) VALUES (%s)', (ticker,))
            conn.commit()
        except Exception as e:
            print(f"Erro ao salvar consulta: {e}")
        finally:
            conn.close()

def get_historico_consultas(limit=10):
    """Retorna histórico de consultas"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT ticker, COUNT(*) as consultas, MAX(data_consulta) as ultima_consulta 
                FROM historico_consultas 
                GROUP BY ticker 
                ORDER BY consultas DESC, ultima_consulta DESC 
                LIMIT %s
            ''', (limit,))
            return cursor.fetchall()
        except Exception as e:
            st.error(f"Erro ao buscar histórico: {e}")
            return []
        finally:
            conn.close()
    return []

def salvar_configuracao(chave, valor):
    """Salva uma configuração do usuário"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO configuracoes_usuario (chave, valor) 
                VALUES (%s, %s) 
                ON CONFLICT (chave) 
                DO UPDATE SET valor = EXCLUDED.valor, data_atualizacao = CURRENT_TIMESTAMP
            ''', (chave, valor))
            conn.commit()
            return True
        except Exception as e:
            st.error(f"Erro ao salvar configuração: {e}")
            return False
        finally:
            conn.close()
    return False

def get_configuracao(chave, valor_padrao=None):
    """Retorna uma configuração do usuário"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT valor FROM configuracoes_usuario WHERE chave = %s', (chave,))
            resultado = cursor.fetchone()
            return resultado[0] if resultado else valor_padrao
        except Exception as e:
            st.error(f"Erro ao buscar configuração: {e}")
            return valor_padrao
        finally:
            conn.close()
    return valor_padrao

st.set_page_config(
    page_title="Dashboard B3 - Robusto e Otimizado",
    page_icon="📈",
    layout="wide"
)

@st.cache_data(ttl=300)
def buscar_dados_ativo(ticker):
    """
    Busca dados de um ativo com cache e uma lógica de retentativa
    para lidar com a instabilidade da API.
    """
    tentativas = 3
    delay = 1
    for i in range(tentativas):
        try:
            ativo = yf.Ticker(ticker)
            info = ativo.info
            
            hist = ativo.history(period="3mo")
            if hist.empty:
                return None
                
            preco_atual = hist['Close'].iloc[-1]
            preco_anterior = hist['Close'].iloc[-2] if len(hist) > 1 else preco_atual
            
            variacao_diaria = ((preco_atual - preco_anterior) / preco_anterior) * 100
            
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
                'receita': info.get('totalRevenue', 0),
                'margem': info.get('profitMargins', 0) * 100 if info.get('profitMargins') else 0,
                'market_cap': info.get('marketCap', 0),
                'pvp': info.get('priceToBook', 0),
                'ebitda': info.get('ebitda', 0),
                'volume': info.get('volume', 0)
            }
        except Exception as e:
            # Se falhou, espera e tenta de novo.
            print(f"Tentativa {i+1} falhou para {ticker}: {e}. Tentando novamente em {delay}s...")
            time.sleep(delay)
            delay *= 2
            
    print(f"Todas as {tentativas} tentativas falharam para {ticker}.")
    return None

@st.cache_data(ttl=300)
def buscar_todos_dados():
    acoes_monitoradas = [
        'PETR4.SA', 'VALE3.SA', 'ITUB4.SA', 'BBDC4.SA', 'ABEV3.SA', 'WEGE3.SA', 
        'RENT3.SA', 'BBAS3.SA', 'B3SA3.SA', 'SUZB3.SA', 'RAIL3.SA', 'UGPA3.SA', 
        'LREN3.SA', 'MGLU3.SA', 'JBSS3.SA', 'EMBR3.SA', 'GGBR4.SA', 'CSAN3.SA', 'VIVT3.SA'
    ]
    fiis_monitorados = [
        'HGLG11.SA', 'XPML11.SA', 'HABT11.SA', 'IRDM11.SA', 'BTLG11.SA', 'XPIN11.SA', 
        'HGRU11.SA', 'KNRI11.SA', 'RBRF11.SA', 'VGHF11.SA'
    ]
    todos_ativos = acoes_monitoradas + fiis_monitorados
    dados = []
    
    with ThreadPoolExecutor(max_workers=8) as executor:
        resultados = executor.map(buscar_dados_ativo, todos_ativos)
        for resultado in resultados:
            if resultado:
                dados.append(resultado)
    
    return dados

def mostrar_dados_ativo(ticker):
    if not ticker: return
    if not ticker.endswith('.SA'): ticker = f"{ticker}.SA"
    
    # Salvar consulta no histórico
    salvar_consulta(ticker.replace('.SA', ''))
    
    with st.spinner(f"Buscando {ticker}..."):
        dados = buscar_dados_ativo(ticker)
    if dados:
        st.subheader(f"📊 Dados de {dados['ticker']}")
        
        # Botão para adicionar/remover dos favoritos
        favoritos = [f[0] for f in get_favoritos()]
        if dados['ticker'] in favoritos:
            if st.button(f"❤️ Remover {dados['ticker']} dos favoritos"):
                if remover_favorito(dados['ticker']):
                    st.success(f"{dados['ticker']} removido dos favoritos!")
                    st.rerun()
        else:
            if st.button(f"🤍 Adicionar {dados['ticker']} aos favoritos"):
                if salvar_favorito(dados['ticker'], dados['nome']):
                    st.success(f"{dados['ticker']} adicionado aos favoritos!")
                    st.rerun()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Preço", f"R$ {dados['preco']:.2f}")
            st.metric("Variação Diária", f"{dados['variacao_diaria']:.2f}%")
        with col2:
            st.metric("Receita", f"R$ {dados['receita']/1e9:.1f}B" if dados['receita'] else "N/A")
            st.metric("Margem", f"{dados['margem']:.1f}%" if dados['margem'] else "N/A")
        with col3:
            st.metric("Market Cap", f"R$ {dados['market_cap']/1e9:.1f}B" if dados['market_cap'] else "N/A")
            st.metric("P/VP", f"{dados['pvp']:.2f}" if dados['pvp'] else "N/A")
        try:
            hist = yf.Ticker(ticker).history(period="1mo")
            if not hist.empty: st.line_chart(hist['Close'], use_container_width=True)
        except: st.info("Gráfico não disponível.")
    else: st.error(f"Não foi possível encontrar dados para {ticker}")

# Inicializar banco de dados
init_database()

st.title("📈 Dashboard B3 - Desempenho do Mercado")
st.markdown("---")

# Sidebar com funcionalidades do banco
st.sidebar.title("🔍 Pesquisar Ativo")
ticker_pesquisa = st.sidebar.text_input("Digite o ticker (ex: PETR4)", "").upper()
if ticker_pesquisa:
    mostrar_dados_ativo(ticker_pesquisa)
    st.sidebar.markdown("---")

# Seção de Favoritos
st.sidebar.title("⭐ Favoritos")
favoritos = get_favoritos()
if favoritos:
    for ticker, nome in favoritos:
        col1, col2 = st.sidebar.columns([3, 1])
        with col1:
            if st.button(f"{ticker}", key=f"fav_{ticker}"):
                st.session_state.ticker_pesquisa = ticker
                st.rerun()
        with col2:
            if st.button("❌", key=f"del_{ticker}"):
                if remover_favorito(ticker):
                    st.success(f"{ticker} removido!")
                    st.rerun()
else:
    st.sidebar.info("Nenhum favorito adicionado ainda.")

# Seção de Histórico
st.sidebar.title("📋 Histórico de Consultas")
historico = get_historico_consultas(5)
if historico:
    for ticker, consultas, ultima in historico:
        if st.sidebar.button(f"{ticker} ({consultas}x)", key=f"hist_{ticker}"):
            st.session_state.ticker_pesquisa = ticker
            st.rerun()
else:
    st.sidebar.info("Nenhuma consulta registrada.")

# Configurações
st.sidebar.title("⚙️ Configurações")
auto_refresh = st.sidebar.checkbox(
    "Atualização automática", 
    value=get_configuracao('auto_refresh', 'false') == 'true'
)
if auto_refresh:
    salvar_configuracao('auto_refresh', 'true')
else:
    salvar_configuracao('auto_refresh', 'false')

if st.sidebar.button("🔄 Forçar Atualização"):
    st.cache_data.clear()
    st.rerun()

# Verificar se há ticker na sessão
if 'ticker_pesquisa' in st.session_state:
    mostrar_dados_ativo(st.session_state.ticker_pesquisa)
    del st.session_state.ticker_pesquisa

with st.spinner("Buscando dados de mercado (versão robusta)..."):
    todos_dados = buscar_todos_dados()

if not todos_dados:
    st.error("Não foi possível buscar dados dos ativos. Tente atualizar em alguns minutos.")
    st.stop()

df = pd.DataFrame(todos_dados)
df_altas = df[df['variacao_diaria'] > 0].nlargest(5, 'variacao_diaria')
df_baixas = df[df['variacao_diaria'] < 0].nsmallest(5, 'variacao_diaria')

col1, col2 = st.columns(2)
with col1:
    st.subheader("🚀 Top 5 Maiores Altas")
    if not df_altas.empty:
        for _, row in df_altas.iterrows():
            st.markdown(f"**{row['ticker']}** - {row['nome'][:30]}")
            c1, c2 = st.columns(2)
            c1.metric("Preço", f"R$ {row['preco']:.2f}", f"{row['variacao_diaria']:.2f}%")
            c2.metric("Market Cap", f"R$ {row['market_cap']/1e9:.1f}B" if row['market_cap'] else "N/A", f"Margem: {row['margem']:.1f}%" if row['margem'] else "N/A")
            st.markdown("---")
    else: st.info("Nenhuma alta significativa hoje.")
with col2:
    st.subheader("📉 Top 5 Maiores Baixas")
    if not df_baixas.empty:
        for _, row in df_baixas.iterrows():
            st.markdown(f"**{row['ticker']}** - {row['nome'][:30]}")
            c1, c2 = st.columns(2)
            c1.metric("Preço", f"R$ {row['preco']:.2f}", f"{row['variacao_diaria']:.2f}%")
            c2.metric("Market Cap", f"R$ {row['market_cap']/1e9:.1f}B" if row['market_cap'] else "N/A", f"Margem: {row['margem']:.1f}%" if row['margem'] else "N/A")
            st.markdown("---")
    else: st.info("Nenhuma baixa significativa hoje.")

st.subheader("📊 Dados Completos")
df_display = df.copy()

df_display['receita'] = df_display['receita'].apply(lambda x: x/1e9 if x else 0)
df_display['market_cap'] = df_display['market_cap'].apply(lambda x: x/1e9 if x else 0)

colunas_para_exibir = ['ticker', 'nome', 'preco', 'variacao_diaria', 'variacao_semanal', 'variacao_mensal', 'receita', 'margem', 'market_cap', 'pvp']
df_display = df_display[colunas_para_exibir].rename(columns={
    'ticker': 'Ticker', 'nome': 'Nome', 'preco': 'Preço', 'variacao_diaria': 'Var. Diária (%)',
    'variacao_semanal': 'Var. Semanal (%)', 'variacao_mensal': 'Var. Mensal (%)', 
    'receita': 'Receita (B)', 'margem': 'Margem (%)', 'market_cap': 'Market Cap (B)', 'pvp': 'P/VP'
})
st.dataframe(df_display, use_container_width=True, column_config={
    "Preço": st.column_config.NumberColumn(format="R$ %.2f"),
    "Var. Diária (%)": st.column_config.NumberColumn(format="%.2f%%"),
    "Var. Semanal (%)": st.column_config.NumberColumn(format="%.2f%%"),
    "Var. Mensal (%)": st.column_config.NumberColumn(format="%.2f%%"),
    "Receita (B)": st.column_config.NumberColumn(format="R$ %.1fB"),
    "Margem (%)": st.column_config.NumberColumn(format="%.1f%%"),
    "Market Cap (B)": st.column_config.NumberColumn(format="R$ %.1fB"),
    "P/VP": st.column_config.NumberColumn(format="%.2f"),
}, hide_index=True)

st.markdown("---")
st.markdown(f"**Última atualização:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} | **Ativos carregados com sucesso:** {len(todos_dados)}")