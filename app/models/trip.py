from datetime import datetime
import json
try:
    from .toolbox import ID_operation
    from . import trip_UserNet
except:
    from toolbox import ID_operation
    import trip_UserNet
    

class Trip:
    """
    Trip are under user, describe a "project" that includes users, events, and transations
    additon information such as map and weather are stored
    Trip act as a folder to store Events and Transations
    """
    STR_FORMAT = '%Y-%m-%d'
    FILE_PATH = "app/data/trips.json"
    


    def __init__(self, tripID: str, ownerID: str, accessBy: list, linkedEvent: list, linkedTransaction: list, name: str, startDate: str, endDate: str, tripDescription: str, location: str) -> None:
        # PK
        self.ID = tripID
        # FK
        self.ownerID = ownerID
        self.accessBy = accessBy
        # Dependent
        self.linkedEvent = linkedEvent
        self.linkedTransaction = linkedTransaction
        # Attribute
        self.name = name
        self.startDate = datetime.strptime(startDate, Trip.STR_FORMAT).date()
        self.endDate = datetime.strptime(endDate, Trip.STR_FORMAT).date()
        self.tripDescription = tripDescription
        self.location = location

    
    @classmethod
    def create(cls, ownerID: str, name: str, startDate: str, endDate: str, tripDescription: str, location: str, accessBy: list=[]) -> 'Trip':
        """
        Create a trip class from user input, will also auto create a list of Trip_UserNet
        """
        # Make 
        tripID = ID_operation.id_gen(2)
        linkedEvent = []
        linkedTransaction = []
        if ownerID not in accessBy:
            accessBy.append(ownerID)
        temp = cls(tripID, ownerID, accessBy, linkedEvent, linkedTransaction, name, startDate, endDate, tripDescription, location)
        temp.write()

        # Auto create a list of Trip_UserNet
        for id in accessBy:
            trip_UserNet.Trip_UserNet.create(id, temp.ID).write()

        return temp
    

    @classmethod
    def read(cls, tripID: str):
        try:
            with open(Trip.FILE_PATH, "r") as file:
                try:
                    existing_data = json.load(file)
                except:
                    existing_data = {}
        except FileNotFoundError:
            print(f"File {Trip.FILE_PATH} not found")
        
        try:
            current_net = existing_data[tripID]
        except:
            print(f"ERROR: trip.read - Trip {tripID} not found")
            return -1
    
        return cls(**current_net)


    def view_linked(self) -> dict:
        # Process Event dict
        if self.linkedEvent:
            e_dict = ID_operation.id_read(3, self.linkedEvent)
            for key, values in e_dict.items():
                values['type'] = "Event"
                pop_items = ['eventID', 'linkedTrip', 'description']
                for item in pop_items:
                    values.pop(item)
        else:
            e_dict={}
            
        # Process Transaction dict
        CATEGORY_DICT = {
        0: "Uncategorized",
        1: "Accommodation",
        2: "Food and Drinks",
        3: "Groceries",
        4: "Tickets",
        5: "Transportation",
        6: "Others"
        }
        linked_t_dict = {}
        un_t_dict = {}
        if self.linkedTransaction:
            t_dict = ID_operation.id_read(4, self.linkedTransaction)
            for key, values in t_dict.items():
                # values['ID'] = values["transactionID"]
                values['type'] = "Transaction"
                values['startTime'] = values['transDateTime']
                values['category'] = CATEGORY_DICT.get(values['category'])
                
                paid_users = []
                received_users = []

                for user_id, user_data in values['linkedUser'].items():
                    if user_data['paid'] > 0:
                        paid_users.append(user_id)
                    if user_data['received'] > 0:
                        received_users.append(user_id)

                values['paid'] = paid_users
                values['received'] = received_users

                pop_items = ['transactionID', 'linkedTrip', "transDateTime"]
                for item in pop_items:
                    values.pop(item)
                
                
                if values['linkedEvent'] is not None:
                    linked_t_dict.update({key: values})
                else:
                    un_t_dict.update({key: values})
                    pass

        else:
            t_dict = {}

        a_dict = {**un_t_dict, **e_dict}
        a_dict = {k: v for k, v in sorted(a_dict.items(), key = lambda item: item[1]['startTime'])}

        linked_t_dict = {k: v for k, v in sorted(linked_t_dict.items(), key = lambda item: item[1]['startTime'])}

        A_dict = {}
        for k, v in a_dict.items():
            A_dict.update({k:v})
            for key, values in linked_t_dict.items():
                if k == values['linkedEvent']:
                    A_dict.update({key: values})

        
        return A_dict
    

    def write(self) -> None:
        try:
            with open(Trip.FILE_PATH, "r") as file:
                try:
                    existing_data = json.load(file)

                except:
                    existing_data = {}

        except FileNotFoundError:
            existing_data = {}
        
        existing_data.update(self.to_dict())

        with open(Trip.FILE_PATH, "w") as file:
            json.dump(existing_data, file, indent=4)
            file.write('\n')
    

    def __str__(self) -> str:
        return (f'tripID: {self.ID}, ownerID: {self.ownerID}, accessBy: {self.accessBy},' +
                f'linkedEvent: {self.linkedEvent}, linkedTransaction: {self.linkedTransaction},' +
                f'name: {self.name},' +
                f'startDate: {self.startDate.strftime(self.STR_FORMAT)}, endDate: {self.endDate.strftime(self.STR_FORMAT)},' +
                f'tripDescription: {self.tripDescription}, location: {self.location}\n')

    
    def to_dict(self) -> dict:
        data = {f"{self.ID}":{
            "tripID": self.ID,
            "ownerID": self.ownerID,
            "accessBy":self.accessBy,
            "linkedEvent": self.linkedEvent,
            "linkedTransaction": self.linkedTransaction,
            "name": self.name,
            "startDate": self.startDate.strftime(self.STR_FORMAT),
            "endDate": self.endDate.strftime(self.STR_FORMAT),
            "tripDescription": self.tripDescription,
            "location": self.location,
            }
        }
        return data
    
    
    def to_json_str(self) -> str:
        json_str = json.dumps({self.ID: (self.to_dict())})
        return json_str


def main():
    test = Trip.create("100002","trip A", "2023-11-15", "2023-11-16" ,'GG', "HONG KONG") 
    # test = Trip.create("100000","trip A", "2023-11-15", "2023-11-16" ,'GG', "HONG KONG", accessBy=['100001', '100002'])
    test = Trip.read('200000')
    # print(test)
    test.view_linked()
    

if __name__ == '__main__':
    main()
