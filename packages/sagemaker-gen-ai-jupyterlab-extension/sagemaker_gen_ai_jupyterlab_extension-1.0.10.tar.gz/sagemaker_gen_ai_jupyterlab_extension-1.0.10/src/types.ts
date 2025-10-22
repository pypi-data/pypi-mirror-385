export type ContextCommandIconType =
  | 'file'
  | 'folder'
  | 'code-block'
  | 'list-add'
  | 'magic';

export type IconType =
  | ContextCommandIconType
  | 'help'
  | 'trash'
  | 'search'
  | 'calendar'
  | string;

/**
 * Configuration object for chat quick action.
 */
export interface QuickActionCommand {
  command: string;
  description?: string;
  placeholder?: string;
  icon?: IconType;
}

export interface ContextCommand extends QuickActionCommand {
  id?: string;
  route?: string[];
  label?: 'file' | 'folder' | 'code' | 'image';
  content?: Uint8Array;

  // Nested command groups under a command (e.g., Folders, Files)
  children?: ContextCommandGroup[];
}

export interface ContextCommandGroup {
  groupName?: string;

  // These are the actual .aws, .bash_history, etc. entries
  commands: ContextCommand[];
}

export interface ContextCommandParams {
  contextCommandGroups: {
    // Top-level structure: array of command entries like 'Folders', 'Files'
    commands: ContextCommand[];
  }[];
}

export interface FileContext {
  path: string;
}
