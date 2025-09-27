import io
import json
import pytest
from squirrel_server import SquirrelServerHandler
from squirrel_db import SquirrelDB

# use @todo to cause pytest to skip that section
# handy for stubbing things out and then coming back later to finish them.
# @todo is heirarchical, and not sequential. Meaning that
# it will not skip 'peers' of other todos, only children.
todo = pytest.mark.skip(reason='TODO: pending spec')

class FakeRequest():
    def __init__(self, mock_wfile, method, path, body=None):
        self._mock_wfile = mock_wfile
        self._method = method
        self._path = path
        self._body = body

    def sendall(self, x):
        return

    #this is not a 'makefile' like in c++ instead it 'makes' a response file
    def makefile(self, *args, **kwargs):
        if args[0] == 'rb':
            if self._body:
                headers = 'Content-Length: {}\r\n'.format(len(self._body))
                body = self._body
            else:
                headers = ''
                body = ''
            request = bytes('{} {} HTTP/1.0\r\n{}\r\n{}'.format(self._method, self._path, headers, body), 'utf-8')
            return io.BytesIO(request)
        elif args[0] == 'wb':
            return self._mock_wfile

#dummy client and dummy server to pass as params
#when creating SquirrelServerHandler
@pytest.fixture
def dummy_client():
    return ('127.0.0.1', 80)

@pytest.fixture
def dummy_server():
    return None

#a patch for mocking the DB initialize 
# function - this gets called a lot.
@pytest.fixture
def mock_db_init(mocker):
    return mocker.patch.object(SquirrelDB, '__init__', return_value=None)

@pytest.fixture
def mock_db_get_squirrels(mocker, mock_db_init):
    return mocker.patch.object(SquirrelDB, 'getSquirrels', return_value=['squirrel'])


@pytest.fixture
def mock_db_get_squirrel(mocker, mock_db_init):
    return mocker.patch.object(SquirrelDB, 'getSquirrel', return_value='squirrel')

# patch SquirrelServerHandler to make our FakeRequest work correctly
@pytest.fixture(autouse=True)
def patch_wbufsize(mocker):
    mocker.patch.object(SquirrelServerHandler, 'wbufsize', 1)
    mocker.patch.object(SquirrelServerHandler, 'end_headers')


# Fake Requests
@pytest.fixture
def fake_get_squirrels_request(mocker):
    return FakeRequest(mocker.Mock(), 'GET', '/squirrels')


@pytest.fixture
def fake_create_squirrel_request(mocker):
    return FakeRequest(mocker.Mock(), 'POST', '/squirrels', body='name=Chippy&size=small')

@pytest.fixture
def fake_bad_request(mocker):
    return FakeRequest(mocker.Mock(), 'POST', '/squirrels', body='name=Josh&')


#send_response, send_header and end_headers are inherited functions
#from the BaseHTTPRequestHandler. Go look at documentation here:
# https://docs.python.org/3/library/http.server.html
# Seriously. Go look at it. Pay close attention to what wfile is. :o)
# this fixture mocks all of the send____ that we use. 
# It is really just for convenience and cleanliness of code.
@pytest.fixture
def mock_response_methods(mocker):
    mock_send_response = mocker.patch.object(SquirrelServerHandler, 'send_response')
    mock_send_header = mocker.patch.object(SquirrelServerHandler, 'send_header')
    mock_end_headers = mocker.patch.object(SquirrelServerHandler, 'end_headers')
    return mock_send_response, mock_send_header, mock_end_headers


def describe_Squirrel_Server_Handlers():

    def describe_handle_Squirrels_Index():

        def it_calls_db_get_Squirrels(fake_get_squirrels_request, dummy_client, dummy_server, mock_db_get_squirrels):
            SquirrelServerHandler(fake_get_squirrels_request, dummy_client, dummy_server)

            mock_db_get_squirrels.assert_called_once()

        def it_returns_status_code_200(fake_get_squirrels_request, dummy_client, dummy_server, mock_response_methods):
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods

            SquirrelServerHandler(fake_get_squirrels_request, dummy_client, dummy_server)

            mock_send_response.assert_called_once_with(200)

        def it_calls_send_header_with_correct_info(fake_get_squirrels_request, dummy_client, dummy_server, mock_response_methods):
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods

            SquirrelServerHandler(fake_get_squirrels_request, dummy_client, dummy_server)

            mock_send_header.assert_called_once_with("Content-Type", "application/json")

        def it_calls_end_headers(fake_get_squirrels_request, dummy_client, dummy_server, mock_response_methods):
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods

            SquirrelServerHandler(fake_get_squirrels_request, dummy_client, dummy_server)

            mock_end_headers.assert_called_once

        def it_writes_json_list_of_squirrels(fake_get_squirrels_request, dummy_client, dummy_server, mocker):
            mocker.patch.object(SquirrelDB, "getSquirrels", return_value=["squirrel"])
            
            handler = SquirrelServerHandler(fake_get_squirrels_request, dummy_client, dummy_server)

            handler.wfile.write.assert_called_once_with(bytes(json.dumps(['squirrel']), "utf-8"))

    def describe_handle_Squirrels_Retrieve():
        
        def describe_when_squirrel_exists():

            def it_queries_db_with_correct_id(fake_get_squirrels_request, dummy_client, dummy_server, mock_db_get_squirrels, mock_db_get_squirrel):
                handler = SquirrelServerHandler(fake_get_squirrels_request, dummy_client, dummy_server)

                handler.handleSquirrelsRetrieve("39")

                mock_db_get_squirrel.assert_called_once_with("39")

            def it_sends_200_status_code(fake_get_squirrels_request, dummy_client, dummy_server, mock_db_get_squirrels, mock_response_methods):
                mock_send_response, mock_send_header, mock_end_headers = mock_response_methods

                handler = SquirrelServerHandler(fake_get_squirrels_request, dummy_client, dummy_server)

                mock_send_response.assert_called_once_with(200)

            def it_sends_json_content_type_header(fake_get_squirrels_request, dummy_client, dummy_server, mock_db_get_squirrels, mock_response_methods):
                mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
                
                handler = SquirrelServerHandler(fake_get_squirrels_request, dummy_client, dummy_server)

                mock_send_header.assert_called_once_with("Content-Type", "application/json")

            def it_calls_end_headers(fake_get_squirrels_request, dummy_client, dummy_server, mock_db_get_squirrels, mock_db_get_squirrel, mock_response_methods):
                mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
                
                handler = SquirrelServerHandler(fake_get_squirrels_request, dummy_client, dummy_server)
                                
                mock_end_headers.assert_called_once()

            def it_writes_json_of_squirrel(fake_get_squirrels_request, dummy_client, dummy_server, mock_db_get_squirrels, mocker):
                mocker.patch.object(SquirrelDB, "getSquirrel", return_value=["squirrel"])
            
                handler = SquirrelServerHandler(fake_get_squirrels_request, dummy_client, dummy_server)

                handler.wfile.write.assert_called_once_with(bytes(json.dumps(['squirrel']), "utf-8"))

        def describe_when_squirrel_does_not_exist():

            def it_calls_handle404(mocker, fake_get_squirrels_request, dummy_client, dummy_server):
                mocker.patch("squirrel_server.SquirrelDB.getSquirrel", return_value=None)
                
                handler = SquirrelServerHandler(fake_get_squirrels_request, dummy_client, dummy_server)
                mock_404 = mocker.patch.object(SquirrelServerHandler, "handle404")
                
                handler.handleSquirrelsRetrieve("99")
                mock_404.assert_called_once()

    def describe_handle_Squirrels_Create():
       
        def describe_create_squirrels_with_good_request():

            def it_creates_squirrel_with_correct_data(mocker, fake_create_squirrel_request, dummy_client, dummy_server):
                mock_create = mocker.patch("squirrel_server.SquirrelDB.createSquirrel")
                handler = SquirrelServerHandler(fake_create_squirrel_request, dummy_client, dummy_server)
                mock_create.assert_called_once_with("Chippy", "small")

            def it_sends_201_status_code(mocker, fake_create_squirrel_request, dummy_client, dummy_server, mock_response_methods):
                handler = SquirrelServerHandler(fake_create_squirrel_request, dummy_client, dummy_server)
                mock_response_methods[0].assert_called_once_with(201)

            def it_calls_end_headers(mocker, fake_create_squirrel_request, dummy_client, dummy_server, mock_response_methods):
                handler = SquirrelServerHandler(fake_create_squirrel_request, dummy_client, dummy_server)
                mock_response_methods[2].assert_called_once()
                
    def describe_handle_Squirrels_Update():
        
        def describe_squirrel_exists():

            def it_updates_existing_squirrel(mocker, dummy_client, dummy_server, mock_response_methods):
                mocker.patch("squirrel_server.SquirrelDB.updateSquirrel")
                mocker.patch("squirrel_server.SquirrelDB.getSquirrel", return_value={"id": "1"})
                mocker.patch.object(SquirrelServerHandler, "getRequestData", return_value={"name": "Chippy", "size": "small"})
                mock_send_response, mock_send_header, mock_end_headers = mock_response_methods

                fake_request = FakeRequest(mocker.Mock(), "PUT", "/squirrels/1")
                handler = SquirrelServerHandler(fake_request, dummy_client, dummy_server)

                mock_send_response.assert_called_once_with(204)

            def it_calls_getSquirrel_when_handle_squirrels_update_is_called(mocker, dummy_client, dummy_server, mock_response_methods):
                mocker.patch("squirrel_server.SquirrelDB.updateSquirrel")
                mock_get_squirrel = mocker.patch("squirrel_server.SquirrelDB.getSquirrel", return_value={"id": "1"})
                mocker.patch.object(SquirrelServerHandler, "getRequestData", return_value={"name": "Chippy", "size": "small"})
                mock_send_response, mock_send_header, mock_end_headers = mock_response_methods

                fake_request = FakeRequest(mocker.Mock(), "PUT", "/squirrels/1")
                handler = SquirrelServerHandler(fake_request, dummy_client, dummy_server)

                mock_get_squirrel.assert_called_once_with('1')

            def it_calls_updateSquirrel_when_handle_squirrels_update_is_called(mocker, dummy_client, dummy_server, mock_response_methods):
                mock_update = mocker.patch("squirrel_server.SquirrelDB.updateSquirrel")
                mocker.patch("squirrel_server.SquirrelDB.getSquirrel", return_value={"id": "1"})
                mocker.patch.object(SquirrelServerHandler, "getRequestData", return_value={"name": "Chippy", "size": "small"})
                mock_send_response, mock_send_header, mock_end_headers = mock_response_methods

                fake_request = FakeRequest(mocker.Mock(), "PUT", "/squirrels/1")
                handler = SquirrelServerHandler(fake_request, dummy_client, dummy_server)

                mock_update.assert_called_once()

            def it_calls_getRequestData_when_handle_squirrels_update_is_called(mocker, dummy_client, dummy_server, mock_response_methods):
                mocker.patch("squirrel_server.SquirrelDB.updateSquirrel")
                mocker.patch("squirrel_server.SquirrelDB.getSquirrel", return_value={"id": "1"})
                mock_get_data = mocker.patch.object(SquirrelServerHandler, "getRequestData", return_value={"name": "Chippy", "size": "small"})
                mock_send_response, mock_send_header, mock_end_headers = mock_response_methods

                fake_request = FakeRequest(mocker.Mock(), "PUT", "/squirrels/1")
                handler = SquirrelServerHandler(fake_request, dummy_client, dummy_server)

                mock_get_data.assert_called_once()

            def it_calls_end_headers_when_handle_squirrels_update_is_called(mocker, dummy_client, dummy_server, mock_response_methods):
                mocker.patch("squirrel_server.SquirrelDB.updateSquirrel")
                mocker.patch("squirrel_server.SquirrelDB.getSquirrel", return_value={"id": "1"})
                mocker.patch.object(SquirrelServerHandler, "getRequestData", return_value={"name": "Chippy", "size": "small"})
                mock_send_response, mock_send_header, mock_end_headers = mock_response_methods

                fake_request = FakeRequest(mocker.Mock(), "PUT", "/squirrels/1")
                handler = SquirrelServerHandler(fake_request, dummy_client, dummy_server)

                mock_end_headers.assert_called_once()

        def describe_squirrel_does_not_exist():
            
            def it_returns_404_when_squirrel_does_not_exist(mocker, dummy_client, dummy_server):
                mocker.patch("squirrel_server.SquirrelDB.getSquirrel", return_value=None)
                mock_404 = mocker.patch.object(SquirrelServerHandler, "handle404")

                fake_request = FakeRequest(mocker.Mock(), "PUT", "/squirrels/999")
                handler = SquirrelServerHandler(fake_request, dummy_client, dummy_server)

                mock_404.assert_called_once()

            def it_calls_getSquirrel_when_handle_squirrels_update_is_called_and_squirrel_does_not_exist(mocker, dummy_client, dummy_server, mock_response_methods):
                mock_get_squirrel = mocker.patch("squirrel_server.SquirrelDB.getSquirrel", return_value=None)
                mock_404 = mocker.patch.object(SquirrelServerHandler, "handle404")

                fake_request = FakeRequest(mocker.Mock(), "PUT", "/squirrels/999")
                handler = SquirrelServerHandler(fake_request, dummy_client, dummy_server)

                mock_get_squirrel.assert_called_once_with("999")


    def describe_handle_squirrels_delete():

        def describe_squirrel_exists():

            def it_deletes_existing_squirrel(mocker, dummy_client, dummy_server, mock_response_methods):
                mocker.patch("squirrel_server.SquirrelDB.deleteSquirrel")
                mocker.patch("squirrel_server.SquirrelDB.getSquirrel", return_value={"id": "1"})
                mock_send_response, mock_send_header, mock_end_headers = mock_response_methods

                handler = SquirrelServerHandler.__new__(SquirrelServerHandler)
                handler.handleSquirrelsDelete("1")

                SquirrelDB.deleteSquirrel.assert_called_once_with("1")
                mock_send_response.assert_called_once_with(204)

            def it_calls_getSquirrel_when_delete_squirrels_is_called(mocker, dummy_client, dummy_server, mock_response_methods):
                mocker.patch("squirrel_server.SquirrelDB.deleteSquirrel")
                mock_get = mocker.patch("squirrel_server.SquirrelDB.getSquirrel", return_value={"id": "1"})
                mock_send_response, mock_send_header, mock_end_headers = mock_response_methods

                handler = SquirrelServerHandler.__new__(SquirrelServerHandler)
                handler.handleSquirrelsDelete("1")

                mock_get.assert_called_once()

            def it_calls_end_headers_when_delete_squirrels_is_called(mocker, dummy_client, dummy_server, mock_response_methods):
                mocker.patch("squirrel_server.SquirrelDB.deleteSquirrel")
                mock_get = mocker.patch("squirrel_server.SquirrelDB.getSquirrel", return_value={"id": "1"})
                mock_send_response, mock_send_header, mock_end_headers = mock_response_methods

                handler = SquirrelServerHandler.__new__(SquirrelServerHandler)
                handler.handleSquirrelsDelete("1")

                mock_end_headers.assert_called_once()

        def describe_squirrel_does_not_exist():

            def it_returns_404_when_squirrel_does_not_exist(mocker, dummy_client, dummy_server):
                mocker.patch("squirrel_server.SquirrelDB.getSquirrel", return_value=None)
                mock_404 = mocker.patch.object(SquirrelServerHandler, "handle404")

                handler = SquirrelServerHandler.__new__(SquirrelServerHandler)
                handler.handleSquirrelsDelete("999")

                mock_404.assert_called_once()


    def describe_handle_404():

        def it_sends_404_status_code(mocker, dummy_client, dummy_server, mock_response_methods):
            fake_wfile = mocker.Mock()
            handler = SquirrelServerHandler.__new__(SquirrelServerHandler)
            handler.wfile = fake_wfile
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
            
            handler.handle404()
            
            mock_send_response.assert_called_once_with(404)

        def it_calls_send_header_with_correct_information(mocker, dummy_client, dummy_server, mock_response_methods):
            fake_wfile = mocker.Mock()
            handler = SquirrelServerHandler.__new__(SquirrelServerHandler)
            handler.wfile = fake_wfile
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
            
            handler.handle404()
            
            mock_send_header.assert_called_once_with("Content-Type", "text/plain")


