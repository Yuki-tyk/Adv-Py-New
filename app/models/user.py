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
        try:
            try:
                with open(User.FILE_PATH, "r") as file:
                    try:
                        existing_data = json.load(file)

                    except:
                        existing_data = {}

            except FileNotFoundError:
                existing_data = {}

            # pure delete, dont use this
            # del existing_data[userID]

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
    
    


if __name__ == '__main__':
    main()