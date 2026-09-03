import { useState, useCallback } from "react";

export function useResource<T>(
  service: {
    list: (params?: any) => Promise<any>;
    update: (id: string, payload: Record<string, unknown>) => Promise<T>;
  },
  keyName: string,
  idField: string = "user_id"
) {
  const [items, setItems] = useState<T[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const list = useCallback(async (params?: Record<string, unknown>) => {
    setLoading(true);
    setError(null);
    try {
      const result = await service.list(params);
      setItems(result[keyName] || []);
      return result;
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to load items";
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [service, keyName]);

  const update = useCallback(async (id: string, payload: Record<string, unknown>) => {
    setLoading(true);
    setError(null);
    try {
      const updated = await service.update(id, payload);
      setItems((prev) => prev.map((item: any) => (item[idField] === id ? updated : item)));
      return updated;
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to update item";
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [service, idField]);

  return {
    items,
    loading,
    error,
    list,
    update,
  };
}
