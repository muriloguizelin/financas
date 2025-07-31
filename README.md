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
   http://localhost:8080
   ```

## 🛠️ Tecnologias Utilizadas

- **Python 3.11** - Linguagem principal
- **Streamlit** - Framework web para dashboards
- **yfinance** - API para dados financeiros do Yahoo Finance
- **pandas** - Manipulação de dados
- **Nginx** - Proxy reverso e monitoramento de logs
- **Docker** - Containerização

## 🐳 Arquitetura Docker

O projeto utiliza uma arquitetura de 2 containers:

### 📊 Containers

1. **`web`** - Aplicação Streamlit
   - Porta: 8501 (interno)
   - Framework: Streamlit
   - Função: Dashboard principal

2. **`logs`** - Proxy e Monitoramento
   - Porta: 8080 (externo)
   - Imagem: nginx:alpine
   - Função: Proxy reverso + monitoramento detalhado de acessos

### 📊 Monitoramento Avançado

O container `logs` captura informações detalhadas:

- **IP do usuário** e localização
- **Tempo de resposta** (request_time)
- **User-Agent** (navegador/dispositivo)
- **Referrer** (página de origem)
- **Status codes** e bytes transferidos
- **Timezone** do usuário

### 📋 Logs Disponíveis

```bash
# Ver logs de acesso
docker-compose logs -f logs

# Ver logs salvos localmente
cat logs/access.log
cat logs/error.log
```

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

## 📈 Ativos Monitorados

### 🏢 Ações Principais
PETR4, VALE3, ITUB4, BBDC4, ABEV3, WEGE3, RENT3, BBAS3, B3SA3, SUZB3, RAIL3, UGPA3, LREN3, MGLU3, JBSS3, EMBR3, GGBR4, CSAN3, VIVT3

### 🏠 FIIs Populares
HGLG11, XPML11, HABT11, IRDM11, BTLG11, XPIN11, HGRU11, KNRI11, RBRF11, VGHF11

## 🐳 Comandos Docker Úteis

```bash
# Construir e executar
docker-compose up --build

# Executar em background
docker-compose up -d

# Parar containers
docker-compose down

# Ver logs
docker-compose logs -f

# Ver logs de um serviço específico
docker-compose logs -f web
docker-compose logs -f logs
```

## 📝 Licença

Este projeto é de código aberto e está disponível sob a licença MIT.