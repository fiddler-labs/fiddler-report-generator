import requests


class FrontEndCall:

    def __init__(self, api, endpoint):
        self.api = api
        self.url = f'{api.url}/{endpoint}'

    def post(self, request):
        return requests.post(self.url, headers=self.api.request_headers, json=request).json()
