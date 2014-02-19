"""
Speak to an API
"""
import os
import requests
from requests.structures import CaseInsensitiveDict


class APIClient(object):

    def __init__(self, token=None, endpoint=None):
        try:
            self.key = token or os.environ['API_CLIENT_TOKEN']
            self.endpoint = endpoint or os.environ['API_CLIENT_ENDPOINT']
        except KeyError as e:
            raise RuntimeError('Environment variable %s is not properly configured for APIClient' % e.message)

        self.headers = {'Authorization': 'Token %s' % self.key}

    def request(self, method='get', data={}, path=""):
        url = self.endpoint + path
        request_method = getattr(requests, method)
        response = request_method(url, data=data, headers=self.headers)

        response.raise_for_status()
        return response.json()

    def get(self, *args, **kwargs):
        return self.request(*args, method="get", **kwargs)

    def post(self, *args, **kwargs):
        return self.request(*args, method="post", **kwargs)

    def put(self, *args, **kwargs):
        return self.request(*args, method="put", **kwargs)

    def patch(self, *args, **kwargs):
        return self.request(*args, method="patch", **kwargs)