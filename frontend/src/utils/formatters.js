// frontend/src/utils/formatters.js
export const formatCurrency = (amount, currency = 'INR', locale = 'en-IN') => {
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 2
  }).format(amount);
};

export const formatNumber = (number, locale = 'en-IN') => {
  return new Intl.NumberFormat(locale).format(number);
};

export const formatLakhs = (amount) => {
  const lakhs = amount / 100000;
  return `₹${lakhs.toFixed(1)}L`;
};

export const formatCrores = (amount) => {
  const crores = amount / 10000000;
  return `₹${crores.toFixed(2)}Cr`;
};

export const formatDistance = (distanceKm) => {
  if (distanceKm < 1) {
    return `${Math.round(distanceKm * 1000)}m`;
  }
  return `${distanceKm.toFixed(1)}km`;
};

export const formatDuration = (months) => {
  if (months < 12) {
    return `${months} month${months !== 1 ? 's' : ''}`;
  }
  const years = Math.floor(months / 12);
  const remainingMonths = months % 12;
  
  if (remainingMonths === 0) {
    return `${years} year${years !== 1 ? 's' : ''}`;
  }
  
  return `${years}y ${remainingMonths}m`;
};

export const formatScore = (score) => {
  return score.toFixed(1);
};

export const getScoreColor = (score) => {
  if (score >= 8) return 'text-green-600';
  if (score >= 6) return 'text-blue-600';
  if (score >= 4) return 'text-yellow-600';
  return 'text-red-600';
};

export const getScoreBackgroundColor = (score) => {
  if (score >= 8) return 'bg-green-100';
  if (score >= 6) return 'bg-blue-100';
  if (score >= 4) return 'bg-yellow-100';
  return 'bg-red-100';
};