from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import yaml 

with open('app_conf.yaml', 'r') as af:
    app_config = yaml.safe_load(af.read())

# does not create the database file. 
# engine = create_engine("mysql://user:loser@storage/trains_database")
engine = create_engine(f"mysql://{app_config['datastore']['user']}:{app_config['datastore']['password']}@db/trains_database")

def make_session():
    return sessionmaker(bind=engine)()