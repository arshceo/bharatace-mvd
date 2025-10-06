// Cache utility for optimizing API calls and preventing unnecessary reloads
// Implements intelligent caching with automatic invalidation

interface CacheEntry<T> {
  data: T;
  timestamp: number;
  ttl: number; // Time to live in milliseconds
}

class DataCache {
  private cache: Map<string, CacheEntry<any>>;
  private readonly DEFAULT_TTL = 5 * 60 * 1000; // 5 minutes default

  constructor() {
    this.cache = new Map();
  }

  /**
   * Get data from cache if valid, otherwise return null
   */
  get<T>(key: string): T | null {
    const entry = this.cache.get(key);
    
    if (!entry) {
      return null;
    }

    const isExpired = Date.now() - entry.timestamp > entry.ttl;
    
    if (isExpired) {
      this.cache.delete(key);
      return null;
    }

    return entry.data as T;
  }

  /**
   * Set data in cache with optional TTL
   */
  set<T>(key: string, data: T, ttl?: number): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl: ttl || this.DEFAULT_TTL,
    });
  }

  /**
   * Invalidate specific cache entry
   */
  invalidate(key: string): void {
    this.cache.delete(key);
  }

  /**
   * Invalidate all cache entries matching a pattern
   */
  invalidatePattern(pattern: string): void {
    const regex = new RegExp(pattern);
    const keys = Array.from(this.cache.keys());
    
    keys.forEach(key => {
      if (regex.test(key)) {
        this.cache.delete(key);
      }
    });
  }

  /**
   * Clear all cache
   */
  clear(): void {
    this.cache.clear();
  }

  /**
   * Check if cache has valid entry
   */
  has(key: string): boolean {
    const data = this.get(key);
    return data !== null;
  }
}

// Singleton instance
export const dataCache = new DataCache();

// Cache key generators
export const CacheKeys = {
  students: (filters?: string) => `students${filters ? `-${filters}` : ''}`,
  student: (id: string) => `student-${id}`,
  marks: (filters?: string) => `marks${filters ? `-${filters}` : ''}`,
  attendance: (filters?: string) => `attendance${filters ? `-${filters}` : ''}`,
  fees: (filters?: string) => `fees${filters ? `-${filters}` : ''}`,
  subjects: () => 'subjects',
  events: () => 'events',
  library: () => 'library-books',
  dashboard: () => 'dashboard-stats',
};

// Cache invalidation helpers
export const invalidateCache = {
  students: () => {
    dataCache.invalidatePattern('^students');
    dataCache.invalidate(CacheKeys.dashboard());
  },
  marks: () => {
    dataCache.invalidatePattern('^marks');
    dataCache.invalidate(CacheKeys.dashboard());
  },
  attendance: () => {
    dataCache.invalidatePattern('^attendance');
    dataCache.invalidate(CacheKeys.dashboard());
  },
  fees: () => {
    dataCache.invalidatePattern('^fees');
    dataCache.invalidate(CacheKeys.dashboard());
  },
  subjects: () => {
    dataCache.invalidate(CacheKeys.subjects());
  },
  events: () => {
    dataCache.invalidate(CacheKeys.events());
  },
  library: () => {
    dataCache.invalidate(CacheKeys.library());
  },
  all: () => {
    dataCache.clear();
  },
};
