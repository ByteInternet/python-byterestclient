import json
from unittest import TestCase
from requests import HTTPError
import mock
from byterestclient import ByteRESTClient


REST_CLIENT_TOKEN = 'default_api_key'
REST_CLIENT_ENDPOINT = 'http://example.com/api'


@mock.patch.dict('os.environ', {'REST_CLIENT_TOKEN': REST_CLIENT_TOKEN, 'REST_CLIENT_ENDPOINT': REST_CLIENT_ENDPOINT})
class TestByteRESTClient(TestCase):

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

    def test_restclient_stores_api_key(self):
        client = ByteRESTClient(token="mykey")
        self.assertEqual(client.key, "mykey")

    def test_restclient_defaults_to_key_from_environment_if_not_provider(self):
        client = ByteRESTClient()
        self.assertEqual(client.key, "default_api_key")

    def test_api_client_stores_api_endoint(self):
        client = ByteRESTClient(endpoint="myurl")
        self.assertEqual(client.endpoint, "myurl")

    def test_restclient_defaults_to_endpoint_from_environment_if_not_provided(self):
        client = ByteRESTClient()
        self.assertEqual(client.endpoint, REST_CLIENT_ENDPOINT)

    def test_restclient_has_default_headers(self):
        client = ByteRESTClient()
        self.assertEqual(client.headers, {
            'Authorization': 'Token %s' % client.key,
            'Content-Type': 'application/json'
        })

    def test_restclient_request_makes_correct_call_using_requests(self):
        client = ByteRESTClient()
        client.request('get', '/', data={"a": "b"})
        self.mock_get.assert_called_once_with(REST_CLIENT_ENDPOINT + "/", data=json.dumps({"a": "b"}), headers=client.headers)

    def test_restclient_request_honours_given_method_name(self):
        client = ByteRESTClient()
        client.request('post', '/', data={"a": "b"})
        self.assertEqual(self.mock_get.call_count, 0)  # get is not called, because post is requested
        self.mock_post.assert_called_once_with(REST_CLIENT_ENDPOINT + "/", data=json.dumps({"a": "b"}), headers=client.headers)

    def test_restclient_appends_path_to_url(self):
        client = ByteRESTClient()
        client.request('get', '/varnish/v2/config/henkslaaf.nl')
        self.mock_get.assert_called_once_with(REST_CLIENT_ENDPOINT + "/varnish/v2/config/henkslaaf.nl", data='{}', headers=client.headers)

    def test_restclient_request_returns_decoded_json_response(self):
        client = ByteRESTClient()
        ret = client.request('get', '/get/', data={"a": "b"})
        self.assertEqual(ret, {"b": "a"})

    def test_restclient_raises_RuntimeError_when_response_is_not_in_200_range(self):
        self.mock_response.raise_for_status.side_effect = HTTPError
        client = ByteRESTClient()
        with self.assertRaises(HTTPError):
            client.request('get', '/get/', data={"a": "b"})

    def test_restclient_returns_none_when_status_is_204(self):
        self.mock_response.status_code = 204
        client = ByteRESTClient()
        ret = client.request('get', '/get/', data={"a": "b"})
        self.assertIsNone(ret)

    def test_restclient_has_get_shortcut(self):
        client = ByteRESTClient()
        client.request = mock.MagicMock(return_value=42)

        ret = client.get("/get/")

        client.request.assert_called_once_with('get', "/get/")
        self.assertEqual(ret, 42)  # returned client.request return value

    def test_restclient_has_post_shortcut(self):
        client = ByteRESTClient()
        client.request = mock.MagicMock(return_value=42)

        ret = client.post("/post/", data={"a": 1, "b": 2})

        client.request.assert_called_once_with('post', "/post/", data={"a": 1, "b": 2})
        self.assertEqual(ret, 42)  # returned client.request return value

    def test_restclient_has_put_shortcut(self):
        client = ByteRESTClient()
        client.request = mock.MagicMock(return_value=42)

        ret = client.put("/put/")

        client.request.assert_called_once_with('put', "/put/")
        self.assertEqual(ret, 42)  # returned client.request return value

    def test_restclient_has_patch_shortcut(self):
        client = ByteRESTClient()
        client.request = mock.MagicMock(return_value=42)

        ret = client.patch("/patch/")

        client.request.assert_called_once_with('patch', "/patch/")
        self.assertEqual(ret, 42)  # returned client.request return value

    def test_restclient_has_delete_shortcut(self):
        client = ByteRESTClient()
        client.request = mock.MagicMock(return_value=42)

        ret = client.delete("/delete/")

        client.request.assert_called_once_with('delete', "/delete/")
        self.assertEqual(ret, 42)  # returned client.request return value

    def test_restclient_corrects_double_slashes_in_urls(self):
        client = ByteRESTClient(endpoint="http://henk.nl/api/")
        client.headers = {}
        mock_get = self._set_up_patch('requests.get')

        client.get("/hypernode/")

        mock_get.assert_called_once_with("http://henk.nl/api/hypernode/", data='{}', headers={})

    def test_restclient_corrects_missing_slashes_in_urls(self):
        client = ByteRESTClient(endpoint="http://henk.nl/api")
        client.headers = {}
        mock_get = self._set_up_patch('requests.get')

        client.get("hypernode/")

        mock_get.assert_called_once_with("http://henk.nl/api/hypernode/", data='{}', headers={})

    def test_restclient_passes_extra_parameters_to_requests(self):
        client = ByteRESTClient(endpoint='http://henk.nl/api')
        client.headers = {}
        mock_get = self._set_up_patch('requests.get')

        client.get('hypernode', params={"q": "mynode"})

        mock_get.assert_called_once_with("http://henk.nl/api/hypernode", headers={}, params={"q": "mynode"}, data='{}')

    def test_that_get_absolute_url_concatenates_a_path_to_the_endpoint(self):
        client = ByteRESTClient(endpoint="http://henk.nl/api/")
        absolute_url = client.get_absolute_url("foo/bar")
        self.assertEqual(absolute_url, "http://henk.nl/api/foo/bar")

    def test_that_get_absolute_url_adds_a_slash_between_endpoint_and_path(self):
        client = ByteRESTClient(endpoint="http://henk.nl/api")
        absolute_url = client.get_absolute_url("foo/bar")
        self.assertEqual(absolute_url, "http://henk.nl/api/foo/bar")

    def test_that_get_absolute_url_removes_double_slashes_between_endpoint_and_path(self):
        client = ByteRESTClient(endpoint="http://henk.nl/api/")
        absolute_url = client.get_absolute_url("/foo/bar")
        self.assertEqual(absolute_url, "http://henk.nl/api/foo/bar")

    def test_that_get_absolute_url_accepts_empty_paths(self):
        client = ByteRESTClient(endpoint="http://henk.nl/api/")
        absolute_url = client.get_absolute_url("")
        self.assertEqual(absolute_url, "http://henk.nl/api/")
