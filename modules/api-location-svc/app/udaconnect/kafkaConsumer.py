import logging
from kafka import KafkaConsumer
import threading
import time
from typing import List
import json
from json import loads
from app.udaconnect.services import LocationService

TOPIC_NAME = 'location'
KAFKA_SERVER = 'kafka:9092'

def kafka_consumer(time):

    consumer = KafkaConsumer(
        bootstrap_servers=KAFKA_SERVER,
        consumer_timeout_ms=1000,
        group_id='location-group')

    consumer.subscribe(TOPIC_NAME)
    while True:
        for message in consumer:
            result = json.loads(message.value.decode('utf-8'))
            logging.info('Received kafka message: ')
            LocationService.kafka_consumed_create(result)
    
  
def start_server(app_context):
    logging.info('Starting server')
    t = threading.Thread(target=kafka_consumer, args=[1])
    t.start()
    logging.info('Consuming from kafka on: %s', {KAFKA_SERVER})
