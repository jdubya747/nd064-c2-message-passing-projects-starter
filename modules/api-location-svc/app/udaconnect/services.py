import logging
import json
from datetime import datetime, timedelta
from typing import Dict
from app import db
from app.udaconnect.models import Location
from app.udaconnect.schemas import LocationSchema
from flask import g, Response
from geoalchemy2.functions import ST_AsText, ST_Point
from sqlalchemy.sql import text

class LocationService:
    @staticmethod
    def retrieve(location_id) -> Location:
        location, coord_text = (
            db.session.query(Location, Location.coordinate.ST_AsText())
            .filter(Location.id == location_id)
            .one()
        )

        # Rely on database to return text form of point to reduce overhead of conversion in app code
        location.wkt_shape = coord_text
        return location

    @staticmethod
    def create(location: Dict) -> Response:
        validation_results: Dict = LocationSchema().validate(location)
        if validation_results:
            logging.warning(f"Unexpected data format in payload: {validation_results}")
            raise Exception(f"Invalid payload: {validation_results}")

        TOPIC_NAME = 'location'
        KAFKA_SERVER = 'kafka:9092'
        try:
            logging.info('Sending kafka message with person_id = %s', location["person_id"])
            send_bytes = json.dumps(location).encode('utf-8')
            kafka_producer = g.kafka_producer
            kafka_producer.send(TOPIC_NAME, send_bytes)
            kafka_producer.flush(timeout=5.0)
            logging.info('Sent kafka message')
            response = Response(status=202)
        except Exception as ex:
            response = Response(status=500)
            logging.info('Exception in publishing message: ', {ex})
        finally:
            logging.info(f"response: {response}")
        return response


    
