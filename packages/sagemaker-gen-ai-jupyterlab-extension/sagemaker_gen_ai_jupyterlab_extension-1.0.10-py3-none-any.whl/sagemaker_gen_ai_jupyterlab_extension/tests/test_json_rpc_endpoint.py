import pytest
import json
from unittest.mock import Mock
from sagemaker_gen_ai_jupyterlab_extension.pylspclient.json_rpc_endpoint import JsonRpcEndpoint
from sagemaker_gen_ai_jupyterlab_extension.pylspclient.lsp_errors import ResponseError, ErrorCodes


class TestJsonRpcEndpoint:
    
    def test_init(self):
        """Test JsonRpcEndpoint initialization"""
        stdin = Mock()
        stdout = Mock()
        endpoint = JsonRpcEndpoint(stdin, stdout)
        
        assert endpoint.stdin == stdin
        assert endpoint.stdout == stdout
        assert endpoint.read_lock is not None
        assert endpoint.write_lock is not None
    
    def test_add_header(self):
        """Test header addition to JSON string"""
        json_string = '{"test": "data"}'
        result = JsonRpcEndpoint._JsonRpcEndpoint__add_header(json_string)
        
        expected = f"Content-Length: {len(json_string)}\r\n\r\n{json_string}"
        assert result == expected
    
    def test_send_request(self):
        """Test sending a request"""
        stdin = Mock()
        stdout = Mock()
        endpoint = JsonRpcEndpoint(stdin, stdout)
        
        message = {"method": "test", "params": {}}
        endpoint.send_request(message)
        
        # Verify write was called
        stdin.write.assert_called_once()
        stdin.flush.assert_called_once()
        
        # Verify the content format
        written_data = stdin.write.call_args[0][0].decode()
        assert "Content-Length:" in written_data
        assert '"method": "test"' in written_data
    
    def test_recv_response_success(self):
        """Test receiving a successful response"""
        stdin = Mock()
        stdout = Mock()
        
        # Mock response data
        response_data = {"result": "success"}
        json_string = json.dumps(response_data)
        content_length = len(json_string)
        
        # Mock stdout.readline to return headers
        stdout.readline.side_effect = [
            f"Content-Length: {content_length}\r\n".encode(),
            "\r\n".encode()
        ]
        
        # Mock stdout.read to return JSON content
        stdout.read.return_value = json_string.encode()
        
        endpoint = JsonRpcEndpoint(stdin, stdout)
        result = endpoint.recv_response()
        
        assert result == response_data
    
    def test_recv_response_with_content_type(self):
        """Test receiving response with content-type header"""
        stdin = Mock()
        stdout = Mock()
        
        response_data = {"result": "success"}
        json_string = json.dumps(response_data)
        content_length = len(json_string)
        
        stdout.readline.side_effect = [
            f"Content-Length: {content_length}\r\n".encode(),
            "Content-Type: application/vscode-jsonrpc; charset=utf-8\r\n".encode(),
            "\r\n".encode()
        ]
        stdout.read.return_value = json_string.encode()
        
        endpoint = JsonRpcEndpoint(stdin, stdout)
        result = endpoint.recv_response()
        
        assert result == response_data
    
    def test_recv_response_server_quit(self):
        """Test handling server quit (empty response)"""
        stdin = Mock()
        stdout = Mock()
        stdout.readline.return_value = b""
        
        endpoint = JsonRpcEndpoint(stdin, stdout)
        result = endpoint.recv_response()
        
        assert result is None
    
    def test_recv_response_bad_header_missing_newline(self):
        """Test error handling for bad header without newline"""
        stdin = Mock()
        stdout = Mock()
        stdout.readline.return_value = "Content-Length: 10".encode()  # Missing \r\n
        
        endpoint = JsonRpcEndpoint(stdin, stdout)
        
        with pytest.raises(ResponseError) as exc_info:
            endpoint.recv_response()
        
        assert exc_info.value.code == ErrorCodes.ParseError
        assert "missing newline" in exc_info.value.message
    
    def test_recv_response_bad_header_invalid_size(self):
        """Test error handling for invalid content length"""
        stdin = Mock()
        stdout = Mock()
        stdout.readline.side_effect = [
            "Content-Length: invalid\r\n".encode(),
            "\r\n".encode()
        ]
        
        endpoint = JsonRpcEndpoint(stdin, stdout)
        
        with pytest.raises(ResponseError) as exc_info:
            endpoint.recv_response()
        
        assert exc_info.value.code == ErrorCodes.ParseError
        assert "size is not int" in exc_info.value.message
    
    def test_recv_response_unknown_header(self):
        """Test error handling for unknown header"""
        stdin = Mock()
        stdout = Mock()
        stdout.readline.side_effect = [
            "Unknown-Header: value\r\n".encode(),
            "\r\n".encode()
        ]
        
        endpoint = JsonRpcEndpoint(stdin, stdout)
        
        with pytest.raises(ResponseError) as exc_info:
            endpoint.recv_response()
        
        assert exc_info.value.code == ErrorCodes.ParseError
        assert "unkown header" in exc_info.value.message
    
    def test_recv_response_missing_size(self):
        """Test error handling for missing content length"""
        stdin = Mock()
        stdout = Mock()
        stdout.readline.side_effect = [
            "\r\n".encode()  # Empty header, no Content-Length
        ]
        
        endpoint = JsonRpcEndpoint(stdin, stdout)
        
        with pytest.raises(ResponseError) as exc_info:
            endpoint.recv_response()
        
        assert exc_info.value.code == ErrorCodes.ParseError
        assert "missing size" in exc_info.value.message
    
    def test_recv_response_unexpected_eof(self):
        """Test error handling for unexpected EOF while reading body"""
        stdin = Mock()
        stdout = Mock()
        
        stdout.readline.side_effect = [
            "Content-Length: 100\r\n".encode(),
            "\r\n".encode()
        ]
        stdout.read.return_value = b""  # Empty read simulates EOF
        
        endpoint = JsonRpcEndpoint(stdin, stdout)
        
        with pytest.raises(ResponseError) as exc_info:
            endpoint.recv_response()
        
        assert exc_info.value.code == ErrorCodes.ParseError
        assert "Unexpected EOF" in exc_info.value.message
    
    def test_recv_response_chunked_reading(self):
        """Test reading response in chunks"""
        stdin = Mock()
        stdout = Mock()
        
        response_data = {"result": "success"}
        json_string = json.dumps(response_data)
        content_length = len(json_string)
        
        stdout.readline.side_effect = [
            f"Content-Length: {content_length}\r\n".encode(),
            "\r\n".encode()
        ]
        
        # Simulate chunked reading
        json_bytes = json_string.encode()
        chunk_size = len(json_bytes) // 2
        stdout.read.side_effect = [
            json_bytes[:chunk_size],
            json_bytes[chunk_size:]
        ]
        
        endpoint = JsonRpcEndpoint(stdin, stdout)
        result = endpoint.recv_response()
        
        assert result == response_data