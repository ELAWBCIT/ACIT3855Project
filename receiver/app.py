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

import os.path

# Lab 6 imports
from pykafka import KafkaClient

if os.path.exists('/conf/app_conf_prod.yml'):
    with open('/conf/app_conf_prod.yml', 'r') as af:
        app_config = yaml.safe_load(af.read())
else:
    with open('/conf/app_conf_dev.yml', 'r') as af:
        app_config = yaml.safe_load(af.read())

with open('/conf/log_conf.yml', 'r') as lf:
    LOG_CONFIG = yaml.safe_load(lf.read())
    logging.config.dictConfig(LOG_CONFIG)

# create logger from basicLogger defined in the configuration file. 
logger = logging.getLogger('basicLogger')

# Need to import kafkaclient from pykafka
# The following base is from Tim's code
client = KafkaClient(hosts=f'{app_config['events']['hostname']}:{app_config['events']['port']}')
topic = client.topics[str.encode('events')]
producer = topic.get_sync_producer()

# name the function based on the operationID
# by default the parameter for the payload data of endpoint received as arg
# must be named body
def post_wait_time(body):
    """ Receives information on trains at stations """
    # Write code to display the payload to the console via print
    print('Payload: ', body)
    # commented out to remove print statements
    
    # When an event is received, a trace_id is added to the JSON payload and sent to the storage service
    trace_id = time.time_ns()

    body['trace_id'] = trace_id 
    logger.info(f'Received event status with a trace id of {trace_id}')

    msg = { 
        "type": "station",
        "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "payload": body,
    }

    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))


    logger.info(f'Response for event status (id: {trace_id}) has status 201')

    # In the receivers service, return NoContent and the Status Code from storage service 
    return NoContent, 201


# name the function based on the operationID 
# by default the parameter for the payload data of endpoint received as arg
# must be named body
def post_maintenance_yard(body):
    """ Receives information on trains at maintenace """
    # Write code to display the payload to the console via print
    print('Payload: ', body)
    # commented out to remove print statements
    
    # When an event is received, a trace_id is added to the JSON payload and sent to the storage service
    trace_id = time.time_ns()

    body['trace_id'] = trace_id 
    print('Payload: ', body)
    logger.info(f'Received event maintenance with a trace id of {trace_id}')

    msg = { 
        "type": "maintenance",
        "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "payload": body,
    }

    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))


    logger.info(f'Response for event maintenace (id: {trace_id}) has status 201')

    # In the receivers service, return NoContent and the Status Code from storage service 
    return NoContent, 201


app = connexion.FlaskApp(__name__, specification_dir='')
# Enable validations on the request and response of your API. 
app.add_api("ELAWVC-API_3855_L1-1.0.0-swagger.yaml", strict_validation=True, validate_responses=True)


if __name__ == "__main__":
    app.run(port=8080, host="0.0.0.0")
