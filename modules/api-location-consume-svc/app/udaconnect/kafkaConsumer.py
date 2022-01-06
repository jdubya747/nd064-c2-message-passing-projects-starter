import logging
from kafka import KafkaConsumer
import threading
from typing import Dict, List
import json
from json import loads
from app.udaconnect.services import LocationService

TOPIC_NAME = 'location'
KAFKA_SERVER = 'kafka:9092'

def kafka_consumer(app_context):

    consumer = KafkaConsumer(
        bootstrap_servers=KAFKA_SERVER,
        consumer_timeout_ms=1000,
        group_id='location-group')

    consumer.subscribe(TOPIC_NAME)
    while True:
        for message in consumer:
            result = json.loads(message.value.decode('utf-8'))
            logging.info('Received kafka message for person_id = %s', result["person_id"])
            with app_context:
                LocationService.kafka_consumed_create(result)
        
  
def start_server(app_context):
    logging.info('Starting kafka consuming thread')
    t = threading.Thread(target=kafka_consumer, args=[app_context])
    t.start()
    logging.info('Consumer startup completed. Consuming from kafka on: %s', KAFKA_SERVER)
