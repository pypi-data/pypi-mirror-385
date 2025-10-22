import pytest
from unittest.mock import Mock, patch
from pydantic import ValidationError
from sagemaker_gen_ai_jupyterlab_extension.pylspclient.lsp_client import LspClient
from sagemaker_gen_ai_jupyterlab_extension.pylspclient.lsp_pydantic_strcuts import (
    TextDocumentItem, TextDocumentIdentifier, Position, CompletionContext,
    DocumentSymbol, SymbolInformation, Location, LocationLink, SignatureHelp,
    CompletionItem, CompletionList, WorkspaceEdit
)


class TestLspClient:
    
    def test_init(self):
        """Test LspClient initialization"""
        mock_endpoint = Mock()
        client = LspClient(mock_endpoint)
        
        assert client.lsp_endpoint == mock_endpoint
    
    def test_initialize_success(self):
        """Test successful initialization"""
        mock_endpoint = Mock()
        mock_endpoint.call_method.return_value = {"capabilities": {}}
        client = LspClient(mock_endpoint)
        
        result = client.initialize(
            processId=1234,
            rootPath="/test/path",
            rootUri="file:///test/path",
            capabilities={},
            trace="on"
        )
        
        mock_endpoint.start.assert_called_once()
        mock_endpoint.call_method.assert_called_once_with(
            "initialize",
            processId=1234,
            rootPath="/test/path",
            rootUri="file:///test/path",
            initializationOptions=None,
            capabilities={},
            trace="on",
            workspaceFolders=None,
            clientInfo=None
        )
        assert result == {"capabilities": {}}
    
    def test_initialize_missing_capabilities(self):
        """Test initialization with missing capabilities"""
        mock_endpoint = Mock()
        client = LspClient(mock_endpoint)
        
        with pytest.raises(ValueError, match="capabilities is required"):
            client.initialize()
    
    def test_initialized(self):
        """Test initialized notification"""
        mock_endpoint = Mock()
        client = LspClient(mock_endpoint)
        
        client.initialized()
        
        mock_endpoint.send_notification.assert_called_once_with("initialized")
    
    def test_shutdown(self):
        """Test shutdown"""
        mock_endpoint = Mock()
        mock_endpoint.call_method.return_value = None
        client = LspClient(mock_endpoint)
        
        result = client.shutdown()
        
        mock_endpoint.stop.assert_called_once()
        mock_endpoint.call_method.assert_called_once_with("shutdown")
        assert result is None
    
    def test_exit(self):
        """Test exit notification"""
        mock_endpoint = Mock()
        client = LspClient(mock_endpoint)
        
        client.exit()
        
        mock_endpoint.send_notification.assert_called_once_with("exit")
    
    def test_did_open(self):
        """Test didOpen notification"""
        mock_endpoint = Mock()
        client = LspClient(mock_endpoint)
        
        text_doc = TextDocumentItem(
            uri="file:///test.py",
            languageId="python",
            version=1,
            text="print('hello')"
        )
        
        client.didOpen(text_doc)
        
        mock_endpoint.send_notification.assert_called_once_with(
            "textDocument/didOpen", textDocument=text_doc
        )
    
    def test_did_change(self):
        """Test didChange notification"""
        mock_endpoint = Mock()
        client = LspClient(mock_endpoint)
        
        text_doc = TextDocumentItem(
            uri="file:///test.py",
            languageId="python", 
            version=2,
            text="print('hello world')"
        )
        content_changes = [{"text": "print('hello world')"}]
        
        client.didChange(text_doc, content_changes)
        
        mock_endpoint.send_notification.assert_called_once_with(
            "textDocument/didChange",
            textDocument=text_doc,
            contentChanges=content_changes
        )
    
    def test_document_symbol_document_symbols(self):
        """Test documentSymbol returning DocumentSymbol list"""
        mock_endpoint = Mock()
        mock_endpoint.call_method.return_value = [
            {
                "name": "test_function",
                "kind": 12,
                "range": {
                    "start": {"line": 0, "character": 0},
                    "end": {"line": 5, "character": 0}
                },
                "selectionRange": {
                    "start": {"line": 0, "character": 4},
                    "end": {"line": 0, "character": 17}
                }
            }
        ]
        client = LspClient(mock_endpoint)
        
        text_doc = TextDocumentIdentifier(uri="file:///test.py")
        result = client.documentSymbol(text_doc)
        
        assert len(result) == 1
        assert isinstance(result[0], DocumentSymbol)
        assert result[0].name == "test_function"
    
    def test_document_symbol_symbol_information(self):
        """Test documentSymbol returning SymbolInformation list"""
        mock_endpoint = Mock()
        # Mock response that will fail DocumentSymbol validation but succeed with SymbolInformation
        mock_endpoint.call_method.return_value = [
            {
                "name": "test_function",
                "kind": 12,
                "location": {
                    "uri": "file:///test.py",
                    "range": {
                        "start": {"line": 0, "character": 0},
                        "end": {"line": 5, "character": 0}
                    }
                }
            }
        ]
        client = LspClient(mock_endpoint)
        
        text_doc = TextDocumentIdentifier(uri="file:///test.py")
        
        with patch('sagemaker_gen_ai_jupyterlab_extension.pylspclient.lsp_client.DocumentSymbol.model_validate', side_effect=ValidationError.from_exception_data('DocumentSymbol', [])):
            result = client.documentSymbol(text_doc)
        
        assert len(result) == 1
        assert isinstance(result[0], SymbolInformation)
    
    def test_type_definition(self):
        """Test typeDefinition request"""
        mock_endpoint = Mock()
        mock_endpoint.call_method.return_value = [
            {
                "uri": "file:///test.py",
                "range": {
                    "start": {"line": 0, "character": 0},
                    "end": {"line": 0, "character": 10}
                }
            }
        ]
        client = LspClient(mock_endpoint)
        
        text_doc = TextDocumentIdentifier(uri="file:///test.py")
        position = Position(line=1, character=5)
        
        result = client.typeDefinition(text_doc, position)
        
        mock_endpoint.call_method.assert_called_once_with(
            "textDocument/typeDefinition", textDocument=text_doc, position=position
        )
        assert len(result) == 1
        assert isinstance(result[0], Location)
    
    def test_signature_help(self):
        """Test signatureHelp request"""
        mock_endpoint = Mock()
        mock_endpoint.call_method.return_value = {
            "signatures": [
                {
                    "label": "test_function(param1: str)",
                    "parameters": [
                        {"label": "param1: str"}
                    ]
                }
            ],
            "activeSignature": 0,
            "activeParameter": 0
        }
        client = LspClient(mock_endpoint)
        
        text_doc = TextDocumentIdentifier(uri="file:///test.py")
        position = Position(line=1, character=5)
        
        result = client.signatureHelp(text_doc, position)
        
        mock_endpoint.call_method.assert_called_once_with(
            "textDocument/signatureHelp", textDocument=text_doc, position=position
        )
        assert isinstance(result, SignatureHelp)
    
    def test_completion_list(self):
        """Test completion returning CompletionList"""
        mock_endpoint = Mock()
        mock_endpoint.call_method.return_value = {
            "isIncomplete": False,
            "items": [
                {"label": "test_item", "kind": 1}
            ]
        }
        client = LspClient(mock_endpoint)
        
        text_doc = TextDocumentIdentifier(uri="file:///test.py")
        position = Position(line=1, character=5)
        context = CompletionContext(triggerKind=1)
        
        result = client.completion(text_doc, position, context)
        
        assert isinstance(result, CompletionList)
        assert result.isIncomplete is False
    
    def test_completion_items(self):
        """Test completion returning CompletionItem list"""
        mock_endpoint = Mock()
        mock_endpoint.call_method.return_value = [
            {"label": "test_item", "kind": 1}
        ]
        client = LspClient(mock_endpoint)
        
        text_doc = TextDocumentIdentifier(uri="file:///test.py")
        position = Position(line=1, character=5)
        context = CompletionContext(triggerKind=1)
        
        result = client.completion(text_doc, position, context)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], CompletionItem)
    
    def test_declaration_single_location(self):
        """Test declaration returning single Location"""
        mock_endpoint = Mock()
        mock_endpoint.call_method.return_value = {
            "uri": "file:///test.py",
            "range": {
                "start": {"line": 0, "character": 0},
                "end": {"line": 0, "character": 10}
            }
        }
        client = LspClient(mock_endpoint)
        
        text_doc = TextDocumentIdentifier(uri="file:///test.py")
        position = Position(line=1, character=5)
        
        result = client.declaration(text_doc, position)
        
        assert isinstance(result, Location)
    
    def test_declaration_location_list(self):
        """Test declaration returning Location list"""
        mock_endpoint = Mock()
        mock_endpoint.call_method.return_value = [
            {
                "uri": "file:///test.py",
                "range": {
                    "start": {"line": 0, "character": 0},
                    "end": {"line": 0, "character": 10}
                }
            }
        ]
        client = LspClient(mock_endpoint)
        
        text_doc = TextDocumentIdentifier(uri="file:///test.py")
        position = Position(line=1, character=5)
        
        result = client.declaration(text_doc, position)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], Location)
    
    def test_declaration_location_link_list(self):
        """Test declaration returning LocationLink list"""
        mock_endpoint = Mock()
        mock_endpoint.call_method.return_value = [
            {
                "targetUri": "https://example.com/test.py",
                "targetRange": {
                    "start": {"line": 0, "character": 0},
                    "end": {"line": 0, "character": 10}
                },
                "targetSelectionRange": {
                    "start": {"line": 0, "character": 0},
                    "end": {"line": 0, "character": 10}
                },
                "originSelectionRange": {
                    "start": {"line": 1, "character": 5},
                    "end": {"line": 1, "character": 10}
                }
            }
        ]
        client = LspClient(mock_endpoint)
        
        text_doc = TextDocumentIdentifier(uri="file:///test.py")
        position = Position(line=1, character=5)
        
        with patch('sagemaker_gen_ai_jupyterlab_extension.pylspclient.lsp_client.Location.model_validate', side_effect=ValidationError.from_exception_data('Location', [])):
            result = client.declaration(text_doc, position)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], LocationLink)
    
    def test_definition_single_location(self):
        """Test definition returning single Location"""
        mock_endpoint = Mock()
        mock_endpoint.call_method.return_value = {
            "uri": "file:///test.py",
            "range": {
                "start": {"line": 0, "character": 0},
                "end": {"line": 0, "character": 10}
            }
        }
        client = LspClient(mock_endpoint)
        
        text_doc = TextDocumentIdentifier(uri="file:///test.py")
        position = Position(line=1, character=5)
        
        result = client.definition(text_doc, position)
        
        assert isinstance(result, Location)
    
    def test_rename(self):
        """Test rename request"""
        mock_endpoint = Mock()
        mock_endpoint.call_method.return_value = {
            "changes": {
                "file:///test.py": [
                    {
                        "range": {
                            "start": {"line": 0, "character": 0},
                            "end": {"line": 0, "character": 10}
                        },
                        "newText": "new_name"
                    }
                ]
            }
        }
        client = LspClient(mock_endpoint)
        
        text_doc = TextDocumentIdentifier(uri="file:///test.py")
        position = Position(line=1, character=5)
        new_name = "new_name"
        
        result = client.rename(text_doc, position, new_name)
        
        mock_endpoint.call_method.assert_called_once_with(
            "textDocument/rename",
            textDocument=text_doc,
            position=position.dict(),
            newName=new_name
        )
        assert isinstance(result, WorkspaceEdit)
        assert "file:///test.py" in result.changes