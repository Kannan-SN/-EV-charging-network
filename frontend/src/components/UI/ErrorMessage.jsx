
// frontend/src/components/UI/ErrorMessage.jsx
import React from 'react';
import { AlertCircle, X } from 'lucide-react';

const ErrorMessage = ({ 
  message, 
  onClose, 
  type = 'error',
  className = '' 
}) => {
  const typeClasses = {
    error: 'bg-red-50 border-red-200 text-red-800',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    info: 'bg-blue-50 border-blue-200 text-blue-800'
  };

  const iconColors = {
    error: 'text-red-400',
    warning: 'text-yellow-400',
    info: 'text-blue-400'
  };

  return (
    <div className={`border rounded-lg p-4 ${typeClasses[type]} ${className}`}>
      <div className="flex items-start">
        <AlertCircle className={`h-5 w-5 ${iconColors[type]} mt-0.5 mr-3 flex-shrink-0`} />
        <div className="flex-1">
          <p className="text-sm">{message}</p>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className={`ml-3 flex-shrink-0 ${iconColors[type]} hover:opacity-70`}
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>
    </div>
  );
};

export default ErrorMessage;