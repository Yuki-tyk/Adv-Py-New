from datetime import datetime
import json
try:
    from .toolbox import ID_operation
    from . import trip_UserNet, trip
except:
    from toolbox import ID_operation
    import trip_UserNet, trip


class Transaction:
    """
    Transaction are under trips or events that describe the transaction user spent.
    """
    STR_FORMAT = "%Y-%m-%d %H:%M"
    FILE_PATH = "app/data/transactions.json"
    CATEGORY_DICT = {
        0: "Uncategorized",
        1: "Accommodation",
        2: "Food and Drinks",
        3: "Groceries",
        4: "Tickets",
        5: "Transportation",
        6: "Others"
    }

    def __init__(self, transactionID: str, linkedUser: dict, linkedTrip: str, linkedEvent: str, debtSettlement: bool, name: str, category: int, transDateTime: str, totalAmount: float, currency: str) -> None:
        # PK
        self.ID = transactionID
        # FK
        self.linkedUser = linkedUser
        self.linkedTrip = linkedTrip
        self.linkedEvent = linkedEvent
        # Atributes
        self.debtSettlement = debtSettlement # bool
        self.name = name
        self.category = category
        self.transDateTime = datetime.strptime(transDateTime, Transaction.STR_FORMAT)
        self.totalAmount = totalAmount
        self.currency = currency


    @classmethod
    def create(cls, linkedUser: dict, linkedTrip: str, name: str, category: int, transDateTime: str, currency: str, debtSettlement: bool = False, linkedEvent: str = None) -> "Transaction":
        # check if the linkedTrip is valid
        if ID_operation.id_read(2, linkedTrip) == -1:
            return -2 # ERROR: No such trip
        
        ### NOT WOKRING FOR NOW
        # # check if the linkedUser is valid
        # if ID_operation.id_read(1, linkedUser) == -1:
        #     return -1 # ERROR: No such user
        # print("Transaction.create - linkedUser: ", ID_operation.id_read(1, linkedUser))

        # create a Transaction
        transactionID = ID_operation.id_gen(4)

        # auto create a transaction_by user
        totalAmount = 0
        for key, spending in linkedUser.items():
            paid = spending['paid']
            totalAmount += paid
            received = spending['received']
            net = paid - received

            instance = trip_UserNet.Trip_UserNet.read(key, linkedTrip)
            instance.net += net
            instance.write()

        temp = cls(transactionID, linkedUser, linkedTrip, linkedEvent, debtSettlement, name, category, transDateTime, totalAmount, currency)
        temp.write()

        # auto link to the linked trip
        t_trip = trip.Trip(**(ID_operation.id_read(2, linkedTrip)[linkedTrip]))
        t_trip.linkedTransaction.append(temp.ID)
        t_trip.write()

        return temp
    
    
    def write(self) -> None:
        try:
            with open(Transaction.FILE_PATH, "r") as file:
                try:
                    existing_data = json.load(file)

                except:
                    existing_data = {}

        except FileNotFoundError:
            existing_data = {}
        
        existing_data.update(self.to_dict())

        with open(Transaction.FILE_PATH, "w") as file:
            json.dump(existing_data, file, indent=4)
            file.write("\n")

        return


    def __str__(self) -> str:
        return (f"\transactionID: {self.ID}," +
                f"\nlinkedUser: {self.linkedUser}, linkedTrp: {self.linkedTrip}, linkedEvent: {self.linkedEvent}," + 
                f"\ndebtSettlement: {self.debtSettlement}, name: {self.name}, category: {self.category}," +
                f"\ntransDateTime: {self.transDateTime}, totalAmount: {self.totalAmount}, currency: {self.currency}\n")


    def __repr__(self) -> str:
        return f"Event({self.ID}, {self.linkedUser}, {self.linkedTrip}, {self.linkedEvent}, {self.debtSettlement}, {self.name}, {self.category}, {self.transDateTime}, {self.totalAmount}, {self.currency})"


    def to_dict(self) -> dict:
        data = {f"{self.ID}":{
            "transactionID": self.ID,
            "linkedUser": self.linkedUser,
            "linkedTrip": self.linkedTrip,
            "linkedEvent": self.linkedEvent,
            "name": self.name,
            "debtSettlement": self.debtSettlement,
            "category": self.category,
            "transDateTime": self.transDateTime.strftime(self.STR_FORMAT),
            "totalAmount": self.totalAmount,
            "currency": self.currency,
            }
        }
        return data
    

    def to_json_str(self) -> str:
        json_str = json.dumps({self.ID: (self.to_dict())})
        return json_str
    
    def getCategoryInt(value):
        for key, val in Transaction.CATEGORY_DICT.items():
            if val == value:
                return key
        return 0


# Test
def main():
    test = Transaction.create({'100900':{'paid': 50, 'received': 25},'100001': {'paid': 25, 'received': 25}, '100002': {'paid': 0, 'received': 25}}, "200000", "Test - Transaction", 1, "2023-11-15 00:00:00", "HKD")
    print(test)
    # print(test.to_json_str())
    # test.write()
    
    
if __name__ == "__main__":
    main()