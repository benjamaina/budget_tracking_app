// Utility functions for handling API errors from Django REST Framework

/**
 * Extracts and formats error messages from Django REST Framework responses
 * Handles various error formats including field errors, non-field errors, and general errors
 */
export const extractErrorMessage = (error: any): string => {
  if (!error?.response?.data) {
    return "An unexpected error occurred";
  }

  const data = error.response.data;

  // Handle simple detail/message format
  if (typeof data === 'string') {
    return data;
  }

  if (data.detail) {
    return data.detail;
  }

  if (data.message) {
    return data.message;
  }

  // Handle field-specific errors
  const fieldErrors: string[] = [];
  
  // Handle non_field_errors (general validation errors)
  if (data.non_field_errors && Array.isArray(data.non_field_errors)) {
    fieldErrors.push(...data.non_field_errors);
  }

  // Handle individual field errors
  Object.keys(data).forEach(field => {
    if (field !== 'non_field_errors' && Array.isArray(data[field])) {
      const fieldName = field.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
      data[field].forEach((msg: string) => {
        fieldErrors.push(`${fieldName}: ${msg}`);
      });
    } else if (field !== 'non_field_errors' && typeof data[field] === 'string') {
      const fieldName = field.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
      fieldErrors.push(`${fieldName}: ${data[field]}`);
    }
  });

  if (fieldErrors.length > 0) {
    return fieldErrors.join('\n');
  }

  // Fallback for any other error format
  return "Validation error occurred";
};

/**
 * Formats error messages for toast notifications
 * Splits multiple errors into bullet points for better readability
 */
export const formatErrorForToast = (error: any): { title: string; description: string } => {
  // Handle protected object deletion errors
  if (error?.response?.data?.detail && error?.response?.data?.related_objects) {
    const detail = error.response.data.detail;
    const relatedObjects = error.response.data.related_objects;
    return {
      title: "Cannot Delete",
      description: `${detail}\nRelated items: ${relatedObjects.join(', ')}`
    };
  }

  const message = extractErrorMessage(error);
  
  // If multiple errors, format with bullet points
  if (message.includes('\n')) {
    const errors = message.split('\n');
    return {
      title: "Validation Error",
      description: errors.map(err => `• ${err}`).join('\n')
    };
  }

  return {
    title: "Error",
    description: message
  };
};