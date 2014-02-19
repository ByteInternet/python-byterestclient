import os
from unittest import TestCase
from requests import HTTPError
import mock
from apiclient import APIClient


API_CLIENT_TOKEN = 'default_api_key'
API_CLIENT_ENDPOINT = 'http://example.com/api'


@mock.patch.dict('os.environ', {'API_CLIENT_TOKEN': API_CLIENT_TOKEN, 'API_CLIENT_ENDPOINT': API_CLIENT_ENDPOINT})
class TestAPIClient(TestCase):

    def _set_up_patch(self, topatch, themock=None):
        if themock is None:
            themock = mock.Mock()

        patcher = mock.patch(topatch, themock)
        self.addCleanup(patcher.stop)
        return patcher.start()

    def setUp(self):
        self.mock_get = self._set_up_patch('requests.get')
        self.mock_post = self._set_up_patch('requests.post')

        self.mock_response = mock.MagicMock()
        self.mock_response.status_code = 200
        self.mock_response.content.return_value = '{"b": "a"}'
        self.mock_response.json.return_value = {"b": "a"}

        self.mock_get.return_value = self.mock_response
        self.mock_post.return_value = self.mock_response

        self.token = os.environ.get('API_CLIENT_TOKEN')
        self.endpoint = os.environ.get('API_CLIENT_ENDPOINT')

    def test_apiclient_stores_api_key(self):
        client = APIClient(token="mykey")
        self.assertEqual(client.key, "mykey")

    def test_apiclient_defaults_to_key_from_environment_if_not_provider(self):
        client = APIClient()
        self.assertEqual(client.key, "default_api_key")

    def test_api_client_stores_api_endoint(self):
        client = APIClient(endpoint="myurl")
        self.assertEqual(client.endpoint, "myurl")

    def test_apiclient_defaults_to_endpoint_from_environment_if_not_provided(self):
        client = APIClient()
        self.assertEqual(client.endpoint, API_CLIENT_ENDPOINT)

    def test_apiclient_has_default_headers(self):
        client = APIClient()
        self.assertEqual(client.headers, {
            'Authorization': 'Token %s' % client.key,
        })

    def test_apiclient_request_makes_correct_call_using_requests(self):
        client = APIClient()
        client.request('get', '/', data={"a": "b"})
        self.mock_get.assert_called_once_with(API_CLIENT_ENDPOINT + "/", data={"a": "b"}, headers=client.headers)

    def test_apiclient_request_honours_given_method_name(self):
        client = APIClient()
        client.request('post', '/', data={"a": "b"})
        self.assertEqual(self.mock_get.call_count, 0)  # get is not called, because post is requested
        self.mock_post.assert_called_once_with(API_CLIENT_ENDPOINT + "/", data={"a": "b"}, headers=client.headers)

    def test_apiclient_appends_path_to_url(self):
        client = APIClient()
        client.request('get', '/varnish/v2/config/henkslaaf.nl')
        self.mock_get.assert_called_once_with(API_CLIENT_ENDPOINT + "/varnish/v2/config/henkslaaf.nl", data={}, headers=client.headers)

    def test_apiclient_request_returns_decoded_json_response(self):
        client = APIClient()
        ret = client.request('get', '/get/', data={"a": "b"})
        self.assertEqual(ret, {"b": "a"})

    def test_apiclient_raises_RuntimeError_when_response_is_not_200_or_201(self):
        self.mock_response.raise_for_status.side_effect = HTTPError
        client = APIClient()
        with self.assertRaises(HTTPError):
            client.request('get', '/get/', data={"a": "b"})

    def test_apiclient_has_get_shortcut(self):
        client = APIClient()
        client.request = mock.MagicMock(return_value=42)

        ret = client.get("/get/")

        client.request.assert_called_once_with('get', "/get/")
        self.assertEqual(ret, 42)  # returned client.request return value

    def test_apiclient_has_post_shortcut(self):
        client = APIClient()
        client.request = mock.MagicMock(return_value=42)

        ret = client.post("/post/", data={"a": 1, "b": 2})

        client.request.assert_called_once_with('post', "/post/", data={"a": 1, "b": 2})
        self.assertEqual(ret, 42)  # returned client.request return value

    def test_apiclient_has_put_shortcut(self):
        client = APIClient()
        client.request = mock.MagicMock(return_value=42)

        ret = client.put("/put/")

        client.request.assert_called_once_with('put', "/put/")
        self.assertEqual(ret, 42)  # returned client.request return value

    def test_apiclient_has_patch_shortcut(self):
        client = APIClient()
        client.request = mock.MagicMock(return_value=42)

        ret = client.patch("/patch/")

        client.request.assert_called_once_with('patch', "/patch/")
        self.assertEqual(ret, 42)  # returned client.request return value