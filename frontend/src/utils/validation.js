/**
 * Validation utility functions
 */

/**
 * Validate email format
 */
export function isValidEmail(email) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
}

/**
 * Validate password strength
 * At least 6 characters
 */
export function isValidPassword(password) {
  return password && password.length >= 6;
}

/**
 * Validate required field
 */
export function isRequired(value) {
  return value !== null && value !== undefined && value !== '';
}

/**
 * Validate form fields
 */
export function validateForm(fields) {
  const errors = {};
  
  for (const [key, value] of Object.entries(fields)) {
    if (!isRequired(value)) {
      errors[key] = `${key} is required`;
    }
  }
  
  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
}
