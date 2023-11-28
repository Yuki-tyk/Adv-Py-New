from datetime import datetime
import json
try:
    from .toolbox import ID_operation
    from . import trip
except:
    from toolbox import ID_operation
    import trip


class Event:
    """
    Events are under trips that describe the activity user planned,
    Event act as a folder to store transactions
    """
    STR_FORMAT = '%Y-%m-%d %H:%M'
    FILE_PATH = "app/data/events.json" 

    def __init__(self, eventID: str, linkedUser: list, linkedTrip: str, name: str, description: str, startTime: str, endTime: str) -> None:
        # PK
        self.ID = eventID
        # FK
        self.linkedUser = linkedUser
        self.linkedTrip = linkedTrip
        # Atributes
        self.name = name
        self.description = description
        self.startTime = datetime.strptime(startTime, Event.STR_FORMAT)
        self.endTime = datetime.strptime(endTime, Event.STR_FORMAT)


    @classmethod
    def create(cls, linkedUser: list, linkedTrip: str, name: str, description: str, startTime: str, endTime: str) -> 'Event':
        # check if the linkedTrip is valid
        if ID_operation.id_read(2, linkedTrip) == -1:
            return -2 # ERROR: No such trip
        
        ### NOT WOKRING FOR NOW
        # # check if the linkedUser is valid
        # if ID_operation.id_read(1, linkedUser) == -1:
        #     return -1 # ERROR: No such user
        
        # create an evnet
        eventID = ID_operation.id_gen(3)

        temp = cls(eventID, linkedUser, linkedTrip, name, description, startTime, endTime)
        temp.write()

        # add the eventID to the linked trip
        # print('-------------------------------------------')
        # print(ID_operation.id_read(2, linkedTrip))
        # print('-------------------------------------------')
        t_trip = trip.Trip(**(ID_operation.id_read(2, linkedTrip)[linkedTrip]))
        t_trip.linkedEvent.append(temp.ID)
        t_trip.write()

        return temp
    
    def write(self) -> None:
        try:
            with open(Event.FILE_PATH, "r") as file:
                try:
                    existing_data = json.load(file)

                except:
                    existing_data = {}

        except FileNotFoundError:
            existing_data = {}
        
        existing_data.update(self.to_dict())

        with open(Event.FILE_PATH, "w") as file:
            json.dump(existing_data, file, indent=4)
            file.write('\n')

    def __str__(self) -> str:
        return (f'\neventID: {self.ID}, linkedUser: {self.linkedUser}, linkedTrip: {self.linkedTrip},' + 
                f'\nevent_name: {self.name}, description: {self.description},' +
                f'\nstart_time: {self.startTime}, end_time: {self.endTime}\n')


    def __repr__(self) -> str:
        return f'Event({self.ID}, {self.linkedUser}, {self.linkedTrip}, {self.name}, {self.description}, {self.startTime}, {self.endTime})'


    def to_dict(self) -> dict:
        data = {f"{self.ID}":{
            "eventID": self.ID,
            "linkedUser": self.linkedUser,
            "linkedTrip":self.linkedTrip,
            "name": self.name,
            "description": self.description,
            "startTime": self.startTime.strftime(self.STR_FORMAT),
            "endTime": self.endTime.strftime(self.STR_FORMAT)
            }
        }
        return data
    
    def to_json_str(self) -> str:
        json_str = json.dumps({self.ID: (self.to_dict())})
        return json_str



# Test
def main():
    #test = Event.create(['100000'], "200000", "event 2", "event 2 description", "2023-11-15 00:00", "2023-11-16 00:00")
    test = Event.create(['100000', '100001'], "200000", "event 2", "event 2 description", "2023-11-15 00:00", "2023-11-16 00:00")
    #print(test)
    #print(test.to_json_str())
    

if __name__ == '__main__':
    main()