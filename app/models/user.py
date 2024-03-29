try:
    from app import bcrypt
    from .toolbox import ID_operation
    from . import trip, transaction, event, trip_UserNet
except:
    import bcrypt
    from toolbox import ID_operation
    import trip, transaction, event, trip_UserNet

import flask_login
import json
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import io
import base64




USER_CREDENTIALS = './app/data/users.json'

class User(flask_login.UserMixin):

    FILE_PATH = "app/data/users.json"

    def __init__(self, userID, username, email_address, password, friends=[], Deleted=False):
        # password will be hashed
        self.id = userID
        self.username = username
        self.email = email_address
        self.password_hash = password
        self.friends = friends
        self.Deleted = Deleted
        
    # can abandon
    @property 
    def password(self):
        return self.password_hash
    
    @password.setter
    def password(self, password_unhashed):
        return bcrypt.generate_password_hash(password_unhashed).decode('utf-8')
    
    def password_check(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)


    def add_friend(self, friendID: str) -> bool:
        if self.id == friendID:
            return False
        if friendID not in User.read_all().keys():
            return False
        temp_set = set(self.friends)
        temp_set.add(friendID)
        self.friends = list(temp_set)
        self.write()

        friend = User.read(friendID)
        temp_set = set(friend.friends)
        temp_set.add(self.id)
        friend.friends = list(temp_set)
        friend.write()
        return True


    def remove_friend(self, friendID: str) -> bool:
        temp_set = set(self.friends)
        temp_set.discard(friendID)
        self.friends = list(temp_set)
        self.write()

        friend = User.read(friendID)
        temp_set = set(friend.friends)
        temp_set.discard(self.id)
        friend.friends = list(temp_set)
        friend.write()
        return True


    @classmethod
    def create(cls, username, email_address, password) -> 'User':
        # userID = 
        userID = ID_operation.id_gen(1)

        temp = cls(userID, username, email_address, password)
        temp.write()
        return temp


    @classmethod
    # given a userID, return a User object
    def read(cls, userID: str):
        try:
            with open(User.FILE_PATH, "r") as file:
                try:
                    existing_data = json.load(file)
                except:
                    existing_data = {}
        except FileNotFoundError:
            print(f"File {User.FILE_PATH} not found")
            return -1
        
        try:
            current_net = existing_data[userID]
        except:
            print(f"ERROR: user.read - User {userID} not found")
            return -1
    
        return cls(**current_net)
    
    @classmethod
    # return a dict of all the users read from the JSON file
    def read_all(cls):
        try:
            with open(User.FILE_PATH, "r") as file:
                try:
                    existing_data = json.load(file)
                except:
                    existing_data = {}
        except FileNotFoundError:
            print(f"File {User.FILE_PATH} not found")
            return -1
        return existing_data

    @classmethod
    def userNamesToUserIDs(cls, userNames: list) -> list:
        '''
        convert a list of userNames to a list of userIDs
        '''
        userIDs = []
        user_data = cls.read_all()
        for user in userNames:
            for key, value in user_data.items():
                if value["username"] == user:
                    userIDs.append(key)
                    break
        return userIDs

    @classmethod
    def userIDsToUserNames(cls, userIDs: list) -> list:
        '''    
        convert a list of userIDs to a list of userNames.
        delected accounts will be ignored
        '''
        userNames = [] # list of linked trip user name
        for user in userIDs:
            name = cls.read(user).username
            if name != "<Deleted Account>":
                userNames.append(cls.read(user).username)
        return userNames

    def write(self) -> None:
        try:
            with open(User.FILE_PATH, "r") as file:
                try:
                    existing_data = json.load(file)

                except:
                    existing_data = {}

        except FileNotFoundError:
            existing_data = {}
        
        existing_data.update(self.to_dict())

        with open(User.FILE_PATH, "w") as file:
            json.dump(existing_data, file, indent=4)
            file.write('\n')

    def delete(userID: str) -> bool:
        """
        delete a user from the JSON file
        clear all the data of the user except the userID and mark it as deleted
        return True if success, False if failed
        """
        # del existing_data[userID] - pure delete, dont use this
        try:
            try:
                with open(User.FILE_PATH, "r") as file:
                    try:
                        existing_data = json.load(file)
                    except:
                        existing_data = {}
            except FileNotFoundError:
                existing_data = {}

            existing_data[userID]["Deleted"] = True
            wipe_list = ["username", "email_address", "password"]
            for wipe in wipe_list:
                existing_data[userID][wipe] = "<Deleted Account>"

            with open(User.FILE_PATH, "w") as file:
                json.dump(existing_data, file, indent=4)
                file.write('\n')

            return True
        except:
            return False
            


    def to_dict(self) -> dict:
        data = {f"{self.id}": {
            "userID": f"{self.id}",
            "username": f"{self.username}",
            "email_address": f"{self.email}",
            "password": f"{self.password}",
            "Deleted": self.Deleted,
            "friends": self.friends
        }}
        return data
    

    def __str__(self) -> str:
        return (f"userID: {self.id}, username: {self.username}, email: {self.email}, password: {self.password}, friends: {self.friends}, Deleted: {self.Deleted}")


    def get_trips(self) -> dict:
        """
        get all trips the users have access to
        """
        all_trip = trip.Trip.read_all()
        user_trips = {}
        for key, value in all_trip.items():
            if self.id in [UID for UID in value["accessBy"]]:
                user_trips[key] = value
        
        return user_trips


    def get_name_by_id(userID: str)-> str:
        temp = User.read(userID)
        return temp.username


    def user_debt(self, tripID):
        """
        Make a graph on the user debt for one trip
        """
        # Get data and clean up
        temp_dict = trip_UserNet.Trip_UserNet.get_related(tripID)
        x = []
        for id in list(temp_dict.keys()):
            x.append(User.get_name_by_id(id))
        y = list(temp_dict.values())

        colors = ['salmon' if val < 0 else 'palegreen' for val in y]

        fig, ax = plt.subplots(figsize=(10, 6))  # Set plot size using figsize

        ax.barh(x, y, color=colors)

        ax.axvline(0, color='blue', linestyle='--')
        ax.axis('off')

        for i, val in enumerate(x):
            ax.annotate(str(val), (0, val), ha='right', va='bottom', fontsize=20)

        for i, val in enumerate(y):
            ax.annotate(str(val), (val, i), ha='left', va='top', fontsize=20)

        ax.set_title("User debt", fontdict={'fontsize': 20}) 

        plot_data = io.BytesIO()
        plt.savefig(plot_data, format='png', bbox_inches='tight', transparent=True)
        plot_data.seek(0)
        plot_url = base64.b64encode(plot_data.getvalue()).decode()

        plt.close()

        return plot_url
            
def main():
    # test = User.create("test", "1234@mail.com", "1234")
    elsa = User.read("100005")
    print(elsa.add_friend("100005"))
    # elsa.add_friend("100001")
    # elsa.add_friend("100002")
    # elsa.add_friend("100003")
    # elsa.add_friend("100004")
    # elsa.add_friend("100001")
    
    
    


if __name__ == '__main__':
    main()