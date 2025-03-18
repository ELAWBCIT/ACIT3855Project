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
from datetime import datetime, timezone


from pathlib import Path 

# Lab 3 imports
import httpx 

# Lab 4 imports 
import time
import uuid
import yaml 
import logging

# Just an import used for checking file existence. 
import os.path

# Lab 5 imports
from apscheduler.schedulers.background import BackgroundScheduler

# Still need the different yaml config files for logger and the application. 
# with open('/app/conf/app_conf_prod.yml', 'r') as af:
#     app_config = yaml.safe_load(af.read())

if os.path.exists('../config/processing/app_conf_prod.yml'):
    with open('../config/processing/app_conf_prod.yml', 'r') as af:
        app_config = yaml.safe_load(af.read())
else:
    with open('../config/processing/app_conf_dev.yml', 'r') as af:
        app_config = yaml.safe_load(af.read())

with open('../config/processing/log_conf.yml', 'r') as lf:
    LOG_CONFIG = yaml.safe_load(lf.read())
    logging.config.dictConfig(LOG_CONFIG)


# create logger from basicLogger defined in the configuration file. 
logger = logging.getLogger('basicLogger')


def get_stats():
    # log info message indicating request received
    logger.info('Request received')

    # read the info.json file 
    try:
        with open(app_config['datastore']['filename'], 'r') as file:
            # When reading file into python dictionary, name it the same thing that you name the empty default dictionary 
            information = json.load(file)
    
    # if file doesn't exist log error message and return a 404 code
    except FileNotFoundError:
        logger.error('Statistics do not exist')
        return NoContent, 404

    # log debug message with contents, log info indicating request complete
    logger.debug(f'{information}')
    logger.info('Request completed')

    # return 200 code. 
    return information, 200


def populate_stats():
    print('In function populate stats!')
    # Log info stating periodic processing has started. 
    logger.info(f'Periodic Processing has started')

    # Open file if it exists, if not create python dictionary of default values
    try:
        with open(app_config['datastore']['filename'], 'r') as file:
            # When reading file into python dictionary, name it the same thing that you name the empty default dictionary 
            information = json.load(file)
    except FileNotFoundError:
        # processing must have four statistics
        information = {
            "num_sw_readings": 0,
            "max_pg_readings": 0, 
            "num_my_readings": 0, 
            "max_tr_readings": 0,
            "last_updated": "2000-01-01 00:00:00"
        }
    

    # take last updated date as the start and then the now is the end timestamp. 

    # set the time to now, is easier to just add a line here to set it as UTC instead of changing mysql. 
    # otherwise would have issue with getting the data back as the time is set in the "future" 
    end_timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    # make a get request to your storage service, using two dates get the rows 

    events_sw = httpx.get(f"{app_config['eventstores']['station']['url']}?start_timestamp={information['last_updated']}&end_timestamp={end_timestamp}")
    if events_sw.status_code != 200:
        # log error message if not a 200 response code 
        logger.error(f'Error, received {events_sw.status_code} - Station')
        return
    else:
        logger.info(f'Information received for Station Wait, number of events: {len(events_sw.json())}')


    events_my = httpx.get(f"{app_config['eventstores']['maintenance']['url']}?start_timestamp={information['last_updated']}&end_timestamp={end_timestamp}")
    if events_my.status_code != 200:
        # log error message if not a 200 resposne code 
        logger.error(f'Error, received {events_my.status_code} - Maintenance')
        return 
    else:
        logger.info(f'Information received for Maintenance Inv, number of events: {len(events_my.json())}')
    

    # Calculate the updated statistics 
    # update your statistics
    # adds to the max events count
    information['num_sw_readings'] += len(events_sw.json())
    information['num_my_readings'] += len(events_my.json()) 
    # gets the max for my specific information field 
    for item in events_sw.json():
        if item['passenger_amount'] >  information['max_pg_readings']:
            information['max_pg_readings'] = item['passenger_amount']
    for item in events_my.json():
        if item['train_count'] > information['max_tr_readings']:
            information['max_tr_readings'] = item['train_count']
    # update the time
    information['last_updated'] = end_timestamp
    

    # write the updated statistics to JSON
    with open(app_config['datastore']['filename'], 'w') as file:
        json.dump(information, file, indent=4)

    # log a debug message with your updated statistics values 
    logger.debug(f'Information updated: {information}')

    # log an info message indicating period processing has ended 
    logger.info(f'Periodic processing has ended.')


def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats, 'interval', seconds=app_config['scheduler']['interval'])
    sched.start()


app = connexion.FlaskApp(__name__, specification_dir='')
# Enable validations on the request and response of your API. 
app.add_api("ELAWVC-API_3855_L1-1.0.0-swagger.yaml", strict_validation=True, validate_responses=True)


if __name__ == "__main__":
    init_scheduler()
    # Change the port use for this server to 8100. 
    app.run(port=8100, host="0.0.0.0")
