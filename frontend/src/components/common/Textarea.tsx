import React from 'react';

interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

export const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ label, error, helperText, className = '', ...props }, ref) => {
    const textareaClasses = `w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 transition-colors
      ${error
        ? 'border-red-500 focus:ring-red-500 focus:border-red-500'
        : 'border-gray-300 focus:ring-indigo-500 focus:border-indigo-500'
      }
      ${props.disabled ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'}
      ${className}`;

    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {label}
            {props.required && <span className="text-red-500 ml-1">*</span>}
          </label>
        )}
        <textarea
          ref={ref}
          className={textareaClasses}
          {...props}
        />
        {error && (
          <p className="mt-1 text-sm text-red-600">{error}</p>
        )}
        {helperText && !error && (
          <p className="mt-1 text-sm text-gray-500">{helperText}</p>
        )}
      </div>
    );
  }
);

Textarea.displayName = 'Textarea';
