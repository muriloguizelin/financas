FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/muriloguizelin/financas.git /app

WORKDIR /app/app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501

CMD ["python", "-m", "streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
