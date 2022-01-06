import logging
from datetime import datetime, timedelta
from typing import Dict
from app import db
from app.udaconnect.models import Location


from geoalchemy2.functions import ST_AsText, ST_Point
from sqlalchemy.sql import text


class LocationService:
    @staticmethod
    def kafka_consumed_create(location: Dict):
        new_location = Location()
        new_location.person_id = location["person_id"]
        new_location.creation_time = location["creation_time"]
        new_location.coordinate = ST_Point(location["latitude"], location["longitude"])
        db.session.add(new_location)
        db.session.commit()
    
