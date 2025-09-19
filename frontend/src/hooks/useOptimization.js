
import { useState, useCallback } from 'react';
import { optimizationAPI } from '../services/api';

export const useOptimization = () => {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [requestId, setRequestId] = useState(null);
  const [processingTime, setProcessingTime] = useState(null);

  const optimizeLocation = useCallback(async (requestData) => {
    setLoading(true);
    setError(null);
    setRecommendations([]);

    try {
      console.log('Optimizing location with data:', requestData);
      
      const response = await optimizationAPI.optimize(requestData);
      
      console.log('Optimization response:', response);
      
      setRecommendations(response.recommendations || []);
      setRequestId(response.request_id);
      setProcessingTime(response.processing_time_seconds);

    
      if (response.metadata?.errors?.length > 0) {
        console.warn('Optimization completed with warnings:', response.metadata.errors);
        setError(`Warning: ${response.metadata.errors.join(', ')}`);
      }

    } catch (err) {
      console.error('Optimization failed:', err);
      setError(err.message || 'Failed to get recommendations');
      setRecommendations([]);
    } finally {
      setLoading(false);
    }
  }, []);

  const clearResults = useCallback(() => {
    setRecommendations([]);
    setError(null);
    setRequestId(null);
    setProcessingTime(null);
  }, []);

  return {
    recommendations,
    loading,
    error,
    requestId,
    processingTime,
    optimizeLocation,
    clearResults
  };
};
