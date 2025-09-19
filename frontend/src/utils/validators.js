

export const validateLocation = (location) => {
  if (!location || typeof location !== 'string') {
    return 'Location is required';
  }
  
  if (location.trim().length < 2) {
    return 'Location must be at least 2 characters';
  }
  
  if (location.trim().length > 100) {
    return 'Location must be less than 100 characters';
  }
  
  return null;
};

export const validateRadius = (radius) => {
  const numRadius = Number(radius);
  
  if (isNaN(numRadius)) {
    return 'Radius must be a number';
  }
  
  if (numRadius < 1) {
    return 'Radius must be at least 1 km';
  }
  
  if (numRadius > 200) {
    return 'Radius cannot exceed 200 km';
  }
  
  return null;
};

export const validateBudget = (budget) => {
  const numBudget = Number(budget);
  
  if (isNaN(numBudget)) {
    return 'Budget must be a number';
  }
  
  if (numBudget < 100000) {
    return 'Budget must be at least ₹1 lakh';
  }
  
  if (numBudget > 100000000) {
    return 'Budget cannot exceed ₹10 crores';
  }
  
  return null;
};

export const validateStationType = (stationType) => {
  const validTypes = ['fast', 'regular', 'ultra_fast'];
  
  if (!validTypes.includes(stationType)) {
    return 'Invalid station type';
  }
  
  return null;
};

export const validateOptimizationRequest = (requestData) => {
  const errors = {};
  
  const locationError = validateLocation(requestData.location);
  if (locationError) errors.location = locationError;
  
  const radiusError = validateRadius(requestData.radius_km);
  if (radiusError) errors.radius_km = radiusError;
  
  const budgetError = validateBudget(requestData.budget);
  if (budgetError) errors.budget = budgetError;
  
  const stationTypeError = validateStationType(requestData.station_type);
  if (stationTypeError) errors.station_type = stationTypeError;
  
  return Object.keys(errors).length > 0 ? errors : null;
};