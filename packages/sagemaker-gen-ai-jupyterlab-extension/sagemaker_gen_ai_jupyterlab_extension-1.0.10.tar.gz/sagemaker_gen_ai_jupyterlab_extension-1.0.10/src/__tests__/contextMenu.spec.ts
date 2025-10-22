import { registerContextMenuActions, GenericCommandVerb } from '../contextMenu';
import { postToWebView } from '../webview';

// Mock the webview module
jest.mock('../webview', () => ({
  postToWebView: jest.fn()
}));

// Mock the utils module using factory pattern
jest.mock('../utils', () => {
  return {
    getSelectionOrCellContent: jest.fn(() => 'test code'),
    hasError: jest.fn(() => true),
    interactiveDebuggingInfo: jest.fn()
  };
});

// Import the mocked modules
import * as utils from '../utils';

describe('contextMenu', () => {
  let mockApp: any;
  let mockNotebookTracker: any;
  let mockShowFlareWidget: jest.Mock;
  let mockActiveCell: any;
  let mockEditor: any;
  let mockOutputs: any;
  
  // Get the mocked functions with proper typing
  const mockGetSelectionOrCellContent = utils.getSelectionOrCellContent as jest.Mock;
  const mockHasError = utils.hasError as jest.Mock;
  const mockInteractiveDebuggingInfo = utils.interactiveDebuggingInfo as jest.Mock;

  beforeEach(() => {
    jest.clearAllMocks();
    jest.spyOn(console, 'log').mockImplementation();
    jest.spyOn(console, 'warn').mockImplementation();

    // Reset mocks to default values
    mockGetSelectionOrCellContent.mockReturnValue('test code');
    mockHasError.mockReturnValue(true);
    mockInteractiveDebuggingInfo.mockReturnValue(null);

    mockShowFlareWidget = jest.fn();

    mockOutputs = {
      length: 0,
      get: jest.fn()
    };

    mockEditor = {
      getSelection: jest.fn(() => ({
        start: { line: 0, column: 0 },
        end: { line: 0, column: 0 }
      })),
      model: {
        sharedModel: {
          getSource: jest.fn(() => 'test code')
        }
      },
      getOffsetAt: jest.fn(() => 0)
    };

    mockActiveCell = {
      model: {
        type: 'code',
        sharedModel: {
          getSource: jest.fn(() => 'test code')
        },
        outputs: mockOutputs
      },
      editor: mockEditor
    };

    mockNotebookTracker = {
      currentWidget: {
        content: {
          activeCell: mockActiveCell
        }
      }
    };

    mockApp = {
      commands: {
        addCommand: jest.fn(),
        execute: jest.fn()
      },
      contextMenu: {
        addItem: jest.fn()
      }
    };
  });

  it('should register commands for all verbs', () => {
    registerContextMenuActions({
      app: mockApp,
      notebookTracker: mockNotebookTracker,
      showFlareWidget: mockShowFlareWidget
    });

    const verbs: GenericCommandVerb[] = [
      'Explain',
      'Refactor',
      'Fix',
      'Optimize'
    ];
    expect(mockApp.commands.addCommand).toHaveBeenCalledTimes(verbs.length);

    verbs.forEach(verb => {
      expect(mockApp.commands.addCommand).toHaveBeenCalledWith(
        `sagemaker-gen-ai:${verb.toLowerCase()}`,
        expect.objectContaining({
          label: verb,
          isEnabled: expect.any(Function),
          execute: expect.any(Function)
        })
      );
    });
  });

  it('should add context menu items for code cells and file editors', () => {
    registerContextMenuActions({
      app: mockApp,
      notebookTracker: mockNotebookTracker,
      showFlareWidget: mockShowFlareWidget
    });

    expect(mockApp.contextMenu.addItem).toHaveBeenCalledTimes(1);
    expect(mockApp.contextMenu.addItem).toHaveBeenCalledWith(
      expect.objectContaining({
        type: 'submenu',
        selector: '.jp-CodeCell',
        rank: 0
      })
    );
  });

  describe('command execution', () => {
    beforeEach(() => {
      registerContextMenuActions({
        app: mockApp,
        notebookTracker: mockNotebookTracker,
        showFlareWidget: mockShowFlareWidget
      });
    });

    it('should execute explain command with cell content', () => {
      const explainCommand = mockApp.commands.addCommand.mock.calls.find(
        (call: any) => call[0] === 'sagemaker-gen-ai:explain'
      )[1];

      explainCommand.execute();

      expect(mockShowFlareWidget).toHaveBeenCalled();
      expect(postToWebView).toHaveBeenCalledWith({
        command: 'genericCommand',
        params: {
          genericCommand: 'Explain',
          selection: 'test code',
          triggerType: 'contextMenu'
        }
      });
    });

    it('should execute command with selected text when available', () => {
      // Mock the getSelectionOrCellContent to return selected text
      mockGetSelectionOrCellContent.mockReturnValue('selected');

      const explainCommand = mockApp.commands.addCommand.mock.calls.find(
        (call: any) => call[0] === 'sagemaker-gen-ai:explain'
      )[1];

      explainCommand.execute();

      expect(postToWebView).toHaveBeenCalledWith({
        command: 'genericCommand',
        params: {
          genericCommand: 'Explain',
          selection: 'selected',
          triggerType: 'contextMenu'
        }
      });
    });

    it('should handle fix command with error output', () => {
      // Mock the getSelectionOrCellContent to return error message format
      mockGetSelectionOrCellContent.mockReturnValue(
        'Code:\ntest code\n\nError:\nErrorType: ValueError; ErrorValue: invalid value; Trace: line 1,line 2'
      );

      const fixCommand = mockApp.commands.addCommand.mock.calls.find(
        (call: any) => call[0] === 'sagemaker-gen-ai:fix'
      )[1];

      fixCommand.execute();

      expect(postToWebView).toHaveBeenCalledWith({
        command: 'genericCommand',
        params: {
          genericCommand: 'Fix',
          selection:
            'Code:\ntest code\n\nError:\nErrorType: ValueError; ErrorValue: invalid value; Trace: line 1,line 2',
          triggerType: 'contextMenu'
        }
      });
    });

    it('should use diagnose-with-amazon-q command when interactive debugging info is available', () => {
      // Mock the interactiveDebuggingInfo to return debugging data
      mockInteractiveDebuggingInfo.mockReturnValue({
        instructionFile: 'test_instruction.json',
        cellId: 'test-cell-id',
        sessionType: 'test-session',
        debuggingInfoFolder: '/path/to/debug',
        magicCommand: '%debug'
      });

      const fixCommand = mockApp.commands.addCommand.mock.calls.find(
        (call: any) => call[0] === 'sagemaker-gen-ai:fix'
      )[1];

      fixCommand.execute();

      // Should execute the diagnose command instead of showing flare widget
      expect(mockApp.commands.execute).toHaveBeenCalledWith(
        'sagemaker:diagnose-with-amazon-q',
        {
          cellId: 'test-cell-id',
          instructionFile: 'test_instruction.json'
        }
      );
      expect(mockShowFlareWidget).not.toHaveBeenCalled();
      expect(postToWebView).not.toHaveBeenCalled();
    });

    it('should fall back to regular fix behavior when diagnose command execution fails', () => {
      // Mock the interactiveDebuggingInfo to return debugging data
      mockInteractiveDebuggingInfo.mockReturnValue({
        instructionFile: 'test_instruction.json',
        cellId: 'test-cell-id',
        sessionType: 'test-session',
        debuggingInfoFolder: '/path/to/debug',
        magicCommand: '%debug'
      });

      // Make the execute command throw an error
      mockApp.commands.execute.mockImplementation(() => {
        throw new Error('Command not found');
      });

      const fixCommand = mockApp.commands.addCommand.mock.calls.find(
        (call: any) => call[0] === 'sagemaker-gen-ai:fix'
      )[1];

      fixCommand.execute();

      // Should log a warning
      expect(console.warn).toHaveBeenCalledWith(
        'Failed to execute sagemaker:diagnose-with-amazon-q, continuing with fallback logic',
        expect.any(Error)
      );

      // Should fall back to regular behavior
      expect(mockShowFlareWidget).toHaveBeenCalled();
      expect(postToWebView).toHaveBeenCalledWith({
        command: 'genericCommand',
        params: {
          genericCommand: 'Fix',
          selection: 'test code',
          triggerType: 'contextMenu'
        }
      });
    });

    it('should use regular fix behavior when debugging info is incomplete', () => {
      // Mock the interactiveDebuggingInfo to return incomplete debugging data
      mockInteractiveDebuggingInfo.mockReturnValue({
        instructionFile: '', // Empty instruction file
        cellId: 'test-cell-id',
        sessionType: 'test-session',
        debuggingInfoFolder: '/path/to/debug',
        magicCommand: '%debug'
      });

      const fixCommand = mockApp.commands.addCommand.mock.calls.find(
        (call: any) => call[0] === 'sagemaker-gen-ai:fix'
      )[1];

      fixCommand.execute();

      // Should not try to execute the diagnose command
      expect(mockApp.commands.execute).not.toHaveBeenCalled();
      
      // Should use regular behavior
      expect(mockShowFlareWidget).toHaveBeenCalled();
      expect(postToWebView).toHaveBeenCalledWith({
        command: 'genericCommand',
        params: {
          genericCommand: 'Fix',
          selection: 'test code',
          triggerType: 'contextMenu'
        }
      });
    });

    it('should use regular fix behavior when debugging info is null', () => {
      // Mock the interactiveDebuggingInfo to return null
      mockInteractiveDebuggingInfo.mockReturnValue(null);

      const fixCommand = mockApp.commands.addCommand.mock.calls.find(
        (call: any) => call[0] === 'sagemaker-gen-ai:fix'
      )[1];

      fixCommand.execute();

      // Should not try to execute the diagnose command
      expect(mockApp.commands.execute).not.toHaveBeenCalled();
      
      // Should use regular behavior
      expect(mockShowFlareWidget).toHaveBeenCalled();
      expect(postToWebView).toHaveBeenCalledWith({
        command: 'genericCommand',
        params: {
          genericCommand: 'Fix',
          selection: 'test code',
          triggerType: 'contextMenu'
        }
      });
    });
  });

  describe('isEnabled conditions', () => {
    beforeEach(() => {
      registerContextMenuActions({
        app: mockApp,
        notebookTracker: mockNotebookTracker,
        showFlareWidget: mockShowFlareWidget
      });
    });

    it('should enable fix command only when error exists', () => {
      const fixCommand = mockApp.commands.addCommand.mock.calls.find(
        (call: any) => call[0] === 'sagemaker-gen-ai:fix'
      )[1];

      // No error
      mockHasError.mockReturnValueOnce(false);
      expect(fixCommand.isEnabled()).toBe(false);

      // With error
      mockHasError.mockReturnValueOnce(true);
      expect(fixCommand.isEnabled()).toBe(true);
    });

    it('should always enable non-fix commands', () => {
      const explainCommand = mockApp.commands.addCommand.mock.calls.find(
        (call: any) => call[0] === 'sagemaker-gen-ai:explain'
      )[1];

      expect(explainCommand.isEnabled()).toBe(true);
    });
  });

  it('should handle missing notebook widget', () => {
    mockNotebookTracker.currentWidget = null;

    registerContextMenuActions({
      app: mockApp,
      notebookTracker: mockNotebookTracker,
      showFlareWidget: mockShowFlareWidget
    });

    // Mock getSelectionOrCellContent to return empty string when notebook widget is missing
    mockGetSelectionOrCellContent.mockReturnValue('');

    const explainCommand = mockApp.commands.addCommand.mock.calls.find(
      (call: any) => call[0] === 'sagemaker-gen-ai:explain'
    )[1];

    explainCommand.execute();

    expect(postToWebView).not.toHaveBeenCalled();
    expect(mockShowFlareWidget).not.toHaveBeenCalled();
  });
});
