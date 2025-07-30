# 📈 Dashboard B3 - Top Altas e Baixas

Dashboard web interativo em Python (Streamlit) que monitora em tempo real as 5 ações e FIIs que mais subiram e caíram no dia, com indicadores fundamentais da B3.

## 🚀 Como Executar

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/muriloguizelin/financas.git
   cd financas
   ```

2. **Execute com Docker Compose:**
   ```bash
   docker-compose up --build
   ```

3. **Acesse no navegador:**
   ```
   http://localhost:8501  # Acesso direto ao Streamlit
   http://localhost        # Acesso via Nginx (proxy reverso)
   ```

## 🛠️ Tecnologias Utilizadas

- **Python 3.11** - Linguagem principal
- **Streamlit** - Framework web para dashboards
- **yfinance** - API para dados financeiros do Yahoo Finance
- **pandas** - Manipulação de dados
- **Redis** - Cache e sessões
- **Nginx** - Proxy reverso e load balancing
- **Docker** - Containerização

## 🐳 Arquitetura Docker

O projeto utiliza uma arquitetura multi-container com os seguintes serviços:

### 📊 Containers

1. **`web`** - Aplicação Streamlit
   - Porta: 8501
   - Framework: Streamlit
   - Função: Dashboard principal

2. **`redis`** - Cache e Sessões
   - Porta: 6379
   - Função: Cache de dados e sessões
   - Persistência: Volume `redis_data`

3. **`nginx`** - Proxy Reverso
   - Porta: 80
   - Função: Load balancing e proxy
   - Configuração: `nginx.conf`

### 🌐 Rede
- **`app-network`** - Rede bridge para comunicação entre containers

### 💾 Volumes
- **`redis_data`** - Persistência dos dados do Redis

## 📊 Funcionalidades

### 📈 Dashboard Principal
- **Top 5 Maiores Altas** do dia com indicadores
- **Top 5 Maiores Baixas** do dia com indicadores
- **Tabela completa** com todos os ativos monitorados

### 🔍 Pesquisa Individual
- **Busca por ticker** específico
- **Dados detalhados** do ativo selecionado
- **Gráfico histórico** de 1 mês

### 📋 Indicadores por Ativo
- **Preço atual** em tempo real
- **Variação diária, semanal, mensal e anual**
- **DY (Dividend Yield)** em porcentagem
- **P/VP (Preço sobre Valor Patrimonial)**
- **Volume de negociação**

### ⚙️ Configurações
- **Atualização automática** configurável
- **Intervalo de refresh** personalizável (30-300 segundos)
- **Cache inteligente** para otimizar performance

## 📈 Ativos Monitorados

### 🏢 Ações Principais
PETR4, VALE3, ITUB4, BBDC4, ABEV3, WEGE3, RENT3, BBAS3, B3SA3, SUZB3, RAIL3, UGPA3, LREN3, MGLU3, JBSS3, EMBR3, GGBR4, CSAN3, VIVT3

### 🏠 FIIs Populares
HGLG11, XPML11, HABT11, IRDM11, BTLG11, XPIN11, HGRU11, KNRI11, RBRF11, VGHF11

## 🐳 Docker

### Estrutura do Projeto
```
financas/
├── app/
│   ├── main.py          # Aplicação Streamlit
│   └── requirements.txt  # Dependências Python
├── Dockerfile           # Configuração do container
├── docker-compose.yml   # Orquestração Docker
├── nginx.conf          # Configuração do Nginx
└── README.md           # Documentação
```

### Comandos Docker Úteis

```bash
# Construir e executar todos os containers
docker-compose up --build

# Executar em background
docker-compose up -d

# Parar todos os containers
docker-compose down

# Ver logs de todos os serviços
docker-compose logs -f

# Ver logs de um serviço específico
docker-compose logs -f web
docker-compose logs -f redis
docker-compose logs -f nginx

# Reconstruir sem cache
docker-compose build --no-cache

# Executar apenas o web e redis (sem nginx)
docker-compose up web redis

# Verificar status dos containers
docker-compose ps
```

### 🔧 Desenvolvimento

### Estrutura do Código
- **`main.py`** - Aplicação principal Streamlit
- **Cache inteligente** - Dados atualizados a cada 5 minutos
- **Tratamento de erros** - Fallbacks para dados indisponíveis
- **Interface responsiva** - Layout adaptável

### Adicionando Novos Ativos
Para adicionar novos ativos, edite a lista em `main.py`:
```python
acoes_monitoradas = [
    'PETR4.SA', 'VALE3.SA', 
    # Adicione novos tickers aqui
]
```

## 📝 Licença