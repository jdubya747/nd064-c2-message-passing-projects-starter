import logging
from concurrent import futures
import grpc
from . import people_pb2 as people_pb2
from . import people_pb2_grpc as people_pb2_grpc
#from svc.auth_grpc import auth_pb2, auth_pb2_grpc
from typing import List
from app.udaconnect.models import Person
from app.udaconnect.services import PersonService

class PeopleServicer(people_pb2_grpc.PeopleServiceServicer):
    #def getPersons(self) -> List[Person]:
    #    persons: List[Person] = PersonService.retrieve_all()
    #    return persons
    def __init__(self, app_context):
        self.app_context = app_context
    
    def Get(self, request, context):
        result = people_pb2.PeopleMessageList()

        with self.app_context:
           for person in PersonService.retrieve_all():
               peoplePerson = people_pb2.PersonMessage(
                  id=int(person.id),
                  first_name=person.first_name,
                  last_name=person.last_name,
                  company_name=person.company_name,
               )
               result.people.extend([peoplePerson])
        
        return result

    def Create(self, request, context):
        print("Received a message!")

        request_value = {
            "id": request.id,
            "first_name": request.first_name,
            "last_name": request.last_name,
            "company_name": request.company_name
        }
        print(request_value)
        return people_pb2.PersonMessage(**request_value)

def start_server(app_context):
    global server
    logging.info('Starting server')
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    people_pb2_grpc.add_PeopleServiceServicer_to_server(PeopleServicer(app_context),  server)
    #auth_pb2_grpc.add_AuthServiceServicer_to_server(app.AuthServiceServicer(),
    #                                                server)
    server.add_insecure_port("[::]:5005")
    server.start()
    print("Server starting on port 5005...")
    logging.info('Server starting on port = %s', 5005)

