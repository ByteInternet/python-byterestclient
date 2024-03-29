import json
from unittest import TestCase
from requests import HTTPError, Response
import mock
from byterestclient import ByteRESTClient


REST_CLIENT_TOKEN = 'default_api_key'
REST_CLIENT_ENDPOINT = 'http://example.com/api'


@mock.patch.dict('os.environ', {'REST_CLIENT_TOKEN': REST_CLIENT_TOKEN, 'REST_CLIENT_ENDPOINT': REST_CLIENT_ENDPOINT})
class TestByteRESTClient(TestCase):

    def _set_up_patch(self, to_patch, the_mock=None, **kwargs):
        if the_mock is None:
            the_mock = mock.Mock()

        patcher = mock.patch(to_patch, the_mock, **kwargs)
        self.addCleanup(patcher.stop)
        return patcher.start()

    def setUp(self):
        self.mock_get = self._set_up_patch('requests.get')
        self.mock_post = self._set_up_patch('requests.post')

        self.mock_get_fqdn = self._set_up_patch('socket.getfqdn')
        self.mock_get_fqdn.return_value = 'myserver1.c6.internal'

        self.mock_response = Response()
        self.mock_response.encoding = "utf8"
        self.mock_response.status_code = 200
        self.mock_response._content = '{"b": "a"}'.encode("utf-8")

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
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'myserver1.c6.internal:byterestclient',
        })

    def test_restclient_has_extra_headers(self):
        client = ByteRESTClient(headers={'test': 'test', 'test1': 'test1'})
        self.assertEqual(client.headers, {
            'Authorization': 'Token %s' % client.key,
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'myserver1.c6.internal:byterestclient',
            'test': 'test', 'test1': 'test1',
        })

    def test_restclient_accepts_identifier_and_adds_it_to_useragent_header(self):
        client = ByteRESTClient(identifier='monkey')
        self.assertEqual(client.headers, {
            'Authorization': 'Token %s' % client.key,
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'myserver1.c6.internal:monkey',
        })

    def test_restclient_request_makes_correct_call_using_requests(self):
        client = ByteRESTClient()
        client.request('get', '/', data={"a": "b"})
        self.mock_get.assert_called_once_with(
            REST_CLIENT_ENDPOINT + "/",
            data=json.dumps({"a": "b"}),
            headers=client.headers,
            allow_redirects=False
        )

    def test_restclient_request_honours_given_method_name(self):
        client = ByteRESTClient()
        client.request('post', '/', data={"a": "b"})
        self.assertEqual(self.mock_get.call_count, 0)  # get is not called, because post is requested
        self.mock_post.assert_called_once_with(
            REST_CLIENT_ENDPOINT + "/",
            data=json.dumps({"a": "b"}),
            headers=client.headers,
            allow_redirects=False
        )

    def test_restclient_appends_path_to_url(self):
        client = ByteRESTClient()
        client.request('get', '/varnish/v2/config/henkslaaf.nl')
        self.mock_get.assert_called_once_with(
            REST_CLIENT_ENDPOINT + "/varnish/v2/config/henkslaaf.nl",
            data='{}',
            headers=client.headers,
            allow_redirects=False
        )

    def test_restclient_request_returns_response_object_if_return_response_object_kwarg_is_true(self):
        client = ByteRESTClient()
        ret = client.request('get', '/varnish/v2/config/henkslaaf.nl', return_response_object=True)
        self.assertEqual(ret, self.mock_get.return_value)

    def test_restclient_request_does_not_call_request_with_response_object_kwarg(self):
        client = ByteRESTClient()
        client.request('get', '/varnish/v2/config/henkslaaf.nl', return_response_object=True)

        args, kwargs = self.mock_get.call_args
        self.assertNotIn('return_response_object', kwargs.keys())

    def test_restclient_request_does_not_call_raise_for_status_if_return_response_object_kwarg_is_true(self):
        client = ByteRESTClient()
        client.request('get', '/varnish/v2/config/henkslaaf.nl', return_response_object=True)
        self.mock_get.raise_for_status.assert_not_called()

    def test_restclient_request_does_not_call_raise_for_status_if_return_response_object_kwarg_is_false(self):
        mock_response = mock.Mock(status_code=200)
        self.mock_get.return_value = mock_response

        client = ByteRESTClient()
        client.request('get', '/varnish/v2/config/henkslaaf.nl', return_response_object=False)

        mock_response.raise_for_status.assert_called_once()

    def test_restclient_request_does_not_call_raise_for_status_if_return_response_object_kwarg_is_absent(self):
        mock_response = mock.Mock(status_code=200)
        self.mock_get.return_value = mock_response

        client = ByteRESTClient()
        client.request('get', '/varnish/v2/config/henkslaaf.nl')

        mock_response.raise_for_status.assert_called_once()

    def test_restclient_request_returns_decoded_json_response(self):
        client = ByteRESTClient()
        ret = client.request('get', '/get/', data={"a": "b"})
        self.assertEqual(ret, {"b": "a"})

    def test_restclient_raises_HTTPError_when_request_is_not_successful(self):
        self.mock_response.status_code = 404
        client = ByteRESTClient()
        with self.assertRaises(HTTPError):
            client.request('get', '/get/', data={"a": "b"})

    def test_restclient_raises_HTTPError_when_request_is_redirect(self):
        self.mock_response.status_code = 302
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
        client.get("/hypernode/")

        self.mock_get.assert_called_once_with(
            "http://henk.nl/api/hypernode/",
            data='{}',
            headers={},
            allow_redirects=False
        )

    def test_restclient_corrects_missing_slashes_in_urls(self):
        client = ByteRESTClient(endpoint="http://henk.nl/api")
        client.headers = {}
        client.get("hypernode/")

        self.mock_get.assert_called_once_with(
            "http://henk.nl/api/hypernode/",
            data='{}',
            headers={},
            allow_redirects=False
        )

    def test_restclient_passes_extra_parameters_to_requests(self):
        client = ByteRESTClient(endpoint='http://henk.nl/api')
        client.headers = {}
        client.get('hypernode', params={"q": "mynode"})

        self.mock_get.assert_called_once_with(
            "http://henk.nl/api/hypernode",
            headers={},
            params={"q": "mynode"},
            data='{}',
            allow_redirects=False
        )

    def test_that_format_absolute_url_concatenates_a_path_to_the_endpoint(self):
        client = ByteRESTClient(endpoint="http://henk.nl/api/")
        absolute_url = client.format_absolute_url("foo/bar")
        self.assertEqual(absolute_url, "http://henk.nl/api/foo/bar")

    def test_that_format_absolute_url_adds_a_slash_between_endpoint_and_path(self):
        client = ByteRESTClient(endpoint="http://henk.nl/api")
        absolute_url = client.format_absolute_url("foo/bar")
        self.assertEqual(absolute_url, "http://henk.nl/api/foo/bar")

    def test_that_format_absolute_url_removes_double_slashes_between_endpoint_and_path(self):
        client = ByteRESTClient(endpoint="http://henk.nl/api/")
        absolute_url = client.format_absolute_url("/foo/bar")
        self.assertEqual(absolute_url, "http://henk.nl/api/foo/bar")

    def test_that_format_absolute_url_corrects_double_slashes_in_path(self):
        client = ByteRESTClient(endpoint="http://henk.nl/api/")
        absolute_url = client.format_absolute_url("/web1.c79//ips")
        self.assertEqual(absolute_url, "http://henk.nl/api/web1.c79/ips")

    def test_that_format_absolute_url_accepts_empty_paths(self):
        client = ByteRESTClient(endpoint="http://henk.nl/api/")
        absolute_url = client.format_absolute_url("")
        self.assertEqual(absolute_url, "http://henk.nl/api/")

    def test_that_format_absolute_url_works_correctly_if_path_has_query_params_and_fragments(self):
        client = ByteRESTClient(endpoint="http://henk:pass@aap.nl:8080/mies/")
        absolute_url = client.format_absolute_url("/henk;zus?aap=noot#noot")
        self.assertEqual(absolute_url, "http://henk:pass@aap.nl:8080/mies/henk;zus?aap=noot#noot")

    def test_handles_200_response_with_empty_body(self):
        self.mock_response._content = ''
        client = ByteRESTClient()

        response = client.get('http://henk.nl')

        self.assertEqual(response.status_code, 200)

    def test_handles_200_response_without_body(self):
        self.mock_response._content = None
        client = ByteRESTClient()

        response = client.get('http://henk.nl')

        self.assertEqual(response.status_code, 200)

    def test_restclient_request_makes_correct_call_using_preprocess_data(self):
        self.preprocess_data = self._set_up_patch('byterestclient.ByteRESTClient.preprocess_data')

        client = ByteRESTClient()
        client.request('get', '/', data={"a": "b"})
        self.mock_get.assert_called_once_with(
            REST_CLIENT_ENDPOINT + "/",
            data=self.preprocess_data.return_value,
            headers=client.headers,
            allow_redirects=False
        )

    def test_calls_preprocess_data_correctly(self):
        self.preprocess_data = self._set_up_patch('byterestclient.ByteRESTClient.preprocess_data')

        client = ByteRESTClient()
        client.request('get', '/', data={"a": "b"})
        self.preprocess_data.assert_called_once_with({'a': 'b'})

    def test_preprocess_data_returns_json_dumped_data(self):
        client = ByteRESTClient()
        data = client.preprocess_data({"a": "b"})

        self.assertEqual(data, json.dumps({"a": "b"}))
