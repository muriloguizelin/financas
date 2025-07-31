# 📈 Dashboard B3 - Top Altas e Baixas

Dashboard web interativo em Python (Streamlit) que monitora em tempo real as 5 ações e FIIs que mais subiram e caíram no dia, com indicadores fundamentais da B3.

## 🚀 Como Executar

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/muriloguizelin/financas.git
   cd financas
   ```

2. **Configure as notificações do Discord (opcional):**
   - Crie um webhook no Discord: Canal → Editar → Integrações → Webhooks → Novo webhook
   - Copie a URL do webhook
   - Edite o `docker-compose.yml` e substitua `COLE_AQUI_SUA_URL_DO_DISCORD` pela sua URL

3. **Execute com Docker Compose:**
   ```bash
   docker-compose up --build
   ```

4. **Acesse no navegador:**
   ```
   http://localhost:8501
   ```

## 🛠️ Tecnologias Utilizadas

- **Python 3.11** - Linguagem principal
- **Streamlit** - Framework web para dashboards
- **yfinance** - API para dados financeiros do Yahoo Finance
- **pandas** - Manipulação de dados
- **Discord Webhooks** - Notificações automáticas
- **Docker** - Containerização

## 🐳 Arquitetura Docker

O projeto utiliza uma arquitetura de 3 containers:

### 📊 Containers

1. **`web`** - Aplicação Streamlit
   - Porta: 8501
   - Framework: Streamlit
   - Função: Dashboard principal
   - Cache: Interno do Streamlit (5 minutos)

2. **`notifier`** - Sistema de Notificações Discord
   - Função: Monitora preços e envia alertas
   - Configuração: Via variáveis de ambiente
   - Frequência: Verificação a cada 60 segundos

3. **`logs`** - Monitoramento de Logs
   - Imagem: busybox
   - Função: Gera logs de monitoramento
   - Volume: `./logs:/logs`
   - Frequência: Log a cada 30 segundos

### ⚙️ Configuração das Notificações

**Variáveis de ambiente no `docker-compose.yml`:**
```yaml
environment:
  - DISCORD_WEBHOOK_URL=sua_url_do_discord
  - TICKER=PETR4.SA          # Ação a monitorar
  - TARGET_PRICE=40.00       # Preço alvo
  - CHECK_INTERVAL=60        # Intervalo em segundos
```

### 🔔 Funcionalidades das Notificações

- **🚨 Alerta de Preço Alvo:** Notifica quando a ação atinge o preço configurado
- **📉 Alerta de Queda:** Notifica quando o preço cai abaixo do alvo
- **⏰ Timestamp:** Inclui data e hora da notificação
- **🔄 Anti-Spam:** Evita notificações repetidas
- **📊 Logs Detalhados:** Mostra preços em tempo real no console

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
- **Cache inteligente** - Dados atualizados a cada 5 minutos

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
├── notifier/
│   ├── notifier.py      # Sistema de notificações Discord
│   ├── requirements.txt  # Dependências do notifier
│   └── Dockerfile       # Container de notificações
├── logs/                # Diretório de logs (criado automaticamente)
├── Dockerfile           # Configuração do container
├── docker-compose.yml   # Orquestração Docker
└── README.md           # Documentação
```

### Comandos Docker Úteis

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
docker-compose logs -f notifier
docker-compose logs -f logs

# Verificar status dos containers
docker-compose ps

# Ver logs salvos localmente
cat logs/app.log
```

### 🔧 Desenvolvimento

### Estrutura do Código
- **`main.py`** - Aplicação principal Streamlit
- **`notifier.py`** - Sistema de notificações Discord
- **Cache inteligente** - Dados atualizados a cada 5 minutos usando `@st.cache_data`
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

Este projeto é de código aberto e está disponível sob a licença MIT.

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para:
- Reportar bugs
- Sugerir novas funcionalidades
- Enviar pull requests

## 📞 Suporte

Para dúvidas ou problemas, abra uma issue no repositório.