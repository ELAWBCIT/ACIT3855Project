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

# Lab 4 - Loading the app_conf.yml file
with open('/app/conf/app_conf.yml', 'r') as af:
    app_config = yaml.safe_load(af.read())

with open('/app/conf/log_conf.yml', 'r') as lf:
    LOG_CONFIG = yaml.safe_load(lf.read())
    logging.config.dictConfig(LOG_CONFIG)

# create logger from basicLogger defined in the configuration file. 
logger = logging.getLogger('basicLogger')

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


def get_station_wait_reading(index):
    client = KafkaClient(hosts=f"{hostname}:{port}")
    topic = client.topics[app_config["kafka"]["topic"].encode()]
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)
    
    counter = 0
    for msg in consumer:
        message = msg.value.decode('utf-8')
        data = json.loads(message)

        # Look for index requested
        item = data['payload']

        if data['type'] == 'station':
            if counter == index:
                # Return payload with 200 status code   
                return item, 200
            counter += 1
        
    return { "message": f"No message at index {index}!"}, 404



def get_maintenance_yard_reading(index):
    client = KafkaClient(hosts=f"{hostname}:{port}")
    topic = client.topics[app_config["kafka"]["topic"].encode()]
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)
    
    counter = 0
    for msg in consumer:
        message = msg.value.decode('utf-8')
        data = json.loads(message)

        # Look for index requested
        item = data['payload']

        print(data, counter, index)

        if data['type'] == 'maintenance':
            if counter == index:
                # Return payload with 200 status code
                return item, 200
            counter += 1
        
    return { "message": f"No message at index {index}!"}, 404


def get_event_stats():
    client = KafkaClient(hosts=f"{hostname}:{port}")
    topic = client.topics[app_config["kafka"]["topic"].encode()]
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)
    
    station_count = 0
    maintenance_count = 0

    for msg in consumer:
        message = msg.value.decode('utf-8')
        data = json.loads(message)
        if data['type'] == 'station':
            station_count += 1
            # print(data)
        if data['type'] == 'maintenance':
            maintenance_count += 1
            # print(data)
    
    display = {
        "num_station_count": station_count,
        "num_maintenance_count": maintenance_count
    }

    return display, 200
    


app = connexion.FlaskApp(__name__, specification_dir='')
# Enable validations on the request and response of your API. 
app.add_api("ELAWVC-API_3855_L1-1.0.0-swagger.yaml", strict_validation=True, validate_responses=True)

app.add_middleware(
    CORSMiddleware,
    position=MiddlewarePosition.BEFORE_EXCEPTION,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    app.run(port=8101, host="0.0.0.0")
