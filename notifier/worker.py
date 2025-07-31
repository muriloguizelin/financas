import pika
import json

def callback(ch, method, properties, body):
    data = json.loads(body)
    print(f"Notificação: A ação {data['ticker']} atingiu o preço alvo de {data['target_price']}! Preço atual: {data['current_price']}")

connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
channel = connection.channel()
channel.queue_declare(queue='stock_alerts')

channel.basic_consume(queue='stock_alerts', on_message_callback=callback, auto_ack=True)
print('Aguardando notificações...')
channel.start_consuming() 