from models.trip import Trip
from models.event import Event
from models.transaction import Transaction
from models.trip_UserNet import Trip_UserNet

from models.toolbox import clean

from models.toolbox import ID_operation

def main():

    clean.clean()
    A_userID = '100005'
    

    input('Pause')
    # Create trip
    d_trip = {
            "ownerID": A_userID,
            "accessBy": ['100003', '100004'],
            "name": 'Business Trip in Las Vegas',
            "startDate": '2023-08-01',
            "endDate": '2023-08-03',
            "tripDescription": 'Doing Business in Las Vegas',
            "location": 'Las Vegas',
            }
    Trip.create(**d_trip)

    d_trip = {
            "ownerID": A_userID,
            "accessBy": ['100001', '100004'],
            "name": 'Site Seeing in Moscow',
            "startDate": '2023-11-24',
            "endDate": '2023-11-28',
            "tripDescription": 'Site seeing in Moscow',
            "location": 'Moscow',
            }
    Trip.create(**d_trip)

    d_trip = {
            "ownerID": A_userID,
            "accessBy": ['100001', '100002'],
            "name": 'Christmas trip to Tokyo',
            "startDate": '2023-12-25',
            "endDate": '2023-12-30',
            "tripDescription": 'Tokyo is not hot',
            "location": 'Tokyo',
            }
    Trip.create(**d_trip)

    # Create Event
    d_event = {
            "linkedUser": ['100005', '100003', '100004'],
            "linkedTrip": "200000",
            "name": "Business meeting at Casino",
            "description": 'Discuss about an investment',
            "startTime": '2023-08-01 12:00',
            "endTime": '2023-08-01 22:00',
            }
    Event.create(**d_event)
    
    d_event = {
            "linkedUser": ['100005', '100003', '100004'],
            "linkedTrip": "200000",
            "name": "High Roller Observation Wheel",
            "description": 'Visit the High Roller Observation Wheel',
            "startTime": '2023-08-02 12:00',
            "endTime": '2023-08-02 22:00',
            }
    Event.create(**d_event)

    d_event = {
            "linkedUser": ['100005', '100003', '100004'],
            "linkedTrip": "200000",
            "name": "Take a Helicopter Tour of the Grand Canyon",
            "description": 'Take a Helicopter Tour of the Grand Canyon',
            "startTime": '2023-08-03 12:00',
            "endTime": '2023-08-03 22:00',
            }
    Event.create(**d_event)



    # Create Event for Moscow
    d_event = {
            "linkedUser": ['100005', '100001', '100004'],
            "linkedTrip": "200001",
            "name": "Refined vodka experience",
            "description": 'Na zdorovye!',
            "startTime": '2023-11-24 12:00',
            "endTime": '2023-11-24 22:00',
            }
    Event.create(**d_event)
    
    d_event = {
            "linkedUser": ['100005', '100001', '100004'],
            "linkedTrip": "200001",
            "name": "St. Basil's Cathedral",
            "description": "Explore the magnificent St. Basil's Cathedral",
            "startTime": '2023-11-25 12:00',
            "endTime": '2023-11-25 22:00',
            }
    Event.create(**d_event)

    d_event = {
            "linkedUser": ['100005', '100001', '100004'],
            "linkedTrip": "200001",
            "name": "The State Tretyakov Gallery",
            "description": 'Discover the treasures of the State Tretyakov Gallery',
            "startTime": '2023-11-26 12:00',
            "endTime": '2023-11-26 22:00',
            }
    Event.create(**d_event)

    d_event = {
            "linkedUser": ['100005', '100001', '100004'],
            "linkedTrip": "200001",
            "name": "Gorky Park",
            "description": 'leisurely stroll through the beautiful and historic Gorky Park',
            "startTime": '2023-11-27 12:00',
            "endTime": '2023-11-27 22:00',
            }
    Event.create(**d_event)

    d_event = {
            "linkedUser": ['100005', '100001', '100004'],
            "linkedTrip": "200001",
            "name": "Bolshoi Theatre",
            "description": 'world-class ballet or opera performance',
            "startTime": '2023-11-28 12:00',
            "endTime": '2023-11-28 22:00',
            }
    Event.create(**d_event)


    d_event = {
            "linkedUser": ['100005', '100001', '100002'],
            "linkedTrip": "200002",
            "name": "Tokyo Disneyland",
            "description": 'Disneyland <3',
            "startTime": '2023-11-25 12:00',
            "endTime": '2023-11-26 22:00',
            }
    Event.create(**d_event)

    # Transaction
    d_transaction = {
            "linkedUser": {
                           '100005':{'paid': 200,'received': 100},
                           '100003':{'paid': 0,'received': 100},
                           '100004':{'paid': 100,'received': 100}
                           },
            "linkedTrip": "200000",
            "name": "Business Expense",
            "category": 6,
            "transDateTime": '2023-08-01 12:00',
            "currency": 'USD',
            "debtSettlement": False,
            "linkedEvent": '300000'
            }
    Transaction.create(**d_transaction)


    d_transaction = {
            "linkedUser": {
                           '100005':{'paid': 200,'received': 100},
                           '100003':{'paid': 0,'received': 100},
                           '100004':{'paid': 100,'received': 100}
                           },
            "linkedTrip": "200000",
            "name": "High Roller Observation Wheel",
            "category": 0,
            "transDateTime": '2023-08-02 12:00',
            "currency": 'USD',
            "debtSettlement": False,
            "linkedEvent": '300001'
            }
    Transaction.create(**d_transaction)

    d_transaction = {
            "linkedUser": {
                           '100005':{'paid': 200,'received': 100},
                           '100003':{'paid': 0,'received': 100},
                           '100004':{'paid': 100,'received': 100}
                           },
            "linkedTrip": "200000",
            "name": "Helicopter Tour",
            "category": 5,
            "transDateTime": '2023-08-01 12:00',
            "currency": 'USD',
            "debtSettlement": False,
            "linkedEvent": '300002'
            }
    Transaction.create(**d_transaction)

    d_transaction = {
            "linkedUser": {
                           '100005':{'paid': 200,'received': 100},
                           '100003':{'paid': 0,'received': 100},
                           '100004':{'paid': 100,'received': 100}
                           },
            "linkedTrip": "200000",
            "name": "Fancy Dinner",
            "category": 2,
            "transDateTime": '2023-08-01 12:00',
            "currency": 'USD',
            "debtSettlement": False,
            "linkedEvent": None
            }
    Transaction.create(**d_transaction)

if __name__ == '__main__':
    main()