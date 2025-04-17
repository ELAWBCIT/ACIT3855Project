# File Author: Ernest Law 

"""
Precursor Notes - As per each Lab. 
=======================================================================
Lab 2: 
- It is good practice to create a virtual environment prior to the installation of certain packages. Can create within the Powershell Terminal in VSCode:
    - python -m venv venv
    - ./venv/Scripts/Activate
- Once completed installed the following packages with the following commands:  
    - pip install connexion[flask]
    - pip install [uvicorn]
    - pip install swagger-ui-bundle 
- Jmeter runs via the bat file under desktop/apache-jmeter-5.6.3/bin
=======================================================================
Lab 3:
- Install Sqlalchemy within the venv environment 
    - pip install sqlalchemy
    - found I have to do that before I install all the items for Lab 2
    - If I were to test Bruno, need to get the items from my L1-2 folder. 
- Install httpx:
    - pip install httpx
"""

# Necessary imports 
import logging.config
import connexion
from connexion import NoContent

import json

import datetime
from datetime import datetime


from pathlib import Path 

# Lab 3 imports
import httpx 

# Lab 4 imports 
import time
import uuid
import yaml 
import logging

# Lab 6 imports
from pykafka import KafkaClient

from connexion.middleware import MiddlewarePosition
from starlette.middleware.cors import CORSMiddleware

import os 


# Lab 4 - Loading the app_conf.yml file
with open('/app/conf/app_conf.yml', 'r') as af:
    app_config = yaml.safe_load(af.read())

with open('/app/conf/log_conf.yml', 'r') as lf:
    LOG_CONFIG = yaml.safe_load(lf.read())
    logging.config.dictConfig(LOG_CONFIG)

# create logger from basicLogger defined in the configuration file. 
logger = logging.getLogger('basicLogger')
logger.info('INFO - Service startup - Will look for and log anomaly threshold values')

# Need to import kafkaclient from pykafka
# The following base is from Tim's code
# client = KafkaClient(hosts='localhost:9092')

hostname = app_config['kafka']['hostname']
port = app_config['kafka']['port']
topic = app_config['kafka']['topic']
interval = app_config['scheduler']['interval']

# client = KafkaClient(hosts=f"{hostname}:{port}")
# topic = client.topics[str.encode(f'{topic}')]
# # producer = topic.get_sync_producer()
# consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)

try:
    with open(app_config['datastore']['filename'], 'r') as file:
        information = json.load(file)
except FileNotFoundError:
    information = {
        "event_id": "placeholder",
        "event_trace_id": "placeholder",
        "event_type": "placeholder", 
        "event_desc": "placeholder", 
        "last_updated": "2000-01-01 00:00:00"
    }


def update_anomalies():
    start_time = datetime.now()
    logger.debug(f'DEBUG - Accessing Update Endpoint ')
    # Reads from the Kafka Queue
    client = KafkaClient(hosts=f"{hostname}:{port}")
    topic = client.topics[app_config["kafka"]["topic"].encode()]
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)

    # Finds events with anomalies
    for msg in consumer: 
        message = msg.value.decode('utf-8')
        data = json.loads(message)

        item = data['payload']

        if data['type'] == 'station':
            if item['passenger_amount'] <= 50:
                dictionary_item = {
                    "event_id": item['station_id'],
                    "event_trace_id": item['trace_id'],
                    "event_type": "station",
                    "event_desc": f"Value {item['passenger_amount']} is below threshold of 50."
                }

        
        elif data['type'] == 'maintenance':
            if item['train_count'] <= 50:
                dictionary_item = {
                    "event_id": item['maintenance_yard_id'],
                    "event_trace_id": item['trace_id'],
                    "event_type": 'maintenance',
                    "event_desc": f"Value {item['train_count']} is below threshold of 50."
                }

    logger.debug(f'DEBUG - {dictionary_item} has been added to the JSON file after falling below threshold of 50.')
    # Updates JSON datastore from scratch with anomaly data
    with open(app_config['datastore']['filename'], 'w') as file:
        json.dump(dictionary_item, file, indent=4)

    end_time = datetime.now()

    elapsed_time = end_time - start_time

    logger.info(f'INFO - Elapsed time was {elapsed_time} to complete operation')

def get_anomalies(event_type=None):

    client = KafkaClient(hosts=f"{hostname}:{port}")
    topic = client.topics[app_config["kafka"]["topic"].encode()]
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)
    # If the event type provided is invalid, return 400
    for msg in consumer:
        logger.debug(f'DEBUG - Received a message')
        message = msg.value.decode('utf-8')
        data = json.loads(message)

        item = data['payload']

        if data['type'] != 'maintenance' or 'station':
            return 400
        
    # If event type is not provided, show all anomalies
        elif data['type'] == None:
            return file, 200 

    # If no anomalies, return 204
        elif data['type'] == None:
            if file == None:
                return 204
            
    # If no file, return a 404. 
        elif data['type'] == None:
            if file == FileNotFoundError:
                return 404

app = connexion.FlaskApp(__name__, specification_dir='')
# Enable validations on the request and response of your API. 
app.add_api("ELAWVC-API_3855_L1-1.0.0-swagger.yaml", base_path="/anomaly", strict_validation=True, validate_responses=True)

if "CORS_ALLOW_ALL" in os.environ and os.environ["CORS_ALLOW_ALL"] == "yes":
    app.add_middleware(
        CORSMiddleware,
        position=MiddlewarePosition.BEFORE_EXCEPTION,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


if __name__ == "__main__":
    app.run(port=8115, host="0.0.0.0")
