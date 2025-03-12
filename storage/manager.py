# Create a script to manage your database

import sys
from models import Base
from db import engine


def create_tables():
    # this creates the sqlite file if I don't have it. 
    Base.metadata.create_all(engine)


def drop_tables():
    Base.metadata.drop_all(engine)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "drop":
        drop_tables()
    
    create_tables()


# Note in Terminal:
#   Create all tables - python manager.py 
#   Drop all tables - python manager.py drop 
