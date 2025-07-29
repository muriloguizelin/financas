FROM python:3.11-slim

RUN apt-get update && apt-get install -y git

RUN git clone https://github.com/muriloguizelin/financas.git /app

WORKDIR /app/app
RUN pip install --no-cache-dir -r requirements.txt

CMD ["flask", "--app", "main", "run", "--host=0.0.0.0"]
