"use client";

import { useState, useMemo, useEffect, useCallback } from "react";
import { Calendar } from "@/components/Calendar";
import { EventModal } from "@/components/EventModal";
import { CategoryFilter } from "@/components/CategoryFilter";
import { SettingsMenu } from "@/components/SettingsMenu";
import { InterestedList } from "@/components/InterestedList";
import { useEvents } from "@/hooks/useEvents";
import { useInterested } from "@/hooks/useInterested";
import { useTheme } from "@/hooks/useTheme";
import { Button } from "@/components/ui/button";
import type { Event } from "@/lib/types";

const SOURCES_STORAGE_KEY = "nyc-events-enabled-sources";

function readEnabledSources(allSourceIds: string[]): Set<string> {
  if (typeof window === "undefined") return new Set(allSourceIds);
  try {
    const raw = localStorage.getItem(SOURCES_STORAGE_KEY);
    if (raw) return new Set(JSON.parse(raw));
  } catch {}
  return new Set(allSourceIds);
}

export default function Home() {
  const { events, sources, loading, error } = useEvents();
  const { interestedIds, toggle, isInterested } = useInterested();
  const { isDark, toggle: toggleTheme } = useTheme();

  const [activeCategories, setActiveCategories] = useState<Set<string>>(new Set(["all"]));
  const [enabledSources, setEnabledSources] = useState<Set<string>>(new Set());
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);
  const [modalOpen, setModalOpen] = useState(false);

  useEffect(() => {
    if (sources.length > 0) {
      const ids = sources.map((s) => s.id);
      setEnabledSources(readEnabledSources(ids));
    }
  }, [sources]);

  const handleToggleSource = useCallback((sourceId: string) => {
    setEnabledSources((prev) => {
      const next = new Set(prev);
      if (next.has(sourceId)) {
        next.delete(sourceId);
      } else {
        next.add(sourceId);
      }
      localStorage.setItem(SOURCES_STORAGE_KEY, JSON.stringify([...next]));
      return next;
    });
  }, []);

  const filteredEvents = useMemo(() => {
    return events
      .filter(
        (e) => activeCategories.has("all") || activeCategories.has(e.category || "")
      )
      .filter((e) => enabledSources.has(e.source_id));
  }, [events, activeCategories, enabledSources]);

  const handleEventClick = useCallback((event: Event) => {
    setSelectedEvent(event);
    setModalOpen(true);
  }, []);

  const selectedSource = useMemo(
    () => sources.find((s) => s.id === selectedEvent?.source_id),
    [sources, selectedEvent]
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <p className="text-muted-foreground">Loading events...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen">
        <p className="text-red-500">Error: {error}</p>
      </div>
    );
  }

  return (
    <main className="h-screen flex flex-col p-4">
      <header className="flex items-center justify-between mb-2">
        <h1 className="text-xl font-bold">NYC Events</h1>
        <div className="flex items-center gap-1">
          <Button variant="ghost" size="sm" onClick={toggleTheme} aria-label="Toggle theme">
            {isDark ? "☀" : "☾"}
          </Button>
          <InterestedList
            events={events}
            sources={sources}
            interestedIds={interestedIds}
            onEventClick={handleEventClick}
          />
          <SettingsMenu
            sources={sources}
            enabledSources={enabledSources}
            onToggleSource={handleToggleSource}
          />
        </div>
      </header>

      <CategoryFilter
        activeCategories={activeCategories}
        onChange={setActiveCategories}
      />

      <div className="flex-1 min-h-0">
        <Calendar events={filteredEvents} onEventClick={handleEventClick} isDark={isDark} />
      </div>

      <EventModal
        event={selectedEvent}
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        isInterested={selectedEvent ? isInterested(selectedEvent.id) : false}
        onToggleInterested={() => selectedEvent && toggle(selectedEvent.id)}
        source={selectedSource}
      />
    </main>
  );
}
