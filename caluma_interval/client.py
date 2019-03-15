import json

import requests


class CalumaClient:
    def __init__(self, endpoint):
        self.endpoint = endpoint

    def execute(self, query, variables=None):
        return self._send(query, json.dumps(variables))

    def _send(self, query, variables):
        data = {"query": query, "variables": variables}
        headers = {"Accept": "application/json", "Content-Type": "application/json"}

        try:
            response = requests.post(self.endpoint, data, headers)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(e)
            raise e
