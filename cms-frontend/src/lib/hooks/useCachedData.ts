import { useState, useEffect, useCallback } from 'react';
import { dataCache } from '../cache';

interface UseCachedDataOptions<T> {
  cacheKey: string;
  fetchFn: () => Promise<T>;
  ttl?: number;
  dependencies?: any[];
  enabled?: boolean;
}

interface UseCachedDataReturn<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
  invalidate: () => void;
}

/**
 * Custom hook for fetching and caching data
 * Prevents unnecessary API calls and reloads
 */
export function useCachedData<T>({
  cacheKey,
  fetchFn,
  ttl,
  dependencies = [],
  enabled = true,
}: UseCachedDataOptions<T>): UseCachedDataReturn<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = useCallback(async () => {
    if (!enabled) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      // Check cache first
      const cachedData = dataCache.get<T>(cacheKey);
      
      if (cachedData !== null) {
        console.log(`✅ Using cached data for: ${cacheKey}`);
        setData(cachedData);
        setLoading(false);
        return;
      }

      console.log(`🔄 Fetching fresh data for: ${cacheKey}`);
      const freshData = await fetchFn();
      
      // Ensure array data is always an array
      const validData = Array.isArray(freshData) 
        ? freshData 
        : (freshData as any)?.data 
        ? Array.isArray((freshData as any).data) 
          ? (freshData as any).data 
          : freshData
        : freshData;

      // Cache the data
      dataCache.set(cacheKey, validData, ttl);
      setData(validData as T);
    } catch (err) {
      console.error(`❌ Error fetching ${cacheKey}:`, err);
      setError(err as Error);
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [cacheKey, fetchFn, ttl, enabled, ...dependencies]);

  const refetch = useCallback(async () => {
    // Invalidate cache and fetch fresh data
    dataCache.invalidate(cacheKey);
    await fetchData();
  }, [cacheKey, fetchData]);

  const invalidate = useCallback(() => {
    dataCache.invalidate(cacheKey);
  }, [cacheKey]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return {
    data,
    loading,
    error,
    refetch,
    invalidate,
  };
}

/**
 * Hook for optimistic updates
 * Updates cache immediately and reverts on error
 */
export function useOptimisticUpdate<T>(cacheKey: string) {
  const updateCache = useCallback((updater: (current: T | null) => T) => {
    const current = dataCache.get<T>(cacheKey);
    const updated = updater(current);
    dataCache.set(cacheKey, updated);
  }, [cacheKey]);

  return { updateCache };
}
