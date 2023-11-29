from datetime import datetime
import json
try:
    from .toolbox import ID_operation
    from . import trip, transaction
except:
    from toolbox import ID_operation
    import trip, transaction


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
    

    @classmethod
    def read(cls, eventID: str):
        try:
            with open(Event.FILE_PATH, "r") as file:
                try:
                    existing_data = json.load(file)
                except:
                    existing_data = {}
        except FileNotFoundError:
            print(f"File {Event.FILE_PATH} not found")
        
        try:
            current_net = existing_data[eventID]
        except:
            print(f"ERROR: transaction.read - transaction {eventID} not found")
            return -1
    
        return cls(**current_net)
    
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


    def delete(eventID) -> None:

        del_event = Event.read(eventID)

        try:
            with open(Event.FILE_PATH, "r") as file:
                try:
                    existing_data = json.load(file)

                except:
                    existing_data = {}

        except FileNotFoundError:
            existing_data = {}

        del existing_data[eventID]
        
        with open(Event.FILE_PATH, "w") as file:
            json.dump(existing_data, file, indent=4)
            file.write('\n')

        # Remove the link in trip
        try:
            affected_trip = trip.Trip.read(del_event.linkedTrip)
            affected_trip.linkedEvent.remove(eventID)
            affected_trip.write()
        except:
            pass


        # Delete trnasaction with the event
        try:
            with open(transaction.Transaction.FILE_PATH, "r") as file:
                try:
                    existing_data = json.load(file)
                except:
                    existing_data = {}
        except FileNotFoundError:
            existing_data = {}

        for key, value in existing_data.items():
            if value["linkedEvent"] == eventID:
                transaction.Transaction.delete(key)
        
        return 

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
    test = Event.create(["100001"], "200003", "test", "des", "2023-11-25 12:00", "2023-11-25 12:00")
    # print(test)
    #print(test.to_json_str())
    input()
    Event.delete("300001")
    

if __name__ == '__main__':
    main()