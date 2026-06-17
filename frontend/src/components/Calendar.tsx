"use client";

import { useEffect, useState } from "react";
import { ScheduleXCalendar, useCalendarApp } from "@schedule-x/react";
import {
  createViewDay,
  createViewWeek,
  createViewMonthGrid,
} from "@schedule-x/calendar";
import { createEventsServicePlugin } from "@schedule-x/events-service";
import "temporal-polyfill/global";
import type { Event } from "@/lib/types";

const CATEGORY_COLORS: Record<string, string> = {
  museum: "#3b82f6",
  outdoor: "#22c55e",
  film: "#a855f7",
  theater: "#ef4444",
  "performing-arts": "#f97316",
};

interface CalendarProps {
  events: Event[];
  onEventClick: (event: Event) => void;
}

function toScheduleXEvent(event: Event) {
  const start = event.start_time
    ? `${event.start_date} ${event.start_time}`
    : event.start_date;

  let end: string | undefined;
  if (event.end_date && event.end_date !== event.start_date) {
    end = event.end_time
      ? `${event.end_date} ${event.end_time}`
      : event.end_date;
  } else if (event.end_time) {
    end = `${event.start_date} ${event.end_time}`;
  }

  return {
    id: event.id,
    title: event.title,
    start,
    end: end || start,
    calendarId: event.category || "default",
    _originalEvent: event,
  };
}

export function Calendar({ events, onEventClick }: CalendarProps) {
  const [eventsPlugin] = useState(() => createEventsServicePlugin());

  const calendar = useCalendarApp({
    views: [createViewMonthGrid(), createViewWeek(), createViewDay()],
    defaultView: "month-grid",
    events: [],
    calendars: {
      museum: {
        colorName: "museum",
        lightColors: { main: CATEGORY_COLORS.museum, container: "#dbeafe", onContainer: "#1e3a5f" },
        darkColors: { main: CATEGORY_COLORS.museum, container: "#1e3a5f", onContainer: "#dbeafe" },
      },
      outdoor: {
        colorName: "outdoor",
        lightColors: { main: CATEGORY_COLORS.outdoor, container: "#dcfce7", onContainer: "#14532d" },
        darkColors: { main: CATEGORY_COLORS.outdoor, container: "#14532d", onContainer: "#dcfce7" },
      },
      film: {
        colorName: "film",
        lightColors: { main: CATEGORY_COLORS.film, container: "#f3e8ff", onContainer: "#3b0764" },
        darkColors: { main: CATEGORY_COLORS.film, container: "#3b0764", onContainer: "#f3e8ff" },
      },
      theater: {
        colorName: "theater",
        lightColors: { main: CATEGORY_COLORS.theater, container: "#fee2e2", onContainer: "#7f1d1d" },
        darkColors: { main: CATEGORY_COLORS.theater, container: "#7f1d1d", onContainer: "#fee2e2" },
      },
      "performing-arts": {
        colorName: "performing-arts",
        lightColors: { main: CATEGORY_COLORS["performing-arts"], container: "#ffedd5", onContainer: "#7c2d12" },
        darkColors: { main: CATEGORY_COLORS["performing-arts"], container: "#7c2d12", onContainer: "#ffedd5" },
      },
      default: {
        colorName: "default",
        lightColors: { main: "#6b7280", container: "#f3f4f6", onContainer: "#1f2937" },
        darkColors: { main: "#6b7280", container: "#1f2937", onContainer: "#f3f4f6" },
      },
    },
    callbacks: {
      onEventClick(calendarEvent) {
        const original = calendarEvent._originalEvent as Event | undefined;
        if (original) onEventClick(original);
      },
    },
    plugins: [eventsPlugin],
  });

  useEffect(() => {
    if (eventsPlugin) {
      eventsPlugin.set(events.map(toScheduleXEvent));
    }
  }, [events, eventsPlugin]);

  return (
    <div className="sx-react-calendar-wrapper">
      <ScheduleXCalendar calendarApp={calendar} />
    </div>
  );
}
