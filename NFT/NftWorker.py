import requests
import json

USER_ADDRESS = "EQDuVM_M2Cqx0bco0cYlNeW_aa2mvtvLy-UuPJQkzZEVmrmN"
OWNER_ADDRESS = "0%3A89f356bd10b3c8609187c5abcd7bb1d5840c7f8a88e73debff8e64ffd8f12010"


class NFTWorker:
    BASE_URL = "https://tonapi.io/v2"

    def get_data(self, user_address):
        url = f"{self.BASE_URL}/accounts/{OWNER_ADDRESS}/nfts?collection={user_address}&limit=1000&offset=0&indirect_ownership=false"

        try:
            response = requests.get(url)
            data = response.json()["nft_items"]
            metadata = data[0]["metadata"]
            name, description, image_url = (
                metadata["name"],
                metadata["description"],
                metadata["image"],
            )
            return name, description, image_url
        except:
            print("Unsupported adress")
