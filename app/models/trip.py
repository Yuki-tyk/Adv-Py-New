from datetime import datetime, timedelta
import json
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib import dates as mdates
import io
import base64
try:
    from .toolbox import ID_operation
    from . import trip_UserNet, event, transaction
except:
    from toolbox import ID_operation
    import trip_UserNet, event, transaction
    

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
            trip_UserNet.Trip_UserNet.create(id, temp.ID)

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


    def delete(tripID: str) -> bool:
        try:
            del_trip = Trip.read(tripID)

            # delete trip in trip
            try:
                with open(Trip.FILE_PATH, "r") as file:
                    try:
                        existing_data = json.load(file)

                    except:
                        existing_data = {}

            except FileNotFoundError:
                existing_data = {}

            del existing_data[tripID]

            with open(Trip.FILE_PATH, "w") as file:
                json.dump(existing_data, file, indent=4)
                file.write('\n')
            
            # delete event
            for eventID in del_trip.linkedEvent:
                event.Event.delete(eventID)
            
            # delete trip
            for transactionID in del_trip.linkedTransaction:
                transaction.Transaction.delete(transactionID)

            # delete trip_UserNet
            for userID in del_trip.accessBy:
                trip_UserNet.Trip_UserNet.delete(userID, tripID)

            return True
        except:
            return False


    @classmethod
    #read trips.json file and return a dict of all trips
    def read_all(cls) -> dict:
        try:
            with open(cls.FILE_PATH, "r") as file:
                try:
                    existing_data = json.load(file)
                except:
                    existing_data = {}
        except FileNotFoundError:
            print(f"File {Trip.FILE_PATH} not found")
            return -1
        return existing_data
    

    @classmethod
    #convert a trip name to trip ID
    def getTripIDbyName(cls, tripName):
        trips_data = cls.read_all()
        for key, value in trips_data.items():
            if value["name"] == tripName:
                return key
        return -1
    

    def view_linked(self) -> dict:
        # Process Event dict
        if self.linkedEvent:
            e_dict = ID_operation.id_read(3, self.linkedEvent)

            for key, values in e_dict.items():

                values['ID'] = values["eventID"]
                # change user id to user name
                user_name = []
                for userID in values["linkedUser"]:
                    try:
                        user_name.append((ID_operation.id_read(1, userID)[userID]["username"]))
                    except:
                        user_name.append("[Deleted Account]")
                
                values["linkedUser"] = user_name

                values['type'] = "Event"
                pop_items = ['eventID', 'linkedTrip']
                for item in pop_items:
                    values.pop(item)
        else:
            e_dict={}
            
        # Process Transaction dict
        CATEGORY_DICT = transaction.Transaction.CATEGORY_DICT
        linked_t_dict = {}
        un_t_dict = {}
        if self.linkedTransaction:
            t_dict = ID_operation.id_read(4, self.linkedTransaction)
            for key, values in t_dict.items():
                values['ID'] = values["transactionID"]
                values['type'] = "Transaction"
                values['startTime'] = values['transDateTime']
                values['category'] = CATEGORY_DICT.get(values['category'])
                
                paid_users = []
                received_users = []

                for userID, user_data in values['linkedUser'].items():
                    if user_data['paid'] > 0:
                        paid_users.append(userID)
                    if user_data['received'] > 0:
                        received_users.append(userID)

                # change user id to user name [paid]
                user_name = []
                for userID in paid_users:
                    try:
                        user_name.append((ID_operation.id_read(1, userID)[userID]["username"]))
                    except:
                        user_name.append("[Deleted Account]")
                paid_users = user_name
                # chante user id to user name [received]
                user_name = []
                for userID in received_users:
                    try:
                        user_name.append((ID_operation.id_read(1, userID)[userID]["username"]))
                    except:
                        user_name.append("[Deleted Account]")
                received_users = user_name
                

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


    def plot_daily_expense(self):

        # Get the dates
        start_day = self.startDate
        end_day = self.endDate
        days = [start_day + timedelta(days=i) for i in range((end_day - start_day).days + 1)]
        data_dict = {day: 0 for day in days}

        # Get the values
        transLInked = ID_operation.id_read(4, self.linkedTransaction)
        for key, values in transLInked.items():
            if values['debtSettlement'] is False:
                temp_date = datetime.strptime(values['transDateTime'], "%Y-%m-%d %H:%M").date()
                try:
                    data_dict[temp_date] += values['totalAmount']
                except:
                    data_dict[temp_date] = values['totalAmount']
        
        # Plot the data
        x = data_dict.keys()
        y = data_dict.values()

        plt.bar(x, y)
        # Format the x-axis as dates
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator())

        plt.ylim(bottom=0)
        # Add labels and title
        plt.xlabel('Date')
        plt.ylabel('Total Amount')
        plt.title(f'Daily Expense in <{self.name}>', fontsize=14)

        # Display the graph
        plt.tight_layout()
        # save graph
        plot_data = io.BytesIO()
        plt.savefig(plot_data, format='png', bbox_inches='tight', transparent=True)
        plot_data.seek(0)
        plot_url = base64.b64encode(plot_data.getvalue()).decode()

        plt.close()

        return plot_url
    
    def plot_spending(self):
        """
        plot the spending of a trip in a pie chart (by category)
        debt settlement is not included
        """
        # get the linked transaction 
        linkedTransactionIDs = self.linkedTransaction
        linkedTransactions = ID_operation.id_read(4, linkedTransactionIDs)
        
        totalAmounts = []
        categoriesInt = []

        for id, data in linkedTransactions.items():
            if data['category'] not in categoriesInt:
                totalAmounts.append(data['totalAmount'])
                categoriesInt.append(data['category'])
            else:
                totalAmounts[categoriesInt.index(data['category'])] += data['totalAmount']

        # convert the category int to string
        CATEGORY_DICT = transaction.Transaction.CATEGORY_DICT
        categories = [CATEGORY_DICT.get(category) for category in categoriesInt]               

        plt.clf()  # Clear the current figure

        # Plotting the total amounts for each category
        fig, ax = plt.subplots(facecolor='none')
        ax.pie(totalAmounts, labels=categories, autopct='%1.1f%%', startangle=90, counterclock=False, textprops={'fontsize': 12}, colors=['cornflowerblue', 'cornsilk', 'lightsalmon', 'yellowgreen', 'lightgrey', 'plum'])
        
        plt.title(f'Expense for each category in <{self.name}>', fontsize=13)

        # Convert plot to image
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()

        # Close the plot
        plt.close()

        return plot_url

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
    test = Trip.create("100000","trip A", "2023-11-15", "2023-11-16" ,'GG', "HONG KONG", accessBy=['100001', '100002'])
    t_e = event.Event.create(["100001"], test.ID, "test", "des", "2023-11-25 12:00", "2023-11-25 12:00")
    transaction.Transaction.create({'100000':{'paid': 50, 'received': 25},'100001': {'paid': 25, 'received': 25}, '100002': {'paid': 0, 'received': 25}}, test.ID, "Test - Transaction", 1, "2023-11-15 00:00", "HKD", linkedEvent= t_e.ID)
    transaction.Transaction.create({'100000':{'paid': 50, 'received': 25},'100001': {'paid': 25, 'received': 25}, '100002': {'paid': 0, 'received': 25}}, test.ID, "Test - Transaction", 1, "2023-11-15 00:00", "HKD")

    # test = Trip.read('200000')
    # print(test)
    input()
    Trip.delete(test.ID)
    
if __name__ == '__main__':
    main()
