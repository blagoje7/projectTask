/**
 * Formatting utility functions
 */

/**
 * Format Unix timestamp to readable date
 */
export function formatDate(timestamp) {
  if (!timestamp) return 'N/A';
  const date = new Date(timestamp * 1000);
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric' 
  });
}

/**
 * Format Unix timestamp to readable date and time
 */
export function formatDateTime(timestamp) {
  if (!timestamp) return 'N/A';
  const date = new Date(timestamp * 1000);
  return date.toLocaleString('en-US', { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

/**
 * Format status string to display format
 */
export function formatStatus(status) {
  if (!status) return 'N/A';
  return status.split('_').map(word => 
    word.charAt(0).toUpperCase() + word.slice(1)
  ).join(' ');
}

/**
 * Capitalize first letter of string
 */
export function capitalize(str) {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1);
}

/**
 * Get initials from first and last name
 */
export function getInitials(firstName, lastName) {
  const first = firstName ? firstName[0].toUpperCase() : '';
  const last = lastName ? lastName[0].toUpperCase() : '';
  return first + last;
}
