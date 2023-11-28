"""
The models of the application, add your class here
"""
try:
    from app import bcrypt
except:
    import bcrypt

import flask_login
import json




USER_CREDENTIALS = './app/data/users.json'

class User(flask_login.UserMixin):

    FILE_PATH = "app/data/users.json"

    def __init__(self, user_id, username, email_address, password):
        # password will be hashed
        self.id = user_id
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
    def read(cls, userID: str):
        try:
            with open(User.FILE_PATH, "r") as file:
                try:
                    existing_data = json.load(file)
                except:
                    existing_data = {}
        except FileNotFoundError:
            print(f"File {User.FILE_PATH} not found")
        
        try:
            current_net = existing_data[userID]
        except:
            print(f"ERROR: user.read - User {userID} not found")
            return -1
    
        return cls(**current_net)


def main():
    test = User.read("100000")
    print(test.password)

if __name__ == '__main__':
    main()