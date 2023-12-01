import json


class Trip_UserNet():
    """
    Trip_UserNet store the totall net of debt or receivable of each user in one trip
    for every trip user is in, there is one Trip-User Net
    """
    FILE_PATH = "app/data/trip_UserNet.json"

    def __init__(self, pk: list | str, net: float) -> None:
        # PK
        self.pk = pk
        # Atributes
        self.net = net

    @classmethod
    def create(cls, userID: str, tripID: str):
        net = 0.0
        temp = cls([userID, tripID], net)
        temp.write()
        return temp
    
    
    @classmethod
    def read(cls, userID: str, tripID: str):
        try:
            with open(Trip_UserNet.FILE_PATH, "r") as file:
                try:
                    existing_data = json.load(file)

                except:
                    existing_data = {}

        except FileNotFoundError:
            print(f"File {Trip_UserNet.FILE_PATH} not found")
        
        current_net = existing_data[f"['{userID}', '{tripID}']"]['net']
    
        return cls([userID, tripID], current_net)
    

    def delete(userID: str, tripID: str) -> bool:
        try:
            try:
                with open(Trip_UserNet.FILE_PATH, "r") as file:
                    try:
                        existing_data = json.load(file)

                    except:
                        existing_data = {}

            except FileNotFoundError:
                existing_data = {}

            del existing_data[f"['{userID}', '{tripID}']"]
            
            with open(Trip_UserNet.FILE_PATH, "w") as file:
                json.dump(existing_data, file, indent=4)
                file.write('\n')
            return True
        except:
            return False

    def write(self) -> None:
        try:
            with open(Trip_UserNet.FILE_PATH, "r") as file:
                try:
                    existing_data = json.load(file)

                except:
                    existing_data = {}

        except FileNotFoundError:
            print(f"File {Trip_UserNet.FILE_PATH} not found")
            
        existing_data.update(self.to_dict())

        with open(Trip_UserNet.FILE_PATH, "w") as file:
            json.dump(existing_data, file, indent=4)
            file.write("\n")


    def to_dict(self) -> dict:
        data = {f"{self.pk}":{
                "net": self.net
            }
        }
        return data
    
    def __str__(self) -> str:
        return (f'pk: {self.pk}, net: {self.net}')
    

def main():
    # test = Trip_UserNet(["100000", "200000"], 50)
    # test.write()
    # t2 = Trip_UserNet.read("100000", "200000")
    # print(t2)

    testc = Trip_UserNet.create("100000", "200100")
    print(testc)
    input()
    Trip_UserNet.delete("100000", "200100")



if __name__ == "__main__":
    main()