# 📈 Dashboard B3 - Top Altas e Baixas

Dashboard web interativo em Python (Streamlit) que monitora em tempo real as 5 ações e FIIs que mais subiram e caíram no dia, com indicadores fundamentais da B3 e integração com banco de dados PostgreSQL.

## 🚀 Funcionalidades

### 📈 Dashboard Principal
- ✅ **Top 5 Maiores Altas** do dia com indicadores
- ✅ **Top 5 Maiores Baixas** do dia com indicadores
- ✅ **Tabela completa** com todos os ativos monitorados
- ✅ **Busca por ticker** específico
- ✅ **Dados detalhados** do ativo selecionado
- ✅ **Gráfico histórico** de 1 mês
- ✅ **Cache inteligente** para otimização de performance

### 💾 Funcionalidades do Banco de Dados
- ✅ **Sistema de Favoritos** - Salve seus ativos preferidos
- ✅ **Histórico de Consultas** - Acompanhe seus ativos mais pesquisados
- ✅ **Configurações Salvas** - Suas preferências ficam guardadas
- ✅ **Persistência de Dados** - Informações mantidas entre sessões

## 🛠️ Tecnologias Utilizadas

- **Python 3.11** - Linguagem principal
- **Streamlit** - Framework web para dashboards
- **yfinance** - API para dados financeiros do Yahoo Finance
- **pandas** - Manipulação de dados
- **PostgreSQL** - Banco de dados para armazenamento
- **psycopg2** - Driver PostgreSQL para Python
- **Nginx** - Proxy reverso e monitoramento de logs
- **Docker** - Containerização

## 📋 Pré-requisitos

- Docker
- Docker Compose
- Git

## 🚀 Como Executar

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/financas-app.git
cd financas-app
```

### 2. Configure o repositório no Dockerfile
Edite o arquivo `Dockerfile` e substitua a URL do repositório:
```dockerfile
RUN git clone https://github.com/seu-usuario/financas-app.git .
```

### 3. Execute com Docker Compose
```bash
docker-compose up -d
```

### 4. Acesse a aplicação
Abra seu navegador e acesse: http://localhost:8080

## 🔧 Configuração

### Variáveis de Ambiente

A aplicação usa as seguintes variáveis de ambiente (já configuradas no docker-compose.yml):

```env
DB_HOST=postgres          # Host do banco de dados
DB_PORT=5432             # Porta do PostgreSQL
DB_NAME=financas         # Nome do banco de dados
DB_USER=postgres         # Usuário do banco
DB_PASSWORD=postgres     # Senha do banco
STREAMLIT_SERVER_PORT=8501  # Porta da aplicação Streamlit
```

## 📊 Estrutura do Banco de Dados

A aplicação cria automaticamente 3 tabelas no PostgreSQL:

### 🏷️ Tabela `ativos_favoritos`
- `id`: Identificador único (SERIAL PRIMARY KEY)
- `ticker`: Código do ativo (VARCHAR, UNIQUE)
- `nome`: Nome do ativo (VARCHAR)
- `data_criacao`: Data de criação (TIMESTAMP)

### 📋 Tabela `historico_consultas`
- `id`: Identificador único (SERIAL PRIMARY KEY)
- `ticker`: Código do ativo consultado (VARCHAR)
- `data_consulta`: Data/hora da consulta (TIMESTAMP)

### ⚙️ Tabela `configuracoes_usuario`
- `id`: Identificador único (SERIAL PRIMARY KEY)
- `chave`: Nome da configuração (VARCHAR, UNIQUE)
- `valor`: Valor da configuração (TEXT)
- `data_atualizacao`: Data da última atualização (TIMESTAMP)

## 📈 Ativos Monitorados

### 🏢 Ações Principais
PETR4, VALE3, ITUB4, BBDC4, ABEV3, WEGE3, RENT3, BBAS3, B3SA3, SUZB3, RAIL3, UGPA3, LREN3, MGLU3, JBSS3, EMBR3, GGBR4, CSAN3, VIVT3

### 🏠 FIIs Populares
HGLG11, XPML11, HABT11, IRDM11, BTLG11, XPIN11, HGRU11, KNRI11, RBRF11, VGHF11

## 🐳 Containers Docker

O projeto utiliza três containers:

1. **web**: Aplicação Streamlit (porta 8501)
2. **postgres**: Banco de dados PostgreSQL (porta 5432)
3. **logs**: Proxy reverso Nginx (porta 8080)

## 📁 Estrutura do Projeto

```
financas-app/
├── app/
│   ├── main.py              # Aplicação Streamlit
│   └── requirements.txt     # Dependências Python
├── docker-compose.yml       # Configuração dos containers
├── Dockerfile              # Imagem da aplicação
├── logs/                   # Logs do Nginx
└── README.md               # Este arquivo
```

## 🔍 Comandos Úteis

### Ver logs da aplicação
```bash
docker-compose logs web
```

### Conectar ao banco de dados
```bash
docker-compose exec postgres psql -U postgres -d financas
```

### Parar os containers
```bash
docker-compose down
```

### Reconstruir e executar
```bash
docker-compose up --build -d
```

## 🎯 Como Usar

### 📊 Dashboard Principal
1. **Visualizar Top Altas/Baixas**: Acompanhe as 5 ações e FIIs com maior variação
2. **Tabela Completa**: Veja todos os ativos monitorados com indicadores
3. **Atualizar Dados**: Use o botão "Forçar Atualização" para buscar dados mais recentes

### 🔍 Funcionalidades do Banco de Dados
1. **⭐ Favoritos**: Adicione ativos aos favoritos clicando no coração
2. **📋 Histórico**: Veja seus ativos mais consultados na barra lateral
3. **⚙️ Configurações**: Salve suas preferências (ex: atualização automática)
4. **Pesquisar Ativo**: Use a barra lateral para buscar um ticker específico
5. **Ver Dados Detalhados**: Clique em um ativo para ver gráficos e indicadores

## 🔒 Segurança

⚠️ **Importante**: Esta é uma aplicação de demonstração. Para uso em produção:

- Altere as senhas padrão
- Use variáveis de ambiente seguras
- Configure HTTPS
- Implemente autenticação de usuários

## 📝 Licença

Este projeto é de código aberto e está disponível sob a licença MIT.

## 🤝 Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.