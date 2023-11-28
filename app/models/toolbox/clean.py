# delete all data in json files

def clean():

    # TYPES = {1: 'users', 2: 'trips', 3: 'events', 4: 'transactions', 5: 'trip_UserNet'}
    TYPES = {2: 'trips', 3: 'events', 4: 'transactions', 5: 'trip_UserNet'}

    
    # Check data
    for keys, value in TYPES.items():
        with open(f'app/data/{value}.json', 'w') as file:
            file.write('')

if __name__ =='__main__':
    clean()