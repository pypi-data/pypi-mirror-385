# Original Copyright https://github.com/yeger00/pylspclient. Licensed under MIT License.
from __future__ import print_function
import json
import threading
from typing import Any, IO
from .lsp_errors import ErrorCodes, ResponseError

JSON_RPC_REQ_FORMAT = "Content-Length: {json_string_len}\r\n\r\n{json_string}"
LEN_HEADER = "Content-Length: "
TYPE_HEADER = "Content-Type: "


# TODO: add content-type


class MyEncoder(json.JSONEncoder):
    """
    Encodes an object in JSON
    """

    def default(self, o: Any):  # pylint: disable=E0202
        return o.__dict__


class JsonRpcEndpoint(object):
    """
    Thread safe JSON RPC endpoint implementation. Responsible to recieve and send JSON RPC messages, as described in the
    protocol. More information can be found: https://www.jsonrpc.org/
    """

    def __init__(self, stdin: IO, stdout: IO):
        self.stdin = stdin
        self.stdout = stdout
        self.read_lock = threading.Lock()
        self.write_lock = threading.Lock()

    @staticmethod
    def __add_header(json_string: str) -> str:
        """
        Adds a header for the given json string

        :param str json_string: The string
        :return: the string with the header
        """
        return JSON_RPC_REQ_FORMAT.format(
            json_string_len=len(json_string), json_string=json_string
        )

    def send_request(self, message: Any) -> None:
        """
        Sends the given message.

        :param dict message: The message to send.
        """
        json_string = json.dumps(message, cls=MyEncoder)
        jsonrpc_req = self.__add_header(json_string)
        with self.write_lock:
            self.stdin.write(jsonrpc_req.encode())
            self.stdin.flush()

    def recv_response(self) -> Any:
        """
        Recives a message.

        :return: a message
        """
        with self.read_lock:
            message_size = None
            while True:
                # read header
                line = self.stdout.readline()
                if not line:
                    # server quit
                    return None
                line = line.decode("utf-8")
                if not line.endswith("\r\n"):
                    raise ResponseError(
                        ErrorCodes.ParseError, "Bad header: missing newline"
                    )
                # remove the "\r\n"
                line = line[:-2]
                if line == "":
                    # done with the headers
                    break
                elif line.startswith(LEN_HEADER):
                    line = line[len(LEN_HEADER) :]
                    if not line.isdigit():
                        raise ResponseError(
                            ErrorCodes.ParseError, "Bad header: size is not int"
                        )
                    message_size = int(line)
                elif line.startswith(TYPE_HEADER):
                    # nothing todo with type for now.
                    pass
                else:
                    raise ResponseError(
                        ErrorCodes.ParseError, "Bad header: unkown header"
                    )
            if not message_size:
                raise ResponseError(ErrorCodes.ParseError, "Bad header: missing size")
                
        # Decode stdout by chunks split by message size to prevent JSON parsing error when content is too long
        content = b""
        while len(content) < message_size:
            # Read up to the remaining number of bytes needed to complete the message. If message_size is too large, only n number of bytes will be returned. 
            # stdout.read maintains a pointer to keep track where next read operaton should begin
            chunk = self.stdout.read(message_size - len(content))

            # Handles reading error in the process
            if not chunk:
                raise ResponseError(ErrorCodes.ParseError, "Unexpected EOF while reading body")
            content += chunk

        jsonrpc_res = content.decode("utf-8")
        return json.loads(jsonrpc_res)
