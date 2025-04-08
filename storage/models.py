from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy import BigInteger, Integer, String, DateTime, func


class Base(DeclarativeBase):
    pass


class StationStatus(Base):
    __tablename__ = "station_wait"
    id = mapped_column(Integer, primary_key=True)
    station_id = mapped_column(String(50), nullable=False)
    line_id = mapped_column(String(50), nullable=False)
    timestamp = mapped_column(DateTime, nullable=False)
    passenger_amount = mapped_column(Integer, nullable=False)
    # make sure both models also have a date_created column set to current datetime of record add
    date_created = mapped_column(DateTime, nullable=False, default=func.now()) 
    trace_id = mapped_column(BigInteger, nullable=False)
    
    def to_dict(self):
        """Dictionary Representation of Station Wait"""
        station_dict = {}
        station_dict['id'] = self.id
        station_dict['station_id'] = self.station_id
        station_dict['line_id'] = self.line_id
        station_dict['timestamp'] = self.timestamp
        station_dict['passenger_amount'] = self.passenger_amount
        station_dict['date_created'] = self.date_created
        station_dict['trace_id'] = self.trace_id 

        return station_dict
    
    def to_id(self):
        station_dict = {}
        station_dict['station_id'] = self.station_id
        station_dict['trace_id'] = self.trace_id 
        station_dict['event_type'] = "Station Status"
        

class MaintenanceStatus(Base):
    __tablename__ = "maintenance_inventory"
    id = mapped_column(Integer, primary_key=True)
    maintenance_yard_id = mapped_column(String(50), nullable=False) 
    model = mapped_column(String(50), nullable=False)
    timestamp = mapped_column(DateTime, nullable=False)
    train_count = mapped_column(Integer, nullable=False)
    # make sure both models also have a date_created column set to current datetime of record add
    date_created = mapped_column(DateTime, nullable=False, default=func.now())
    trace_id = mapped_column(BigInteger, nullable=False)
    
    def to_dict(self):
        """Dictionary Representation of Maintenance Inventory"""
        maintenance_dict = {}
        maintenance_dict['id'] = self.id
        maintenance_dict['maintenance_yard_id'] = self.maintenance_yard_id
        maintenance_dict['model'] = self.model
        maintenance_dict['timestamp'] = self.timestamp
        maintenance_dict['train_count'] = self.train_count
        maintenance_dict['date_created'] = self.date_created
        maintenance_dict['trace_id'] = self.trace_id 

        return maintenance_dict

    def to_id(self):
        maintenance_dict = {}
        maintenance_dict['maintenance_yard_id'] = self.maintenance_yard_id
        maintenance_dict['trace_id'] = self.trace_id 
        maintenance_dict['event_type'] = "Maintenance Status"