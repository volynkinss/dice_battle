import requests

USER_ADDRESS = "EQDuVM_M2Cqx0bco0cYlNeW_aa2mvtvLy-UuPJQkzZEVmrmN"
OWNER_ADDRESS = "0%3A69171dc426e7761ceca7eca4f3f9228ec1dc268a4199613f058e334408eab215"


class NFTWorker:
    BASE_URL = "https://tonapi.io/v2"

    def get_nfts(self, user_address):
        url = f"{self.BASE_URL}/accounts/{OWNER_ADDRESS}/nfts?collection={user_address}&limit=1000&offset=0&indirect_ownership=false"

        try:
            response = requests.get(url)
            data = response.json()["nft_items"]
            data_nfts = {}
            for i in range(len(data)):
                metadata = data[i]["metadata"]
                i += 1
                id = i
                name, description, image_url = (
                    metadata["name"],
                    metadata["description"],
                    metadata["image"],
                )
                data_nfts[id] = (name, description, image_url)
            return data_nfts
        except:
            print("Unsupported adress")
