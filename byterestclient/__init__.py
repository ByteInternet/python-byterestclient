"""
Speak to an API
"""
import json
import os
import requests
from urlparse import urlsplit, urlunsplit

HTTPError = requests.HTTPError  # introspection


class ByteRESTClient(object):

    def __init__(self, token=None, endpoint=None):
        try:
            self.key = token or os.environ['REST_CLIENT_TOKEN']
            self.endpoint = endpoint or os.environ['REST_CLIENT_ENDPOINT']
        except KeyError as e:
            raise RuntimeError('Environment variable %s is not properly configured for ByteRESTClient' % e.message)

        self.headers = {
            'Authorization': 'Token %s' % self.key,
            'Content-Type': 'application/json',
        }

    def request(self, method, path, data=None, *args, **kwargs):
        url = self.format_absolute_url(path)
        request_method = getattr(requests, method)
        response = request_method(url, data=json.dumps(data or {}), headers=self.headers, *args, **kwargs)

        response.raise_for_status()

        if response.status_code == 204:
            return None

        if hasattr(response.json, "__call__"):
            return response.json()
        else:
            return response.json

    def format_absolute_url(self, path):
        url = urlsplit(self.endpoint)
        total_path = '/'.join([p.lstrip('/') for p in [url.path, path]])
        clean_path = total_path.replace('//', '/')
        return urlunsplit([url.scheme, url.netloc, clean_path, url.query, url.fragment])

    def get(self, path, *args, **kwargs):
        return self.request("get", path, *args, **kwargs)

    def post(self, path, *args, **kwargs):
        return self.request("post", path, *args, **kwargs)

    def put(self, path, *args, **kwargs):
        return self.request("put", path, *args, **kwargs)

    def delete(self, path, *args, **kwargs):
        return self.request("delete", path, *args, **kwargs)

    def patch(self, path, *args, **kwargs):
        return self.request("patch", path, *args, **kwargs)
