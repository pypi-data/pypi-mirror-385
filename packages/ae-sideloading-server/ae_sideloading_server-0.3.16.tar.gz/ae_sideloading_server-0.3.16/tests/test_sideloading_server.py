""" unit tests - still very basic - have to fix the multiple connect/test error: [Errno 98] Address already in use. """
import os
import pytest
import threading
import time

from io import BytesIO
from socket import socket
from unittest.mock import MagicMock

from ae.base import defuse, os_local_ip
from ae.files import write_file_text
from ae.paths import PATH_PLACEHOLDERS, normalize
from ae.sideloading_server import (
    SERVER_PORT, SOCKET_BUF_LEN, content_disposition_file_name, server_factory, SideloadingServerApp)
from ae.console import ConsoleApp


tst_apk_content = "tst_apk_content"


@pytest.fixture
def threaded_server(restore_app_env):
    """ yielding an instantiated and started server app. """
    app = server_factory()
    app.run_app()
    PATH_PLACEHOLDERS['downloads'] = "tests"
    test_downloadable = normalize(os.path.join("{downloads}", "sideloading_server.apk"))
    write_file_text(tst_apk_content, test_downloadable)
    app.start_server(threaded=True)

    yield app

    app.stop_server()
    os.remove(test_downloadable)
    while app.server_instance or app.server_thread:
        time.sleep(0.6)


def test_class_import():
    assert SideloadingServerApp


def test_constants_import():
    assert SERVER_PORT
    assert SOCKET_BUF_LEN


class TestHelpers:
    def test_content_disposition_file_name(self):
        assert content_disposition_file_name("").startswith("filename=")
        assert content_disposition_file_name("tst_fil_nam.txt").startswith("filename=")

        assert content_disposition_file_name("t_äst_€_ß").startswith("filename*=")
        assert content_disposition_file_name(defuse("://.;?&\\")).startswith("filename*=")

    def test_server_factory(self, restore_app_env):
        app = server_factory()
        assert isinstance(app, ConsoleApp)
        assert app.id_of_task is SideloadingServerApp.id_of_task

    def test_service_factory_id_of_task_patch(self, restore_app_env):
        def _id_of_task(act, obj, key):
            return act + "_" + obj + ":" + key
        app = server_factory(task_id_func=_id_of_task)
        assert app.id_of_task is _id_of_task


class TestSideloadingServerApp:
    def test_client_progress_no_req_local_ip(self, threaded_server):
        tra, tot = threaded_server.client_progress(os_local_ip())
        assert tra == -2
        assert tot == 0

    def test_client_progress_no_req_localhost(self, threaded_server):
        tra, tot = threaded_server.client_progress('localhost')
        assert tra == -2
        assert tot == 0

    def test_client_progress_and_fetch_log_entries_req(self, threaded_server):
        # failing the second one if split into two separate tests (for client_progress() and for fetch_log_entries())
        with socket() as sock:
            sock.connect(('localhost', SERVER_PORT))
            sock.sendall(b"GET / HTTP/1.0\r\n\r\n")
            response = sock.recv(SOCKET_BUF_LEN)
            file_content = sock.recv(SOCKET_BUF_LEN)

        assert response
        assert response[:15] == b"HTTP/1.0 200 OK"
        assert bytes(os.path.basename(threaded_server.sideloading_file_path), 'utf-8') in response

        assert str(file_content, 'utf-8') == tst_apk_content

        client_ip = list(threaded_server.client_handlers.keys())[0]
        assert client_ip in ('localhost', '127.0.0.1', os_local_ip())
        while True:
            tra, tot = threaded_server.client_progress(client_ip)
            if tra >= 0:        # wait for server handler thread
                break
        assert tot == len(tst_apk_content)
        assert tra == len(tst_apk_content)

        assert threaded_server.client_handlers
        handler = list(threaded_server.client_handlers.values())[0]
        assert handler.progress_total == len(tst_apk_content)
        assert handler.progress_transferred == len(tst_apk_content)

        log_entries = threaded_server.fetch_log_entries()
        assert isinstance(log_entries, dict)
        logs = list(log_entries.values())
        assert threaded_server.debug == bool(logs)

    def test_fetch_log_entries_req(self, threaded_server):
        with socket() as sock:
            sock.connect(('localhost', SERVER_PORT))
            sock.sendall(b"GET / HTTP/1.0\r\n\r\n")

        log_entries = threaded_server.fetch_log_entries()
        assert isinstance(log_entries, dict)
        logs = list(log_entries.values())
        assert threaded_server.debug == bool(logs)

        tst_msg = "test message to be logged"
        threaded_server.log('print', tst_msg)
        logs = list(threaded_server.fetch_log_entries().values())
        assert logs
        assert logs[-1]['message'] == tst_msg

    def test_id_of_task(self, threaded_server):
        assert threaded_server.id_of_task('action', 'object', 'key')
        assert 'action' in threaded_server.id_of_task('action', 'object', 'key')
        assert 'object' in threaded_server.id_of_task('action', 'object', 'key')
        assert 'key' in threaded_server.id_of_task('action', 'object', 'key')

    def test_log_out_method(self, threaded_server):
        def _out(*args):
            nonlocal called
            called = args
        called = ()
        setattr(threaded_server, 'tst_out', _out)

        msg = "message"
        threaded_server.log('tst', msg)
        assert called
        assert msg in called[0]

    def test_log_append(self, threaded_server):
        rt_id_part = "xyz"
        threaded_server.log(rt_id_part, "message")
        req = threaded_server.load_requests[-1]
        assert req['method_name'] == rt_id_part + "_log"
        assert req['message'] == "message"
        assert req['log_time']
        assert rt_id_part in req['rt_id']

    def test_response_to_request(self, threaded_server):
        handler = MagicMock()
        handler.wfile = BytesIO()
        threaded_server.response_to_request(handler)
        assert handler.wfile.tell() == len(tst_apk_content)
        handler.wfile.seek(0)
        assert str(handler.wfile.read(), 'utf-8') == tst_apk_content

    def test_response_to_request_copy_bytes_error(self, threaded_server):
        handler = MagicMock()
        handler.wfile = None
        threaded_server.response_to_request(handler)
        assert threaded_server.load_requests
        assert 'copy_bytes error' in threaded_server.load_requests[-1]['message']

    def test_response_to_request_exception(self, threaded_server):
        handler = MagicMock()
        threaded_server.sideloading_file_path = ""
        threaded_server.response_to_request(handler)
        assert threaded_server.load_requests
        assert 'exception' in threaded_server.load_requests[-1]['message']

    def test_server_url(self, threaded_server):
        assert threaded_server.server_url()

    def test_start_server(self, restore_app_env):
        app = server_factory()
        PATH_PLACEHOLDERS['downloads'] = "tests"
        test_downloadable = normalize(os.path.join("{downloads}", "sideloading_server.apk"))
        write_file_text("tst_apk_content", test_downloadable)
        thread = threading.Thread(name='TestStartServer', target=app.start_server)
        thread.start()
        while not getattr(app, 'server_instance', False) and not getattr(app, 'server_thread', False):
            time.sleep(0.6)
        app.stop_server()
        os.remove(test_downloadable)
        while app.server_instance or app.server_thread:
            time.sleep(0.6)

    def test_start_server_error(self, restore_app_env):
        app = server_factory()
        assert app.start_server(file_mask=': invalid file :')

    def test_start_server_exception(self, restore_app_env):
        app = server_factory()
        app.run_app()
        app.set_opt('bind', ":invalid bind address:", save_to_config=False)
        app.set_opt('port', ":invalid port:", save_to_config=False)
        assert app.start_server(file_mask=os.path.join("tests", "conftest.py"), threaded=True)
