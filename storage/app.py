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

# Necessary imports - Labs 1 and 2
import logging.config
import connexion
from connexion import NoContent

import json

import datetime
from datetime import datetime

import uuid

from pathlib import Path 

# Necessary imports - Lab 3
from db import make_session
from models import StationStatus, MaintenanceStatus
import httpx 

# Necessary imports - Lab 4
import yaml
import logging 
import time
import uuid 
import manager 

# Necessary imports - Lab 5
from sqlalchemy import select 

# Lab 6 imports
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread

import os.path 

manager.create_tables()

# with open('/app/conf/app_conf_prod.yaml', 'r') as af:
#     app_config = yaml.safe_load(af.read())

if os.path.exists('../config/storage/app_conf_prod.yml'):
    with open('../config/storage/app_conf_prod.yml', 'r') as af:
        app_config = yaml.safe_load(af.read())
else:
    with open('../config/storage/app_conf_dev.yml', 'r') as af:
        app_config = yaml.safe_load(af.read())

with open('../config/storage/log_conf.yml', 'r') as lf:
    LOG_CONFIG = yaml.safe_load(lf.read())
    logging.config.dictConfig(LOG_CONFIG)

logger = logging.getLogger('basicLogger')

# name the function based on the operationID
# by default the parameter for the payload data of endpoint received as arg
# must be named body
def post_wait_time(body):
    """ Receives information on trains at stations """
    # Write code to display the payload to the console via print
    print('Payload: ', body)

    # Lab 3:
    # Needed to format the timestamp because of the error it throws that it isn't a string. 
    wait_time_timestamp = body['timestamp'] 
    print(wait_time_timestamp)
    # using striptime, need to match it to the bruno method of 2025-01-25 example of date. 
    formatted_wt_timestamp = datetime.strptime(wait_time_timestamp, "%Y-%m-%d %H:%M:%S")

    # Lab 3: Skeleton Code
    wait_time_obj = StationStatus(station_id=body['station_ID'], line_id=body['line_ID'], timestamp=formatted_wt_timestamp, passenger_amount=body['passenger_amount'], trace_id=body['trace_id'])
    session = make_session()
    session.add(wait_time_obj)
    session.commit()
    session.close()

    logger.debug(f"Stored event status with a trace id of {body['trace_id']}")

    # Return a 201 response code 
    return NoContent, 201


# name the function based on the operationID 
# by default the parameter for the payload data of endpoint received as arg
# must be named body
def post_maintenance_yard(body):
    """ Receives information on trains at maintenace """
    # Write code to display the payload to the console via print
    print('Payload: ', body)
    # commented out to remove print statements

    # Lab 3:
    # Needed to format the timestamp because of the error it throws that it isn't a string. 
    maintenance_timestamp = body['timestamp'] 
    print(maintenance_timestamp)
    # using striptime, need to match it to the bruno method of 2025-01-25 example of date. 
    formatted_mt_timestamp = datetime.strptime(maintenance_timestamp, "%Y-%m-%d %H:%M:%S")

    # Lab 3: Skeleton Code
    wait_time_obj = MaintenanceStatus(maintenance_yard_id=body['maintenance_yard_id'], model=body['model'], timestamp=formatted_mt_timestamp, train_count=body['train_count'], trace_id=body['trace_id'] )
    session = make_session()
    session.add(wait_time_obj)
    session.commit()
    session.close()

    logger.debug(f"Stored event status with a trace id of {body['trace_id']}")

    # Return a 201 response code 
    return NoContent, 201


def get_wait_time(start_timestamp, end_timestamp):
    """ Gets new wait time readings between the start and the end."""
    session = make_session()

    # originally .fromtimestamp
    # couldn't get it to work cause fromtimestamp was unix based time code
    # ended up using strptime, ran into issue with two arguments needing to be called. So added 
    start = datetime.strptime(start_timestamp, "%Y-%m-%d %H:%M:%S")
    end = datetime.strptime(end_timestamp, "%Y-%m-%d %H:%M:%S") 
    print(start)
    print(end)

    statement = select(StationStatus).where(StationStatus.date_created >= start).where(StationStatus.date_created < end)
    
    results = [
        result.to_dict()
        for result in session.execute(statement).scalars().all()
    ]

    session.close()

    logger.info("Found %d station wait time readings (start: %s, end: %s)", len(results), start, end)

    return results 


def get_maintenance_yard(start_timestamp, end_timestamp):
    """ Gets new maintenance inventory readings between the start and the end."""
    session = make_session()

    # originally .fromtimestamp
    # couldn't get it to work cause fromtimestamp was unix based time code
    # ended up using strptime, ran into issue with two arguments needing to be called. So added 
    start = datetime.strptime(start_timestamp, "%Y-%m-%d %H:%M:%S")
    end = datetime.strptime(end_timestamp, "%Y-%m-%d %H:%M:%S") 
    print(start)
    print(end)

    statement = select(MaintenanceStatus).where(MaintenanceStatus.date_created >= start).where(MaintenanceStatus.date_created < end)
    
    results = [
        result.to_dict()
        for result in session.execute(statement).scalars().all()
    ]

    session.close()

    logger.info("Found %d maintenace inventory readings (start: %s, end: %s)", len(results), start, end)

    return results 


def process_messages():
    """Process event messages"""
    hostname = f'{app_config['events']['hostname']}:{app_config['events']['port']}'
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode('events')]
    logger.debug("before")

    # Create a consume or consumer group that only reads new messages
    # (uncommitted messages) when the service re-starts - it doesn't red all old msgs from history in queue
    consumer = topic.get_simple_consumer(consumer_group=b'event_group', 
                                         reset_offset_on_start=False,
                                         auto_offset_reset=OffsetType.LATEST) 
    logger.debug("after")

    for msg in consumer:
        logger.debug("new msg in kafka")
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)

        payload = msg['payload']

        try:
            if msg['type'] == 'station':
                post_wait_time(payload)
            elif msg['type'] == 'maintenance':
                post_maintenance_yard(payload) 
        except:
            logger.error(" ISSUE ")
        consumer.commit_offsets()
    logger.debug("end")

def setup_kafka_thread():
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()

app = connexion.FlaskApp(__name__, specification_dir='')
# Enable validations on the request and response of your API. 
app.add_api("ELAWVC-API_3855_L1-1.0.0-swagger.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    # receiver service port = 8080.
    # lab 3 - change the port used for this service.
    # storage service uses different port than receiver service. Should be 8090. 
    setup_kafka_thread()
    app.run(port=8090, host="0.0.0.0")
    