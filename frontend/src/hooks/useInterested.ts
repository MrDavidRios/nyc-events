"use client";

import { useState, useCallback, useEffect } from "react";

const STORAGE_KEY = "nyc-events-interested";

function readFromStorage(): Set<string> {
  if (typeof window === "undefined") return new Set();
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? new Set(JSON.parse(raw)) : new Set();
  } catch {
    return new Set();
  }
}

export function useInterested() {
  const [interestedIds, setInterestedIds] = useState<Set<string>>(new Set());

  useEffect(() => {
    setInterestedIds(readFromStorage());
  }, []);

  const toggle = useCallback((id: string) => {
    setInterestedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      localStorage.setItem(STORAGE_KEY, JSON.stringify([...next]));
      return next;
    });
  }, []);

  const isInterested = useCallback(
    (id: string) => interestedIds.has(id),
    [interestedIds]
  );

  return { interestedIds, toggle, isInterested };
}
