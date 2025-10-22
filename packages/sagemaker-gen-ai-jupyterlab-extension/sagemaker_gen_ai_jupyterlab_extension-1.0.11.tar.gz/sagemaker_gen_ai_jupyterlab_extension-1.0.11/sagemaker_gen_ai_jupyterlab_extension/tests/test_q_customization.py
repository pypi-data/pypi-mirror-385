import unittest
import tempfile
import os
import json
from unittest.mock import Mock, patch, MagicMock
from ..lsp_server_connection import LspServerConnection


class TestQCustomization(unittest.TestCase):
    
    def setUp(self):
        self.lsp_connection = LspServerConnection()
        self.lsp_connection.lsp_endpoint = Mock()
        
    def test_update_q_customization_with_arn(self):
        test_arn = "arn:aws:codewhisperer:us-east-1:123456789012:customization/test-customization"
        
        self.lsp_connection.update_q_customization(test_arn)
        
        self.lsp_connection.lsp_endpoint.send_notification.assert_called_once_with(
            "workspace/didChangeConfiguration"
        )
    
    def test_update_q_customization_empty_arn(self):
        self.lsp_connection.update_q_customization("")
        
        self.lsp_connection.lsp_endpoint.send_notification.assert_not_called()
    
    def test_update_q_customization_none_arn(self):
        self.lsp_connection.update_q_customization(None)
        
        self.lsp_connection.lsp_endpoint.send_notification.assert_not_called()
    
    @patch('sagemaker_gen_ai_jupyterlab_extension.lsp_server_connection.extract_q_customization_arn')
    def test_handle_workspace_configuration_aws_q(self, mock_extract):
        mock_extract.return_value = "test-arn"
        params = {
            "items": [
                {"section": "aws.q"},
                {"section": "other.section"}
            ]
        }
        
        mock_callback = MagicMock()
        with patch.object(self.lsp_connection, 'get_response_callback', return_value=mock_callback):
            self.lsp_connection.handle_workspace_configuration(params, 1)
            
            mock_callback.assert_called_once()
            call_args = mock_callback.call_args[0][0]
            expected_result = [
                {"customization": "test-arn"},
                None,
                None
            ]
            self.assertEqual(call_args["params"]["result"], expected_result)
    
    @patch('sagemaker_gen_ai_jupyterlab_extension.lsp_server_connection.extract_q_customization_arn')
    def test_handle_workspace_configuration_no_arn(self, mock_extract):
        mock_extract.return_value = None
        params = {
            "items": [{"section": "aws.q"}]
        }
        
        mock_callback = MagicMock()
        with patch.object(self.lsp_connection, 'get_response_callback', return_value=mock_callback):
            self.lsp_connection.handle_workspace_configuration(params, 1)
            
            mock_callback.assert_called_once()
            call_args = mock_callback.call_args[0][0]
            expected_result = [{"customization": ""}, None]
            self.assertEqual(call_args["params"]["result"], expected_result)
    
    def test_handle_workspace_configuration_empty_params(self):
        # When params is empty, the method returns early without calling callback
        result = self.lsp_connection.handle_workspace_configuration({}, 1)
        self.assertEqual(result, [])
    
    def test_handle_workspace_configuration_no_items(self):
        # When no items key exists, the method returns early without calling callback
        result = self.lsp_connection.handle_workspace_configuration({"other": "data"}, 1)
        self.assertEqual(result, [])
    
    def test_get_q_customizations(self):
        mock_response = {"customizations": ["arn1", "arn2"]}
        self.lsp_connection.lsp_endpoint.call_method.return_value = mock_response
        
        result = self.lsp_connection.get_q_customizations()
        
        self.lsp_connection.lsp_endpoint.call_method.assert_called_once_with(
            "aws/getConfigurationFromServer", 
            section="aws.q.customizations"
        )
        self.assertEqual(result, mock_response)
    
    def test_get_q_customizations_error(self):
        self.lsp_connection.lsp_endpoint.call_method.side_effect = Exception("Test error")
        
        result = self.lsp_connection.get_q_customizations()
        
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()