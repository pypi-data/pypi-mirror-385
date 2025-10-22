import pytest
import threading
from unittest.mock import Mock, patch
from sagemaker_gen_ai_jupyterlab_extension.pylspclient.lsp_endpoint import LspEndpoint
from sagemaker_gen_ai_jupyterlab_extension.pylspclient.lsp_errors import ResponseError, ErrorCodes


class TestLspEndpoint:
    
    def test_init(self):
        """Test LspEndpoint initialization"""
        json_rpc_endpoint = Mock()
        method_callbacks = {"test_method": Mock()}
        notify_callbacks = {"test_notify": Mock()}
        timeout = 5
        
        endpoint = LspEndpoint(json_rpc_endpoint, method_callbacks, notify_callbacks, timeout)
        
        assert endpoint.json_rpc_endpoint == json_rpc_endpoint
        assert endpoint.method_callbacks == method_callbacks
        assert endpoint.notify_callbacks == notify_callbacks
        assert endpoint._timeout == timeout
        assert endpoint.next_id == 0
        assert endpoint.shutdown_flag is False
        assert isinstance(endpoint.event_dict, dict)
        assert isinstance(endpoint.response_dict, dict)
    
    def test_handle_result(self):
        """Test handling results from server"""
        json_rpc_endpoint = Mock()
        endpoint = LspEndpoint(json_rpc_endpoint)
        
        # Setup condition for request
        rpc_id = 1
        condition = threading.Condition()
        endpoint.event_dict[rpc_id] = condition
        
        result = {"success": True}
        error = None
        
        endpoint.handle_result(rpc_id, result, error)
        
        assert endpoint.response_dict[rpc_id] == (result, error)
    
    def test_handle_result_unknown_id(self):
        """Test handling result for unknown request ID"""
        json_rpc_endpoint = Mock()
        endpoint = LspEndpoint(json_rpc_endpoint)
        
        with patch('logging.error') as mock_log:
            endpoint.handle_result(999, {"result": "test"}, None)
            mock_log.assert_called_once()
    
    def test_stop(self):
        """Test stopping the endpoint"""
        json_rpc_endpoint = Mock()
        endpoint = LspEndpoint(json_rpc_endpoint)
        
        endpoint.stop()
        assert endpoint.shutdown_flag is True
    
    def test_send_response(self):
        """Test sending response to server"""
        json_rpc_endpoint = Mock()
        endpoint = LspEndpoint(json_rpc_endpoint)
        
        rpc_id = 1
        result = {"success": True}
        
        endpoint.send_response(rpc_id, result)
        
        json_rpc_endpoint.send_request.assert_called_once()
        call_args = json_rpc_endpoint.send_request.call_args[0][0]
        assert call_args["jsonrpc"] == "2.0"
        assert call_args["id"] == rpc_id
        assert call_args["result"] == result
    
    def test_send_response_with_error(self):
        """Test sending error response"""
        json_rpc_endpoint = Mock()
        endpoint = LspEndpoint(json_rpc_endpoint)
        
        rpc_id = 1
        error = Exception("Test error")
        
        endpoint.send_response(rpc_id, None, error)
        
        json_rpc_endpoint.send_request.assert_called_once()
        call_args = json_rpc_endpoint.send_request.call_args[0][0]
        assert call_args["error"] == error
    
    def test_send_message(self):
        """Test sending message to server"""
        json_rpc_endpoint = Mock()
        endpoint = LspEndpoint(json_rpc_endpoint)
        
        method_name = "test/method"
        params = {"key": "value"}
        rpc_id = 1
        
        endpoint.send_message(method_name, params, rpc_id)
        
        json_rpc_endpoint.send_request.assert_called_once()
        call_args = json_rpc_endpoint.send_request.call_args[0][0]
        assert call_args["jsonrpc"] == "2.0"
        assert call_args["method"] == method_name
        assert call_args["params"] == params
        assert call_args["id"] == rpc_id
    
    def test_send_message_no_params(self):
        """Test sending message with None params"""
        json_rpc_endpoint = Mock()
        endpoint = LspEndpoint(json_rpc_endpoint)
        
        endpoint.send_message("test/method", None)
        
        json_rpc_endpoint.send_request.assert_called_once()
        call_args = json_rpc_endpoint.send_request.call_args[0][0]
        assert call_args["params"] == {}
    
    def test_send_message_none_endpoint(self):
        """Test sending message with None endpoint"""
        endpoint = LspEndpoint(None)
        
        with patch('logging.error') as mock_log:
            endpoint.send_message("test/method", {})
            mock_log.assert_called_once()
    
    def test_send_message_none_method(self):
        """Test sending message with None method name"""
        json_rpc_endpoint = Mock()
        endpoint = LspEndpoint(json_rpc_endpoint)
        
        with patch('logging.error') as mock_log:
            endpoint.send_message(None, {})
            mock_log.assert_called_once()
    
    def test_call_method_success(self):
        """Test successful method call"""
        json_rpc_endpoint = Mock()
        endpoint = LspEndpoint(json_rpc_endpoint, timeout=1)
        
        # Mock the response
        expected_result = {"success": True}
        
        # Mock the condition wait to return immediately with success
        with patch('threading.Condition') as mock_condition_class:
            mock_condition = Mock()
            mock_condition.wait.return_value = True  # Simulate successful wait
            mock_condition_class.return_value = mock_condition
            
            # Set up the response in the response_dict
            endpoint.response_dict[0] = (expected_result, None)
            
            result = endpoint.call_method("test/method", param1="value1")
            
            assert result == expected_result
    
    def test_call_method_timeout(self):
        """Test method call timeout"""
        json_rpc_endpoint = Mock()
        endpoint = LspEndpoint(json_rpc_endpoint, timeout=0.1)
        
        # Don't simulate any response to cause timeout
        endpoint.send_message = Mock()
        
        with pytest.raises(TimeoutError):
            endpoint.call_method("test/method")
    
    def test_call_method_with_error(self):
        """Test method call returning error"""
        json_rpc_endpoint = Mock()
        endpoint = LspEndpoint(json_rpc_endpoint, timeout=1)
        
        error = {"code": ErrorCodes.InternalError, "message": "Test error"}
        
        # Mock the condition wait to return immediately with success
        with patch('threading.Condition') as mock_condition_class:
            mock_condition = Mock()
            mock_condition.wait.return_value = True  # Simulate successful wait
            mock_condition_class.return_value = mock_condition
            
            # Set up the error response in the response_dict
            endpoint.response_dict[0] = (None, error)
            
            with pytest.raises(ResponseError) as exc_info:
                endpoint.call_method("test/method")
            
            assert exc_info.value.code == ErrorCodes.InternalError
            assert exc_info.value.message == "Test error"
    
    def test_call_method_shutdown(self):
        """Test method call when shutdown flag is set"""
        json_rpc_endpoint = Mock()
        endpoint = LspEndpoint(json_rpc_endpoint)
        endpoint.shutdown_flag = True
        
        result = endpoint.call_method("test/method")
        assert result is None
    
    def test_send_notification(self):
        """Test sending notification"""
        json_rpc_endpoint = Mock()
        endpoint = LspEndpoint(json_rpc_endpoint)
        
        with patch.object(endpoint, 'send_message') as mock_send:
            endpoint.send_notification("test/notify", param1="value1")
            mock_send.assert_called_once_with("test/notify", {"param1": "value1"})
    
    def test_run_method_call_from_server(self):
        """Test handling method call from server"""
        json_rpc_endpoint = Mock()
        method_callback = Mock(return_value={"response": "test"})
        endpoint = LspEndpoint(json_rpc_endpoint, method_callbacks={"test/method": method_callback})
        
        # Mock receiving a method call
        json_rpc_endpoint.recv_response.side_effect = [
            {"jsonrpc": "2.0", "id": 1, "method": "test/method", "params": {"key": "value"}},
            None  # End the loop
        ]
        
        with patch.object(endpoint, 'send_response') as mock_send_response:
            endpoint.run()
            
            method_callback.assert_called_once_with({"key": "value"}, 1)
    
    def test_run_notification_from_server(self):
        """Test handling notification from server"""
        json_rpc_endpoint = Mock()
        notify_callback = Mock()
        endpoint = LspEndpoint(json_rpc_endpoint, notify_callbacks={"test/notify": notify_callback})
        
        json_rpc_endpoint.recv_response.side_effect = [
            {"jsonrpc": "2.0", "method": "test/notify", "params": {"key": "value"}},
            None
        ]
        
        endpoint.run()
        
        notify_callback.assert_called_once_with({"key": "value"})
    
    def test_run_unknown_notification(self):
        """Test handling unknown notification from server"""
        json_rpc_endpoint = Mock()
        endpoint = LspEndpoint(json_rpc_endpoint)
        
        json_rpc_endpoint.recv_response.side_effect = [
            {"jsonrpc": "2.0", "method": "unknown/notify", "params": {}},
            None
        ]
        
        # Should not raise exception, just log
        endpoint.run()
    
    def test_run_unknown_method(self):
        """Test handling unknown method call from server"""
        json_rpc_endpoint = Mock()
        endpoint = LspEndpoint(json_rpc_endpoint)
        
        json_rpc_endpoint.recv_response.side_effect = [
            {"jsonrpc": "2.0", "id": 1, "method": "unknown/method", "params": {}},
            None
        ]
        
        with patch.object(endpoint, 'send_response') as mock_send_response:
            endpoint.run()
            
            # Should send error response
            mock_send_response.assert_called_once()
            args = mock_send_response.call_args[0]
            assert args[0] == 1  # rpc_id
            assert args[1] is None  # result
            assert isinstance(args[2], ResponseError)  # error
    
    def test_run_response_handling(self):
        """Test handling response from server"""
        json_rpc_endpoint = Mock()
        endpoint = LspEndpoint(json_rpc_endpoint)
        
        json_rpc_endpoint.recv_response.side_effect = [
            {"jsonrpc": "2.0", "id": 1, "result": {"success": True}},
            None
        ]
        
        with patch.object(endpoint, 'handle_result') as mock_handle:
            endpoint.run()
            mock_handle.assert_called_once_with(1, {"success": True}, None)
    
    def test_run_json_decode_error(self):
        """Test handling JSON decode error"""
        json_rpc_endpoint = Mock()
        endpoint = LspEndpoint(json_rpc_endpoint)
        
        from json import JSONDecodeError
        json_rpc_endpoint.recv_response.side_effect = [
            JSONDecodeError("Invalid JSON", "", 0),
            None
        ]
        
        with patch('logging.error') as mock_log:
            endpoint.run()
            mock_log.assert_called()
    
    def test_run_general_exception(self):
        """Test handling general exception in run loop"""
        json_rpc_endpoint = Mock()
        endpoint = LspEndpoint(json_rpc_endpoint)
        
        json_rpc_endpoint.recv_response.side_effect = Exception("Test error")
        
        with patch('logging.error') as mock_log:
            endpoint.run()
            mock_log.assert_called()
    
    def test_run_none_endpoint(self):
        """Test run with None json_rpc_endpoint"""
        endpoint = LspEndpoint(None)
        
        with patch('logging.error') as mock_log:
            endpoint.run()
            mock_log.assert_called_once()