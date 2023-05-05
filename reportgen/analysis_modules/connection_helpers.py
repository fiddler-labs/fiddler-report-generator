import requests


class FrontEndCall:

    def __init__(self, api, endpoint):
        self.api = api
        self.url = f'{api.v1.connection.url}/v2/{endpoint}'

    def post(self, request):
        return requests.post(self.url, headers=self.api.v1.connection.auth_header, json=request).json()
