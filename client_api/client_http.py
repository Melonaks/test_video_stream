import requests


class HttpClient:
    def __init__(self, host):
        self.base_url = f"http://{host}/channel/"

    def get(self, endpoint, channel):
        url = f"{self.base_url}{channel}/recording/{endpoint}"
        response = requests.get(url)
        return response.json()

    def post(self, endpoint, channel, json=None):
        url = f"{self.base_url}{channel}/recording/{endpoint}"
        response = requests.post(url, json=json)
        return response.json()