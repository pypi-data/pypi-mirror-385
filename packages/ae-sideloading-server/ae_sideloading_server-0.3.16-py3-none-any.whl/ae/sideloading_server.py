"""
sideloading server
==================

this ae namespace portion provides a simple http server to download a file to another device in the same local network,
using any web browser.

by adding this module to your android app, you can distribute e.g., the APK file of your app directly to another android
device to install it there - without requiring an app store or an internet connection.

the implementation is inspired by the accepted answer to `<https://stackoverflow.com/questions/18543640
/how-would-i-create-a-python-web-server-that-downloads-a-file-on-any-get-request>`_.

useful debugging tools can be found at `<https://www.maketecheasier.com/transferring-files-using-python-http-server>`_.


sideloading server lifecycle
----------------------------

the sideloading server provided by this ae namespace portion can be started by first creating an instance of the
sideloading app and then calling its :meth:`~SideloadingServerApp.start_server` method::

    from ae.sideloading_server import server_factory

    sideloading_server_app = server_factory()
    sideloading_server_app.start_server()

by calling :meth:`~SideloadingServerApp.start_server` without arguments, the default file mask defined by
:data:`DEFAULT_APK_FILE_MASK` will be used to determine the APK file of the main app situated in the
`Downloads` folder of the device.

the web address that has to be entered in the web browser of the receiving device can be determined with the
:meth:`~SideloadingServerApp.server_url` method::

    client_url = sideloading_server_app.server_url()

while the server is running, the :meth:`~SideloadingServerApp.client_progress` method is providing the progress state
of any currently running sideloading task. more detailed info of the running sideloading process can be gathered
by calling the :meth:`~SideloadingServerApp.fetch_log_entries` method.

to temporarily stop the sideloading server simple call the :meth:`~SideloadingServerApp.stop_server` method. On app
exit additionally call the method :meth:`~SideloadingServerApp.shutdown`.

.. hint::
    the ae namespace portion :mod:`~ae.kivy_sideloading` is providing a package for an easy integration of this
    sideloading server into your kivy app.

    an example usage of this sideloading server and the :mod:`ae.kivy_sideloading` package is integrated into the demo
    apps `GlslTester <https://github.com/AndiEcker/glsl_tester>`_, `Lisz <https://gitlab.com/ae-group/kivy_lisz>`_ and
    `ComPartY <https://gitlab.com/ae-group/comparty>`_.

"""
import datetime
import glob
import os
import threading

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer     # ThreadingHTTPServer available in Python>=3.7
from typing import Any, Callable, Optional
from urllib.parse import quote

from ae.base import DATE_TIME_ISO, dummy_function, os_local_ip, os_path_basename    # type: ignore
from ae.files import copy_bytes                                                     # type: ignore
from ae.paths import normalize                                                      # type: ignore
from ae.console import ConsoleApp                                                   # type: ignore


__version__ = '0.3.16'


DEFAULT_APK_FILE_MASK = "{downloads}/{main_app_name}*.apk"  #: default glob file mask to sideloading file
FILE_COUNT_MISMATCH = " files found matching "              #: err msg part of :meth:`SideloadingServerApp.start_server`

SERVER_BIND = ""                    #: setting BIND to '' or None to allow connections for all local devices
SERVER_PORT = 36996                 #: http server listening port (a port number under 1024 requires root privileges)

SOCKET_BUF_LEN = 16 * 1024          #: buf length for socket sends in :meth:`~SideloadingServerApp.response_to_request`

SHUTDOWN_TIMEOUT = 3.9              #: timeout(in seconds) to shut down/stop the console app and http sideloading server

SideloadingKwargs = dict[str, Any]  #: command/log format of sideloading requests

clients_lock = threading.Lock()
requests_lock = threading.Lock()

server_app: Optional['SideloadingServerApp'] = None     #: sideloading service server app


def content_disposition_file_name(file_path: str) -> str:
    """ encode non-ASCII characters in the file name to be passed in http header to the client.

    :param file_path:           file name/path to encode.
    :return:                    base name of the specified file, encoded to ASCII/latin-1.

    inspired by django 4.2 helper function utils/http.py/content_disposition_header()
    """
    file_name = os_path_basename(file_path)
    try:
        file_name.encode('ascii')
        file_expr = 'filename="{}"'.format(file_name.replace("\\", "\\\\").replace('"', r"\""))
    except UnicodeEncodeError:
        file_expr = f"filename*=utf-8''{quote(file_name)}"
    return file_expr


def server_factory(task_id_func: Optional[Callable[[str, str, str], str]] = None) -> 'SideloadingServerApp':
    """ create server app instance.

    :param task_id_func:        callable to return an unique id for a transfer request task.
    :return:                    sideloading server app instance.
    """
    global server_app           # pylint: disable=global-statement

    server_app = SideloadingServerApp(app_name='sideloading_server', multi_threading=True, disable_buffering=True)
    server_app.add_option('bind', "server bind address", SERVER_BIND, short_opt='b')
    server_app.add_option('port', "server listening port", SERVER_PORT, short_opt='p')
    server_app.add_option('file_mask', "file mask for the sideloading file", DEFAULT_APK_FILE_MASK, short_opt='m')
    server_app.add_option('buf_len', "socket buffer length", SOCKET_BUF_LEN, short_opt='l')

    if task_id_func:
        # noinspection PyTypeHints
        server_app.id_of_task = task_id_func    # type: ignore

    return server_app


def update_handler_progress(handler: Optional['SimpleHTTPRequestHandler'] = None,
                            transferred_bytes: int = -3, total_bytes: int = -3, **_kwargs):
    """ default progress update callback.

    :param handler:             server request handler - containing the attributes to be updated.
    :param transferred_bytes:   already transferred bytes or error code.
    :param total_bytes:         total sideloading bytes.
    :param _kwargs:             additional/optional kwargs (e.g., client_ip).
    """
    if handler:
        handler.progress_transferred = transferred_bytes
        handler.progress_total = total_bytes


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    """ server request handler. """
    progress_total: int = -1                            #: total file size in bytes to be transferred
    progress_transferred: int = -1                      #: transferred bytes in this sideloading progress thread

    # noinspection PyPep8Naming
    def do_GET(self):           # pylint: disable=invalid-name
        """ handler callback for an http GET command request. """
        server_app.response_to_request(self)

    def log_request(self, code='-', size='-'):
        """ overwrite to prevent console output if not in debug mode. """
        if server_app.debug:
            super().log_request(code=code, size=size)       # pragma: no cover


class SideloadingServerApp(ConsoleApp):
    """ server service app class """
    client_handlers: dict[str, SimpleHTTPRequestHandler]                    #: handler for each active client connection
    sideloading_file_path: str                                              #: path to the found sideloading file
    load_requests: list[SideloadingKwargs]                                  #: sideloading requests and error/debug log
    progress_callback: Callable = dummy_function                            #: progress event callback
    server_instance: Optional[ThreadingHTTPServer]                          #: server class instance
    server_thread: Optional[threading.Thread]                               #: server thread (main or separate thread)

    def client_progress(self, client_ip: str) -> tuple[int, int]:
        """ determine sideloading progress (transferred bytes) for the client with the passed ip address.

        this method can be used alternatively to the callback :attr:`~SideloadingServerApp.progress_callback`.

        :param client_ip:       client ip address.
        :return:                tuple of two int values: status and file size of the sideloading file.
                                a positive status value signifies the number of already transferred bytes.
                                A negative value in this first int signals an error. possible error codes are:
                                * -1 if the sideloading task did not start yet
                                * -2 if not exists or the sideloading task has already finished
                                * -3 if the default
                                please note that the file size given in the second int can be 0 if an error has occurred
                                or if the sideloading task is not yet fully created/started.
        """
        with clients_lock:
            handler = self.client_handlers.get(client_ip, None)

        return (handler.progress_transferred, handler.progress_total) if handler else (-2, 0)

    @staticmethod
    def id_of_task(action: str, object_type: str, object_key: str) -> str:
        """ compile the id of the sideloading request task.

        :param action:          action or log level string.
        :param object_type:     task object type (currently only 'log' is implemented/supported).
        :param object_key:      task key (for log entries the timestamp of the log entry is used).
        :return:                unique key identifying the task/log-entry.
        """
        return action + '_' + object_type + ':' + object_key

    def log(self, log_level: str, message: str):
        """ print a log message and optionally add it to the requests (to be read by controller app).

        :param log_level:       'print' always prints, 'debug' prints if `self.debug` is True, and 'verbose' prints a
                                message to the log if `self.verbose` is True.
        :param message:         message to print.
        """
        out_method = getattr(self, log_level + '_out', None)
        if callable(out_method):
            out_method(("" if self.active_log_stream else f"{threading.current_thread().name: <15}") + f"{message}")

        if getattr(self, log_level, True) and hasattr(self, 'load_requests'):
            log_time = datetime.datetime.now()
            with requests_lock:
                self.load_requests.append(
                    {'method_name': log_level + '_' + 'log', 'message': message, 'log_time': log_time,
                     'rt_id': self.id_of_task(log_level, 'log', log_time.strftime(DATE_TIME_ISO))})

    def fetch_log_entries(self) -> dict[str, SideloadingKwargs]:
        """ collect last log entries, return them and remove them from this app instance.

        :return:                dict[request_tasks_id, sideloading_request_kwargs] with fetched requests log entries.
        """
        with requests_lock:
            log_entries = {}
            requests = self.load_requests
            for entry in requests:
                log_entries[entry['rt_id']] = entry
            requests[:] = []

        return log_entries

    def response_to_request(self, handler: SimpleHTTPRequestHandler):
        """ process a request to this server and return the response string.

        .. note:: this method may run in a separate thread (created by the server to process this request).

        :param handler:         stream request handler instance.
        """
        pre = "SideloadingServerApp.response_to_request()"
        self.log('verbose', f"{pre} from client={handler.client_address}")
        client_ip = handler.client_address[0]
        with clients_lock:
            self.client_handlers[client_ip] = handler   # removed by controlling process/app on finished sideloading

        errors: list[str] = []
        try:
            handler.send_response(200)
            handler.send_header("Content-Type", 'application/octet-stream')
            handler.send_header("Content-Disposition",
                                f"attachment; {content_disposition_file_name(self.sideloading_file_path)}")
            with open(self.sideloading_file_path, 'rb') as file_handle:
                file_size = os.fstat(file_handle.fileno()).st_size
                handler.progress_total = file_size
                handler.send_header("Content-Length", str(file_size))
                handler.end_headers()

                progress_kwargs = {'client_ip': client_ip, 'handler': handler}
                copy_bytes(file_handle, handler.wfile, total_bytes=file_size, buf_size=self.get_opt('buf_len'),
                           errors=errors, progress_func=self.progress_callback, **progress_kwargs)
                if errors:
                    self.log('print', f"{pre} copy_bytes errors: {errors}")
                else:
                    handler.progress_transferred = file_size

        except (KeyError, IOError, OSError, Exception) as ex:       # pylint: disable=broad-exception-caught
            self.log('print', f"{pre} exception {ex} on send of {self.sideloading_file_path}")

        else:
            if not errors:
                self.log('debug', f"{pre} side-loaded {file_size} bytes of {self.sideloading_file_path} to {client_ip}")

    def server_url(self) -> str:
        """ determine the url string to put into the address field of any browser to start sideloading.

        :return:                server url string.
        """
        # noinspection HttpUrlsUsage
        url = "http://" + os_local_ip()
        port = self.get_opt('port')
        if port != 80:
            url += ":" + str(port)
        return url

    def shutdown(self, exit_code: Optional[int] = 0, timeout: Optional[float] = None):
        """ overwritten to stop any running sideloading server instance/threads on shutdown of this app instance.

        :param exit_code:   set application OS exit code - see :meth:`~ae.core.AppBase.shutdown`.
        :param timeout:     timeout float value in seconds - see :meth:`~ae.core.AppBase.shutdown`.
        """
        self.stop_server()
        super().shutdown(exit_code=exit_code, timeout=timeout)

    def start_server(self, file_mask: str = "", threaded: bool = False, progress: Callable = update_handler_progress
                     ) -> str:
        """ start http file sideloading server to run until :meth:`~.stop_server` gets called.

        :param file_mask:       optional glob.glob file mask to specify the sideloading file. if not passed, then
                                the :data:`DEFAULT_APK_FILE_MASK` will be used which specifies an APK file of the
                                main app situated in the `Downloads` folder of the device.
                                the sideloading server will only be started if the file mask matches exactly one file.
                                the file path of the matched file can be accessed via the
                                :attr:`~SideloadingServerApp.sideloading_file_path` attribute.
        :param threaded:        optionally pass True to use a separate thread to run the server instance.
        :param progress:        an optional callback is executed for each transferred/side-loaded chunk. if not
                                specified, then the default callback method :func:`update_handler_progress`
                                will be called to update the progress attributes of the request handler, which can
                                be polled via the :meth:`~SideloadingServerApp.client_progress` method.
        :return:                empty string/"" if server instance/thread got started else the error message string.

        .. note::
            if :paramref:`~.start_server.threaded` is `True`, then the :paramref:`~.start_server.progress` callback gets
            executed in its own thread.
        """
        pre = "SideloadingServerApp.start_server()"
        if not file_mask:
            file_mask = self.get_option('file_mask', DEFAULT_APK_FILE_MASK)
        self.progress_callback = progress

        self.server_instance = self.server_thread = None
        self.client_handlers = {}
        self.load_requests = []

        if requests_lock.locked():  # pragma: no cover
            requests_lock.release()             # release before self.log() call (new acquiring)
            self.log('print', f"{pre}: released requests lock")
        if clients_lock.locked():   # pragma: no cover
            self.log('print', f"{pre}: releasing clients lock")
            clients_lock.release()

        self.log('debug', f"{pre}: {threaded=} {file_mask=} {progress=}")

        err_msg = ""
        try:
            files = glob.glob(normalize(file_mask))
            file_count = len(files)
            if file_count != 1:
                return f"{pre}: {str(file_count) if file_count else 'no'}{FILE_COUNT_MISMATCH}{file_mask}"
            self.sideloading_file_path = files[0]

            server_address = (self.get_opt('bind'), self.get_opt('port'))
            ThreadingHTTPServer.allow_reuse_address = True
            SimpleHTTPRequestHandler.protocol_version = "HTTP/1.0"
            # noinspection PyTypeChecker
            self.server_instance = ThreadingHTTPServer(server_address, SimpleHTTPRequestHandler)
            self.server_instance.timeout = SHUTDOWN_TIMEOUT

            self.log('verbose', f"{pre}: {self.sideloading_file_path=} {server_address=}"
                                f"/{self.server_instance.server_address}"
                                f"/{self.server_instance.socket.getsockname()}")
            tct = threading.current_thread()
            if threaded:
                # start a thread with the server -- that thread will then start one more thread for each request
                self.server_thread = threading.Thread(name="SideloadingTrd", target=self.server_instance.serve_forever)
                self.server_thread.start()
                self.log('verbose', f"{pre}: started server from {tct.name=} in {self.server_thread.name=}")
            else:
                self.log('verbose', f"{pre}: starting server loop; blocking this main {tct.name=}")
                self.server_thread = tct
                self.server_instance.serve_forever()

        except (IOError, OSError, Exception) as ex:                 # pylint: disable=broad-exception-caught
            err_msg = f"{pre}: exception {ex}"
            self.log('print', err_msg)
            self.server_instance = self.server_thread = None

        return err_msg

    def stop_server(self):
        """ stop/pause sideloading server - callable also if not running to reset/prepare this app instance. """
        pre = "SideloadingServerApp.stop_server()"
        if requests_lock.locked():  # pragma: no cover
            requests_lock.release()             # release before self.log() call (new acquiring)
            self.log('print', f"{pre}: released requests lock")
        if clients_lock.locked():   # pragma: no cover
            self.log('print', f"{pre}: releasing clients lock")
            clients_lock.release()
        self.log('verbose', f"{pre}")

        if getattr(self, 'server_instance', False) and getattr(self, 'server_thread', False):
            if self.server_thread == threading.current_thread():                # pragma: no cover
                thread = threading.Thread(name="StopSideloadingServerThread", target=self.server_instance.shutdown)
                thread.start()
                thread.join(timeout=SHUTDOWN_TIMEOUT)
                if thread.is_alive():
                    self.log('print', f"{pre}: server shutdown thread join timed out")
            else:
                self.server_instance.shutdown()
                self.server_thread.join(timeout=SHUTDOWN_TIMEOUT)
                if self.server_thread.is_alive():
                    self.log('print', f"{pre}: server thread join timed out")   # pragma: no cover
        self.server_instance = self.server_thread = None


if __name__ == '__main__':              # pragma: no cover
    server_app = server_factory()
    server_app.run_app()
    server_app.start_server()
