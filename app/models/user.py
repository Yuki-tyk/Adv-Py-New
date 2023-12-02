try:
    from app import bcrypt
    from .toolbox import ID_operation
except:
    import bcrypt
    from toolbox import ID_operation

import flask_login
import json




USER_CREDENTIALS = './app/data/users.json'

class User(flask_login.UserMixin):

    FILE_PATH = "app/data/users.json"

    def __init__(self, userID, username, email_address, password):
        # password will be hashed
        self.id = userID
        self.username = username
        self.email = email_address
        self.password_hash = password
        
    # can abandon
    @property 
    def password(self):
        return self.password_hash
    
    @password.setter
    def password(self, password_unhashed):
        return bcrypt.generate_password_hash(password_unhashed).decode('utf-8')
    
    def password_check(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

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
    # convert a list of userNames to a list of userIDs
    def userNamesToUserIDs(cls, userNames: list) -> list:
        userIDs = []
        user_data = cls.read_all()
        for user in userNames:
            for key, value in user_data.items():
                if value["username"] == user:
                    userIDs.append(key)
                    break
        return userIDs

    @classmethod
    # convert a list of userIDs to a list of userNames
    # delected accounts will be ignored
    def userIDsToUserNames(cls, userIDs: list) -> list:
        userNames = [] # list of linked trip user name
        for user in userIDs:
            try:
                userNames.append(cls.read(user).username)
            except:
                pass # do nothing if user not found [delected account]
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

    @classmethod
    # delete a user from the JSON file
    # clear all the data of the user except the userID and mark it as deleted
    # return True if success, False if failed
    # del existing_data[userID] - pure delete, dont use this
    def delete(userID: str) -> bool:
        try:
            try:
                with open(User.FILE_PATH, "r") as file:
                    try:
                        existing_data = json.load(file)
                    except:
                        existing_data = {}
            except FileNotFoundError:
                existing_data = {}

            existing_data[userID] = {"Deleted": True}

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
        }}
        return data
    

    def __str__(self) -> str:
        return (f"userID: {self.id}, username: {self.username}, email: {self.email}, password: {self.password}")


def main():
    test = User.create("test", "1234@mail.com", "1234")
    print(User.read("100000"))
    
    


if __name__ == '__main__':
    main()