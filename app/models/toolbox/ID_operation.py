import json


def id_gen(category : int) -> str:
    """
    generate a id for the given category
    parameter - category: {1: 'User', 2: 'Trip', 3: 'Event', 4: 'Transaction'}
    return - id: str
    """
    TYPES = {1: 'users', 2: 'trips', 3: 'events', 4: 'transactions'}

    # Check data
    try:
        with open(f'app/data/{TYPES[category]}.json', 'r') as file:
            try:
                data = json.load(file)
                id_list = sorted(list(data.keys()))
                id = int(id_list[-1]) + 1
                
            except json.JSONDecodeError:
                id = str(category) + '00000'

            except IndexError:
                new_id = str(category) + '00000'
                json.dump({}, file)
                return new_id
    except:
        print("ERROR : id_gen - No such file, wrong category")
        return
        
    return str(id)

def id_read(category : int, ID: str | list) -> dict:
    """
    generate a dict with the content of all the existing IDs given within one data type
    [MUST BE SAME DATA TYPE]
    parameter - category: {1: 'User', 2: 'Trip', 3: 'Event', 4: 'Transaction'}
    parameter - ID: str | list of str (IDs from the same data type)
    return - ID_dict: dict 
    generate a dict with the content of all the existing IDs given within one data type
    [MUST BE SAME DATA TYPE]
    parameter - category: {1: 'User', 2: 'Trip', 3: 'Event', 4: 'Transaction'}
    parameter - ID: str | list of str (IDs from the same data type)
    return - ID_dict: dict 
    """
    TYPES = {1: 'users', 2: 'trips', 3: 'events', 4: 'transactions'}

    # process input
    if type(ID) is not list:
        ID = [ID]
    
    # open file
    with open(f'app/data/{TYPES[category]}.json', 'r') as file:
        try:
            data = json.load(file)
            ID_dict = {}

            for i in ID:
                try:
                    ID_dict[i] = data[i]
                except:
                    ID_dict[i] = f'ERROR: id_read - No such ID'
                    return -1
        except:
            print("ERROR: id_read - No such file, wrong category. Category inputted: %d" % category)
            return

    return ID_dict
    

'''
import app.models.trip as trip
import app.models.user as user
import app.models.event as event
import app.models.transaction as transaction

def dictToObj(category : int, input_dict : dict) -> list:
    """
    convert a dict to a (list of) instance for the given type
    can use with the return value of id_read()
    parameter - category: {1: 'User', 2: 'Trip', 3: 'Event', 4: 'Transaction'}
    parameter - dict: dict (with the same data type)
    reutrn - obj_list: list of instance
    """
    TYPES = {1: 'user', 2: 'trip', 3: 'event', 4: 'transaction'}
    class_name = TYPES.get(category)

    if class_name:
        class_obj = globals().get(class_name)
        if class_obj:
            if isinstance(input_dict, dict):
                obj_list = []
                for key, obj_details in input_dict.items():
                    obj = class_obj(**obj_details)
                    obj_list.append(obj)

                return obj_list
'''

# Test id_gen() & id_read()
def main():
    # test id_gen()
    print('\nTest id_gen')
    #print(id_gen(1))
    #print(id_gen(2))
    #print(id_gen(3))
    print(id_gen(4))
    #print(id_gen(5))

    # test id_read()
    print('\nTest id_read')
    print("id_read(1, ['100000']) ", id_read(1, ['100000']))
    print("id_read(2, '200000') ", id_read(2, '200000'))

    print(id_read(2, '200004'))
    #id_read(3, '300000')
    #id_read(4, ['400000', '400001', '400002'])

    # test dictToObj
    #print(dictToObj(3, id_read(3, 300000)))

if __name__ == '__main__':
    main()