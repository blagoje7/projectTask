/**
 * Application constants
 */

// User Roles
export const ROLE_ADMIN = 'admin';
export const ROLE_MANAGER = 'manager';
export const ROLE_USER = 'user';

// Task Status
export const STATUS_TODO = 'to_do';
export const STATUS_IN_PROGRESS = 'in_progress';
export const STATUS_FOR_REVIEW = 'for_review';
export const STATUS_DONE = 'done';

export const STATUS_LABELS = {
  [STATUS_TODO]: 'To Do',
  [STATUS_IN_PROGRESS]: 'In Progress',
  [STATUS_FOR_REVIEW]: 'For Review',
  [STATUS_DONE]: 'Done'
};

// Task Priority
export const PRIORITY_LOW = 'low';
export const PRIORITY_MEDIUM = 'medium';
export const PRIORITY_HIGH = 'high';

export const PRIORITY_LABELS = {
  [PRIORITY_LOW]: 'Low',
  [PRIORITY_MEDIUM]: 'Medium',
  [PRIORITY_HIGH]: 'High'
};

// View Modes
export const VIEW_LIST = 'list';
export const VIEW_GRID = 'grid';
export const VIEW_CALENDAR = 'calendar';

// Local Storage Keys
export const LS_TOKEN = 'token';
export const LS_ROLE = 'role';
export const LS_USER_ID = 'userId';
export const LS_USERNAME = 'username';
