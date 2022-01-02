import logging
from datetime import datetime, timedelta
from typing import List
from app import db
from app.udaconnect.models import Connection, Location, Person
from app.udaconnect.schemas import ConnectionSchema, LocationSchema, PersonSchema
from geoalchemy2.functions import ST_AsText, ST_Point
from sqlalchemy.sql import text
import grpc
from . import people_pb2 as people_pb2
from . import people_pb2_grpc as people_pb2_grpc

#logging.basicConfig(level=logging.WARNING)
#logger = logging.getLogger("udaconnect-api")

#this is a comment to invode change


class ConnectionService:
    @staticmethod
    def find_contacts(person_id: int, start_date: datetime, end_date: datetime, meters=5
    ) -> List[Connection]:
        """
        Finds all Person who have been within a given distance of a given Person within a date range.

        This will run rather quickly locally, but this is an expensive method and will take a bit of time to run on
        large datasets. This is by design: what are some ways or techniques to help make this data integrate more
        smoothly for a better user experience for API consumers?
        """
        locations: List = db.session.query(Location).filter(
            Location.person_id == person_id
        ).filter(Location.creation_time < end_date).filter(
            Location.creation_time >= start_date
        ).all()

        # Cache all users in memory for quick lookup
        #person_map: Dict[str, Person] = {person.id: person for person in PersonService.retrieve_all()}
        #channel = grpc.insecure_channel("localhost:30005")
        #channel = grpc.insecure_channel("10.42.0.79:5005")
        channel = grpc.insecure_channel("udaconnect-api-people-svc:5005")
        stub = people_pb2_grpc.PeopleServiceStub(channel)
        person_map = {}
        peopleMessageList = stub.Get(people_pb2.Empty())
        for peeps in peopleMessageList.people:
            pee = Person
            pee.id = peeps.id
            pee.first_name = peeps.first_name
            pee.last_name = peeps.last_name
            pee.company_name = peeps.company_name
            person_map[pee.id] = pee
        #person_map: Dict[int, Person] = {person.id: person for person in stub.Get(people_pb2.Empty())}
        # Prepare arguments for queries
        data = []
        for location in locations:
            data.append(
                {
                    "person_id": person_id,
                    "longitude": location.longitude,
                    "latitude": location.latitude,
                    "meters": meters,
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": (end_date + timedelta(days=1)).strftime("%Y-%m-%d"),
                }
            )

        query = text(
            """
        SELECT  person_id, id, ST_X(coordinate), ST_Y(coordinate), creation_time
        FROM    location
        WHERE   ST_DWithin(coordinate::geography,ST_SetSRID(ST_MakePoint(:latitude,:longitude),4326)::geography, :meters)
        AND     person_id != :person_id
        AND     TO_DATE(:start_date, 'YYYY-MM-DD') <= creation_time
        AND     TO_DATE(:end_date, 'YYYY-MM-DD') > creation_time;
        """
        )
        result: List[Connection] = []
        for line in tuple(data):
            for (
                exposed_person_id,
                location_id,
                exposed_lat,
                exposed_long,
                exposed_time,
            ) in db.engine.execute(query, **line):
                location = Location(
                    id=location_id,
                    person_id=exposed_person_id,
                    creation_time=exposed_time,
                )
                location.set_wkt_with_coords(exposed_lat, exposed_long)

                result.append(
                    Connection(
                        person=person_map[exposed_person_id], location=location,
                    )
                )

        return result

