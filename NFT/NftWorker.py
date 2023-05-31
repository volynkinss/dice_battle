import requests
import json


user_address = 'EQDuVM_M2Cqx0bco0cYlNeW_aa2mvtvLy-UuPJQkzZEVmrmN'
url = f'https://tonapi.io/v2/nfts/collections/{user_address}/items?limit=1000&offset=0'
owner_address = '0:89f356bd10b3c8609187c5abcd7bb1d5840c7f8a88e73debff8e64ffd8f12010'


response = requests.get(url, params=user_address)
print(response)
data = response.json()
data = data["nft_items"]


def get_data_nft(data, owner_address):
    for i in range(len(data)):
        if data[i]["owner"]["address"] == owner_address:
            print(data[i])
            name = data[i]['metadata']['name']
            description = data[i]['metadata']['description']
            image_url = data[i]['metadata']['image']
            return name, description, image_url
        


