"use client";

import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Button } from "@/components/ui/button";
import type { Event, Source } from "@/lib/types";

interface InterestedListProps {
  events: Event[];
  sources: Source[];
  interestedIds: Set<string>;
  onEventClick: (event: Event) => void;
}

export function InterestedList({
  events,
  sources,
  interestedIds,
  onEventClick,
}: InterestedListProps) {
  const interestedEvents = events
    .filter((e) => interestedIds.has(e.id))
    .sort((a, b) => a.start_date.localeCompare(b.start_date));

  const sourceMap = new Map(sources.map((s) => [s.id, s]));

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="ghost" size="sm" aria-label="Interested events">
          ★{interestedIds.size > 0 && ` ${interestedIds.size}`}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-72" align="end">
        <h4 className="font-medium text-sm mb-2">Interested Events</h4>
        {interestedEvents.length === 0 ? (
          <p className="text-sm text-muted-foreground">No events marked yet</p>
        ) : (
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {interestedEvents.map((event) => {
              const source = sourceMap.get(event.source_id);
              return (
                <button
                  key={event.id}
                  className="w-full text-left p-2 rounded hover:bg-muted transition-colors"
                  onClick={() => onEventClick(event)}
                >
                  <p className="text-sm font-medium truncate">{event.title}</p>
                  <div className="flex items-center gap-1 text-xs text-muted-foreground">
                    {source?.favicon_url && (
                      <img src={source.favicon_url} alt="" className="w-3 h-3" />
                    )}
                    <span>{event.start_date}</span>
                  </div>
                </button>
              );
            })}
          </div>
        )}
      </PopoverContent>
    </Popover>
  );
}
