# Usar imagem base do Python
FROM python:3.11-slim

# Definir diretório de trabalho
WORKDIR /app

# Instalar git para clonar o repositório
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Clonar o repositório do GitHub (substitua pela URL do seu repositório)
RUN git clone https://github.com/seu-usuario/financas-app.git .

# Instalar dependências Python
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código da aplicação
COPY app/main.py .

# Expor a porta
EXPOSE 8501

# Comando para executar a aplicação Streamlit
CMD ["python", "-m", "streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
