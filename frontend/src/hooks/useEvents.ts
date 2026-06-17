"use client";

import { useState, useEffect } from "react";
import type { Event, Source, SourcesFile } from "@/lib/types";

interface UseEventsResult {
  events: Event[];
  sources: Source[];
  loading: boolean;
  error: string | null;
}

export function useEvents(): UseEventsResult {
  const [events, setEvents] = useState<Event[]>([]);
  const [sources, setSources] = useState<Source[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        const [eventsRes, sourcesRes] = await Promise.all([
          fetch(`${process.env.NEXT_PUBLIC_BASE_PATH || ""}/data/events-upcoming.json`),
          fetch(`${process.env.NEXT_PUBLIC_BASE_PATH || ""}/scraper/sources.json`),
        ]);

        if (!eventsRes.ok) throw new Error(`Events fetch failed: ${eventsRes.status}`);
        if (!sourcesRes.ok) throw new Error(`Sources fetch failed: ${sourcesRes.status}`);

        const eventsData: Event[] = await eventsRes.json();
        const sourcesData: SourcesFile = await sourcesRes.json();

        setEvents(eventsData);
        setSources(sourcesData.sources.filter((s) => s.enabled));
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to load events");
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  return { events, sources, loading, error };
}
