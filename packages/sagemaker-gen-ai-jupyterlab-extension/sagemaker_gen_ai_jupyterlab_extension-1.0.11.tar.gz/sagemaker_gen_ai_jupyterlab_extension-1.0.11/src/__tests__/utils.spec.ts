import { getErrorMessage, hasError, getSelectionOrCellContent, insertToCursorPosition, interactiveDebuggingInfo } from '../utils';
import { INotebookTracker } from '@jupyterlab/notebook';

// Mock the INotebookTracker interface
const createMockNotebookTracker = (options: {
  hasActiveCell?: boolean;
  cellType?: string;
  hasOutputs?: boolean;
  hasError?: boolean;
  errorDetails?: { ename: string; evalue: string; traceback: string[] };
  selectedText?: string;
  selectionRange?: {
    start: { line: number; column: number };
    end: { line: number; column: number };
  };
  cellContent?: string;
  hasDebuggingInfo?: boolean;
  debuggingData?: any;
  cellId?: string;
}): INotebookTracker => {
  const {
    hasActiveCell = true,
    cellType = 'code',
    hasOutputs = true,
    hasError = false,
    errorDetails = {
      ename: 'Error',
      evalue: 'Test error',
      traceback: ['line1', 'line2']
    },
    selectionRange = {
      start: { line: 0, column: 0 },
      end: { line: 0, column: 0 }
    },
    cellContent = 'print("Hello World")',
    hasDebuggingInfo = false,
    debuggingData = {
      instruction_file: 'test_instruction.json',
      session_type: 'test_session',
      debugging_info_folder: '/path/to/debug',
      magic_command: '%debug'
    },
    cellId = 'test-cell-id'
  } = options;

  // Create outputs array with or without error or debugging info
  const outputs = {
    length: hasOutputs ? (hasError || hasDebuggingInfo ? 1 : 0) : 0,
    get: jest.fn().mockImplementation(() => {
      if (hasError) {
        return {
          type: 'error',
          _raw: errorDetails
        };
      }
      if (hasDebuggingInfo) {
        return {
          type: 'display_data',
          data: {
            'application/sagemaker-interactive-debugging': debuggingData
          }
        };
      }
      return { type: 'execute_result' };
    })
  };

  // Create editor with selection capabilities
  const editor = {
    getSelection: jest.fn().mockReturnValue(selectionRange),
    getOffsetAt: jest.fn().mockImplementation(pos => {
      return pos.column;
    }),
    model: {
      sharedModel: {
        getSource: jest.fn().mockReturnValue(cellContent)
      }
    }
  };

  // Create active cell
  const activeCell = hasActiveCell
    ? {
        model: {
          type: cellType,
          id: cellId,
          outputs: hasOutputs ? outputs : undefined,
          sharedModel: {
            getSource: jest.fn().mockReturnValue(cellContent)
          }
        },
        editor: editor
      }
    : null;

  // Create notebook widget
  const notebookWidget = {
    content: {
      activeCell: activeCell
    }
  };

  // Create and return the mock tracker
  return {
    currentWidget: notebookWidget
  } as unknown as INotebookTracker;
};

describe('utils.ts', () => {
  describe('getErrorMessage', () => {
    it('should return empty string when no notebook is active', () => {
      const mockTracker = createMockNotebookTracker({ hasActiveCell: false });
      expect(getErrorMessage(mockTracker)).toBe('');
    });

    it('should return empty string when active cell is not code cell', () => {
      const mockTracker = createMockNotebookTracker({ cellType: 'markdown' });
      expect(getErrorMessage(mockTracker)).toBe('');
    });

    it('should return empty string when no outputs exist', () => {
      const mockTracker = createMockNotebookTracker({ hasOutputs: false });
      expect(getErrorMessage(mockTracker)).toBe('');
    });

    it('should return empty string when no error output exists', () => {
      const mockTracker = createMockNotebookTracker({ hasError: false });
      expect(getErrorMessage(mockTracker)).toBe('');
    });

    it('should return formatted error message when error output exists', () => {
      const errorDetails = {
        ename: 'TypeError',
        evalue: 'cannot convert NaN to integer',
        traceback: ['line1', 'line2']
      };
      const mockTracker = createMockNotebookTracker({
        hasError: true,
        errorDetails: errorDetails
      });

      const expected = `ErrorType: ${errorDetails.ename}; ErrorValue: ${errorDetails.evalue}; Trace: ${errorDetails.traceback.toString()}`;
      expect(getErrorMessage(mockTracker)).toBe(expected);
    });
  });

  describe('hasError', () => {
    it('should return false when no notebook is active', () => {
      const mockTracker = createMockNotebookTracker({ hasActiveCell: false });
      expect(hasError(mockTracker)).toBe(false);
    });

    it('should return false when active cell is not code cell', () => {
      const mockTracker = createMockNotebookTracker({ cellType: 'markdown' });
      expect(hasError(mockTracker)).toBe(false);
    });

    it('should return false when no outputs exist', () => {
      const mockTracker = createMockNotebookTracker({ hasOutputs: false });
      expect(hasError(mockTracker)).toBe(false);
    });

    it('should return false when no error output exists', () => {
      const mockTracker = createMockNotebookTracker({ hasError: false });
      expect(hasError(mockTracker)).toBe(false);
    });

    it('should return true when error output exists', () => {
      const mockTracker = createMockNotebookTracker({ hasError: true });
      expect(hasError(mockTracker)).toBe(true);
    });
  });

  describe('interactiveDebuggingInfo', () => {
    it('should return null when no notebook is active', () => {
      const mockTracker = createMockNotebookTracker({ hasActiveCell: false });
      expect(interactiveDebuggingInfo(mockTracker)).toBeNull();
    });

    it('should return null when active cell is not code cell', () => {
      const mockTracker = createMockNotebookTracker({ cellType: 'markdown' });
      expect(interactiveDebuggingInfo(mockTracker)).toBeNull();
    });

    it('should return null when no outputs exist', () => {
      const mockTracker = createMockNotebookTracker({ hasOutputs: false });
      expect(interactiveDebuggingInfo(mockTracker)).toBeNull();
    });

    it('should return null when no debugging info exists', () => {
      const mockTracker = createMockNotebookTracker({ hasDebuggingInfo: false });
      expect(interactiveDebuggingInfo(mockTracker)).toBeNull();
    });

    it('should return debugging info when it exists', () => {
      const debuggingData = {
        instruction_file: 'test_instruction.json',
        session_type: 'test_session',
        debugging_info_folder: '/path/to/debug',
        magic_command: '%debug'
      };
      const cellId = 'test-cell-id-123';
      
      const mockTracker = createMockNotebookTracker({
        hasDebuggingInfo: true,
        debuggingData: debuggingData,
        cellId: cellId
      });

      const result = interactiveDebuggingInfo(mockTracker);
      expect(result).not.toBeNull();
      expect(result).toEqual({
        instructionFile: debuggingData.instruction_file,
        cellId: cellId,
        sessionType: debuggingData.session_type,
        debuggingInfoFolder: debuggingData.debugging_info_folder,
        magicCommand: debuggingData.magic_command
      });
    });

    it('should handle missing fields in debugging data', () => {
      const debuggingData = {
        // Missing some fields
        instruction_file: 'test_instruction.json'
        // No session_type, debugging_info_folder, or magic_command
      };
      const cellId = 'test-cell-id-123';
      
      const mockTracker = createMockNotebookTracker({
        hasDebuggingInfo: true,
        debuggingData: debuggingData,
        cellId: cellId
      });

      const result = interactiveDebuggingInfo(mockTracker);
      expect(result).not.toBeNull();
      expect(result).toEqual({
        instructionFile: debuggingData.instruction_file,
        cellId: cellId,
        sessionType: "",
        debuggingInfoFolder: "",
        magicCommand: ""
      });
    });

    it('should handle empty debugging data', () => {
      const debuggingData = {};
      const cellId = 'test-cell-id-123';
      
      const mockTracker = createMockNotebookTracker({
        hasDebuggingInfo: true,
        debuggingData: debuggingData,
        cellId: cellId
      });

      const result = interactiveDebuggingInfo(mockTracker);
      expect(result).not.toBeNull();
      expect(result).toEqual({
        instructionFile: "",
        cellId: cellId,
        sessionType: "",
        debuggingInfoFolder: "",
        magicCommand: ""
      });
    });
  });

  describe('getSelectionOrCellContent', () => {
    it('should return empty string when no notebook is active', () => {
      const mockTracker = createMockNotebookTracker({ hasActiveCell: false });
      expect(getSelectionOrCellContent(mockTracker)).toBe('');
    });

    it('should return empty string when active cell is not code cell', () => {
      const mockTracker = createMockNotebookTracker({ cellType: 'markdown' });
      expect(getSelectionOrCellContent(mockTracker)).toBe('');
    });

    it('should return cell content when no text is selected', () => {
      const cellContent = 'print("Hello World")';
      const mockTracker = createMockNotebookTracker({
        cellContent: cellContent,
        selectionRange: {
          start: { line: 0, column: 0 },
          end: { line: 0, column: 0 }
        }
      });
      expect(getSelectionOrCellContent(mockTracker)).toBe(cellContent);
    });

    it('should return selected text when text is selected', () => {
      const cellContent = 'print("Hello World")';
      const mockTracker = createMockNotebookTracker({
        cellContent: cellContent,
        selectionRange: {
          start: { line: 0, column: 0 },
          end: { line: 0, column: 5 }
        }
      });
      expect(getSelectionOrCellContent(mockTracker)).toBe('print');
    });

    it('should return selected text for middle of string selection', () => {
      const cellContent = 'print("Hello World")';
      const mockTracker = createMockNotebookTracker({
        cellContent: cellContent,
        selectionRange: {
          start: { line: 0, column: 7 },
          end: { line: 0, column: 12 }
        }
      });
      expect(getSelectionOrCellContent(mockTracker)).toBe('Hello');
    });

    it('should return error message and code when verb is Fix and cell has error', () => {
      const cellContent = 'print(undefined_variable)';
      const errorDetails = {
        ename: 'NameError',
        evalue: "name 'undefined_variable' is not defined",
        traceback: ['line1', 'line2']
      };

      const mockTracker = createMockNotebookTracker({
        cellContent: cellContent,
        hasError: true,
        errorDetails: errorDetails
      });

      const errorMessage = `ErrorType: ${errorDetails.ename}; ErrorValue: ${errorDetails.evalue}; Trace: ${errorDetails.traceback.toString()}`;
      const expectedFormat = `Code:\n${cellContent}\n\nError:\n${errorMessage}`;

      const result = getSelectionOrCellContent(mockTracker, 'Fix');
      expect(result).toBe(expectedFormat);
    });
  });

  describe('insertToCursorPosition', () => {
    let mockNotebookTracker: INotebookTracker;
    let mockEditor: any;
    let mockActiveCell: any;
    let mockNotebook: any;
    let mockSharedModel: any;

    beforeEach(() => {
      jest.clearAllMocks();

      mockSharedModel = {
        source: 'existing code'
      };

      mockEditor = {
        getCursorPosition: jest.fn().mockReturnValue({
          line: 0,
          column: 8
        }),
        getOffsetAt: jest.fn(position => {
          return position.column;
        }),
        getPositionAt: jest.fn(offset => {
          return { line: 0, column: offset };
        }),
        setCursorPosition: jest.fn(),
        model: {
          sharedModel: mockSharedModel
        }
      };

      mockActiveCell = {
        model: {
          type: 'code'
        },
        editor: mockEditor
      };

      mockNotebook = {
        content: {
          activeCell: mockActiveCell
        }
      };

      mockNotebookTracker = {
        currentWidget: mockNotebook
      } as unknown as INotebookTracker;
    });

    it('should insert code at cursor position', () => {
      const codeToInsert = 'new code';
      insertToCursorPosition(mockNotebookTracker, codeToInsert);
      expect(mockEditor.getOffsetAt).toHaveBeenCalledWith({
        line: 0,
        column: 8
      });
      // After "existing" (8 chars), insert "new code", then "code"
      expect(mockSharedModel.source).toBe('existingnew code code');
      expect(mockEditor.setCursorPosition).toHaveBeenCalledWith({
        line: 0,
        column: 16
      });
    });

    it('should insert code at the beginning of content', () => {
      const codeToInsert = 'prefix ';
      mockEditor.getCursorPosition.mockReturnValue({
        line: 0,
        column: 0
      });
      insertToCursorPosition(mockNotebookTracker, codeToInsert);
      expect(mockSharedModel.source).toBe('prefix existing code');
      expect(mockEditor.setCursorPosition).toHaveBeenCalledWith({
        line: 0,
        column: 7
      });
    });

    it('should insert code at the end of content', () => {
      const codeToInsert = ' suffix';
      mockEditor.getCursorPosition.mockReturnValue({
        line: 0,
        column: 13
      });
      mockEditor.getOffsetAt.mockReturnValue(13); // End of "existing code"
      insertToCursorPosition(mockNotebookTracker, codeToInsert);
      expect(mockSharedModel.source).toBe('existing code suffix');
      expect(mockEditor.setCursorPosition).toHaveBeenCalledWith({
        line: 0,
        column: 20
      });
    });

    it('should do nothing when there is no active cell', () => {
      (mockNotebookTracker as any).currentWidget = null;
      const codeToInsert = 'new code';
      insertToCursorPosition(mockNotebookTracker, codeToInsert);
      expect(mockSharedModel.source).toBe('existing code'); // Unchanged
    });

    it('should do nothing when active cell is not a code cell', () => {
      mockActiveCell.model.type = 'markdown';
      const codeToInsert = 'new code';
      insertToCursorPosition(mockNotebookTracker, codeToInsert);
      expect(mockSharedModel.source).toBe('existing code'); // Unchanged
    });

    it('should do nothing when active cell has no editor', () => {
      mockActiveCell.editor = null;
      const codeToInsert = 'new code';
      insertToCursorPosition(mockNotebookTracker, codeToInsert);
      expect(mockSharedModel.source).toBe('existing code'); // Unchanged
    });

    it('should handle errors during insertion', () => {
      const codeToInsert = 'new code';
      const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation();
      mockEditor.getOffsetAt.mockImplementation(() => {
        throw new Error('Test error');
      });

      insertToCursorPosition(mockNotebookTracker, codeToInsert);
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        'Error inserting the code:',
        expect.any(Error)
      );
      expect(mockSharedModel.source).toBe('existing code'); // Unchanged
    });

    it('should handle multiline code insertion', () => {
      const codeToInsert = 'line1\nline2\nline3';
      insertToCursorPosition(mockNotebookTracker, codeToInsert);
      expect(mockSharedModel.source).toBe('existingline1\nline2\nline3 code');
      expect(mockEditor.setCursorPosition).toHaveBeenCalledWith({
        line: 0,
        column: 25
      });
    });

    it('should handle insertion when newPosition is undefined', () => {
      const codeToInsert = 'new code';
      mockEditor.getPositionAt.mockReturnValue(undefined);
      insertToCursorPosition(mockNotebookTracker, codeToInsert);
      expect(mockSharedModel.source).toBe('existingnew code code');
      expect(mockEditor.setCursorPosition).not.toHaveBeenCalled();
    });
  });
});
