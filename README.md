# 📈 Dashboard B3 - Top Altas e Baixas

Dashboard web interativo que monitora as maiores altas e baixas da B3 (Ações e FIIs), com consulta de indicadores e histórico de buscas salvo em banco de dados.

---

### ✨ Funcionalidades Principais
- **Monitoramento em tempo real** do Top 5 de altas e baixas.
- **Tabela completa** de ativos com indicadores fundamentalistas.
- **Consulta de ticker específico** com dados detalhados e gráfico histórico.
- **Histórico de consultas** e salvamento de preferências do usuário.
- **Cache inteligente** para otimização da busca de dados.

### 🛠️ Tecnologias
Python | Streamlit | PostgreSQL | Docker | Nginx | yfinance

---

### 🚀 Como Executar

**Pré-requisitos:** Git, Docker e Docker Compose.

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/seu-usuario/financas-app.git](https://github.com/seu-usuario/financas-app.git)
    cd financas-app
    ```

2.  **Suba os containers:**
    ```bash
    docker-compose up -d
    ```

3.  **Acesse o dashboard:**
    Abra seu navegador em: `http://localhost:8080`

---

### 🐳 Comandos Úteis

-   **Ver logs da aplicação:**
    ```bash
    docker-compose logs -f web
    ```

-   **Conectar ao banco de dados:**
    ```bash
    docker-compose exec postgres psql -U postgres -d financas
    ```

-   **Parar a aplicação:**
    ```bash
    docker-compose down
    ```

-   **Reconstruir as imagens e executar:**
    ```bash
    docker-compose up --build -d
    ```

---
> ⚠️ **Aviso:** Esta é uma aplicação de demonstração. Para uso em produção, altere as senhas padrão, configure HTTPS e implemente um sistema de autenticação."