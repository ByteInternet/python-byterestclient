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

    def request(self, method, path, data={}):
        url = self.endpoint + path
        request_method = getattr(requests, method)
        response = request_method(url, data=data, headers=self.headers)

        response.raise_for_status()
        return response.json()

    def get(self, path, *args, **kwargs):
        return self.request("get", path, *args, **kwargs)

    def post(self, path, *args, **kwargs):
        return self.request("post", path, *args, **kwargs)

    def put(self, path, *args, **kwargs):
        return self.request("put", path, *args, **kwargs)

    def patch(self, path, *args, **kwargs):
        return self.request("patch", path, *args, **kwargs)

